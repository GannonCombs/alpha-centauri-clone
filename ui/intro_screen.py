"""Intro screen and faction selection UI."""

import pygame
from .data import FACTIONS


class IntroScreenManager:
    """Manages the intro screen, faction selection, and name input."""

    def __init__(self, font, small_font):
        """Initialize the intro screen manager.

        Args:
            font: Regular pygame font
            small_font: Small pygame font
        """
        self.font = font
        self.small_font = small_font
        self.large_font = pygame.font.Font(None, 72)
        self.title_font = pygame.font.Font(None, 48)

        # Screen state
        self.mode = 'intro'  # 'intro', 'map_select', 'map_size', 'land_composition', 'erosive_forces', 'alien_life', 'skill_level', 'faction_select', 'name_input', None (game started)
        self.selected_faction_id = None
        self.player_name_input = ""
        self.name_input_selected = False  # Track if name input text is selected for replacement
        self.cursor_visible = True
        self.cursor_timer = 0
        self.show_exit_confirm = False  # Exit confirmation dialog

        # Map customization settings
        self.selected_map_size = 'standard'  # Only standard for now
        self.selected_ocean_percentage = None  # Will be set when ocean composition is selected
        self.selected_erosive_forces = None  # 'abundant', 'average', 'desert'
        self.selected_alien_life = None  # 'abundant', 'average', 'rare'
        self.selected_skill_level = None  # 1-6

        # UI elements
        self.new_game_button_rect = None
        self.load_game_button_rect = None
        self.exit_game_button_rect = None
        self.random_map_button_rect = None
        self.custom_map_button_rect = None
        self.map_size_button_rects = []  # Map size selection buttons
        self.land_comp_button_rects = []  # Land composition selection buttons
        self.erosive_forces_button_rects = []  # Erosive forces selection buttons
        self.alien_life_button_rects = []  # Alien life form selection buttons
        self.skill_level_button_rects = []  # Skill level selection buttons
        self.faction_button_rects = []
        self.ok_button_rect = None
        self.cancel_button_rect = None
        self.name_input_rect = None
        self.exit_confirm_ok_rect = None
        self.exit_confirm_cancel_rect = None

    def draw(self, screen, screen_width, screen_height):
        """Render the active intro screen.

        Args:
            screen: Pygame screen surface
            screen_width: Screen width
            screen_height: Screen height
        """
        if self.mode == 'intro':
            self._draw_intro(screen, screen_width, screen_height)
        elif self.mode == 'map_select':
            self._draw_map_select(screen, screen_width, screen_height)
        elif self.mode == 'map_size':
            self._draw_map_size(screen, screen_width, screen_height)
        elif self.mode == 'land_composition':
            self._draw_land_composition(screen, screen_width, screen_height)
        elif self.mode == 'erosive_forces':
            self._draw_erosive_forces(screen, screen_width, screen_height)
        elif self.mode == 'alien_life':
            self._draw_alien_life(screen, screen_width, screen_height)
        elif self.mode == 'skill_level':
            self._draw_skill_level(screen, screen_width, screen_height)
        elif self.mode == 'faction_select':
            self._draw_faction_select(screen, screen_width, screen_height)
        elif self.mode == 'name_input':
            self._draw_name_input(screen, screen_width, screen_height)

        # Draw exit confirmation dialog on top if active
        if self.show_exit_confirm:
            self._draw_exit_confirm(screen, screen_width, screen_height)

    def _draw_intro(self, screen, screen_width, screen_height):
        """Draw the main intro screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "ALPHA CENTAURI"
        title_surf = self.large_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 150))

        subtitle_text = "Clone Edition"
        subtitle_surf = self.font.render(subtitle_text, True, (150, 180, 200))
        screen.blit(subtitle_surf, (screen_width // 2 - subtitle_surf.get_width() // 2, 240))

        # Buttons
        button_w = 300
        button_h = 70
        button_spacing = 30

        # New Game button
        new_game_y = screen_height // 2 - 50
        self.new_game_button_rect = pygame.Rect(
            screen_width // 2 - button_w // 2,
            new_game_y,
            button_w,
            button_h
        )
        new_game_hover = self.new_game_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if new_game_hover else (45, 55, 65),
                        self.new_game_button_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 180, 200), self.new_game_button_rect, 3, border_radius=8)

        new_game_text = self.font.render("New Game", True, (220, 230, 240))
        screen.blit(new_game_text, (self.new_game_button_rect.centerx - new_game_text.get_width() // 2,
                                   self.new_game_button_rect.centery - 10))

        # Load Game button
        load_game_y = new_game_y + button_h + button_spacing
        self.load_game_button_rect = pygame.Rect(
            screen_width // 2 - button_w // 2,
            load_game_y,
            button_w,
            button_h
        )
        load_game_hover = self.load_game_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if load_game_hover else (45, 55, 65),
                        self.load_game_button_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 180, 200), self.load_game_button_rect, 3, border_radius=8)

        load_game_text = self.font.render("Load Game", True, (220, 230, 240))
        screen.blit(load_game_text, (self.load_game_button_rect.centerx - load_game_text.get_width() // 2,
                                    self.load_game_button_rect.centery - 10))

        # Exit Game button
        exit_game_y = load_game_y + button_h + button_spacing
        self.exit_game_button_rect = pygame.Rect(
            screen_width // 2 - button_w // 2,
            exit_game_y,
            button_w,
            button_h
        )
        exit_game_hover = self.exit_game_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (110, 70, 70) if exit_game_hover else (65, 45, 45),
                        self.exit_game_button_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 100, 100), self.exit_game_button_rect, 3, border_radius=8)

        exit_game_text = self.font.render("Exit Game", True, (220, 230, 240))
        screen.blit(exit_game_text, (self.exit_game_button_rect.centerx - exit_game_text.get_width() // 2,
                                    self.exit_game_button_rect.centery - 10))

    def _draw_map_select(self, screen, screen_width, screen_height):
        """Draw map selection screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "Map Selection"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 150))

        # Buttons
        button_w = 400
        button_h = 80
        button_spacing = 40
        start_y = screen_height // 2 - 100

        # Make Random Map button
        self.random_map_button_rect = pygame.Rect(
            screen_width // 2 - button_w // 2,
            start_y,
            button_w,
            button_h
        )
        random_hover = self.random_map_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if random_hover else (45, 55, 65),
                        self.random_map_button_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 180, 200), self.random_map_button_rect, 3, border_radius=8)

        random_text = self.font.render("Make Random Map", True, (220, 230, 240))
        screen.blit(random_text, (self.random_map_button_rect.centerx - random_text.get_width() // 2,
                                 self.random_map_button_rect.centery - 10))

        # Customize Map button (now enabled)
        custom_y = start_y + button_h + button_spacing
        self.custom_map_button_rect = pygame.Rect(
            screen_width // 2 - button_w // 2,
            custom_y,
            button_w,
            button_h
        )
        custom_hover = self.custom_map_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if custom_hover else (45, 55, 65),
                        self.custom_map_button_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 180, 200), self.custom_map_button_rect, 3, border_radius=8)

        custom_text = self.font.render("Customize Map", True, (220, 230, 240))
        screen.blit(custom_text, (self.custom_map_button_rect.centerx - custom_text.get_width() // 2,
                                 self.custom_map_button_rect.centery - 10))

    def _draw_map_size(self, screen, screen_width, screen_height):
        """Draw map size selection screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "Select Map Size"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 100))

        # Map size options
        map_sizes = [
            ('tiny', 'Tiny Map', False),
            ('small', 'Small Map', False),
            ('standard', 'Standard Map', True),  # Only this one is enabled
            ('large', 'Large Map', False),
            ('huge', 'Huge Map', False)
        ]

        button_w = 400
        button_h = 70
        button_spacing = 20
        start_y = 240

        self.map_size_button_rects = []

        for i, (size_id, size_name, enabled) in enumerate(map_sizes):
            button_y = start_y + i * (button_h + button_spacing)
            button_rect = pygame.Rect(
                screen_width // 2 - button_w // 2,
                button_y,
                button_w,
                button_h
            )

            if enabled:
                is_hover = button_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (70, 90, 110) if is_hover else (45, 55, 65)
                border_color = (120, 180, 200)
                text_color = (220, 230, 240)
            else:
                bg_color = (30, 35, 40)
                border_color = (80, 90, 100)
                text_color = (100, 110, 120)

            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, button_rect, 2 if enabled else 1, border_radius=8)

            text_surf = self.font.render(size_name, True, text_color)
            screen.blit(text_surf, (button_rect.centerx - text_surf.get_width() // 2,
                                   button_rect.centery - 10))

            self.map_size_button_rects.append((button_rect, size_id, enabled))

    def _draw_land_composition(self, screen, screen_width, screen_height):
        """Draw ocean composition selection screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "Select Planet Composition"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 120))

        # Subtitle
        subtitle_text = "Choose the percentage of ocean on your planet"
        subtitle_surf = self.small_font.render(subtitle_text, True, (150, 180, 200))
        screen.blit(subtitle_surf, (screen_width // 2 - subtitle_surf.get_width() // 2, 190))

        # Ocean composition options
        land_compositions = [
            ((30, 50), '30-50% Ocean', 'Dry Planet - Large continents and inland seas'),
            ((50, 70), '50-70% Ocean', 'Balanced - Mix of land and sea'),
            ((70, 90), '70-90% Ocean', 'Wet Planet - Archipelagos and small continents')
        ]

        button_w = 600
        button_h = 90
        button_spacing = 30
        start_y = 280

        self.land_comp_button_rects = []

        for i, (range_tuple, range_name, description) in enumerate(land_compositions):
            button_y = start_y + i * (button_h + button_spacing)
            button_rect = pygame.Rect(
                screen_width // 2 - button_w // 2,
                button_y,
                button_w,
                button_h
            )

            is_hover = button_rect.collidepoint(pygame.mouse.get_pos())
            bg_color = (70, 90, 110) if is_hover else (45, 55, 65)

            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 180, 200), button_rect, 3, border_radius=8)

            # Main text
            text_surf = self.font.render(range_name, True, (220, 230, 240))
            screen.blit(text_surf, (button_rect.x + 20, button_rect.y + 15))

            # Description
            desc_surf = self.small_font.render(description, True, (150, 170, 190))
            screen.blit(desc_surf, (button_rect.x + 20, button_rect.y + 50))

            self.land_comp_button_rects.append((button_rect, range_tuple))

    def _draw_erosive_forces(self, screen, screen_width, screen_height):
        """Draw erosive forces selection screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "Adjust Erosive Forces"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 150))

        # Erosive forces options (only first one enabled)
        erosive_options = [
            ('abundant', 'Abundant', True),  # Only this is enabled
            ('average', 'Average', False),
            ('desert', 'Desert', False)
        ]

        button_w = 400
        button_h = 70
        button_spacing = 30
        start_y = 300

        self.erosive_forces_button_rects = []

        for i, (erosive_id, erosive_name, enabled) in enumerate(erosive_options):
            button_y = start_y + i * (button_h + button_spacing)
            button_rect = pygame.Rect(
                screen_width // 2 - button_w // 2,
                button_y,
                button_w,
                button_h
            )

            if enabled:
                is_hover = button_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (70, 90, 110) if is_hover else (45, 55, 65)
                border_color = (120, 180, 200)
                text_color = (220, 230, 240)
            else:
                bg_color = (30, 35, 40)
                border_color = (80, 90, 100)
                text_color = (100, 110, 120)

            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, button_rect, 3 if enabled else 1, border_radius=8)

            text_surf = self.font.render(erosive_name, True, text_color)
            screen.blit(text_surf, (button_rect.centerx - text_surf.get_width() // 2,
                                   button_rect.centery - 10))

            self.erosive_forces_button_rects.append((button_rect, erosive_id, enabled))

    def _draw_alien_life(self, screen, screen_width, screen_height):
        """Draw alien life form prominence selection screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "Alien Life Form Prominence"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 150))

        # Alien life options (only first one enabled)
        alien_options = [
            ('abundant', 'Abundant', True),  # Only this is enabled
            ('average', 'Average', False),
            ('rare', 'Rare', False)
        ]

        button_w = 400
        button_h = 70
        button_spacing = 30
        start_y = 300

        self.alien_life_button_rects = []

        for i, (alien_id, alien_name, enabled) in enumerate(alien_options):
            button_y = start_y + i * (button_h + button_spacing)
            button_rect = pygame.Rect(
                screen_width // 2 - button_w // 2,
                button_y,
                button_w,
                button_h
            )

            if enabled:
                is_hover = button_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (70, 90, 110) if is_hover else (45, 55, 65)
                border_color = (120, 180, 200)
                text_color = (220, 230, 240)
            else:
                bg_color = (30, 35, 40)
                border_color = (80, 90, 100)
                text_color = (100, 110, 120)

            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, button_rect, 3 if enabled else 1, border_radius=8)

            text_surf = self.font.render(alien_name, True, text_color)
            screen.blit(text_surf, (button_rect.centerx - text_surf.get_width() // 2,
                                   button_rect.centery - 10))

            self.alien_life_button_rects.append((button_rect, alien_id, enabled))

    def _draw_skill_level(self, screen, screen_width, screen_height):
        """Draw skill level selection screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "Skill Level"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 100))

        # Skill level options (only first one enabled)
        skill_options = [
            (1, '1', True),  # Only this is enabled
            (2, '2', False),
            (3, '3', False),
            (4, '4', False),
            (5, '5', False),
            (6, '6 (hardest)', False)
        ]

        button_w = 300
        button_h = 60
        button_spacing = 20
        start_y = 220

        self.skill_level_button_rects = []

        for i, (level, level_text, enabled) in enumerate(skill_options):
            button_y = start_y + i * (button_h + button_spacing)
            button_rect = pygame.Rect(
                screen_width // 2 - button_w // 2,
                button_y,
                button_w,
                button_h
            )

            if enabled:
                is_hover = button_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (70, 90, 110) if is_hover else (45, 55, 65)
                border_color = (120, 180, 200)
                text_color = (220, 230, 240)
            else:
                bg_color = (30, 35, 40)
                border_color = (80, 90, 100)
                text_color = (100, 110, 120)

            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, button_rect, 3 if enabled else 1, border_radius=8)

            text_surf = self.font.render(level_text, True, text_color)
            screen.blit(text_surf, (button_rect.centerx - text_surf.get_width() // 2,
                                   button_rect.centery - 10))

            self.skill_level_button_rects.append((button_rect, level, enabled))

    def _draw_faction_select(self, screen, screen_width, screen_height):
        """Draw faction selection screen."""
        # Background
        screen.fill((10, 15, 25))

        # Title
        title_text = "Choose Your Faction"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 80))

        # Faction buttons (all 7 factions)
        self.faction_button_rects = []
        button_w = 700
        button_h = 70
        start_y = 180

        for i, faction in enumerate(FACTIONS):
            button_y = start_y + i * 85
            button_rect = pygame.Rect(
                screen_width // 2 - button_w // 2,
                button_y,
                button_w,
                button_h
            )

            is_selected = i == self.selected_faction_id
            is_hover = button_rect.collidepoint(pygame.mouse.get_pos())

            # Background color
            if is_selected:
                bg_color = (90, 120, 140)
            elif is_hover:
                bg_color = (70, 90, 110)
            else:
                bg_color = (45, 55, 65)

            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, faction['color'], button_rect, 3, border_radius=8)

            # Faction name and leader
            name_text = self.font.render(f"{faction['name']}", True, faction['color'])
            leader_text = self.small_font.render(f"{faction['leader']}", True, (180, 190, 200))

            screen.blit(name_text, (button_rect.x + 20, button_rect.y + 15))
            screen.blit(leader_text, (button_rect.x + 20, button_rect.y + 45))

            self.faction_button_rects.append((button_rect, i))

        # OK button (only show if faction selected)
        if self.selected_faction_id is not None:
            ok_button_w = 200
            ok_button_h = 50
            ok_button_y = start_y + len(FACTIONS) * 85 + 30
            self.ok_button_rect = pygame.Rect(
                screen_width // 2 - ok_button_w // 2,
                ok_button_y,
                ok_button_w,
                ok_button_h
            )

            ok_hover = self.ok_button_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (70, 140, 70) if ok_hover else (50, 100, 50),
                           self.ok_button_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 200, 100), self.ok_button_rect, 2, border_radius=8)

            ok_text = self.font.render("Continue", True, (220, 230, 240))
            screen.blit(ok_text, (self.ok_button_rect.centerx - ok_text.get_width() // 2,
                                 self.ok_button_rect.centery - 10))

    def _draw_name_input(self, screen, screen_width, screen_height):
        """Draw name input screen."""
        # Background
        screen.fill((10, 15, 25))

        # Get selected faction
        faction = FACTIONS[self.selected_faction_id]

        # Title
        title_text = f"Enter Your Name"
        title_surf = self.title_font.render(title_text, True, (100, 200, 255))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 150))

        # Subtitle with faction
        subtitle_text = f"{faction['name']} Leader"
        subtitle_surf = self.font.render(subtitle_text, True, faction['color'])
        screen.blit(subtitle_surf, (screen_width // 2 - subtitle_surf.get_width() // 2, 220))

        # Input field
        input_w = 500
        input_h = 60
        input_y = screen_height // 2 - 50
        self.name_input_rect = pygame.Rect(
            screen_width // 2 - input_w // 2,
            input_y,
            input_w,
            input_h
        )

        pygame.draw.rect(screen, (50, 60, 70), self.name_input_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 180, 200), self.name_input_rect, 2, border_radius=8)

        # Text content
        text_x = self.name_input_rect.x + 15
        text_y = self.name_input_rect.centery - self.font.get_height() // 2

        # If text is selected, draw selection highlight
        if self.name_input_selected and self.player_name_input:
            text_surf = self.font.render(self.player_name_input, True, (255, 255, 255))
            # Draw selection background
            selection_rect = pygame.Rect(text_x - 2, text_y - 2,
                                        text_surf.get_width() + 4, text_surf.get_height() + 4)
            pygame.draw.rect(screen, (80, 120, 200), selection_rect)  # Blue highlight
            screen.blit(text_surf, (text_x, text_y))
        else:
            text_surf = self.font.render(self.player_name_input, True, (220, 230, 240))
            screen.blit(text_surf, (text_x, text_y))

        # Blinking cursor
        if self.cursor_visible:
            cursor_x = text_x + text_surf.get_width() + 3
            pygame.draw.line(screen, (220, 230, 240),
                           (cursor_x, text_y), (cursor_x, text_y + text_surf.get_height()), 2)

        # Buttons
        button_w = 150
        button_h = 50
        button_y = input_y + 120

        # OK button
        ok_x = screen_width // 2 - button_w - 10
        self.ok_button_rect = pygame.Rect(ok_x, button_y, button_w, button_h)

        ok_hover = self.ok_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 140, 70) if ok_hover else (50, 100, 50),
                        self.ok_button_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 100), self.ok_button_rect, 2, border_radius=8)

        ok_text = self.font.render("OK", True, (220, 230, 240))
        screen.blit(ok_text, (self.ok_button_rect.centerx - ok_text.get_width() // 2,
                             self.ok_button_rect.centery - 10))

        # Cancel button
        cancel_x = screen_width // 2 + 10
        self.cancel_button_rect = pygame.Rect(cancel_x, button_y, button_w, button_h)

        cancel_hover = self.cancel_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (140, 70, 70) if cancel_hover else (100, 50, 50),
                        self.cancel_button_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 100, 100), self.cancel_button_rect, 2, border_radius=8)

        cancel_text = self.font.render("Cancel", True, (220, 230, 240))
        screen.blit(cancel_text, (self.cancel_button_rect.centerx - cancel_text.get_width() // 2,
                                 self.cancel_button_rect.centery - 10))

    def _draw_exit_confirm(self, screen, screen_width, screen_height):
        """Draw exit confirmation dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Small dialog box
        dialog_w = 400
        dialog_h = 200
        dialog_x = screen_width // 2 - dialog_w // 2
        dialog_y = screen_height // 2 - dialog_h // 2

        # Dialog background
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 140, 160), dialog_rect, 3, border_radius=10)

        # Message
        message_text = "Are you sure you want to exit?"
        message_surf = self.font.render(message_text, True, (220, 230, 240))
        screen.blit(message_surf, (dialog_x + dialog_w // 2 - message_surf.get_width() // 2, dialog_y + 50))

        # Buttons
        button_w = 120
        button_h = 50
        button_y = dialog_y + dialog_h - 80

        # OK button
        ok_x = dialog_x + dialog_w // 2 - button_w - 10
        self.exit_confirm_ok_rect = pygame.Rect(ok_x, button_y, button_w, button_h)

        ok_hover = self.exit_confirm_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (110, 70, 70) if ok_hover else (90, 50, 50),
                        self.exit_confirm_ok_rect, border_radius=6)
        pygame.draw.rect(screen, (180, 100, 100), self.exit_confirm_ok_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, (220, 230, 240))
        screen.blit(ok_text, (self.exit_confirm_ok_rect.centerx - ok_text.get_width() // 2,
                             self.exit_confirm_ok_rect.centery - 10))

        # Cancel button
        cancel_x = dialog_x + dialog_w // 2 + 10
        self.exit_confirm_cancel_rect = pygame.Rect(cancel_x, button_y, button_w, button_h)

        cancel_hover = self.exit_confirm_cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if cancel_hover else (50, 70, 90),
                        self.exit_confirm_cancel_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 140, 180), self.exit_confirm_cancel_rect, 2, border_radius=6)

        cancel_text = self.font.render("Cancel", True, (220, 230, 240))
        screen.blit(cancel_text, (self.exit_confirm_cancel_rect.centerx - cancel_text.get_width() // 2,
                                 self.exit_confirm_cancel_rect.centery - 10))

    def handle_event(self, event):
        """Handle intro screen events.

        Args:
            event: Pygame event

        Returns:
            str or tuple: Action to take ('new_game', 'load_game', 'start_game', 'exit', etc.)
        """
        # Handle exit confirmation dialog first (highest priority)
        if self.show_exit_confirm:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.exit_confirm_ok_rect and self.exit_confirm_ok_rect.collidepoint(event.pos):
                    # Exit confirmed
                    return 'exit'
                elif self.exit_confirm_cancel_rect and self.exit_confirm_cancel_rect.collidepoint(event.pos):
                    # Cancel exit
                    self.show_exit_confirm = False
                    return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Close dialog
                    self.show_exit_confirm = False
                    return None
                elif event.key == pygame.K_RETURN:
                    # Enter = OK
                    return 'exit'
            return None  # Consume all events when dialog is showing

        # Check for Escape key to show exit confirmation
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_exit_confirm = True
            return None

        # Normal event handling
        if self.mode == 'intro':
            return self._handle_intro_event(event)
        elif self.mode == 'map_select':
            return self._handle_map_select_event(event)
        elif self.mode == 'map_size':
            return self._handle_map_size_event(event)
        elif self.mode == 'land_composition':
            return self._handle_land_composition_event(event)
        elif self.mode == 'erosive_forces':
            return self._handle_erosive_forces_event(event)
        elif self.mode == 'alien_life':
            return self._handle_alien_life_event(event)
        elif self.mode == 'skill_level':
            return self._handle_skill_level_event(event)
        elif self.mode == 'faction_select':
            return self._handle_faction_select_event(event)
        elif self.mode == 'name_input':
            return self._handle_name_input_event(event)

        return None

    def _handle_intro_event(self, event):
        """Handle intro screen events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.new_game_button_rect and self.new_game_button_rect.collidepoint(event.pos):
                # Start map selection
                self.mode = 'map_select'
                return None
            elif self.load_game_button_rect and self.load_game_button_rect.collidepoint(event.pos):
                return 'load_game'
            elif self.exit_game_button_rect and self.exit_game_button_rect.collidepoint(event.pos):
                return 'exit'

        return None

    def _handle_map_select_event(self, event):
        """Handle map selection events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.random_map_button_rect and self.random_map_button_rect.collidepoint(event.pos):
                # Proceed to faction selection with random/default map settings
                self.mode = 'faction_select'
                self.selected_faction_id = None
                self.selected_ocean_percentage = None  # Use default (70%)
                return None
            elif self.custom_map_button_rect and self.custom_map_button_rect.collidepoint(event.pos):
                # Go to map size selection
                self.mode = 'map_size'
                return None

        return None

    def _handle_map_size_event(self, event):
        """Handle map size selection events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button_rect, size_id, enabled in self.map_size_button_rects:
                if enabled and button_rect.collidepoint(event.pos):
                    self.selected_map_size = size_id
                    # Proceed to land composition
                    self.mode = 'land_composition'
                    return None

        return None

    def _handle_land_composition_event(self, event):
        """Handle land composition selection events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button_rect, range_tuple in self.land_comp_button_rects:
                if button_rect.collidepoint(event.pos):
                    # Generate random percentage in the selected range
                    import random
                    min_pct, max_pct = range_tuple
                    self.selected_ocean_percentage = random.randint(min_pct, max_pct)
                    # Proceed to erosive forces
                    self.mode = 'erosive_forces'
                    return None

        return None

    def _handle_erosive_forces_event(self, event):
        """Handle erosive forces selection events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button_rect, erosive_id, enabled in self.erosive_forces_button_rects:
                if enabled and button_rect.collidepoint(event.pos):
                    self.selected_erosive_forces = erosive_id
                    # Proceed to alien life
                    self.mode = 'alien_life'
                    return None

        return None

    def _handle_alien_life_event(self, event):
        """Handle alien life form prominence selection events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button_rect, alien_id, enabled in self.alien_life_button_rects:
                if enabled and button_rect.collidepoint(event.pos):
                    self.selected_alien_life = alien_id
                    # Proceed to skill level
                    self.mode = 'skill_level'
                    return None

        return None

    def _handle_skill_level_event(self, event):
        """Handle skill level selection events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button_rect, level, enabled in self.skill_level_button_rects:
                if enabled and button_rect.collidepoint(event.pos):
                    self.selected_skill_level = level
                    # Proceed to faction selection
                    self.mode = 'faction_select'
                    self.selected_faction_id = None
                    return None

        return None

    def _handle_faction_select_event(self, event):
        """Handle faction selection events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check faction buttons
            for button_rect, faction_id in self.faction_button_rects:
                if button_rect.collidepoint(event.pos):
                    self.selected_faction_id = faction_id
                    return None

            # Check OK button
            if self.ok_button_rect and self.ok_button_rect.collidepoint(event.pos):
                if self.selected_faction_id is not None:
                    # Move to name input
                    self.mode = 'name_input'
                    # Auto-suggest the faction leader's name (selected for easy replacement)
                    self.player_name_input = FACTIONS[self.selected_faction_id]['leader']
                    self.name_input_selected = True  # Text is selected, will be replaced on first keypress
                    return None

        return None

    def _handle_name_input_event(self, event):
        """Handle name input events."""
        if event.type == pygame.KEYDOWN:
            # Arrow keys or Home/End deselect without clearing
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_HOME, pygame.K_END):
                self.name_input_selected = False
                return None

            # If text is selected, clear it on first keypress (except Return)
            if self.name_input_selected and event.key != pygame.K_RETURN:
                self.player_name_input = ""
                self.name_input_selected = False

            if event.key == pygame.K_BACKSPACE:
                self.player_name_input = self.player_name_input[:-1]
            elif event.key == pygame.K_RETURN:
                # Start game
                if self.player_name_input.strip():
                    return 'start_game', self.selected_faction_id, self.player_name_input.strip(), self.selected_ocean_percentage
            elif len(self.player_name_input) < 50:
                # Add character
                char = event.unicode
                if char.isprintable():
                    self.player_name_input += char

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Clicking in the input box deselects text without clearing
            if hasattr(self, 'name_input_rect') and self.name_input_rect and self.name_input_rect.collidepoint(event.pos):
                self.name_input_selected = False
                return None
            elif self.ok_button_rect and self.ok_button_rect.collidepoint(event.pos):
                # Start game
                if self.player_name_input.strip():
                    return ('start_game', self.selected_faction_id, self.player_name_input.strip(), self.selected_ocean_percentage)
            elif self.cancel_button_rect and self.cancel_button_rect.collidepoint(event.pos):
                # Back to faction select
                self.mode = 'faction_select'
                return None

        return None

    def update(self, dt):
        """Update intro screen state (cursor blink).

        Args:
            dt: Delta time in milliseconds
        """
        if self.mode == 'name_input':
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # Blink every 500ms
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
