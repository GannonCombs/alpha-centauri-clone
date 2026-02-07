"""Rendering engine for game graphics.

This module handles all game world rendering including:
- Map and terrain visualization
- Unit rendering with health bars and status indicators
- Base rendering with ownership colors
- Camera management with scrolling and wrapping
- Special terrain features (monoliths, supply pods, etc.)
- Territory borders and zone of control visualization

The Renderer class manages the viewport, handles coordinate transformations,
and draws all game entities to the screen.
"""
import pygame
from game.data import constants
from game.data.constants import (TILE_SIZE, COLOR_OCEAN, COLOR_LAND, COLOR_GRID, COLOR_BLACK,
                                 COLOR_UNIT_SELECTED,
                                 COLOR_BASE_BORDER,
                                 UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA, UNIT_ARTIFACT)
from game.data.data import FACTIONS


class Camera:
    """Camera system for potential future scrolling features."""

    def __init__(self):
        """Initialize camera at origin."""
        self.x = 0
        self.y = 0

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
        self.camera_offset_y = 0  # Vertical scroll in tiles (no wrapping, with bounds)
        self.base_offset_x = 0  # Centering offset in pixels

    def _update_offsets(self, game_map):
        """Calculate horizontal offset to center the map."""
        map_pixel_width = game_map.width * TILE_SIZE
        # Only center if map is smaller than screen, otherwise no offset
        if map_pixel_width < constants.SCREEN_WIDTH:
            self.base_offset_x = (constants.SCREEN_WIDTH - map_pixel_width) // 2
        else:
            self.base_offset_x = 0

    def scroll_camera(self, dx, dy=0):
        """Scroll the camera horizontally (wraps around) and vertically (hard borders).

        Args:
            dx: Horizontal scroll delta (wraps)
            dy: Vertical scroll delta (bounded)
        """
        self.camera_offset_x += dx
        # No clamping for X - we allow infinite scrolling with wrapping

        # Update Y offset with bounds checking (will be validated when drawing)
        self.camera_offset_y += dy

    def center_on_tile(self, tile_x, tile_y, game_map):
        """Center the camera on a specific tile position.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            game_map: The game map
        """
        # Horizontal centering (always possible due to wrapping)
        visible_tiles_x = constants.SCREEN_WIDTH // TILE_SIZE
        center_offset_x = visible_tiles_x // 2
        self.camera_offset_x = (tile_x - center_offset_x) % game_map.width

        # Vertical centering (bounded by map edges)
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE
        center_offset_y = visible_tiles_y // 2
        target_y = tile_y - center_offset_y

        # Apply bounds
        max_y_offset = max(0, game_map.height - visible_tiles_y)
        self.camera_offset_y = max(0, min(target_y, max_y_offset))

    def draw_map(self, game_map, territory=None, faction_assignments=None):
        """Draw all map tiles with horizontal wrapping and territory borders.

        Args:
            game_map: The game map
            territory: TerritoryManager instance (optional)
            faction_assignments: Dict mapping player_id to faction_id (optional)
        """
        self._update_offsets(game_map)

        # Calculate visible tiles (only complete tiles, no partial)
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE
        max_y_offset = max(0, game_map.height - visible_tiles_y)
        self.camera_offset_y = max(0, min(self.camera_offset_y, max_y_offset))

        # Calculate visible tile range with wrapping
        visible_tiles_x = (constants.SCREEN_WIDTH // TILE_SIZE) + 2

        for screen_y_idx in range(visible_tiles_y):
            map_y = self.camera_offset_y + screen_y_idx
            if map_y >= game_map.height:
                continue

            for screen_x_idx in range(visible_tiles_x):
                # Calculate actual map x with wrapping
                map_x = (self.camera_offset_x + screen_x_idx) % game_map.width
                tile = game_map.get_tile(map_x, map_y)
                self.draw_tile_at_screen_pos(tile, screen_x_idx, screen_y_idx)

        # Draw territory borders after tiles
        if territory:
            self.draw_territory_borders(territory, game_map, faction_assignments)

        # Draw supply pods
        self.draw_supply_pods(game_map)

        # Draw monoliths
        self.draw_monoliths(game_map)

        # Draw map edge indicators
        self.draw_map_edge_indicators(game_map)

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

    def draw_units(self, units, selected_unit, player_id, game_map, faction_assignments=None):
        """Draw all units on the map."""
        for unit in units:
            self.draw_unit(unit, selected_unit, player_id, game_map, faction_assignments)

    def draw_unit(self, unit, selected_unit, player_id, game_map, faction_assignments=None):
        """Draw a single unit with health bar if selected."""
        # Only draw if this is the displayed unit for its tile
        tile = game_map.get_tile(unit.x, unit.y)
        if tile and tile.units:
            # Check if this unit is the one that should be displayed
            if 0 <= tile.displayed_unit_index < len(tile.units):
                if tile.units[tile.displayed_unit_index] != unit:
                    return  # Not the displayed unit, skip
            else:
                # Invalid index, check if it's the first unit
                if tile.units[0] != unit:
                    return

        # Calculate wrapped screen position
        wrapped_x = (unit.x - self.camera_offset_x) % game_map.width
        screen_x = (wrapped_x * TILE_SIZE) + self.base_offset_x
        screen_y = (unit.y - self.camera_offset_y) * TILE_SIZE

        # Only draw if on screen (excluding border areas)
        if screen_x < -TILE_SIZE or screen_x > constants.SCREEN_WIDTH:
            return

        # Calculate visible area
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE
        max_y_offset = max(0, game_map.height - visible_tiles_y)

        # Don't draw in top border area (when at top of map)
        if self.camera_offset_y == 0 and screen_y < TILE_SIZE:
            return

        # Don't draw in bottom border area (when at bottom of map)
        if self.camera_offset_y >= max_y_offset and max_y_offset > 0:
            bottom_border_y = (visible_tiles_y - 1) * TILE_SIZE
            if screen_y >= bottom_border_y:
                return

        # Don't draw if completely off screen
        if screen_y < 0 or screen_y >= constants.MAP_AREA_HEIGHT:
            return

        # Determine unit color based on faction
        faction_id = faction_assignments[unit.owner]
        color = FACTIONS[faction_id]['color']

        center_x = screen_x + TILE_SIZE // 2
        center_y = screen_y + TILE_SIZE // 2
        radius = TILE_SIZE // 3

        # Draw main unit circle
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, COLOR_BLACK, (center_x, center_y), radius, 3)

        # Draw unit type letter
        font = pygame.font.Font(None, 28)
        # Show 'C' for colony pods, 'A' for artifacts, otherwise first letter of type
        if unit.unit_type in [UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA]:
            type_char = 'C'
        elif unit.unit_type == UNIT_ARTIFACT:
            type_char = 'A'
        else:
            type_char = unit.unit_type[0].upper()
        text_surf = font.render(type_char, True, COLOR_BLACK)

        # Explicitly get the rect and set the center attribute
        text_rect = text_surf.get_rect()
        text_rect.center = (center_x, center_y)

        self.screen.blit(text_surf, text_rect)

        # Draw held indicator if unit is held
        if hasattr(unit, 'held') and unit.held:
            held_font = pygame.font.Font(None, 20)
            held_surf = held_font.render('H', True, (255, 255, 100))
            held_rect = held_surf.get_rect()
            held_rect.center = (center_x + radius - 5, center_y - radius + 5)
            # Draw dark background circle for visibility
            pygame.draw.circle(self.screen, (50, 50, 50), held_rect.center, 8)
            self.screen.blit(held_surf, held_rect)

        # Draw selection indicator if selected
        if unit == selected_unit:
            self._draw_selection_indicator(screen_x, screen_y, unit)

    def _draw_selection_indicator(self, tile_x, tile_y, unit):
        """Draw selection indicator and health bar in top-left of tile.

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

        # Selection indicator (pentagon pointing down) next to health bar
        size = 10
        x = bar_x + bar_width + 2
        y = tile_y + 2

        # Pentagon vertices (pentagon pointing down)
        points = [
            (x, y),                    # Top-left
            (x + size, y),             # Top-right
            (x + size, y + size - 3),  # Right before point
            (x + size // 2, y + size), # Bottom point
            (x, y + size - 3)          # Left before point
        ]

        # Draw filled yellow selection indicator
        pygame.draw.polygon(self.screen, COLOR_UNIT_SELECTED, points)
        pygame.draw.polygon(self.screen, COLOR_BLACK, points, 1)

        # Morale indicator - vertical bar with segments to the right of selection indicator
        # Only draw if unit has morale system (backward compatibility)
        if hasattr(unit, 'morale_level'):
            morale_x = x + size + 2
            morale_y = tile_y + 2
            morale_width = 3
            morale_height = 10  # Match selection indicator height
            segment_height = morale_height / 7  # 7 morale levels (0-7)

            # Draw background for morale bar
            morale_bg_rect = pygame.Rect(morale_x, morale_y, morale_width, morale_height)
            pygame.draw.rect(self.screen, (40, 40, 40), morale_bg_rect)
            pygame.draw.rect(self.screen, COLOR_BLACK, morale_bg_rect, 1)

            # Fill segments from top to bottom based on morale level
            # Morale levels: 0-7 (Very Very Green to Elite)
            # Fill (morale_level + 1) segments (so Green=2 fills 3 segments)
            filled_segments = unit.morale_level + 1
            for i in range(filled_segments):
                seg_y = morale_y + (i * segment_height)
                seg_rect = pygame.Rect(morale_x, int(seg_y), morale_width, int(segment_height) + 1)

                # Color based on morale tier
                if unit.morale_level >= 7:  # Elite
                    seg_color = (255, 215, 0)  # Gold
                elif unit.morale_level >= 5:  # Veteran+
                    seg_color = (100, 200, 255)  # Light blue
                elif unit.morale_level >= 3:  # Disciplined+
                    seg_color = (150, 255, 150)  # Light green
                else:  # Below Disciplined
                    seg_color = (180, 180, 180)  # Gray

                pygame.draw.rect(self.screen, seg_color, seg_rect)

    def draw_bases(self, bases, player_id, game_map, faction_assignments=None):
        """Draw all bases on the map."""
        for base in bases:
            self.draw_base(base, player_id, game_map, faction_assignments)

    def draw_base(self, base, player_id, game_map, faction_assignments=None):
        """Draw a single base."""
        wrapped_x = (base.x - self.camera_offset_x) % game_map.width
        screen_x = (wrapped_x * TILE_SIZE) + self.base_offset_x
        screen_y = (base.y - self.camera_offset_y) * TILE_SIZE

        # Only draw if on screen (excluding border areas)
        if screen_x < -TILE_SIZE or screen_x > constants.SCREEN_WIDTH:
            return

        # Calculate visible area
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE
        max_y_offset = max(0, game_map.height - visible_tiles_y)

        # Don't draw in top border area (when at top of map)
        if self.camera_offset_y == 0 and screen_y < TILE_SIZE:
            return

        # Don't draw in bottom border area (when at bottom of map)
        if self.camera_offset_y >= max_y_offset and max_y_offset > 0:
            bottom_border_y = (visible_tiles_y - 1) * TILE_SIZE
            if screen_y >= bottom_border_y:
                return

        # Don't draw if completely off screen
        if screen_y < 0 or screen_y >= constants.MAP_AREA_HEIGHT:
            return

        # Determine color based on faction
        faction_id = faction_assignments[base.owner]
        color = FACTIONS[faction_id]['color']

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

        # Draw current production below name
        if hasattr(base, 'current_production') and base.current_production:
            prod_text = base.current_production
            # Check if governor is enabled
            if hasattr(base, 'governor_enabled') and base.governor_enabled:
                prod_display = f"(Gov:{prod_text})"
            else:
                prod_display = f"({prod_text})"

            small_font = pygame.font.Font(None, 16)
            prod_surf = small_font.render(prod_display, True, (180, 190, 200))
            prod_rect = prod_surf.get_rect()
            prod_rect.centerx = screen_x + TILE_SIZE // 2
            prod_rect.top = name_rect.bottom + 2

            # Draw background for production text
            prod_bg_rect = prod_rect.inflate(4, 2)
            pygame.draw.rect(self.screen, COLOR_BLACK, prod_bg_rect)
            self.screen.blit(prod_surf, prod_rect)

        # Draw population in top-left corner
        pop_size = 20
        pop_rect = pygame.Rect(screen_x + 2, screen_y + 2, pop_size, pop_size)

        # Only draw background fill if there are garrisoned units
        if len(base.garrison) > 0:
            # Use faction color for garrison indicator
            faction_id = faction_assignments[base.owner]
            pop_color = FACTIONS[faction_id]['color']
            pygame.draw.rect(self.screen, pop_color, pop_rect)

        # Always draw black outline (thicker for visibility)
        pygame.draw.rect(self.screen, COLOR_BLACK, pop_rect, 2)

        # Always draw population number in black (bold font for visibility)
        pop_font = pygame.font.Font(None, 18)  # Slightly larger for boldness
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

    def draw_territory_borders(self, territory, game_map, faction_assignments=None):
        """Draw dotted territory borders for all players using faction colors.

        When territories abut, draws both faction colors side-by-side on the border.

        Args:
            territory (TerritoryManager): Territory management system
            game_map: The game map for wrapping calculations
            faction_assignments: Dict mapping player_id to faction_id (optional)
        """
        from game.data.data import FACTIONS

        # Get faction colors for each player
        def get_player_color(player_id):
            if faction_assignments and player_id in faction_assignments:
                faction_id = faction_assignments[player_id]
                if 0 <= faction_id < len(FACTIONS):
                    return FACTIONS[faction_id]['color']
            # Fallback colors if no faction assignment
            fallback = {
                0: (50, 205, 50), 1: (100, 100, 255), 2: (255, 255, 255),
                3: (255, 215, 0), 4: (139, 69, 19), 5: (255, 165, 0), 6: (180, 140, 230)
            }
            return fallback.get(player_id, (150, 150, 150))

        # Calculate visible range with wrapping
        visible_tiles_x = (constants.SCREEN_WIDTH // TILE_SIZE) + 2
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE

        # For each visible tile, draw border edges with dual colors
        for screen_y_idx in range(visible_tiles_y):
            map_y = self.camera_offset_y + screen_y_idx
            if map_y >= game_map.height:
                continue

            for screen_x_idx in range(visible_tiles_x):
                map_x = (self.camera_offset_x + screen_x_idx) % game_map.width
                owner = territory.get_tile_owner(map_x, map_y)
                if owner is None:
                    continue

                # Check each edge and get neighbor owner
                directions = [
                    ('N', 0, -1),
                    ('E', 1, 0),
                    ('S', 0, 1),
                    ('W', -1, 0)
                ]

                for edge_dir, dx, dy in directions:
                    nx = (map_x + dx) % game_map.width
                    ny = map_y + dy

                    # Skip if out of bounds (Y doesn't wrap)
                    if ny < 0 or ny >= game_map.height:
                        neighbor_owner = None
                    else:
                        neighbor_owner = territory.get_tile_owner(nx, ny)

                    # Only draw border if owners differ
                    if neighbor_owner != owner:
                        my_color = get_player_color(owner)
                        neighbor_color = get_player_color(neighbor_owner) if neighbor_owner is not None else None
                        self._draw_dual_color_border_at_screen_pos(
                            screen_x_idx, screen_y_idx, edge_dir, my_color, neighbor_color
                        )

    def _draw_dual_color_border_at_screen_pos(self, screen_x_idx, screen_y_idx, edge_dir, my_color, neighbor_color):
        """Draw territory border with dual colors when territories abut.

        Draws the owner's color on the inside and neighbor's color on the outside.
        If no neighbor, draws only the owner's color.

        Args:
            screen_x_idx (int): Screen X index
            screen_y_idx (int): Screen Y index
            edge_dir (str): Edge direction ('N', 'E', 'S', 'W')
            my_color (tuple): RGB color for this tile's owner
            neighbor_color (tuple or None): RGB color for neighbor owner (None if no neighbor)
        """
        screen_x = (screen_x_idx * TILE_SIZE) + self.base_offset_x
        screen_y = screen_y_idx * TILE_SIZE

        # Dash pattern: 5 pixels on, 3 pixels off
        dash_length = 5
        gap_length = 3
        pattern_length = dash_length + gap_length

        if edge_dir == 'N':
            # Top edge - draw my color below, neighbor color above
            y_pos_inner = screen_y + 1  # Inside the tile
            y_pos_outer = screen_y - 1  # Outside the tile
            for i in range(0, TILE_SIZE, pattern_length):
                x_start = screen_x + i
                x_end = min(screen_x + i + dash_length, screen_x + TILE_SIZE)
                # Draw my color on inner line
                pygame.draw.line(self.screen, my_color, (x_start, y_pos_inner), (x_end, y_pos_inner), 1)
                # Draw neighbor color on outer line if exists
                if neighbor_color:
                    pygame.draw.line(self.screen, neighbor_color, (x_start, y_pos_outer), (x_end, y_pos_outer), 1)

        elif edge_dir == 'S':
            # Bottom edge - draw my color above, neighbor color below
            y_pos_inner = screen_y + TILE_SIZE - 1  # Inside the tile
            y_pos_outer = screen_y + TILE_SIZE + 1  # Outside the tile
            for i in range(0, TILE_SIZE, pattern_length):
                x_start = screen_x + i
                x_end = min(screen_x + i + dash_length, screen_x + TILE_SIZE)
                # Draw my color on inner line
                pygame.draw.line(self.screen, my_color, (x_start, y_pos_inner), (x_end, y_pos_inner), 1)
                # Draw neighbor color on outer line if exists
                if neighbor_color:
                    pygame.draw.line(self.screen, neighbor_color, (x_start, y_pos_outer), (x_end, y_pos_outer), 1)

        elif edge_dir == 'W':
            # Left edge - draw my color right, neighbor color left
            x_pos_inner = screen_x + 1  # Inside the tile
            x_pos_outer = screen_x - 1  # Outside the tile
            for i in range(0, TILE_SIZE, pattern_length):
                y_start = screen_y + i
                y_end = min(screen_y + i + dash_length, screen_y + TILE_SIZE)
                # Draw my color on inner line
                pygame.draw.line(self.screen, my_color, (x_pos_inner, y_start), (x_pos_inner, y_end), 1)
                # Draw neighbor color on outer line if exists
                if neighbor_color:
                    pygame.draw.line(self.screen, neighbor_color, (x_pos_outer, y_start), (x_pos_outer, y_end), 1)

        elif edge_dir == 'E':
            # Right edge - draw my color left, neighbor color right
            x_pos_inner = screen_x + TILE_SIZE - 1  # Inside the tile
            x_pos_outer = screen_x + TILE_SIZE + 1  # Outside the tile
            for i in range(0, TILE_SIZE, pattern_length):
                y_start = screen_y + i
                y_end = min(screen_y + i + dash_length, screen_y + TILE_SIZE)
                # Draw my color on inner line
                pygame.draw.line(self.screen, my_color, (x_pos_inner, y_start), (x_pos_inner, y_end), 1)
                # Draw neighbor color on outer line if exists
                if neighbor_color:
                    pygame.draw.line(self.screen, neighbor_color, (x_pos_outer, y_start), (x_pos_outer, y_end), 1)

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
        base_screen_y = (base.y - self.camera_offset_y) * TILE_SIZE

        pop_size = 20
        pop_rect = pygame.Rect(base_screen_x + 2, base_screen_y + 2, pop_size, pop_size)
        return pop_rect.collidepoint(screen_x, screen_y)

    def screen_to_tile(self, screen_x, screen_y, game_map):
        """Convert screen to tile, accounting for camera wrapping and vertical offset."""
        screen_tile_x = (screen_x - self.base_offset_x) // TILE_SIZE
        tile_x = (self.camera_offset_x + screen_tile_x) % game_map.width
        screen_tile_y = screen_y // TILE_SIZE
        tile_y = self.camera_offset_y + screen_tile_y
        return int(tile_x), int(tile_y)

    def draw_supply_pods(self, game_map):
        """Draw supply pods on the map."""
        visible_tiles_x = (constants.SCREEN_WIDTH // TILE_SIZE) + 2
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE

        for screen_y_idx in range(visible_tiles_y):
            map_y = self.camera_offset_y + screen_y_idx
            if map_y >= game_map.height:
                continue

            for screen_x_idx in range(visible_tiles_x):
                map_x = (self.camera_offset_x + screen_x_idx) % game_map.width
                tile = game_map.get_tile(map_x, map_y)

                if tile and tile.supply_pod:
                    # Calculate screen position
                    screen_x = (screen_x_idx * TILE_SIZE) + self.base_offset_x
                    screen_y = screen_y_idx * TILE_SIZE

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

    def draw_monoliths(self, game_map):
        """Draw monoliths on the map (brown towers)."""
        visible_tiles_x = (constants.SCREEN_WIDTH // TILE_SIZE) + 2
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE

        for screen_y_idx in range(visible_tiles_y):
            map_y = self.camera_offset_y + screen_y_idx
            if map_y >= game_map.height:
                continue

            for screen_x_idx in range(visible_tiles_x):
                map_x = (self.camera_offset_x + screen_x_idx) % game_map.width
                tile = game_map.get_tile(map_x, map_y)

                if tile and tile.monolith:
                    # Calculate screen position
                    screen_x = (screen_x_idx * TILE_SIZE) + self.base_offset_x
                    screen_y = screen_y_idx * TILE_SIZE

                    # Only draw if on screen
                    if screen_x < -TILE_SIZE or screen_x > constants.SCREEN_WIDTH:
                        continue
                    if screen_y < 0 or screen_y >= constants.MAP_AREA_HEIGHT:
                        continue

                    # Draw brown square for monolith base
                    base_size = TILE_SIZE * 2 // 3
                    base_x = screen_x + (TILE_SIZE - base_size) // 2
                    base_y = screen_y + (TILE_SIZE - base_size) // 2
                    pygame.draw.rect(self.screen, (101, 67, 33), (base_x, base_y, base_size, base_size))

                    # Draw dark brown border
                    pygame.draw.rect(self.screen, (70, 45, 20), (base_x, base_y, base_size, base_size), 2)

                    # Draw tower shape (stacked rectangles getting smaller)
                    tower_width = base_size * 2 // 3
                    tower_height = base_size // 4
                    tower_x = base_x + (base_size - tower_width) // 2
                    tower_y = base_y + 4

                    # Three stacked segments
                    for i in range(3):
                        segment_width = tower_width - (i * 4)
                        segment_x = tower_x + (i * 2)
                        segment_y = tower_y + (i * tower_height)
                        pygame.draw.rect(self.screen, (120, 80, 40), (segment_x, segment_y, segment_width, tower_height))
                        pygame.draw.rect(self.screen, (80, 55, 25), (segment_x, segment_y, segment_width, tower_height), 1)

    def draw_map_edge_indicators(self, game_map):
        """Draw full tile height black bars at top and bottom when map edges are visible."""
        visible_tiles_y = constants.MAP_AREA_HEIGHT // TILE_SIZE
        max_y_offset = max(0, game_map.height - visible_tiles_y)

        # Top border: when at y=0, show 1 tile of black at top
        if self.camera_offset_y == 0:
            border_rect = pygame.Rect(0, 0, constants.SCREEN_WIDTH, TILE_SIZE)
            pygame.draw.rect(self.screen, COLOR_BLACK, border_rect)

        # Bottom border: when at max scroll, show 1 tile of black instead of last tile row
        # Same logic as top: occupy the space where the last visible tile row would be
        if self.camera_offset_y >= max_y_offset and max_y_offset > 0:
            # Draw black rectangle at the position of the last tile row (visible_tiles_y - 1)
            bottom_border_y = (visible_tiles_y - 1) * TILE_SIZE
            border_rect = pygame.Rect(0, bottom_border_y, constants.SCREEN_WIDTH, TILE_SIZE)
            pygame.draw.rect(self.screen, COLOR_BLACK, border_rect)