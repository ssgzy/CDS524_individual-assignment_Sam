"""Isometric renderer for ShadowBox using procedural sprites."""

from __future__ import annotations

import math
from typing import Dict, Tuple

import pygame

from game.entities import (
    EMPTY,
    GATE,
    PORTAL_A1,
    PORTAL_A2,
    PORTAL_B1,
    PORTAL_B2,
    PRESSURE,
    SUBLEVEL_ENTRANCE,
    TARGET_BLUE,
    TARGET_GREEN,
    TARGET_PURPLE,
    TARGET_RED,
    TARGET_YELLOW,
    WALL,
    BoxColor,
)

TARGET_TYPES = {TARGET_RED, TARGET_BLUE, TARGET_GREEN, TARGET_YELLOW, TARGET_PURPLE}
PORTAL_TYPES = {PORTAL_A1, PORTAL_A2, PORTAL_B1, PORTAL_B2}

COLOR_MAP = {
    BoxColor.RED: (205, 72, 72),
    BoxColor.BLUE: (74, 109, 202),
    BoxColor.GREEN: (82, 174, 94),
    BoxColor.YELLOW: (214, 183, 67),
    BoxColor.PURPLE: (160, 93, 194),
}

TARGET_COLOR_MAP = {
    TARGET_RED: COLOR_MAP[BoxColor.RED],
    TARGET_BLUE: COLOR_MAP[BoxColor.BLUE],
    TARGET_GREEN: COLOR_MAP[BoxColor.GREEN],
    TARGET_YELLOW: COLOR_MAP[BoxColor.YELLOW],
    TARGET_PURPLE: COLOR_MAP[BoxColor.PURPLE],
}


