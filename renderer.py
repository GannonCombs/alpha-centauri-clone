# renderer.py
import pygame
import constants
from constants import (TILE_SIZE, COLOR_OCEAN, COLOR_LAND, COLOR_GRID, COLOR_BLACK,
                       COLOR_UNIT_SELECTED, COLOR_UNIT_FRIENDLY, COLOR_UNIT_ENEMY,
                       COLOR_BASE_FRIENDLY, COLOR_BASE_ENEMY, COLOR_BASE_BORDER,
                       UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA)


class Camera:
    """Camera system for potential future scrolling features."""

    def __init__(self):
        """Initialize camera at origin."""
        self.x = 0
        self.y = 0

    def move(self, dx, dy):
        """Move camera by offset (currently unused)."""
        pass

    def apply(self, x, y):
        """Apply camera transform to coordinates (currently identity)."""
        return x, y


class Renderer:
    """Handles all drawing operations for the game."""

    def __init__(self, screen):
        """Initialize renderer with pygame screen surface."""
        self.screen = screen
        self.camera = Camera()
        self.camera_offset_x = 0  # Horizontal scroll in tiles (for wrapping)
        self.base_offset_x = 0  # Centering offset in pixels

    def _update_offsets(self, game_map):
        """Calculate horizontal offset to center the map."""
        map_pixel_width = game_map.width * TILE_SIZE
        # Half of the leftover horizontal space
        self.base_offset_x = (constants.SCREEN_WIDTH - map_pixel_width) // 2

    def scroll_camera(self, dx):
        """Scroll the camera horizontally (wraps around)."""
        self.camera_offset_x += dx
        # No clamping - we allow infinite scrolling with wrapping

    def draw_map(self, game_map, territory=None):
        """Draw all map tiles with horizontal wrapping and territory borders."""
        self._update_offsets(game_map)

        # Calculate visible tile range with wrapping
        visible_tiles_x = (constants.SCREEN_WIDTH // TILE_SIZE) + 2

        for y in range(game_map.height):
            for screen_x_idx in range(visible_tiles_x):
                # Calculate actual map x with wrapping
                map_x = (self.camera_offset_x + screen_x_idx) % game_map.width
                tile = game_map.get_tile(map_x, y)
                self.draw_tile_at_screen_pos(tile, screen_x_idx, y)

        # Draw territory borders after tiles
        if territory:
            self.draw_territory_borders(territory, game_map)

        # Draw supply pods
        self.draw_supply_pods(game_map)

    def draw_tile_at_screen_pos(self, tile, screen_x_idx, screen_y_idx):
        """Draw a tile at a specific screen position."""
        screen_x = (screen_x_idx * TILE_SIZE) + self.base_offset_x
        screen_y = screen_y_idx * TILE_SIZE

        color = COLOR_LAND if tile.is_land() else COLOR_OCEAN
        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_tile(self, tile):
        """Draw a tile at its world position (with camera wrapping)."""
        # Calculate screen position accounting for camera offset
        world_x_offset = (tile.x - self.camera_offset_x) % self.screen.get_width() // TILE_SIZE
        screen_x = (world_x_offset * TILE_SIZE) + self.base_offset_x
        screen_y = tile.y * TILE_SIZE

        color = COLOR_LAND if tile.is_land() else COLOR_OCEAN
        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_units(self, units, selected_unit, player_id, game_map):
        """Draw all units on the map."""
        for unit in units:
            self.draw_unit(unit, selected_unit, player_id, game_map)

    def draw_unit(self, unit, selected_unit, player_id, game_map):
        """Draw a single unit with health bar if selected."""
        # Calculate wrapped screen position
        wrapped_x = (unit.x - self.camera_offset_x) % game_map.width
        screen_x = (wrapped_x * TILE_SIZE) + self.base_offset_x
        screen_y = (unit.y * TILE_SIZE)

        # Only draw if on screen
        if screen_x < -TILE_SIZE or screen_x > constants.SCREEN_WIDTH:
            return
        if screen_y < 0 or screen_y >= constants.MAP_AREA_HEIGHT:
            return

        # Determine unit color (not yellow for selected anymore)
        if unit.is_friendly(player_id):
            color = COLOR_UNIT_FRIENDLY
        else:
            color = COLOR_UNIT_ENEMY

        center_x = screen_x + TILE_SIZE // 2
        center_y = screen_y + TILE_SIZE // 2
        radius = TILE_SIZE // 3

        # Draw main unit circle
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, COLOR_BLACK, (center_x, center_y), radius, 3)

        # Draw unit type letter
        font = pygame.font.Font(None, 28)
        # Show 'C' for colony pods, otherwise first letter of type
        if unit.unit_type in [UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA]:
            type_char = 'C'
        else:
            type_char = unit.unit_type[0].upper()
        text_surf = font.render(type_char, True, COLOR_BLACK)

        # Explicitly get the rect and set the center attribute
        text_rect = text_surf.get_rect()
        text_rect.center = (center_x, center_y)

        self.screen.blit(text_surf, text_rect)

        # Draw selection indicator (home plate) if selected
        if unit == selected_unit:
            self._draw_selection_indicator(screen_x, screen_y, unit)

    def _draw_selection_indicator(self, tile_x, tile_y, unit):
        """Draw home plate selection indicator and health bar in top-left of tile.

        Args:
            tile_x (int): Top-left X of tile
            tile_y (int): Top-left Y of tile
            unit (Unit): The selected unit
        """
        # Health bar - thin line on the left, color based on health
        bar_x = tile_x + 2
        bar_y = tile_y + 2
        bar_width = 2
        bar_height = 10

        # Draw background (dark gray)
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

        # Draw health fill based on percentage and color based on health
        health_pct = unit.get_health_percentage()
        fill_height = int(bar_height * health_pct)
        fill_y = bar_y + (bar_height - fill_height)
        health_color = unit.get_health_color()
        pygame.draw.rect(self.screen, health_color, (bar_x, fill_y, bar_width, fill_height))

        # Home plate (pentagon pointing down) next to health bar
        size = 10
        x = bar_x + bar_width + 2
        y = tile_y + 2

        # Pentagon vertices (home plate shape)
        points = [
            (x, y),                    # Top-left
            (x + size, y),             # Top-right
            (x + size, y + size - 3),  # Right before point
            (x + size // 2, y + size), # Bottom point
            (x, y + size - 3)          # Left before point
        ]

        # Draw filled yellow home plate
        pygame.draw.polygon(self.screen, COLOR_UNIT_SELECTED, points)
        pygame.draw.polygon(self.screen, COLOR_BLACK, points, 1)

    def draw_bases(self, bases, player_id, game_map):
        """Draw all bases on the map."""
        for base in bases:
            self.draw_base(base, player_id, game_map)

    def draw_base(self, base, player_id, game_map):
        """Draw a single base."""
        wrapped_x = (base.x - self.camera_offset_x) % game_map.width
        screen_x = (wrapped_x * TILE_SIZE) + self.base_offset_x
        screen_y = (base.y * TILE_SIZE)

        # Only draw if on screen
        if screen_x < -TILE_SIZE or screen_x > constants.SCREEN_WIDTH:
            return
        if screen_y < 0 or screen_y >= constants.MAP_AREA_HEIGHT:
            return

        # Determine color based on ownership
        if base.is_friendly(player_id):
            color = COLOR_BASE_FRIENDLY
        else:
            color = COLOR_BASE_ENEMY

        # Draw base as a square with rounded corners
        base_size = int(TILE_SIZE * 0.7)
        base_offset = (TILE_SIZE - base_size) // 2
        base_rect = pygame.Rect(screen_x + base_offset, screen_y + base_offset, base_size, base_size)

        pygame.draw.rect(self.screen, color, base_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_BASE_BORDER, base_rect, 3, border_radius=8)

        # Draw base name beneath the icon
        font = pygame.font.Font(None, 18)
        name_surf = font.render(base.name, True, COLOR_BASE_BORDER)
        name_rect = name_surf.get_rect()
        name_rect.centerx = screen_x + TILE_SIZE // 2
        name_rect.top = screen_y + TILE_SIZE + 2

        # Draw background for text
        bg_rect = name_rect.inflate(4, 2)
        pygame.draw.rect(self.screen, COLOR_BLACK, bg_rect)
        self.screen.blit(name_surf, name_rect)

        # Draw population in top-left corner
        pop_size = 20
        pop_rect = pygame.Rect(screen_x + 2, screen_y + 2, pop_size, pop_size)
        pop_color = COLOR_BASE_FRIENDLY if base.is_friendly(player_id) else COLOR_BASE_ENEMY
        pygame.draw.rect(self.screen, pop_color, pop_rect)
        pygame.draw.rect(self.screen, COLOR_BASE_BORDER, pop_rect, 1)

        pop_font = pygame.font.Font(None, 16)
        pop_text = pop_font.render(str(base.population), True, COLOR_BLACK)
        pop_text_rect = pop_text.get_rect(center=pop_rect.center)
        self.screen.blit(pop_text, pop_text_rect)

    def draw_status_message(self, game):
        """Draw status message at bottom of map area."""
        if game.status_message:
            font = pygame.font.Font(None, 24)
            text_surf = font.render(game.status_message, True, (255, 255, 255))
            text_rect = text_surf.get_rect()
            text_rect.centerx = constants.SCREEN_WIDTH // 2
            text_rect.bottom = constants.MAP_AREA_HEIGHT - 10

            # Draw background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), bg_rect, 1)

            self.screen.blit(text_surf, text_rect)

    def draw_territory_borders(self, territory, game_map):
        """Draw dotted territory borders for all players.

        Args:
            territory (TerritoryManager): Territory management system
            game_map: The game map for wrapping calculations
        """
        # Get player colors
        player_colors = {
            0: (50, 205, 50),   # Player - Gaian green
            1: (255, 80, 80)    # AI - red
        }

        # Calculate visible range with wrapping
        visible_tiles_x = (constants.SCREEN_WIDTH // TILE_SIZE) + 2

        # For each visible tile, draw border edges
        for y in range(territory.game_map.height):
            for screen_x_idx in range(visible_tiles_x):
                map_x = (self.camera_offset_x + screen_x_idx) % game_map.width
                owner = territory.get_tile_owner(map_x, y)
                if owner is None:
                    continue

                border_edges = territory.get_border_edges(map_x, y)
                if not border_edges:
                    continue

                color = player_colors.get(owner, (150, 150, 150))
                self._draw_tile_borders_at_screen_pos(screen_x_idx, y, border_edges, color)

    def _draw_tile_borders_at_screen_pos(self, screen_x_idx, screen_y_idx, edges, color):
        """Draw dotted borders on specified edges of a tile at screen position.

        Args:
            screen_x_idx (int): Screen X index
            screen_y_idx (int): Screen Y index
            edges (list): List of edge directions ('N', 'E', 'S', 'W')
            color (tuple): RGB color for the border
        """
        screen_x = (screen_x_idx * TILE_SIZE) + self.base_offset_x
        screen_y = screen_y_idx * TILE_SIZE

        # Dash pattern: 5 pixels on, 3 pixels off
        dash_length = 5
        gap_length = 3
        pattern_length = dash_length + gap_length

        for edge in edges:
            if edge == 'N':
                # Top edge
                y_pos = screen_y
                for i in range(0, TILE_SIZE, pattern_length):
                    x_start = screen_x + i
                    x_end = min(screen_x + i + dash_length, screen_x + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_start, y_pos), (x_end, y_pos), 2)

            elif edge == 'S':
                # Bottom edge
                y_pos = screen_y + TILE_SIZE
                for i in range(0, TILE_SIZE, pattern_length):
                    x_start = screen_x + i
                    x_end = min(screen_x + i + dash_length, screen_x + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_start, y_pos), (x_end, y_pos), 2)

            elif edge == 'W':
                # Left edge
                x_pos = screen_x
                for i in range(0, TILE_SIZE, pattern_length):
                    y_start = screen_y + i
                    y_end = min(screen_y + i + dash_length, screen_y + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_pos, y_start), (x_pos, y_end), 2)

            elif edge == 'E':
                # Right edge
                x_pos = screen_x + TILE_SIZE
                for i in range(0, TILE_SIZE, pattern_length):
                    y_start = screen_y + i
                    y_end = min(screen_y + i + dash_length, screen_y + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_pos, y_start), (x_pos, y_end), 2)

    def _draw_tile_borders(self, tile_x, tile_y, edges, color):
        """Draw dotted borders on specified edges of a tile.

        Args:
            tile_x (int): Tile X coordinate
            tile_y (int): Tile Y coordinate
            edges (list): List of edge directions ('N', 'E', 'S', 'W')
            color (tuple): RGB color for the border
        """
        wrapped_x = (tile_x - self.camera_offset_x) % constants.MAP_WIDTH
        screen_x = (wrapped_x * TILE_SIZE) + self.base_offset_x
        screen_y = tile_y * TILE_SIZE

        # Dash pattern: 5 pixels on, 3 pixels off
        dash_length = 5
        gap_length = 3
        pattern_length = dash_length + gap_length

        for edge in edges:
            if edge == 'N':
                # Top edge
                y_pos = screen_y
                for i in range(0, TILE_SIZE, pattern_length):
                    x_start = screen_x + i
                    x_end = min(screen_x + i + dash_length, screen_x + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_start, y_pos), (x_end, y_pos), 2)

            elif edge == 'S':
                # Bottom edge
                y_pos = screen_y + TILE_SIZE
                for i in range(0, TILE_SIZE, pattern_length):
                    x_start = screen_x + i
                    x_end = min(screen_x + i + dash_length, screen_x + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_start, y_pos), (x_end, y_pos), 2)

            elif edge == 'W':
                # Left edge
                x_pos = screen_x
                for i in range(0, TILE_SIZE, pattern_length):
                    y_start = screen_y + i
                    y_end = min(screen_y + i + dash_length, screen_y + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_pos, y_start), (x_pos, y_end), 2)

            elif edge == 'E':
                # Right edge
                x_pos = screen_x + TILE_SIZE
                for i in range(0, TILE_SIZE, pattern_length):
                    y_start = screen_y + i
                    y_end = min(screen_y + i + dash_length, screen_y + TILE_SIZE)
                    pygame.draw.line(self.screen, color, (x_pos, y_start), (x_pos, y_end), 2)

    def is_click_on_pop_square(self, screen_x, screen_y, base, game_map):
        """Check if click is on the population square of a base."""
        wrapped_x = (base.x - self.camera_offset_x) % game_map.width
        base_screen_x = (wrapped_x * TILE_SIZE) + self.base_offset_x
        base_screen_y = base.y * TILE_SIZE

        pop_size = 20
        pop_rect = pygame.Rect(base_screen_x + 2, base_screen_y + 2, pop_size, pop_size)
        return pop_rect.collidepoint(screen_x, screen_y)

    def screen_to_tile(self, screen_x, screen_y, game_map):
        """Convert screen to tile, accounting for camera wrapping."""
        screen_tile_x = (screen_x - self.base_offset_x) // TILE_SIZE
        tile_x = (self.camera_offset_x + screen_tile_x) % game_map.width
        tile_y = screen_y // TILE_SIZE
        return int(tile_x), int(tile_y)

    def draw_supply_pods(self, game_map):
        """Draw supply pods on the map."""
        visible_tiles_x = (constants.SCREEN_WIDTH // TILE_SIZE) + 2

        for y in range(game_map.height):
            for screen_x_idx in range(visible_tiles_x):
                map_x = (self.camera_offset_x + screen_x_idx) % game_map.width
                tile = game_map.get_tile(map_x, y)

                if tile and tile.supply_pod:
                    # Calculate screen position
                    screen_x = (screen_x_idx * TILE_SIZE) + self.base_offset_x
                    screen_y = y * TILE_SIZE

                    # Only draw if on screen
                    if screen_x < -TILE_SIZE or screen_x > constants.SCREEN_WIDTH:
                        continue
                    if screen_y < 0 or screen_y >= constants.MAP_AREA_HEIGHT:
                        continue

                    # Draw gray circle for supply pod
                    center_x = screen_x + TILE_SIZE // 2
                    center_y = screen_y + TILE_SIZE // 2
                    radius = TILE_SIZE // 4

                    pygame.draw.circle(self.screen, (150, 150, 150), (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, (80, 80, 80), (center_x, center_y), radius, 2)