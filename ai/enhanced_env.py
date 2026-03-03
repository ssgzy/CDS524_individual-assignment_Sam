"""Enhanced environment wrapper with CNN state representation and improved rewards."""

from __future__ import annotations

from typing import Tuple, Dict
import numpy as np
from game.environment import ShadowBoxEnv


class EnhancedShadowBoxEnv:
    """
    Enhanced environment wrapper that provides:
    1. CNN-friendly state representation (7x7 local map)
    2. Improved reward shaping
    3. Exploration bonuses
    4. Better state encoding
    """

    def __init__(self, level_id: int = 1, local_view_size: int = 7):
        self.env = ShadowBoxEnv(level_id=level_id)
        self.local_view_size = local_view_size
        self.action_space_size = self.env.action_space_size

        # Track visited states for exploration bonus
        self.visited_states = set()
        self.episode_steps = 0

        # Track box-target distances for better reward shaping
        self.prev_min_distances = []

    def reset(self) -> np.ndarray:
        """Reset environment and return CNN state."""
        self.env.reset()
        self.visited_states.clear()
        self.episode_steps = 0
        self.prev_min_distances = self._compute_box_target_distances()
        return self._get_cnn_state()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """Step environment with enhanced rewards."""
        # Get current state hash for exploration
        state_hash = self._get_state_hash()

        # Take action in base environment
        _, base_reward, done, info = self.env.step(action)

        # Get new state
        next_state = self._get_cnn_state()
        self.episode_steps += 1

        # === Enhanced Reward Shaping ===
        reward = base_reward

        # 1. Exploration bonus (encourage visiting new states)
        new_state_hash = self._get_state_hash()
        if new_state_hash not in self.visited_states:
            reward += 0.1  # Exploration bonus (reduced from 1.0 to prevent over-exploration)
            self.visited_states.add(new_state_hash)

        # 2. Distance-based reward (stronger than before)
        curr_distances = self._compute_box_target_distances()
        if self.prev_min_distances and curr_distances:
            distance_improvement = sum(self.prev_min_distances) - sum(curr_distances)
            reward += 2.0 * distance_improvement  # Increased from 0.5 to 2.0
        self.prev_min_distances = curr_distances

        # 3. Sub-goal rewards
        reward += self._compute_subgoal_rewards(info)

        # 4. Penalty for inefficiency (encourage shorter solutions)
        if self.episode_steps > self.env.max_steps * 0.8:
            reward -= 0.2  # Running out of time

        return next_state, reward, done, info

    def _get_cnn_state(self) -> np.ndarray:
        """
        Get CNN-friendly state representation.

        Returns a 7-channel 7x7 local view around the player:
        Channel 0: Walls
        Channel 1: Boxes
        Channel 2: Targets
        Channel 3: Player
        Channel 4: Gates (open/closed)
        Channel 5: Pressure plates
        Channel 6: Portals
        """
        size = self.local_view_size
        half_size = size // 2

        # Initialize channels
        state = np.zeros((7, size, size), dtype=np.float32)

        # Get player position
        px, py = self.env.player.pos

        # Fill local view
        for dy in range(-half_size, half_size + 1):
            for dx in range(-half_size, half_size + 1):
                world_x = px + dx
                world_y = py + dy
                local_x = dx + half_size
                local_y = dy + half_size

                # Out of bounds = wall
                if not self.env.in_bounds((world_x, world_y)):
                    state[0, local_y, local_x] = 1.0
                    continue

                # Walls
                if self.env.is_wall((world_x, world_y)):
                    state[0, local_y, local_x] = 1.0

                # Boxes
                box = self.env.get_box_at((world_x, world_y))
                if box:
                    state[1, local_y, local_x] = 1.0
                    # Mark if box is on target
                    if self.env.is_box_on_target(box):
                        state[1, local_y, local_x] = 2.0

                # Targets
                for target in self.env.targets:
                    if target.pos == (world_x, world_y):
                        state[2, local_y, local_x] = 1.0

                # Gates
                for gate in self.env.gates:
                    if gate.pos == (world_x, world_y):
                        state[4, local_y, local_x] = 1.0 if gate.is_open else 0.5

                # Pressure plates
                for plate in self.env.pressure_plates:
                    if plate.pos == (world_x, world_y):
                        state[5, local_y, local_x] = 1.0 if plate.is_pressed else 0.5

                # Portals
                for portal in self.env.portals:
                    if portal.entrance == (world_x, world_y):
                        state[6, local_y, local_x] = 1.0
                    elif portal.exit == (world_x, world_y):
                        state[6, local_y, local_x] = 0.5

        # Player (always at center)
        state[3, half_size, half_size] = 1.0

        return state

    def _get_state_hash(self) -> str:
        """Get hash of current state for exploration tracking."""
        player_pos = self.env.player.pos
        boxes_pos = tuple(sorted([box.pos for box in self.env.boxes]))
        return f"{player_pos}_{boxes_pos}"

    def _compute_box_target_distances(self) -> list:
        """Compute minimum Manhattan distance from each box to its matching target."""
        distances = []

        for box in self.env.boxes:
            # Find matching targets
            matching_targets = [
                t for t in self.env.targets if t.color == box.color
            ]

            if matching_targets:
                min_dist = min(
                    abs(box.x - t.x) + abs(box.y - t.y) for t in matching_targets
                )
                distances.append(min_dist)

        return distances

    def _compute_subgoal_rewards(self, info: Dict) -> float:
        """Compute rewards for achieving sub-goals."""
        reward = 0.0

        # Reward for entering sublevel
        if info.get("entered_sublevel"):
            reward += 3.0

        # Reward for completing sublevel
        if info.get("sublevel_complete"):
            reward += 5.0

        # Reward for pressing new plates
        # (already handled in base environment)

        # Reward for opening gates
        # (already handled in base environment)

        return reward

    def load_level(self, level_id: int):
        """Load a new level."""
        self.env.load_level(level_id)

    def close(self):
        """Close environment."""
        self.env.close()

    @property
    def level_id(self):
        return self.env.level_id

    @property
    def max_steps(self):
        return self.env.max_steps


class SimplifiedLevelEnv(EnhancedShadowBoxEnv):
    """
    Simplified curriculum levels for faster learning.

    Level 1: 3x3, 1 box, 1 target
    Level 2: 4x4, 1 box, 1 target
    Level 3: 5x5, 2 boxes, 2 targets
    """

    def __init__(self, curriculum_level: int = 1):
        # Map curriculum level to actual level
        # For now, use the original levels but with reduced max_steps
        super().__init__(level_id=curriculum_level)

        # Reduce max steps for faster training
        if curriculum_level == 1:
            self.env.max_steps = 30
        elif curriculum_level == 2:
            self.env.max_steps = 50
        elif curriculum_level == 3:
            self.env.max_steps = 80
        else:
            self.env.max_steps = 100