class IsometricRenderer:
    def __init__(
        self,
        screen: pygame.Surface,
        tile_w: int = 64,
        tile_h: int = 32,
        screen_width: int = 1280,
        screen_height: int = 720,
    ):
        self.screen = screen
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.origin_x = screen_width // 2
        self.origin_y = 96

        pygame.font.init()
        self.font = pygame.font.SysFont("Menlo", 20)
        self.small_font = pygame.font.SysFont("Menlo", 16)

        self.sprites = self.load_sprites()

    def grid_to_iso(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        screen_x = (grid_x - grid_y) * (self.tile_w // 2) + self.origin_x
        screen_y = (grid_x + grid_y) * (self.tile_h // 2) + self.origin_y
        return screen_x, screen_y

    def load_sprites(self) -> Dict[str, pygame.Surface]:
        return {
            "floor": self.draw_floor_tile(),
            "wall": self.draw_wall_tile(),
            "player": self.draw_player_sprite(),
            "gate_closed": self.draw_gate_sprite(opened=False),
            "gate_open": self.draw_gate_sprite(opened=True),
            "box_red": self.draw_box_tile(COLOR_MAP[BoxColor.RED]),
            "box_blue": self.draw_box_tile(COLOR_MAP[BoxColor.BLUE]),
            "box_green": self.draw_box_tile(COLOR_MAP[BoxColor.GREEN]),
            "box_yellow": self.draw_box_tile(COLOR_MAP[BoxColor.YELLOW]),
            "box_purple": self.draw_box_tile(COLOR_MAP[BoxColor.PURPLE]),
        }

    def draw_floor_tile(self) -> pygame.Surface:
        surf = pygame.Surface((self.tile_w, self.tile_h), pygame.SRCALPHA)
        pts = [
            (self.tile_w // 2, 0),
            (self.tile_w, self.tile_h // 2),
            (self.tile_w // 2, self.tile_h),
            (0, self.tile_h // 2),
        ]
        pygame.draw.polygon(surf, (196, 200, 206), pts)
        pygame.draw.lines(surf, (145, 149, 156), True, pts, 1)
        return surf

    def draw_wall_tile(self) -> pygame.Surface:
        surf = pygame.Surface((self.tile_w, self.tile_h * 2), pygame.SRCALPHA)
        top = [
            (self.tile_w // 2, 0),
            (self.tile_w, self.tile_h // 2),
            (self.tile_w // 2, self.tile_h),
            (0, self.tile_h // 2),
        ]
        left = [
            (0, self.tile_h // 2),
            (self.tile_w // 2, self.tile_h),
            (self.tile_w // 2, self.tile_h * 2),
            (0, self.tile_h + self.tile_h // 2),
        ]
        right = [
            (self.tile_w // 2, self.tile_h),
            (self.tile_w, self.tile_h // 2),
            (self.tile_w, self.tile_h + self.tile_h // 2),
            (self.tile_w // 2, self.tile_h * 2),
        ]
        pygame.draw.polygon(surf, (201, 201, 201), top)
        pygame.draw.polygon(surf, (143, 143, 143), left)
        pygame.draw.polygon(surf, (103, 103, 103), right)
        return surf

    def draw_box_tile(self, top_color: Tuple[int, int, int]) -> pygame.Surface:
        surf = pygame.Surface((self.tile_w, self.tile_h * 2), pygame.SRCALPHA)
        base_top = [
            (self.tile_w // 2, 8),
            (self.tile_w - 6, self.tile_h // 2 + 6),
            (self.tile_w // 2, self.tile_h + 4),
            (6, self.tile_h // 2 + 6),
        ]
        left = [
            (6, self.tile_h // 2 + 6),
            (self.tile_w // 2, self.tile_h + 4),
            (self.tile_w // 2, self.tile_h + 28),
            (6, self.tile_h // 2 + 30),
        ]
        right = [
            (self.tile_w // 2, self.tile_h + 4),
            (self.tile_w - 6, self.tile_h // 2 + 6),
            (self.tile_w - 6, self.tile_h // 2 + 30),
            (self.tile_w // 2, self.tile_h + 28),
        ]
        pygame.draw.polygon(surf, top_color, base_top)
        pygame.draw.polygon(surf, tuple(max(0, c - 36) for c in top_color), left)
        pygame.draw.polygon(surf, tuple(max(0, c - 64) for c in top_color), right)
        return surf

    def draw_player_sprite(self) -> pygame.Surface:
        surf = pygame.Surface((self.tile_w, self.tile_h * 2), pygame.SRCALPHA)
        cx = self.tile_w // 2
        pygame.draw.circle(surf, (232, 236, 238), (cx, self.tile_h // 2 + 3), 11)
        pygame.draw.rect(surf, (82, 108, 132), (cx - 13, self.tile_h // 2 + 14, 26, 22), border_radius=6)
        pygame.draw.circle(surf, (70, 90, 110), (cx - 4, self.tile_h // 2 + 2), 2)
        pygame.draw.circle(surf, (70, 90, 110), (cx + 4, self.tile_h // 2 + 2), 2)
        return surf

    def draw_gate_sprite(self, opened: bool) -> pygame.Surface:
        surf = pygame.Surface((self.tile_w, self.tile_h * 2), pygame.SRCALPHA)
        color = (130, 130, 130) if opened else (76, 76, 84)
        alpha = 90 if opened else 255
        bar_count = 5
        for i in range(bar_count):
            x = 12 + i * 10
            rect = pygame.Rect(x, self.tile_h // 2 - (8 if opened else 0), 4, self.tile_h + (4 if opened else 26))
            bar = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bar.fill((*color, alpha))
            surf.blit(bar, rect.topleft)
        return surf

    def draw_target_marker(self, x: int, y: int, color: Tuple[int, int, int], t: int) -> None:
        pulse = int(30 + 20 * (1 + math.sin(t / 160.0)))
        r = 9 + (pulse // 30)
        pygame.draw.circle(self.screen, color, (x, y + self.tile_h // 2 + 5), r)
        pygame.draw.circle(self.screen, (250, 250, 250), (x, y + self.tile_h // 2 + 5), r, 1)

    def draw_portal(self, x: int, y: int, t: int) -> None:
        radius = 10 + int(2 * math.sin(t / 120.0))
        portal_color = (147, 90, 214)
        pygame.draw.ellipse(
            self.screen,
            portal_color,
            (x - radius, y + self.tile_h // 2 - 3, radius * 2, radius + 8),
            2,
        )

    def draw_pressure_plate(self, x: int, y: int, pressed: bool) -> None:
        color = (234, 203, 83) if pressed else (145, 126, 60)
        plate = [
            (x, y + self.tile_h // 2 + 8),
            (x + 12, y + self.tile_h // 2 + 14),
            (x, y + self.tile_h // 2 + 20),
            (x - 12, y + self.tile_h // 2 + 14),
        ]
        pygame.draw.polygon(self.screen, color, plate)

    def draw_sublevel_entrance(self, x: int, y: int, t: int) -> None:
        r = 8 + int(1.5 * math.sin(t / 150.0))
        pygame.draw.circle(self.screen, (64, 164, 231), (x, y + self.tile_h // 2 + 7), r, 2)

    def render(self, env, extra_ui: Dict[str, str] | None = None) -> None:
        t = pygame.time.get_ticks()
        self.screen.fill((32, 36, 48))

        # Base layers: floor + static markers + walls.
        for y in range(env.map_height):
            for x in range(env.map_width):
                iso_x, iso_y = self.grid_to_iso(x, y)
                self.screen.blit(self.sprites["floor"], (iso_x - self.tile_w // 2, iso_y))

                cell = env.get_cell(x, y)
                center_x = iso_x

                if cell in TARGET_TYPES:
                    self.draw_target_marker(center_x, iso_y, TARGET_COLOR_MAP[cell], t)
                elif cell in PORTAL_TYPES:
                    self.draw_portal(center_x, iso_y, t)
                elif cell == PRESSURE:
                    is_pressed = any(p.pos == (x, y) and p.is_pressed for p in env.pressure_plates)
                    self.draw_pressure_plate(center_x, iso_y, is_pressed)
                elif cell == SUBLEVEL_ENTRANCE:
                    self.draw_sublevel_entrance(center_x, iso_y, t)

                if cell == WALL:
                    self.screen.blit(self.sprites["wall"], (iso_x - self.tile_w // 2, iso_y - self.tile_h))

        # Dynamic entities sorted by depth.
        draw_queue = []

        for box in env.boxes:
            draw_queue.append((box.x + box.y, "box", box))
        for gate in env.gates:
            draw_queue.append((gate.x + gate.y + 0.2, "gate", gate))
        draw_queue.append((env.player.x + env.player.y + 0.4, "player", env.player))

        draw_queue.sort(key=lambda item: item[0])

        for _, kind, entity in draw_queue:
            iso_x, iso_y = self.grid_to_iso(entity.x, entity.y)
            if kind == "box":
                key = f"box_{entity.color.name.lower()}"
                self.screen.blit(self.sprites[key], (iso_x - self.tile_w // 2, iso_y - self.tile_h))
                if env.is_box_on_target(entity):
                    pygame.draw.circle(self.screen, (255, 255, 255), (iso_x, iso_y + 6), 4)
            elif kind == "player":
                self.screen.blit(self.sprites["player"], (iso_x - self.tile_w // 2, iso_y - self.tile_h))
            elif kind == "gate":
                key = "gate_open" if entity.is_open else "gate_closed"
                self.screen.blit(self.sprites[key], (iso_x - self.tile_w // 2, iso_y - self.tile_h))

        # UI overlay
        info_lines = [
            f"Level: {env.level_id}",
            f"Layer: {env.current_layer_name}",
            f"Steps Left: {env.remaining_steps}",
            f"Sublevel Done: {env.sublevel_completed}",
        ]
        if extra_ui:
            for k, v in extra_ui.items():
                info_lines.append(f"{k}: {v}")

        panel = pygame.Surface((320, 140), pygame.SRCALPHA)
        panel.fill((10, 12, 16, 180))
        self.screen.blit(panel, (20, 20))

        for i, line in enumerate(info_lines):
            txt = self.font.render(line, True, (235, 235, 235))
            self.screen.blit(txt, (34, 32 + i * 24))

        hint = self.small_font.render("Arrow: move | Enter: sublevel | R: reset | Esc: quit", True, (214, 214, 214))
        self.screen.blit(hint, (20, self.screen_height - 32))

        pygame.display.flip()
