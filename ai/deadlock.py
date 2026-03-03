"""Deadlock detection for Sokoban-like states."""

from __future__ import annotations

from typing import Iterable, Set, Tuple

GridPos = Tuple[int, int]


class DeadlockDetector:
    """Detect corner, edge, and freeze deadlocks."""

    def is_corner_deadlock(
        self,
        box_pos: GridPos,
        walls: Set[GridPos],
        targets: Set[GridPos],
    ) -> bool:
        if box_pos in targets:
            return False

        x, y = box_pos
        blocked_up = (x, y - 1) in walls
        blocked_down = (x, y + 1) in walls
        blocked_left = (x - 1, y) in walls
        blocked_right = (x + 1, y) in walls

        corners = [
            blocked_up and blocked_left,
            blocked_up and blocked_right,
            blocked_down and blocked_left,
            blocked_down and blocked_right,
        ]
        return any(corners)

    def is_edge_deadlock(
        self,
        box_pos: GridPos,
        walls: Set[GridPos],
        targets: Set[GridPos],
        map_width: int,
        map_height: int,
    ) -> bool:
        if box_pos in targets:
            return False

        x, y = box_pos

        # Touching horizontal wall with no target in the same row.
        if (x, y - 1) in walls or (x, y + 1) in walls:
            if not any(t[1] == y for t in targets):
                return True

        # Touching vertical wall with no target in the same column.
        if (x - 1, y) in walls or (x + 1, y) in walls:
            if not any(t[0] == x for t in targets):
                return True

        # Extra boundary safety if map has open borders.
        if (x == 0 or x == map_width - 1) and not any(t[0] == x for t in targets):
            return True
        if (y == 0 or y == map_height - 1) and not any(t[1] == y for t in targets):
            return True

        return False

    def is_freeze_deadlock(
        self,
        box_pos: GridPos,
        all_boxes: Set[GridPos],
        walls: Set[GridPos],
        targets: Set[GridPos],
    ) -> bool:
        def is_frozen(pos: GridPos, visited: Set[GridPos]) -> bool:
            if pos in visited:
                return True
            if pos in targets:
                return False

            visited = set(visited)
            visited.add(pos)
            x, y = pos

            left_frozen = ((x - 1, y) in walls) or (
                (x - 1, y) in all_boxes and is_frozen((x - 1, y), visited)
            )
            right_frozen = ((x + 1, y) in walls) or (
                (x + 1, y) in all_boxes and is_frozen((x + 1, y), visited)
            )
            up_frozen = ((x, y - 1) in walls) or (
                (x, y - 1) in all_boxes and is_frozen((x, y - 1), visited)
            )
            down_frozen = ((x, y + 1) in walls) or (
                (x, y + 1) in all_boxes and is_frozen((x, y + 1), visited)
            )

            h_frozen = left_frozen and right_frozen
            v_frozen = up_frozen and down_frozen
            return h_frozen and v_frozen

        return is_frozen(box_pos, set())

    def is_deadlock(self, game_state) -> bool:
        """game_state must expose boxes, targets, walls, map_width, map_height."""
        walls_set = set(game_state.walls)
        targets_set = {(t.x, t.y) for t in game_state.targets}

        # Build color-aware target sets for corner deadlock only
        color_targets = {}  # color -> set of positions
        for t in game_state.targets:
            if t.color not in color_targets:
                color_targets[t.color] = set()
            color_targets[t.color].add((t.x, t.y))

        boxes_set = {(b.x, b.y) for b in game_state.boxes}

        for box in game_state.boxes:
            pos = (box.x, box.y)
            # Check if box is on a matching-color target
            matching_targets = color_targets.get(box.color, set())
            if pos in matching_targets:
                continue

            # Corner deadlock: use color-specific targets (strict)
            if self.is_corner_deadlock(pos, walls_set, matching_targets):
                return True

            # Edge and freeze: use all targets (lenient, allows repositioning)
            if self.is_edge_deadlock(
                pos,
                walls_set,
                targets_set,
                game_state.map_width,
                game_state.map_height,
            ):
                return True

            if self.is_freeze_deadlock(pos, boxes_set, walls_set, targets_set):
                return True

        return False
