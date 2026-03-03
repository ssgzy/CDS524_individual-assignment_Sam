"""ShadowBox environment with Gym-style API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from ai.deadlock import DeadlockDetector
from game.entities import (
    Action,
    Box,
    Gate,
    LayerState,
    Player,
    PressurePlate,
    Target,
    EMPTY,
)
from game.levels import ParsedLevel, load_level
from game.mechanics import apply_portal, is_gate_blocking, update_pressure_plates

MAX_BOXES = 5
MAX_GATES = 3
MAX_PLATES = 3


@dataclass
class Snapshot:
    layer_name: str
    boxes: List[Tuple[int, int, int]]
    box_on_target: List[bool]
    plate_pressed: List[bool]
    gate_open: List[bool]
    sublevel_completed: bool
    remaining_steps: int


class ShadowBoxEnv:
    """Environment supporting layered Sokoban with extra mechanics."""

    action_space_size = 5
    state_dim = 36

    def __init__(self, level_id: int = 1):
        self.deadlock_detector = DeadlockDetector()

        self.level_id = level_id
        self.level: ParsedLevel
        self.layer_templates: Dict[str, LayerState] = {}
        self.layer_runtime: Dict[str, Dict[str, object]] = {}

        self.current_layer_name = "outer"
        self.current_layer = 0  # 0=outer, 1=sub
        self.layer_stack: List[str] = []
        self.permanently_open_gates = set()

        self.sublevel_completed = False
        self.max_steps = 100
        self.remaining_steps = 100
        self.last_action_effective = True

        # Active layer pointers, updated by _bind_active_layer.
        self.map_width = 0
        self.map_height = 0
        self.static_map: List[List[int]] = []
        self.player: Player
        self.boxes: List[Box] = []
        self.targets: List[Target] = []
        self.walls: List[Tuple[int, int]] = []
        self.portals = []
        self.pressure_plates: List[PressurePlate] = []
        self.gates: List[Gate] = []
        self.sublevel_spec = None

        self.load_level(level_id)

    # ------------------------------------------------------------------
    # Level lifecycle
    # ------------------------------------------------------------------

    def load_level(self, level_id: int) -> None:
        self.level_id = level_id
        self.level = load_level(level_id)
        self.layer_templates = self.level.layers
        self.max_steps = self.level.max_steps
        self.reset()

    def reset(self) -> np.ndarray:
        self.layer_runtime = {}
        for layer_name, layer in self.layer_templates.items():
            self.layer_runtime[layer_name] = layer.clone_dynamic()

        self.current_layer_name = self.level.start_layer
        self.current_layer = 0
        self.layer_stack = []
        self.permanently_open_gates = set()
        self.sublevel_completed = False
        self.remaining_steps = self.max_steps
        self.last_action_effective = True

        self._bind_active_layer(self.current_layer_name)
        self._update_mechanics()
        return self.get_state()

    def _bind_active_layer(self, layer_name: str) -> None:
        self.current_layer_name = layer_name
        self.current_layer = 0 if layer_name == "outer" else 1

        template = self.layer_templates[layer_name]
        runtime = self.layer_runtime[layer_name]

        self.map_width = template.width
        self.map_height = template.height
        self.static_map = template.static_map
        self.targets = template.targets
        self.walls = template.walls
        self.portals = template.portals
        self.sublevel_spec = template.sublevel_spec

        self.player = runtime["player"]
        self.boxes = runtime["boxes"]
        self.gates = runtime["gates"]
        self.pressure_plates = runtime["plates"]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def in_bounds(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return 0 <= x < self.map_width and 0 <= y < self.map_height

    def is_wall(self, pos: Tuple[int, int]) -> bool:
        return (pos in self.walls) or is_gate_blocking(pos, self._effective_gates())

    def _effective_gates(self) -> List[Gate]:
        if not self.permanently_open_gates:
            return self.gates

        effective = []
        for gate in self.gates:
            gate_open = gate.is_open or (gate.gate_id in self.permanently_open_gates)
            effective.append(Gate(gate.x, gate.y, gate.gate_id, gate_open))
        return effective

    def get_box_at(self, pos: Tuple[int, int]) -> Optional[Box]:
        for box in self.boxes:
            if box.pos == pos:
                return box
        return None

    def is_box_on_target(self, box: Box) -> bool:
        for target in self.targets:
            if box.pos == target.pos and box.color == target.color:
                return True
        return False

    def all_boxes_on_targets(self) -> bool:
        return all(self.is_box_on_target(box) for box in self.boxes)

    def _update_mechanics(self) -> None:
        update_pressure_plates(
            self.player.pos,
            [b.pos for b in self.boxes],
            self.pressure_plates,
            self.gates,
        )

        if self.current_layer_name == "outer" and self.permanently_open_gates:
            for gate in self.gates:
                if gate.gate_id in self.permanently_open_gates:
                    gate.is_open = True

    def _snapshot(self) -> Snapshot:
        return Snapshot(
            layer_name=self.current_layer_name,
            boxes=[(box.x, box.y, box.color.value) for box in self.boxes],
            box_on_target=[self.is_box_on_target(box) for box in self.boxes],
            plate_pressed=[plate.is_pressed for plate in self.pressure_plates],
            gate_open=[gate.is_open for gate in self.gates],
            sublevel_completed=self.sublevel_completed,
            remaining_steps=self.remaining_steps,
        )

    # ------------------------------------------------------------------
    # State representation
    # ------------------------------------------------------------------

    def get_state(self) -> np.ndarray:
        state: List[float] = []

        state.append(float(self.current_layer))
        state.append(self.player.x / max(1, self.map_width - 1))
        state.append(self.player.y / max(1, self.map_height - 1))

        for i in range(MAX_BOXES):
            if i < len(self.boxes):
                box = self.boxes[i]
                state.append(box.x / max(1, self.map_width - 1))
                state.append(box.y / max(1, self.map_height - 1))
                state.append(1.0 if self.is_box_on_target(box) else 0.0)
            else:
                state.extend([0.0, 0.0, 0.0])

        for i in range(MAX_BOXES):
            if i < len(self.targets):
                target = self.targets[i]
                state.append(target.x / max(1, self.map_width - 1))
                state.append(target.y / max(1, self.map_height - 1))
            else:
                state.extend([0.0, 0.0])

        for i in range(MAX_GATES):
            if i < len(self.gates):
                state.append(1.0 if self.gates[i].is_open else 0.0)
            else:
                state.append(0.0)

        for i in range(MAX_PLATES):
            if i < len(self.pressure_plates):
                state.append(1.0 if self.pressure_plates[i].is_pressed else 0.0)
            else:
                state.append(0.0)

        state.append(1.0 if self.sublevel_completed else 0.0)
        state.append(self.remaining_steps / max(1, self.max_steps))

        return np.array(state, dtype=np.float32)

    # ------------------------------------------------------------------
    # Reward
    # ------------------------------------------------------------------

    def count_newly_placed_boxes(self, prev: Snapshot, curr: Snapshot) -> int:
        n = min(len(prev.box_on_target), len(curr.box_on_target))
        return sum((not prev.box_on_target[i]) and curr.box_on_target[i] for i in range(n))

    def count_newly_removed_boxes(self, prev: Snapshot, curr: Snapshot) -> int:
        n = min(len(prev.box_on_target), len(curr.box_on_target))
        return sum(prev.box_on_target[i] and (not curr.box_on_target[i]) for i in range(n))

    def count_newly_pressed_plates(self, prev: Snapshot, curr: Snapshot) -> int:
        n = min(len(prev.plate_pressed), len(curr.plate_pressed))
        return sum((not prev.plate_pressed[i]) and curr.plate_pressed[i] for i in range(n))

    def count_newly_opened_gates(self, prev: Snapshot, curr: Snapshot) -> int:
        n = min(len(prev.gate_open), len(curr.gate_open))
        return sum((not prev.gate_open[i]) and curr.gate_open[i] for i in range(n))

    def potential_reward(self, prev_state: Snapshot, curr_state: Snapshot) -> float:
        if prev_state.layer_name != curr_state.layer_name:
            return 0.0

        def potential(snap: Snapshot) -> float:
            total_dist = 0
            for bx, by, color_value in snap.boxes:
                matching_targets = [t for t in self.targets if t.color.value == color_value]
                if not matching_targets:
                    continue
                min_dist = min(
                    abs(bx - t.x) + abs(by - t.y) for t in matching_targets
                )
                total_dist += min_dist
            return -0.5 * total_dist

        curr_phi = potential(curr_state)
        prev_phi = potential(prev_state)
        return curr_phi - prev_phi  # Fixed: removed 0.99 coefficient that was causing reward accumulation

    def calculate_reward(
        self,
        prev_snapshot: Snapshot,
        curr_snapshot: Snapshot,
        done: bool,
        info: Dict[str, object],
    ) -> float:
        reward = 0.0

        reward -= 0.1

        reward += 10.0 * self.count_newly_placed_boxes(prev_snapshot, curr_snapshot)
        reward -= 5.0 * self.count_newly_removed_boxes(prev_snapshot, curr_snapshot)

        reward += 3.0 * self.count_newly_pressed_plates(prev_snapshot, curr_snapshot)
        reward += 5.0 * self.count_newly_opened_gates(prev_snapshot, curr_snapshot)

        if (not prev_snapshot.sublevel_completed) and curr_snapshot.sublevel_completed:
            reward += 20.0

        if info.get("success"):
            reward += 100.0

        if info.get("deadlock"):
            reward -= 50.0

        if self.remaining_steps <= 0:
            reward -= 20.0

        if not self.last_action_effective:
            reward -= 0.5

        reward += self.potential_reward(prev_snapshot, curr_snapshot)

        return reward

    # ------------------------------------------------------------------
    # Transition logic
    # ------------------------------------------------------------------

    def _enter_sublevel(self) -> Tuple[np.ndarray, float, bool, Dict[str, object]]:
        self.last_action_effective = False

        if self.sublevel_spec and self.player.pos == self.sublevel_spec.entrance:
            if self.sublevel_spec.layer_name in self.layer_templates:
                parent = self.current_layer_name
                self.layer_stack.append(parent)
                self._bind_active_layer(self.sublevel_spec.layer_name)
                self._update_mechanics()
                self.last_action_effective = True
                return self.get_state(), 0.5, False, {"entered_sublevel": True}

        # Allow manual return from sublevel with ENTER.
        if self.layer_stack:
            parent = self.layer_stack.pop()
            self._bind_active_layer(parent)
            self._update_mechanics()
            self.last_action_effective = True
            return self.get_state(), -0.05, False, {"returned_to_outer": True}

        return self.get_state(), -0.1, False, {"reason": "invalid_enter"}

    def _handle_sublevel_complete(self, info: Dict[str, object]) -> None:
        self.sublevel_completed = True
        info["sublevel_complete"] = True

        if "outer" in self.layer_runtime:
            for gate in self.layer_runtime["outer"]["gates"]:
                self.permanently_open_gates.add(gate.gate_id)
                gate.is_open = True

        if self.layer_stack:
            parent = self.layer_stack.pop()
            self._bind_active_layer(parent)
            self._update_mechanics()

    def _check_terminal(self, info: Dict[str, object]) -> bool:
        if self.remaining_steps <= 0:
            info["timeout"] = True
            return True

        if self.deadlock_detector.is_deadlock(self):
            info["deadlock"] = True
            return True

        if self.all_boxes_on_targets():
            if self.current_layer_name != "outer":
                self._handle_sublevel_complete(info)
                return False

            requires_sublevel = self.layer_templates["outer"].sublevel_spec is not None
            if (not requires_sublevel) or self.sublevel_completed:
                info["success"] = True
                return True

        return False

    def step(self, action: int):
        if isinstance(action, int):
            action = Action(action)

        self.remaining_steps -= 1
        prev_snapshot = self._snapshot()
        info: Dict[str, object] = {}

        if action == Action.ENTER:
            next_state, base_reward, done, enter_info = self._enter_sublevel()
            info.update(enter_info)
            curr_snapshot = self._snapshot()
            reward = base_reward + self.calculate_reward(prev_snapshot, curr_snapshot, done, info)
            return next_state, reward, done, info

        move = {
            Action.UP: (0, -1),
            Action.DOWN: (0, 1),
            Action.LEFT: (-1, 0),
            Action.RIGHT: (1, 0),
        }
        dx, dy = move[action]

        self.last_action_effective = False
        curr_player_pos = self.player.pos
        new_player_pos = (curr_player_pos[0] + dx, curr_player_pos[1] + dy)

        if not self.in_bounds(new_player_pos) or self.is_wall(new_player_pos):
            curr_snapshot = self._snapshot()
            done = self._check_terminal(info)
            reward = self.calculate_reward(prev_snapshot, curr_snapshot, done, info)
            return self.get_state(), reward, done, info

        box = self.get_box_at(new_player_pos)
        if box is not None:
            new_box_pos = (box.x + dx, box.y + dy)
            blocked = (
                (not self.in_bounds(new_box_pos))
                or self.is_wall(new_box_pos)
                or (self.get_box_at(new_box_pos) is not None)
            )
            if blocked:
                curr_snapshot = self._snapshot()
                done = self._check_terminal(info)
                reward = self.calculate_reward(prev_snapshot, curr_snapshot, done, info)
                return self.get_state(), reward, done, info

            # Move box then apply portal.
            box.pos = new_box_pos
            teleported_box_pos = apply_portal(box.pos, self.portals)
            if teleported_box_pos != box.pos:
                if (
                    self.in_bounds(teleported_box_pos)
                    and (not self.is_wall(teleported_box_pos))
                    and (self.get_box_at(teleported_box_pos) is None)
                ):
                    box.pos = teleported_box_pos
                else:
                    # Portal exit blocked: revert move as invalid.
                    box.pos = (box.x - dx, box.y - dy)
                    curr_snapshot = self._snapshot()
                    done = self._check_terminal(info)
                    reward = self.calculate_reward(prev_snapshot, curr_snapshot, done, info)
                    return self.get_state(), reward, done, info

        # Move player.
        self.player.pos = new_player_pos

        # Player portal.
        teleported_player_pos = apply_portal(self.player.pos, self.portals)
        if teleported_player_pos != self.player.pos:
            if (
                self.in_bounds(teleported_player_pos)
                and (not self.is_wall(teleported_player_pos))
                and (self.get_box_at(teleported_player_pos) is None)
            ):
                self.player.pos = teleported_player_pos

        self.last_action_effective = True
        self._update_mechanics()

        done = self._check_terminal(info)
        curr_snapshot = self._snapshot()
        reward = self.calculate_reward(prev_snapshot, curr_snapshot, done, info)

        return self.get_state(), reward, done, info

    # ------------------------------------------------------------------
    # Renderer support
    # ------------------------------------------------------------------

    def get_cell(self, x: int, y: int) -> int:
        return self.static_map[y][x]

    def get_entity_at(self, x: int, y: int):
        if self.player.pos == (x, y):
            return ("player", self.player)

        for box in self.boxes:
            if box.pos == (x, y):
                return ("box", box)

        for gate in self.gates:
            if gate.pos == (x, y):
                return ("gate", gate)

        return None

    def close(self) -> None:
        return
