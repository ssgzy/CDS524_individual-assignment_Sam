"""Core entities and constants for ShadowBox."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple

GridPos = Tuple[int, int]


class BoxColor(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    PURPLE = 5


class Action(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    ENTER = 4


# Map codes
EMPTY = 0
WALL = 1
PLAYER_START = 2
BOX_RED = 3
BOX_BLUE = 4
BOX_GREEN = 5
BOX_YELLOW = 6
TARGET_RED = 7
TARGET_BLUE = 8
TARGET_GREEN = 9
TARGET_YELLOW = 10
PORTAL_A1 = 11
PORTAL_A2 = 12
PORTAL_B1 = 13
PORTAL_B2 = 14
PRESSURE = 15
GATE = 16
SUBLEVEL_ENTRANCE = 17
BOX_PURPLE = 18
TARGET_PURPLE = 19


BOX_CODE_TO_COLOR: Dict[int, BoxColor] = {
    BOX_RED: BoxColor.RED,
    BOX_BLUE: BoxColor.BLUE,
    BOX_GREEN: BoxColor.GREEN,
    BOX_YELLOW: BoxColor.YELLOW,
    BOX_PURPLE: BoxColor.PURPLE,
}

TARGET_CODE_TO_COLOR: Dict[int, BoxColor] = {
    TARGET_RED: BoxColor.RED,
    TARGET_BLUE: BoxColor.BLUE,
    TARGET_GREEN: BoxColor.GREEN,
    TARGET_YELLOW: BoxColor.YELLOW,
    TARGET_PURPLE: BoxColor.PURPLE,
}


@dataclass
class Player:
    x: int
    y: int

    @property
    def pos(self) -> GridPos:
        return (self.x, self.y)

    @pos.setter
    def pos(self, value: GridPos) -> None:
        self.x, self.y = value


@dataclass
class Box:
    x: int
    y: int
    color: BoxColor

    @property
    def pos(self) -> GridPos:
        return (self.x, self.y)

    @pos.setter
    def pos(self, value: GridPos) -> None:
        self.x, self.y = value


@dataclass
class Target:
    x: int
    y: int
    color: BoxColor

    @property
    def pos(self) -> GridPos:
        return (self.x, self.y)


@dataclass
class PortalPair:
    label: str
    entrance: GridPos
    exit_pos: GridPos

    def other_side(self, pos: GridPos) -> Optional[GridPos]:
        if pos == self.entrance:
            return self.exit_pos
        if pos == self.exit_pos:
            return self.entrance
        return None


@dataclass
class PressurePlate:
    x: int
    y: int
    plate_id: str
    gate_ids: List[str]
    is_pressed: bool = False

    @property
    def pos(self) -> GridPos:
        return (self.x, self.y)


@dataclass
class Gate:
    x: int
    y: int
    gate_id: str
    is_open: bool = False

    @property
    def pos(self) -> GridPos:
        return (self.x, self.y)


@dataclass
class SublevelSpec:
    entrance: GridPos
    layer_name: str


@dataclass
class LayerState:
    name: str
    width: int
    height: int
    static_map: List[List[int]]
    player_start: GridPos
    boxes: List[Box] = field(default_factory=list)
    targets: List[Target] = field(default_factory=list)
    walls: List[GridPos] = field(default_factory=list)
    portals: List[PortalPair] = field(default_factory=list)
    pressure_plates: List[PressurePlate] = field(default_factory=list)
    gates: List[Gate] = field(default_factory=list)
    sublevel_spec: Optional[SublevelSpec] = None

    def clone_dynamic(self) -> Dict[str, object]:
        return {
            "player": Player(*self.player_start),
            "boxes": [Box(b.x, b.y, b.color) for b in self.boxes],
            "gates": [Gate(g.x, g.y, g.gate_id, g.is_open) for g in self.gates],
            "plates": [
                PressurePlate(p.x, p.y, p.plate_id, list(p.gate_ids), p.is_pressed)
                for p in self.pressure_plates
            ],
        }
