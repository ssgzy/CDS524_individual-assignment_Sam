"""Patrick's Parabox style 2D top-down renderer for ShadowBox."""

from __future__ import annotations

import math
from typing import Dict, Tuple, Any, List

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

# Parabox flat vibrant palette
COLOR_MAP = {
    BoxColor.RED: (255, 90, 90),       # #FF5A5A
    BoxColor.BLUE: (90, 150, 255),     # #5A96FF
    BoxColor.GREEN: (90, 219, 130),    # #5ADB82
    BoxColor.YELLOW: (255, 212, 90),   # #FFD45A
    BoxColor.PURPLE: (196, 114, 255),  # #C472FF
}

TARGET_COLOR_MAP = {
    TARGET_RED: COLOR_MAP[BoxColor.RED],
    TARGET_BLUE: COLOR_MAP[BoxColor.BLUE],
    TARGET_GREEN: COLOR_MAP[BoxColor.GREEN],
    TARGET_YELLOW: COLOR_MAP[BoxColor.YELLOW],
    TARGET_PURPLE: COLOR_MAP[BoxColor.PURPLE],
}

def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(val, max_val))

class TopDownRenderer:
    """Design-driven 2D top-down renderer inspired by Patrick's Parabox."""

    def __init__(
        self,
        screen: pygame.Surface,
        cell_size: int = 64,
        screen_width: int = 1280,
        screen_height: int = 720,
    ):
        self.screen = screen
        self.cell_size = cell_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        pygame.font.init()
        # Defaulting to a clean built-in sans-serif font
        self.title_font = pygame.font.SysFont("Helvetica, Arial", 28, bold=True)
        self.font = pygame.font.SysFont("Helvetica, Arial", 20)
        self.small_font = pygame.font.SysFont("Helvetica, Arial", 16, bold=True)
        self.hint_font = pygame.font.SysFont("Helvetica, Arial", 14)

        # Style Guide Colors
        self.bg_color = (24, 26, 27)      # #181A1B
        self.floor_color = (36, 39, 43)   # #24272B
        self.wall_color = (56, 60, 68)    # #383C44
        self.grid_color = (30, 33, 36)    # #1E2124
        
        self.player_color = (244, 244, 246) # #F4F4F6
        self.ui_text = (209, 213, 219)      # #D1D5DB List/Values
        self.ui_white = (255, 255, 255)

        # Animation State
        self.last_time = pygame.time.get_ticks()
        self.visual_entities: Dict[int, Tuple[float, float]] = {} 
        self.effects: List[Dict[str, Any]] = []  # Store pops/flashes
        self.move_speed = 10.0 / 100.0  # Cells per ms (~100ms per cell)

        # Track targets to emit effects when state changes
        self.boxes_on_target_cache = set()

    def get_game_offset(self, map_width: int, map_height: int) -> Tuple[int, int]:
        """Calculate offset to center the game grid."""
        grid_width = map_width * self.cell_size
        grid_height = map_height * self.cell_size

        offset_x = (self.screen_width - grid_width) // 2
        offset_y = (self.screen_height - grid_height) // 2

        return offset_x, offset_y

    def update_animations(self, env, dt: float):
        """Update linear interpolation for logic->visual transforms."""
        # Entities to track
        entities = []
        entities.append((id(env.player), env.player.x, env.player.y))
        for box in env.boxes:
            entities.append((id(box), box.x, box.y))
        
        active_ids = set()
        for ent_id, target_x, target_y in entities:
            active_ids.add(ent_id)
            if ent_id not in self.visual_entities:
                self.visual_entities[ent_id] = (float(target_x), float(target_y))
            else:
                curr_x, curr_y = self.visual_entities[ent_id]
                
                # Linear move towards target
                dx = target_x - curr_x
                dy = target_y - curr_y
                dist = math.hypot(dx, dy)
                
                if dist > 0.001:
                    move_dist = min(dist, self.move_speed * dt)
                    new_x = curr_x + (dx / dist) * move_dist
                    new_y = curr_y + (dy / dist) * move_dist
                    self.visual_entities[ent_id] = (new_x, new_y)
                else:
                    self.visual_entities[ent_id] = (float(target_x), float(target_y))
                    
        # Cleanup
        keys_to_remove = [k for k in self.visual_entities.keys() if k not in active_ids]
        for k in keys_to_remove:
            del self.visual_entities[k]

        # Check for success pops
        current_on_target = set()
        for box in env.boxes:
            if env.is_box_on_target(box):
                current_on_target.add(id(box))
                if id(box) not in self.boxes_on_target_cache:
                    # Just placed on target -> trigger effect
                    self.effects.append({
                        "type": "pop",
                        "box_id": id(box),
                        "time": 150.0,
                        "max_time": 150.0
                    })
        self.boxes_on_target_cache = current_on_target

        # Update effects
        for effect in self.effects:
            effect["time"] -= dt
        self.effects = [e for e in self.effects if e["time"] > 0]


    def draw_grid(self, offset_x: int, offset_y: int, width: int, height: int) -> None:
        """Draw minimal background grid."""
        for y in range(height + 1):
            start = (offset_x, offset_y + y * self.cell_size)
            end = (offset_x + width * self.cell_size, offset_y + y * self.cell_size)
            pygame.draw.line(self.screen, self.grid_color, start, end, 1)

        for x in range(width + 1):
            start = (offset_x + x * self.cell_size, offset_y)
            end = (offset_x + x * self.cell_size, offset_y + height * self.cell_size)
            pygame.draw.line(self.screen, self.grid_color, start, end, 1)

    def draw_wall(self, px: float, py: float) -> None:
        """Draw a flat wall tile."""
        rect = (px, py, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, self.wall_color, rect, border_radius=4)
        
        # Extremely subtle inner shine for tiny depth
        inner_rect = (px + 2, py + 2, self.cell_size - 4, self.cell_size - 4)
        pygame.draw.rect(self.screen, (255, 255, 255, 8), inner_rect, border_radius=3)

    def draw_target(self, px: float, py: float, color: Tuple[int, int, int], t: int) -> None:
        """Draw a target marker outline."""
        center_x = px + self.cell_size / 2
        center_y = py + self.cell_size / 2
        
        # Slow pulse
        pulse = math.sin(t / 300.0) * 0.15 + 0.85
        size = int(self.cell_size * 0.7 * pulse)
        rect = (center_x - size/2, center_y - size/2, size, size)
        
        pygame.draw.rect(self.screen, color, rect, width=3, border_radius=6)
        
        # Subtle cross mark inside
        cross_size = int(self.cell_size * 0.1)
        pygame.draw.line(self.screen, color, (center_x - cross_size, center_y), (center_x + cross_size, center_y), 2)
        pygame.draw.line(self.screen, color, (center_x, center_y - cross_size), (center_x, center_y + cross_size), 2)

    def draw_box(self, px: float, py: float, box_id: int, color: Tuple[int, int, int], on_target: bool) -> None:
        """Draw a colored box with Parabox rules."""
        padding = 6
        size = self.cell_size - padding * 2
        
        # Base scale
        scale = 1.0
        
        # Apply pop animation
        for effect in self.effects:
            if effect["type"] == "pop" and effect["box_id"] == box_id:
                # 0 to 1 progress
                p = 1.0 - (effect["time"] / effect["max_time"])
                # Scale up to 1.15x then back to 1.0x (simple parabola)
                scale = 1.0 + 0.15 * math.sin(p * math.pi)

        actual_size = size * scale
        offset = (self.cell_size - actual_size) / 2
        box_px = px + offset
        box_py = py + offset
        
        box_rect = (box_px, box_py, actual_size, actual_size)
        pygame.draw.rect(self.screen, color, box_rect, border_radius=6)

        if on_target:
            # White checkmark if satisfied
            cx = box_px + actual_size / 2
            cy = box_py + actual_size / 2
            points = [
                (cx - actual_size*0.2, cy),
                (cx - actual_size*0.05, cy + actual_size*0.15),
                (cx + actual_size*0.25, cy - actual_size*0.15)
            ]
            pygame.draw.lines(self.screen, self.ui_white, False, points, max(2, int(actual_size * 0.08)))

    def draw_player(self, px: float, py: float) -> None:
        """Draw the pristine white player block with eyes."""
        padding = 8
        size = self.cell_size - padding * 2
        box_rect = (px + padding, py + padding, size, size)

        # White body, 2px stroke
        pygame.draw.rect(self.screen, self.player_color, box_rect, border_radius=6)
        pygame.draw.rect(self.screen, (0, 0, 0), box_rect, width=2, border_radius=6)

        # Eyes
        cx = px + self.cell_size / 2
        cy = py + self.cell_size / 2
        
        eye_w = 3
        eye_h = 8
        eye_space = 10
        
        pygame.draw.rect(self.screen, (0, 0, 0), (cx - eye_space/2 - eye_w/2, cy - eye_h/2, eye_w, eye_h))
        pygame.draw.rect(self.screen, (0, 0, 0), (cx + eye_space/2 - eye_w/2, cy - eye_h/2, eye_w, eye_h))

    def draw_portal(self, px: float, py: float, t: int) -> None:
        cx = px + self.cell_size / 2
        cy = py + self.cell_size / 2
        portal_color = (147, 90, 214)

        for i in range(2):
            radius = int(self.cell_size * (0.2 + i * 0.1 + math.sin(t / 500.0) * 0.05))
            pygame.draw.circle(self.screen, portal_color, (cx, cy), radius, width=2)

    def draw_pressure_plate(self, px: float, py: float, pressed: bool) -> None:
        cx = px + self.cell_size / 2
        cy = py + self.cell_size / 2

        color = COLOR_MAP[BoxColor.YELLOW] if pressed else (169, 149, 84) # #A99554
        size = int(self.cell_size * 0.6)

        plate_rect = (cx - size / 2, cy - size / 2, size, size)
        pygame.draw.rect(self.screen, color, plate_rect, border_radius=6)

    def draw_gate(self, px: float, py: float, opened: bool) -> None:
        rect = (px, py, self.cell_size, self.cell_size)
        if opened:
            pygame.draw.rect(self.screen, (100, 100, 100), rect, width=2, border_radius=4)
        else:
            pygame.draw.rect(self.screen, self.wall_color, rect, border_radius=4)
            pygame.draw.rect(self.screen, (30, 30, 35), rect, width=3, border_radius=4)

    def draw_sublevel_entrance(self, px: float, py: float, t: int) -> None:
        cx = px + self.cell_size / 2
        cy = py + self.cell_size / 2

        pulse = math.sin(t / 250.0) * 0.1 + 0.9
        size = int(self.cell_size * 0.4 * pulse)
        
        rect = (cx - size/2, cy - size/2, size, size)
        pygame.draw.rect(self.screen, self.ui_white, rect, width=2, border_radius=4)

    def draw_hud(self, env, extra_ui: Dict[str, str] | None = None) -> None:
        """Minimalist HUD on top left."""
        keys = pygame.key.get_pressed()
        show_stats = keys[pygame.K_TAB] or keys[pygame.K_h]

        y_pos = 20
        x_pos = 20

        # Title / Level 
        title_surf = self.title_font.render(f"Level {env.level_id}/5", True, self.ui_white)
        self.screen.blit(title_surf, (x_pos, y_pos))
        y_pos += 35

        # Steps
        steps_surf = self.font.render(f"Steps: {env.max_steps - env.remaining_steps}/{env.max_steps}", True, self.ui_text)
        self.screen.blit(steps_surf, (x_pos, y_pos))
        y_pos += 25
        
        if env.current_layer_name != "outer":
            layer_surf = self.small_font.render(f"Inside: {env.current_layer_name}", True, COLOR_MAP[BoxColor.BLUE])
            self.screen.blit(layer_surf, (x_pos, y_pos))
            y_pos += 25

        hint_surf = self.hint_font.render("Press [TAB] for Legend & Stats | [R] Reset | [ESC] Quit", True, (100, 105, 110))
        self.screen.blit(hint_surf, (x_pos, self.screen_height - 30))

        if show_stats:
            # Stats Overlay
            overlay_surf = pygame.Surface((300, 400), pygame.SRCALPHA)
            overlay_surf.fill((0, 0, 0, 200)) # 80% Black
            self.screen.blit(overlay_surf, (x_pos, y_pos + 10))
            
            stat_y = y_pos + 25
            stat_x = x_pos + 20
            
            if extra_ui:
                for key, value in extra_ui.items():
                    stat_surf = self.small_font.render(f"{key}: {value}", True, self.ui_white)
                    self.screen.blit(stat_surf, (stat_x, stat_y))
                    stat_y += 24

            stat_y += 10
            legend_title = self.small_font.render("Legend:", True, self.ui_text)
            self.screen.blit(legend_title, (stat_x, stat_y))
            stat_y += 24
            
            legend_items = [
                ("Player", self.player_color),
                ("Red Box", COLOR_MAP[BoxColor.RED]),
                ("Blue Box", COLOR_MAP[BoxColor.BLUE]),
                ("Green Box", COLOR_MAP[BoxColor.GREEN]),
                ("Yellow Box", COLOR_MAP[BoxColor.YELLOW])
            ]
            for text, color in legend_items:
                pygame.draw.rect(self.screen, color, (stat_x, stat_y, 14, 14), border_radius=3)
                if color == self.player_color:
                    pygame.draw.rect(self.screen, (0,0,0), (stat_x, stat_y, 14, 14), width=1, border_radius=3)
                txt_surf = self.hint_font.render(text, True, self.ui_text)
                self.screen.blit(txt_surf, (stat_x + 24, stat_y - 2))
                stat_y += 22

    def render(self, env, extra_ui: Dict[str, str] | None = None) -> None:
        """Main render pass."""
        now = pygame.time.get_ticks()
        dt = float(now - self.last_time)
        self.last_time = now

        # Max dt to prevent jumps if frame drops
        dt = clamp(dt, 0.0, 50.0)
        
        self.update_animations(env, dt)

        # Clear
        self.screen.fill(self.bg_color)

        offset_x, offset_y = self.get_game_offset(env.map_width, env.map_height)

        # Optional faint grid, can be removed for pure minimalism but helps puzzle solving
        self.draw_grid(offset_x, offset_y, env.map_width, env.map_height)

        # Base layer
        for y in range(env.map_height):
            for x in range(env.map_width):
                cell = env.get_cell(x, y)
                px = offset_x + x * self.cell_size
                py = offset_y + y * self.cell_size

                # Draw floor everywhere inside map
                pygame.draw.rect(self.screen, self.floor_color, (px, py, self.cell_size, self.cell_size))

                # Statics
                if cell == WALL:
                    self.draw_wall(px, py)
                elif cell in TARGET_TYPES:
                    self.draw_target(px, py, TARGET_COLOR_MAP[cell], now)
                elif cell in PORTAL_TYPES:
                    self.draw_portal(px, py, now)
                elif cell == PRESSURE:
                    is_pressed = any(p.pos == (x, y) and p.is_pressed for p in env.pressure_plates)
                    self.draw_pressure_plate(px, py, is_pressed)
                elif cell == SUBLEVEL_ENTRANCE:
                    self.draw_sublevel_entrance(px, py, now)

        # Gates
        for gate in env.gates:
            px = offset_x + gate.x * self.cell_size
            py = offset_y + gate.y * self.cell_size
            self.draw_gate(px, py, gate.is_open)

        # Dynamic Entities (lerped)
        for box in env.boxes:
            b_lx, b_ly = self.visual_entities.get(id(box), (float(box.x), float(box.y)))
            px = offset_x + b_lx * self.cell_size
            py = offset_y + b_ly * self.cell_size
            self.draw_box(px, py, id(box), COLOR_MAP[box.color], env.is_box_on_target(box))

        p_lx, p_ly = self.visual_entities.get(id(env.player), (float(env.player.x), float(env.player.y)))
        px = offset_x + p_lx * self.cell_size
        py = offset_y + p_ly * self.cell_size
        self.draw_player(px, py)

        # UI Overlay
        self.draw_hud(env, extra_ui)

        pygame.display.flip()
