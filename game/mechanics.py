"""Game mechanics helpers: portals, gates, and pressure plates."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from game.entities import Gate, PortalPair, PressurePlate

GridPos = Tuple[int, int]


def apply_portal(entity_pos: GridPos, portals: Sequence[PortalPair]) -> GridPos:
    """Teleport an entity if it stands on a portal tile."""
    for portal in portals:
        other = portal.other_side(entity_pos)
        if other is not None:
            return other
    return entity_pos


def update_pressure_plates(
    player_pos: GridPos,
    box_positions: Iterable[GridPos],
    pressure_plates: List[PressurePlate],
    gates: List[Gate],
) -> None:
    """Update plate pressed states and gate open/close states."""
    box_pos_set = set(box_positions)

    pressed_gate_ids = set()
    for plate in pressure_plates:
        plate.is_pressed = (plate.pos == player_pos) or (plate.pos in box_pos_set)
        if plate.is_pressed:
            for gid in plate.gate_ids:
                pressed_gate_ids.add(gid)

    for gate in gates:
        gate.is_open = gate.gate_id in pressed_gate_ids


def is_gate_blocking(pos: GridPos, gates: Sequence[Gate]) -> bool:
    for gate in gates:
        if gate.pos == pos and not gate.is_open:
            return True
    return False
