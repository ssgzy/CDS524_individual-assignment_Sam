"""Fixed environment with proper reward shaping based on human play analysis"""

from __future__ import annotations

from typing import Tuple, Dict
import numpy as np
from game.environment import ShadowBoxEnv


class FixedEnv:
    """
    Fixed environment with proper reward shaping.

    Key insights from human play:
    - Level 2 can be solved in ~13 steps
    - 200 max_steps is MORE than enough
    - Problem is reward function, not max_steps
    """

    def __init__(self, level_id: int = 1, local_view_size: int = 7):
        self.env = ShadowBoxEnv(level_id=level_id)
        self.local_view_size = local_view_size
        self.action_space_size = self.env.action_space_size

        # Track for reward shaping
        self.prev_boxes_on_target = 0

    def reset(self) -> np.ndarray:
        """Reset environment and return CNN state."""
        self.env.reset()
        self.prev_boxes_on_target = sum(1 for box in self.env.boxes if self.env.is_box_on_target(box))
        return self._get_cnn_state()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """Step environment with FIXED rewards."""
        # Take action in base environment
        _, base_reward, done, info = self.env.step(action)

        # Get new state
        next_state = self._get_cnn_state()

        # === SIMPLIFIED REWARD FUNCTION ===
        reward = 0.0

        # 1. Small step penalty (encourage efficiency)
        reward -= 0.1

        # 2. Box placed on target - BIG reward
        curr_boxes_on_target = sum(1 for box in self.env.boxes if self.env.is_box_on_target(box))
        if curr_boxes_on_target > self.prev_boxes_on_target:
            reward += 50.0  # Much bigger than step penalty
        elif curr_boxes_on_target < self.prev_boxes_on_target:
            reward -= 20.0  # Penalty for removing box from target
        self.prev_boxes_on_target = curr_boxes_on_target

        # 3. Success - HUGE reward
        if info.get('success'):
            reward += 100.0

        # 4. Deadlock - penalty
        if info.get('deadlock'):
            reward -= 30.0

        # 5. Timeout - small penalty (not too harsh)
        if info.get('timeout'):
            reward -= 10.0

        # NO exploration bonus
        # NO distance rewards (they were causing problems)
        # Keep it simple!

        return next_state, reward, done, info

    def _get_cnn_state(self) -> np.ndarray:
        """Get CNN-friendly state representation."""
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
                    if hasattr(portal, 'entrance') and portal.entrance == (world_x, world_y):
                        state[6, local_y, local_x] = 1.0
                    elif hasattr(portal, 'exit') and portal.exit == (world_x, world_y):
                        state[6, local_y, local_x] = 0.5

        # Player (always at center)
        state[3, half_size, half_size] = 1.0

        return state

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
