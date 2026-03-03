"""Level definitions and parser for ShadowBox."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from game.entities import (
    BOX_CODE_TO_COLOR,
    EMPTY,
    GATE,
    PLAYER_START,
    PORTAL_A1,
    PORTAL_A2,
    PORTAL_B1,
    PORTAL_B2,
    PRESSURE,
    SUBLEVEL_ENTRANCE,
    TARGET_CODE_TO_COLOR,
    WALL,
    Box,
    Gate,
    LayerState,
    Player,
    PortalPair,
    PressurePlate,
    SublevelSpec,
    Target,
)

Grid = List[List[int]]


@dataclass
class ParsedLevel:
    level_id: int
    max_steps: int
    layers: Dict[str, LayerState]
    start_layer: str = "outer"


def _copy_grid(grid: Grid) -> Grid:
    return [list(row) for row in grid]


def _parse_layer(
    name: str,
    grid: Grid,
    sublevel_layer: Optional[str] = None,
    plate_links: Optional[Dict[int, List[int]]] = None,
) -> LayerState:
    height = len(grid)
    width = len(grid[0]) if height else 0

    walls = []
    boxes = []
    targets = []
    pressure_plates: List[PressurePlate] = []
    gates: List[Gate] = []

    portal_a1 = portal_a2 = None
    portal_b1 = portal_b2 = None
    entrance = None
    player_start = None

    static_map = _copy_grid(grid)

    for y in range(height):
        for x in range(width):
            code = grid[y][x]
            pos = (x, y)

            if code == WALL:
                walls.append(pos)
            elif code == PLAYER_START:
                player_start = pos
                static_map[y][x] = EMPTY
            elif code in BOX_CODE_TO_COLOR:
                boxes.append(Box(x, y, BOX_CODE_TO_COLOR[code]))
                static_map[y][x] = EMPTY
            elif code in TARGET_CODE_TO_COLOR:
                targets.append(Target(x, y, TARGET_CODE_TO_COLOR[code]))
            elif code == PRESSURE:
                plate_id = f"p{len(pressure_plates) + 1}"
                pressure_plates.append(PressurePlate(x, y, plate_id, []))
            elif code == GATE:
                gate_id = f"g{len(gates) + 1}"
                gates.append(Gate(x, y, gate_id, is_open=False))
            elif code == SUBLEVEL_ENTRANCE:
                entrance = pos
            elif code == PORTAL_A1:
                portal_a1 = pos
            elif code == PORTAL_A2:
                portal_a2 = pos
            elif code == PORTAL_B1:
                portal_b1 = pos
            elif code == PORTAL_B2:
                portal_b2 = pos

    if player_start is None:
        raise ValueError(f"Layer {name} has no player start")

    portals = []
    if portal_a1 and portal_a2:
        portals.append(PortalPair("A", portal_a1, portal_a2))
    if portal_b1 and portal_b2:
        portals.append(PortalPair("B", portal_b1, portal_b2))

    # Plate -> gate linking. If omitted, every plate controls every gate.
    if pressure_plates:
        if gates:
            if plate_links:
                for plate_idx, gate_idxs in plate_links.items():
                    p_idx = plate_idx - 1
                    if p_idx < 0 or p_idx >= len(pressure_plates):
                        continue
                    gate_ids = []
                    for g_idx in gate_idxs:
                        g_arr_idx = g_idx - 1
                        if 0 <= g_arr_idx < len(gates):
                            gate_ids.append(gates[g_arr_idx].gate_id)
                    pressure_plates[p_idx].gate_ids = gate_ids
                for plate in pressure_plates:
                    if not plate.gate_ids:
                        plate.gate_ids = [g.gate_id for g in gates]
            else:
                for plate in pressure_plates:
                    plate.gate_ids = [g.gate_id for g in gates]
        else:
            for plate in pressure_plates:
                plate.gate_ids = []

    return LayerState(
        name=name,
        width=width,
        height=height,
        static_map=static_map,
        player_start=player_start,
        boxes=boxes,
        targets=targets,
        walls=walls,
        portals=portals,
        pressure_plates=pressure_plates,
        gates=gates,
        sublevel_spec=SublevelSpec(entrance, sublevel_layer) if (entrance and sublevel_layer) else None,
    )


# ---------------------------------------------------------------------------
# Level data
# ---------------------------------------------------------------------------

LEVEL_1_OUTER = [
    [1, 1, 1, 1, 1],
    [1, 2, 0, 0, 1],
    [1, 0, 3, 0, 1],
    [1, 0, 0, 7, 1],
    [1, 1, 1, 1, 1],
]

LEVEL_2_OUTER = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 0, 1],
    [1, 0, 0, 4, 0, 0, 1],
    [1, 0, 15, 0, 0, 0, 1],
    [1, 7, 0, 8, 16, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
]

LEVEL_3_OUTER = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 7, 8, 9, 1],  # 目标点移到右上角
    [1, 0, 3, 0, 1, 0, 0, 4, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 11, 1, 1, 1, 0, 1, 1, 12, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 5, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],  # 原目标点位置清空
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

LEVEL_4_OUTER = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 0, 1, 0, 4, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 17, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 11, 0, 0, 0, 1, 0, 0, 12, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 5, 0, 0, 0, 1, 0, 6, 0, 0, 1],
    [1, 0, 0, 0, 15, 0, 1, 0, 0, 0, 0, 1],
    [1, 7, 0, 8, 16, 0, 1, 9, 0, 10, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

LEVEL_4_SUB = [
    [1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 1],
    [1, 0, 0, 7, 0, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1],
]

LEVEL_5_OUTER = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 0, 0, 1, 0, 4, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 11, 0, 0, 13, 0, 1, 0, 0, 14, 0, 12, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 5, 0, 0, 0, 0, 1, 0, 6, 0, 0, 0, 1],
    [1, 0, 0, 0, 15, 0, 0, 1, 0, 0, 0, 17, 0, 1],
    [1, 0, 18, 0, 0, 0, 0, 1, 0, 15, 0, 0, 0, 1],
    [1, 7, 0, 8, 16, 0, 0, 1, 9, 0, 10, 16, 19, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

LEVEL_5_SUB = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 15, 16, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 7, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]


def load_level(level_id: int) -> ParsedLevel:
    if level_id == 1:
        layers = {"outer": _parse_layer("outer", LEVEL_1_OUTER)}
        return ParsedLevel(level_id=1, max_steps=100, layers=layers)

    if level_id == 2:
        layers = {
            "outer": _parse_layer(
                "outer",
                LEVEL_2_OUTER,
                plate_links={1: [1]},
            )
        }
        return ParsedLevel(level_id=2, max_steps=200, layers=layers)

    if level_id == 3:
        layers = {"outer": _parse_layer("outer", LEVEL_3_OUTER)}
        return ParsedLevel(level_id=3, max_steps=300, layers=layers)

    if level_id == 4:
        layers = {
            "outer": _parse_layer(
                "outer",
                LEVEL_4_OUTER,
                sublevel_layer="sub1",
                plate_links={1: [1]},
            ),
            "sub1": _parse_layer("sub1", LEVEL_4_SUB),
        }
        return ParsedLevel(level_id=4, max_steps=500, layers=layers)

    if level_id == 5:
        layers = {
            "outer": _parse_layer(
                "outer",
                LEVEL_5_OUTER,
                sublevel_layer="sub1",
                plate_links={1: [1], 2: [2]},
            ),
            "sub1": _parse_layer(
                "sub1",
                LEVEL_5_SUB,
                plate_links={1: [1]},
            ),
        }
        return ParsedLevel(level_id=5, max_steps=800, layers=layers)

    raise ValueError(f"Unsupported level id: {level_id}")


def list_levels() -> List[int]:
    return [1, 2, 3, 4, 5]
