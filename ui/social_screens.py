"""Social Engineering, Tech Tree, and Design Workshop screens."""

import pygame
import constants
from constants import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                       COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)
import unit_components
import social_engineering


class SocialScreensManager:
    """Manages Social Engineering, Tech Tree, and Design Workshop screens."""

    def __init__(self, font, small_font):
        """Initialize social screens manager with fonts."""
        self.font = font
        self.small_font = small_font

        # State
        self.social_engineering_open = False
        self.tech_tree_open = False
        self.design_workshop_open = False

        # Tech tree state
        self.tech_tree_scroll_offset = 0
        self.tech_tree_focused_tech = 'Ecology'  # Start focused on Centauri Ecology (Gaian starting tech)

        # Social Engineering selections (temporary UI state, synced from game.se_selections)
        self.se_selections = None

        # Design Workshop state
        self.unit_designs = [
            {"name": "Scout Patrol", "chassis": "Infantry", "weapon": "Hand Weapons", "armor": "No Armor", "reactor": "Fission"},
            {"name": "Gunship Foil", "chassis": "Foil", "weapon": "Missile", "armor": "No Armor", "reactor": "Fission"},
            {"name": "Gunship Needlejet", "chassis": "Needlejet", "weapon": "Missile", "armor": "No Armor", "reactor": "Fission"},
            {"name": "Colony Pod", "chassis": "Infantry", "weapon": "Colony Pod", "armor": "No Armor", "reactor": "Fission"},
            {"name": "Sea Colony Pod", "chassis": "Foil", "weapon": "Colony Pod", "armor": "No Armor", "reactor": "Fission"}
        ]
        self.design_scroll_offset = 0
        self.designs_per_page = 5

        # Current design being edited
        self.dw_selected_chassis = 'infantry'
        self.dw_selected_weapon = 'hand_weapons'
        self.dw_selected_armor = 'no_armor'
        self.dw_selected_reactor = 'fission'
        self.dw_selected_ability1 = 'none'
        self.dw_selected_ability2 = 'none'

        # Which component panel is currently being edited (None, 'chassis', 'weapon', 'armor', 'reactor', 'ability1', 'ability2')
        self.dw_editing_panel = None
        self.dw_ability_scroll_offset = 0

        # UI elements
        self.se_choice_rects = {}
        self.se_ok_rect = None
        self.se_cancel_rect = None
        self.tech_tree_ok_rect = None
        self.dw_left_arrow_rect = None
        self.dw_right_arrow_rect = None
        self.dw_design_rects = []
        self.dw_apply_rect = None
        self.dw_done_rect = None
        self.dw_obsolete_rect = None
        self.dw_disband_rect = None
        self.dw_cancel_rect = None
        self.dw_chassis_rect = None
        self.dw_weapon_rect = None
        self.dw_armor_rect = None
        self.dw_reactor_rect = None
        self.dw_ability1_rect = None
        self.dw_ability2_rect = None
        self.dw_component_selection_rects = []
        self.dw_component_cancel_rect = None
        self.dw_ability_up_arrow = None
        self.dw_ability_down_arrow = None

    def toggle_social_engineering(self):
        """Toggle social engineering screen."""
        self.social_engineering_open = not self.social_engineering_open

    def toggle_tech_tree(self):
        """Toggle tech tree screen."""
        self.tech_tree_open = not self.tech_tree_open

    def toggle_design_workshop(self):
        """Toggle design workshop screen."""
        self.design_workshop_open = not self.design_workshop_open

    def draw_social_engineering(self, screen, game):
        """Draw the Social Engineering screen."""
        # Sync selections from game (copy so we can cancel)
        if self.se_selections is None:
            self.se_selections = game.se_selections.copy()

        # Fill background
        screen.fill((20, 25, 30))

        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("SOCIAL ENGINEERING", True, (180, 220, 240))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 20))

        # RIGHT PANEL: Social Effects (right quartile)
        effects_w = screen_w // 4
        effects_x = screen_w - effects_w - 10
        effects_y = 80
        effects_h = screen_h - 160

        effects_rect = pygame.Rect(effects_x, effects_y, effects_w, effects_h)
        pygame.draw.rect(screen, (30, 35, 40), effects_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), effects_rect, 2, border_radius=8)

        effects_title = self.font.render("SOCIAL EFFECTS", True, (180, 220, 240))
        screen.blit(effects_title, (effects_x + effects_w // 2 - effects_title.get_width() // 2, effects_y + 10))

        # List of social effects
        effects = ["Economy", "Efficiency", "Support", "Morale", "Police",
                   "Growth", "Planet", "Probe", "Industry", "Research"]

        for i, effect in enumerate(effects):
            y_pos = effects_y + 50 + i * 35
            # Effect name
            effect_text = self.small_font.render(effect, True, COLOR_TEXT)
            screen.blit(effect_text, (effects_x + 15, y_pos))
            # Value (0 for now)
            value_text = self.small_font.render("0", True, (150, 200, 150))
            screen.blit(value_text, (effects_x + effects_w - 40, y_pos))

        # MIDDLE: Choice grid (4 rows x 4 columns)
        choice_categories = [
            ("Politics", ["Frontier", "Police State", "Democratic", "Fundamentalist"]),
            ("Economics", ["Simple", "Free Market", "Planned", "Green"]),
            ("Values", ["Survival", "Power", "Knowledge", "Wealth"]),
            ("Future Society", ["None", "Cybernetic", "Eudaimonic", "Thought Control"])
        ]

        grid_w = effects_x - 40
        grid_x = 20
        grid_y = 100

        row_h = 110
        col_w = grid_w // 4

        self.se_choice_rects = {}

        for row_idx, (category, choices) in enumerate(choice_categories):
            y = grid_y + row_idx * row_h

            # Category label
            cat_label = self.font.render(category, True, (200, 220, 240))
            screen.blit(cat_label, (grid_x, y))

            # Draw each choice
            for col_idx, choice_name in enumerate(choices):
                x = grid_x + col_idx * col_w
                choice_y = y + 30
                choice_w = col_w - 10
                choice_h = 70

                choice_rect = pygame.Rect(x, choice_y, choice_w, choice_h)

                # Check if this choice is unlocked
                available_choices = social_engineering.get_available_choices(category, game.tech_tree)
                is_unlocked = any(c['name'] == choice_name for c in available_choices)

                # Only store unlocked choices for clicking
                if is_unlocked:
                    self.se_choice_rects[(category, col_idx)] = choice_rect

                is_selected = self.se_selections[category] == col_idx
                is_hover = choice_rect.collidepoint(pygame.mouse.get_pos()) and is_unlocked

                # Draw choice box
                if not is_unlocked:
                    # Locked - grayed out
                    bg_color = (25, 25, 25)
                    border_color = (50, 50, 50)
                    text_color = (80, 80, 80)
                elif is_selected:
                    bg_color = (60, 80, 100)
                    border_color = (120, 180, 200)
                    text_color = COLOR_TEXT
                elif is_hover:
                    bg_color = (50, 60, 70)
                    border_color = (100, 140, 160)
                    text_color = COLOR_TEXT
                else:
                    bg_color = (40, 45, 50)
                    border_color = (80, 100, 120)
                    text_color = COLOR_TEXT

                pygame.draw.rect(screen, bg_color, choice_rect, border_radius=6)
                pygame.draw.rect(screen, border_color, choice_rect, 2, border_radius=6)

                # Choice name
                name_surf = self.small_font.render(choice_name, True, text_color)
                screen.blit(name_surf, (choice_rect.centerx - name_surf.get_width() // 2, choice_rect.y + 8))

                # Show lock icon if locked
                if not is_unlocked:
                    lock_text = self.small_font.render("🔒", True, (100, 100, 100))
                    screen.blit(lock_text, (choice_rect.centerx - lock_text.get_width() // 2, choice_rect.y + 35))

                # Show effect icons for non-leftmost choices
                if col_idx > 0:
                    # Placeholder: 3 icons with numbers (2 green, 1 red)
                    icon_y = choice_rect.y + 35
                    icon_spacing = choice_w // 3

                    for icon_idx in range(3):
                        icon_x = choice_rect.x + 10 + icon_idx * icon_spacing
                        icon_size = 12

                        # Draw small circle as icon placeholder
                        if icon_idx < 2:
                            icon_color = (100, 200, 100)  # Green
                        else:
                            icon_color = (200, 100, 100)  # Red

                        pygame.draw.circle(screen, icon_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2)

                        # Number next to icon
                        num_text = self.small_font.render("+1" if icon_idx < 2 else "-1", True, COLOR_TEXT)
                        screen.blit(num_text, (icon_x + icon_size + 2, icon_y - 2))

        # OK and Cancel buttons
        button_y = screen_h - 70
        ok_rect = pygame.Rect(screen_w // 2 - 180, button_y, 150, 50)
        cancel_rect = pygame.Rect(screen_w // 2 + 30, button_y, 150, 50)

        self.se_ok_rect = ok_rect
        self.se_cancel_rect = cancel_rect

        # Draw OK button
        ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - 10))

        # Draw Cancel button
        cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if cancel_hover else COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_text, (cancel_rect.centerx - cancel_text.get_width() // 2, cancel_rect.centery - 10))

    def handle_social_engineering_click(self, pos, game):
        """Handle clicks in the Social Engineering screen. Returns 'close' if should exit, None otherwise."""
        # Check OK button
        if hasattr(self, 'se_ok_rect') and self.se_ok_rect.collidepoint(pos):
            # Save selections to game
            game.se_selections = self.se_selections.copy()
            self.se_selections = None  # Clear UI state
            self.social_engineering_open = False
            game.set_status_message("Social Engineering updated")
            return 'close'

        # Check Cancel button
        if hasattr(self, 'se_cancel_rect') and self.se_cancel_rect.collidepoint(pos):
            # Discard changes
            self.se_selections = None  # Clear UI state (will reload from game next time)
            self.social_engineering_open = False
            return 'close'

        # Check choice selections
        if hasattr(self, 'se_choice_rects'):
            for (category, col_idx), rect in self.se_choice_rects.items():
                if rect.collidepoint(pos):
                    self.se_selections[category] = col_idx
                    break

        return None

    def draw_design_workshop(self, screen, game):
        """Draw the Design Workshop screen."""
        # Fill background
        screen.fill((20, 25, 30))

        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("DESIGN WORKSHOP", True, (180, 220, 240))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 20))

        # Layout constants
        panel_x = 60
        panel_y = 100
        panel_w = 300
        panel_h = 120
        panel_spacing = 20

        right_panel_x = screen_w - panel_x - panel_w

        # LEFT COLUMN PANELS
        # Chassis panel
        chassis_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        self.dw_chassis_rect = chassis_rect
        current_chassis = unit_components.get_chassis_by_id(self.dw_selected_chassis)
        self._draw_component_panel(screen, chassis_rect, "CHASSIS", current_chassis['name'])

        # Weapon panel
        weapon_rect = pygame.Rect(panel_x, panel_y + panel_h + panel_spacing, panel_w, panel_h)
        self.dw_weapon_rect = weapon_rect
        current_weapon = unit_components.get_weapon_by_id(self.dw_selected_weapon)
        self._draw_component_panel(screen, weapon_rect, "WEAPON", current_weapon['name'])

        # Armor panel
        armor_rect = pygame.Rect(panel_x, panel_y + 2 * (panel_h + panel_spacing), panel_w, panel_h)
        self.dw_armor_rect = armor_rect
        current_armor = unit_components.get_armor_by_id(self.dw_selected_armor)
        self._draw_component_panel(screen, armor_rect, "ARMOR", current_armor['name'])

        # RIGHT COLUMN PANELS
        # Reactor panel
        reactor_rect = pygame.Rect(right_panel_x, panel_y, panel_w, panel_h)
        self.dw_reactor_rect = reactor_rect
        current_reactor = unit_components.get_reactor_by_id(self.dw_selected_reactor)
        self._draw_component_panel(screen, reactor_rect, "REACTOR", current_reactor['name'])

        # Special Ability 1 panel
        special1_rect = pygame.Rect(right_panel_x, panel_y + panel_h + panel_spacing, panel_w, panel_h)
        self.dw_ability1_rect = special1_rect
        current_ability1 = unit_components.get_ability_by_id(self.dw_selected_ability1)
        self._draw_component_panel(screen, special1_rect, "SPECIAL ABILITY 1", current_ability1['name'])

        # Special Ability 2 panel
        special2_rect = pygame.Rect(right_panel_x, panel_y + 2 * (panel_h + panel_spacing), panel_w, panel_h)
        self.dw_ability2_rect = special2_rect
        current_ability2 = unit_components.get_ability_by_id(self.dw_selected_ability2)
        self._draw_component_panel(screen, special2_rect, "SPECIAL ABILITY 2", current_ability2['name'])

        # DESIGNS ARRAY AT BOTTOM
        designs_y = panel_y + 3 * (panel_h + panel_spacing) + 40
        designs_label = self.font.render("SAVED DESIGNS", True, (180, 220, 240))
        screen.blit(designs_label, (screen_w // 2 - designs_label.get_width() // 2, designs_y))

        # Design squares
        design_size = 80
        design_spacing = 15
        designs_start_y = designs_y + 35

        # Calculate total width needed for visible designs
        total_designs_w = self.designs_per_page * design_size + (self.designs_per_page - 1) * design_spacing
        arrow_w = 40
        arrow_spacing = 20

        # Center the entire designs section
        designs_center_x = screen_w // 2
        designs_start_x = designs_center_x - (total_designs_w + 2 * arrow_w + 2 * arrow_spacing) // 2

        # Left arrow
        left_arrow_rect = pygame.Rect(designs_start_x, designs_start_y + design_size // 2 - 20, arrow_w, 40)
        self.dw_left_arrow_rect = left_arrow_rect
        can_scroll_left = self.design_scroll_offset > 0
        arrow_color = COLOR_BUTTON if can_scroll_left else (60, 60, 60)
        pygame.draw.rect(screen, arrow_color, left_arrow_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, left_arrow_rect, 2, border_radius=6)
        arrow_text = self.font.render("<", True, COLOR_TEXT if can_scroll_left else (100, 100, 100))
        screen.blit(arrow_text, (left_arrow_rect.centerx - arrow_text.get_width() // 2, left_arrow_rect.centery - 10))

        # Design squares
        self.dw_design_rects = []
        designs_x = designs_start_x + arrow_w + arrow_spacing

        for i in range(self.designs_per_page):
            design_idx = self.design_scroll_offset + i
            if design_idx < len(self.unit_designs):
                design = self.unit_designs[design_idx]
                design_rect = pygame.Rect(designs_x + i * (design_size + design_spacing), designs_start_y,
                                         design_size, design_size)
                self.dw_design_rects.append((design_rect, design_idx))

                # Draw design square
                is_hover = design_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (50, 60, 70) if is_hover else (40, 45, 50)
                pygame.draw.rect(screen, bg_color, design_rect, border_radius=6)
                pygame.draw.rect(screen, (100, 140, 160), design_rect, 2, border_radius=6)

                # Design name (wrapped)
                name_lines = self._wrap_text(design["name"], design_size - 10, self.small_font)
                for j, line in enumerate(name_lines[:3]):  # Max 3 lines
                    line_surf = self.small_font.render(line, True, COLOR_TEXT)
                    screen.blit(line_surf, (design_rect.x + 5, design_rect.y + 10 + j * 18))

        # Right arrow
        right_arrow_rect = pygame.Rect(designs_x + self.designs_per_page * (design_size + design_spacing),
                                       designs_start_y + design_size // 2 - 20, arrow_w, 40)
        self.dw_right_arrow_rect = right_arrow_rect
        can_scroll_right = self.design_scroll_offset + self.designs_per_page < len(self.unit_designs)
        arrow_color = COLOR_BUTTON if can_scroll_right else (60, 60, 60)
        pygame.draw.rect(screen, arrow_color, right_arrow_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, right_arrow_rect, 2, border_radius=6)
        arrow_text = self.font.render(">", True, COLOR_TEXT if can_scroll_right else (100, 100, 100))
        screen.blit(arrow_text, (right_arrow_rect.centerx - arrow_text.get_width() // 2, right_arrow_rect.centery - 10))

        # BOTTOM BUTTONS
        button_y = designs_start_y + design_size + 30
        button_w = 120
        button_h = 45
        button_spacing_x = 15

        # Calculate total width for 5 buttons
        total_buttons_w = 5 * button_w + 4 * button_spacing_x
        button_start_x = screen_w // 2 - total_buttons_w // 2

        buttons = ["Apply", "Done", "Obsolete", "Disband", "Cancel"]
        button_rects = []

        for i, label in enumerate(buttons):
            btn_rect = pygame.Rect(button_start_x + i * (button_w + button_spacing_x), button_y, button_w, button_h)
            is_hover = btn_rect.collidepoint(pygame.mouse.get_pos())

            pygame.draw.rect(screen, COLOR_BUTTON_HOVER if is_hover else COLOR_BUTTON, btn_rect, border_radius=6)
            pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if is_hover else COLOR_BUTTON_BORDER, btn_rect, 2, border_radius=6)

            btn_text = self.font.render(label, True, COLOR_TEXT)
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - 10))

            button_rects.append(btn_rect)

        # Store button rects
        self.dw_apply_rect = button_rects[0]
        self.dw_done_rect = button_rects[1]
        self.dw_obsolete_rect = button_rects[2]
        self.dw_disband_rect = button_rects[3]
        self.dw_cancel_rect = button_rects[4]

        # Draw component selection modal if a panel is being edited
        if self.dw_editing_panel:
            self._draw_component_selection(screen, game)

    def _draw_component_panel(self, screen, rect, title, value):
        """Draw a component selection panel."""
        # Highlight if being edited
        is_editing = (
            (title == "CHASSIS" and self.dw_editing_panel == 'chassis') or
            (title == "WEAPON" and self.dw_editing_panel == 'weapon') or
            (title == "ARMOR" and self.dw_editing_panel == 'armor') or
            (title == "REACTOR" and self.dw_editing_panel == 'reactor') or
            (title == "SPECIAL ABILITY 1" and self.dw_editing_panel == 'ability1') or
            (title == "SPECIAL ABILITY 2" and self.dw_editing_panel == 'ability2')
        )

        border_color = (255, 200, 100) if is_editing else (100, 120, 140)
        pygame.draw.rect(screen, (35, 40, 45), rect, border_radius=8)
        pygame.draw.rect(screen, border_color, rect, 3 if is_editing else 2, border_radius=8)

        # Title
        title_surf = self.small_font.render(title, True, (150, 180, 200))
        screen.blit(title_surf, (rect.x + 10, rect.y + 10))

        # Current value
        value_surf = self.font.render(value, True, COLOR_TEXT)
        screen.blit(value_surf, (rect.x + 10, rect.y + 45))

        # Get stats based on panel type
        stats_text = ""
        if title == "CHASSIS":
            chassis = unit_components.get_chassis_by_id(self.dw_selected_chassis)
            stats_text = f"Speed: {chassis['speed']}, Cost: {chassis['cost']}"
        elif title == "WEAPON":
            weapon = unit_components.get_weapon_by_id(self.dw_selected_weapon)
            mode_abbrev = weapon['mode'][0].upper() if weapon['mode'] != 'noncombat' else 'NC'
            stats_text = f"Atk: {weapon['attack']}, Mode: {mode_abbrev}, Cost: {weapon['cost']}"
        elif title == "ARMOR":
            armor = unit_components.get_armor_by_id(self.dw_selected_armor)
            mode_abbrev = armor['mode'][0].upper() if armor['mode'] != 'psi' else 'Psi'
            stats_text = f"Def: {armor['defense']}, Mode: {mode_abbrev}, Cost: {armor['cost']}"
        elif title == "REACTOR":
            reactor = unit_components.get_reactor_by_id(self.dw_selected_reactor)
            stats_text = f"Power: {reactor['power']}"
        elif title == "SPECIAL ABILITY 1":
            ability = unit_components.get_ability_by_id(self.dw_selected_ability1)
            stats_text = f"Cost: {ability['cost']}"
        elif title == "SPECIAL ABILITY 2":
            ability = unit_components.get_ability_by_id(self.dw_selected_ability2)
            stats_text = f"Cost: {ability['cost']}"

        # Stats (wrap to 2 lines if needed for weapons/armor)
        if title in ["WEAPON", "ARMOR"] and len(stats_text) > 30:
            # Split into 2 lines
            parts = stats_text.split(', ')
            line1 = parts[0] + ', ' + parts[1]
            line2 = parts[2] if len(parts) > 2 else ''
            stats_surf1 = self.small_font.render(line1, True, (180, 190, 200))
            screen.blit(stats_surf1, (rect.x + 10, rect.y + 75))
            if line2:
                stats_surf2 = self.small_font.render(line2, True, (180, 190, 200))
                screen.blit(stats_surf2, (rect.x + 10, rect.y + 90))
        else:
            stats_surf = self.small_font.render(stats_text, True, (180, 190, 200))
            screen.blit(stats_surf, (rect.x + 10, rect.y + 80))

    def _draw_component_selection(self, screen, game):
        """Draw component selection modal overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Selection box
        box_w = 700
        box_h = 600
        box_x = (constants.SCREEN_WIDTH - box_w) // 2
        box_y = (constants.SCREEN_HEIGHT - box_h) // 2

        pygame.draw.rect(screen, (30, 35, 40), pygame.Rect(box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(screen, (150, 180, 200), pygame.Rect(box_x, box_y, box_w, box_h), 3, border_radius=10)

        # Title
        title_text = self.font.render(f"SELECT {self.dw_editing_panel.upper()}", True, (180, 220, 240))
        screen.blit(title_text, (box_x + box_w // 2 - title_text.get_width() // 2, box_y + 20))

        # Get components list based on editing panel
        if self.dw_editing_panel == 'chassis':
            all_components = unit_components.CHASSIS
        elif self.dw_editing_panel == 'weapon':
            all_components = unit_components.WEAPONS
        elif self.dw_editing_panel == 'armor':
            all_components = unit_components.ARMOR
        elif self.dw_editing_panel == 'reactor':
            all_components = unit_components.REACTORS
        elif self.dw_editing_panel in ['ability1', 'ability2']:
            all_components = unit_components.SPECIAL_ABILITIES
        else:
            all_components = []

        # Filter components by tech prerequisites
        components = [c for c in all_components if unit_components.is_component_available(c, game.tech_tree)]

        # Draw components
        self.dw_component_selection_rects = []

        # Grid layout for chassis, weapons, armor, reactor
        if self.dw_editing_panel in ['chassis', 'weapon', 'armor', 'reactor']:
            # Reactor uses 4 columns, others use 5
            grid_cols = 4 if self.dw_editing_panel == 'reactor' else 5
            square_size = 105
            square_spacing = 12
            start_x = box_x + 30
            start_y = box_y + 70

            for i, component in enumerate(components):
                row = i // grid_cols
                col = i % grid_cols

                square_x = start_x + col * (square_size + square_spacing)
                square_y = start_y + row * (square_size + square_spacing)

                square_rect = pygame.Rect(square_x, square_y, square_size, square_size)
                self.dw_component_selection_rects.append((square_rect, component))

                # Highlight on hover
                is_hover = square_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (50, 60, 70) if is_hover else (40, 45, 50)
                pygame.draw.rect(screen, bg_color, square_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 120, 140), square_rect, 2, border_radius=5)

                # Component name (wrapped)
                name_lines = self._wrap_text(component['name'], square_size - 10, self.small_font)
                for j, line in enumerate(name_lines[:2]):  # Max 2 lines
                    line_surf = self.small_font.render(line, True, COLOR_TEXT)
                    screen.blit(line_surf, (square_x + 5, square_y + 5 + j * 16))

                # Component key stat
                if self.dw_editing_panel == 'chassis':
                    stat_text = f"Spd: {component['speed']}"
                elif self.dw_editing_panel == 'weapon':
                    stat_text = f"Atk: {component['attack']}"
                    # Show mode
                    mode_abbrev = component['mode'][0].upper() if component['mode'] != 'noncombat' else 'NC'
                    mode_surf = self.small_font.render(f"({mode_abbrev})", True, (180, 200, 200))
                    screen.blit(mode_surf, (square_x + 5, square_y + 68))
                elif self.dw_editing_panel == 'armor':
                    stat_text = f"Def: {component['defense']}"
                    # Show mode
                    mode_abbrev = component['mode'][0].upper() if component['mode'] != 'psi' else 'Psi'
                    mode_surf = self.small_font.render(f"({mode_abbrev})", True, (180, 200, 200))
                    screen.blit(mode_surf, (square_x + 5, square_y + 68))
                elif self.dw_editing_panel == 'reactor':
                    stat_text = f"Pwr: {component['power']}"
                else:
                    stat_text = ""

                stat_surf = self.small_font.render(stat_text, True, (150, 200, 150))
                screen.blit(stat_surf, (square_x + 5, square_y + 50))

        # List layout for special abilities only
        else:
            item_height = 50
            start_y = box_y + 70
            max_visible = 9

            # Apply scroll offset for special abilities
            visible_components = components[self.dw_ability_scroll_offset:self.dw_ability_scroll_offset + max_visible]

            # Draw scroll arrows if needed
            if len(components) > max_visible:
                # Up arrow
                up_arrow_rect = pygame.Rect(box_x + box_w - 50, start_y - 10, 30, 30)
                can_scroll_up = self.dw_ability_scroll_offset > 0
                arrow_color = COLOR_BUTTON if can_scroll_up else (60, 60, 60)
                pygame.draw.rect(screen, arrow_color, up_arrow_rect, border_radius=4)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, up_arrow_rect, 2, border_radius=4)
                arrow_text = self.font.render("^", True, COLOR_TEXT if can_scroll_up else (100, 100, 100))
                screen.blit(arrow_text, (up_arrow_rect.centerx - arrow_text.get_width() // 2, up_arrow_rect.centery - 10))
                self.dw_ability_up_arrow = up_arrow_rect

                # Down arrow
                down_arrow_rect = pygame.Rect(box_x + box_w - 50, start_y + max_visible * item_height, 30, 30)
                can_scroll_down = self.dw_ability_scroll_offset + max_visible < len(components)
                arrow_color = COLOR_BUTTON if can_scroll_down else (60, 60, 60)
                pygame.draw.rect(screen, arrow_color, down_arrow_rect, border_radius=4)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, down_arrow_rect, 2, border_radius=4)
                arrow_text = self.font.render("v", True, COLOR_TEXT if can_scroll_down else (100, 100, 100))
                screen.blit(arrow_text, (down_arrow_rect.centerx - arrow_text.get_width() // 2, down_arrow_rect.centery - 10))
                self.dw_ability_down_arrow = down_arrow_rect

            for i, component in enumerate(visible_components):
                item_rect = pygame.Rect(box_x + 20, start_y + i * item_height, box_w - 80, item_height - 5)
                self.dw_component_selection_rects.append((item_rect, component))

                # Highlight on hover
                is_hover = item_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (50, 60, 70) if is_hover else (40, 45, 50)
                pygame.draw.rect(screen, bg_color, item_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 120, 140), item_rect, 2, border_radius=5)

                # Component name
                name_surf = self.font.render(component['name'], True, COLOR_TEXT)
                screen.blit(name_surf, (item_rect.x + 10, item_rect.y + 5))

                # Component stats - only special abilities use this section now
                stats = f"Cost: {component['cost']} - {component['description']}"
                stats_surf = self.small_font.render(stats, True, (180, 190, 200))
                screen.blit(stats_surf, (item_rect.x + 10, item_rect.y + 25))

        # Cancel button
        cancel_btn_w = 100
        cancel_btn_h = 40
        cancel_btn_x = box_x + box_w // 2 - cancel_btn_w // 2
        cancel_btn_y = box_y + box_h - 60
        cancel_btn_rect = pygame.Rect(cancel_btn_x, cancel_btn_y, cancel_btn_w, cancel_btn_h)

        is_cancel_hover = cancel_btn_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if is_cancel_hover else COLOR_BUTTON, cancel_btn_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, cancel_btn_rect, 2, border_radius=6)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_text, (cancel_btn_rect.centerx - cancel_text.get_width() // 2, cancel_btn_rect.centery - 10))

        self.dw_component_cancel_rect = cancel_btn_rect

    def _wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def draw_tech_tree(self, screen, game):
        """Draw the Technology Tree screen with visualization."""
        # Fill background
        screen.fill((15, 20, 25))

        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # TOP PROGRESS BAR (~80% screen width)
        progress_bar_w = int(screen_w * 0.8)
        progress_bar_h = 50
        progress_bar_x = (screen_w - progress_bar_w) // 2
        progress_bar_y = 10

        # Progress bar background
        prog_bg_rect = pygame.Rect(progress_bar_x, progress_bar_y, progress_bar_w, progress_bar_h)
        pygame.draw.rect(screen, (30, 35, 40), prog_bg_rect, border_radius=8)

        current_tech_name = game.tech_tree.get_current_tech()
        if current_tech_name and game.tech_tree.current_research:
            # Get category color for progress bar
            category = game.tech_tree.get_current_category()
            fill_color = game.tech_tree.get_category_color(category) if category else (80, 150, 200)

            # Fill progress
            progress_pct = game.tech_tree.get_progress_percentage()
            fill_w = int(progress_bar_w * progress_pct)
            fill_rect = pygame.Rect(progress_bar_x, progress_bar_y, fill_w, progress_bar_h)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=8)

            # Progress text (hide tech name - keep it mysterious!)
            turns_left = game.tech_tree.get_turns_remaining()
            total_cost = game.tech_tree.get_research_cost()
            accumulated = game.tech_tree.research_accumulated
            prog_text = self.font.render(f"Research: {accumulated}/{total_cost} ({turns_left} turns)", True, COLOR_TEXT)
            screen.blit(prog_text, (prog_bg_rect.centerx - prog_text.get_width() // 2, prog_bg_rect.centery - 10))
        else:
            # No research active (should not happen with auto-research)
            prog_text = self.font.render("Selecting research...", True, (180, 150, 100))
            screen.blit(prog_text, (prog_bg_rect.centerx - prog_text.get_width() // 2, prog_bg_rect.centery - 10))

        pygame.draw.rect(screen, (100, 140, 180), prog_bg_rect, 3, border_radius=8)

        # LEFT PANEL: Scrollable alphabetized list
        left_panel_x = 20
        left_panel_y = progress_bar_y + progress_bar_h + 20
        left_panel_w = 320
        left_panel_h = screen_h - left_panel_y - 20

        # Panel background
        left_panel_rect = pygame.Rect(left_panel_x, left_panel_y, left_panel_w, left_panel_h)
        pygame.draw.rect(screen, (25, 30, 35), left_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 100, 120), left_panel_rect, 2, border_radius=8)

        # Panel title
        list_title = self.font.render("Technologies", True, (150, 180, 200))
        screen.blit(list_title, (left_panel_x + 10, left_panel_y + 10))

        # Get all techs alphabetically
        all_techs = [(tech_id, tech_data) for tech_id, tech_data in game.tech_tree.technologies.items()]
        all_techs.sort(key=lambda x: x[1]['name'])

        # Scrollable list
        tech_list_y = left_panel_y + 45
        tech_line_h = 22
        visible_lines = (left_panel_h - 60) // tech_line_h
        self.tech_tree_selection_rects = []

        # Draw scroll arrows if needed
        if len(all_techs) > visible_lines:
            # Up arrow
            up_arrow_rect = pygame.Rect(left_panel_x + left_panel_w - 30, left_panel_y + 10, 20, 20)
            pygame.draw.polygon(screen, (150, 180, 200), [
                (up_arrow_rect.centerx, up_arrow_rect.top + 5),
                (up_arrow_rect.left + 3, up_arrow_rect.bottom - 5),
                (up_arrow_rect.right - 3, up_arrow_rect.bottom - 5)
            ])
            self.tech_tree_up_arrow = up_arrow_rect

            # Down arrow
            down_arrow_rect = pygame.Rect(left_panel_x + left_panel_w - 30, left_panel_y + left_panel_h - 30, 20, 20)
            pygame.draw.polygon(screen, (150, 180, 200), [
                (down_arrow_rect.centerx, down_arrow_rect.bottom - 5),
                (down_arrow_rect.left + 3, down_arrow_rect.top + 5),
                (down_arrow_rect.right - 3, down_arrow_rect.top + 5)
            ])
            self.tech_tree_down_arrow = down_arrow_rect
        else:
            self.tech_tree_up_arrow = None
            self.tech_tree_down_arrow = None

        # Display visible techs
        for i in range(self.tech_tree_scroll_offset, min(self.tech_tree_scroll_offset + visible_lines, len(all_techs))):
            tech_id, tech_data = all_techs[i]
            display_index = i - self.tech_tree_scroll_offset
            tech_y = tech_list_y + display_index * tech_line_h

            # Tech status
            status = game.tech_tree.get_tech_status(tech_id)

            # Color based on status
            if status == "Completed":
                tech_color = (100, 220, 100)
                prefix = "✓ "
            elif status == "Researching":
                tech_color = (200, 220, 100)
                prefix = "→ "
            elif status == "Available":
                tech_color = (180, 200, 220)
                prefix = "  "
            else:  # Locked
                tech_color = (100, 110, 120)
                prefix = "  "

            # Clickable rect
            tech_rect = pygame.Rect(left_panel_x + 10, tech_y, left_panel_w - 50, tech_line_h)

            # Highlight if focused or hovered
            is_focused = (tech_id == self.tech_tree_focused_tech)
            is_hovered = tech_rect.collidepoint(pygame.mouse.get_pos())

            if is_focused:
                pygame.draw.rect(screen, (50, 70, 90), tech_rect, border_radius=4)
            elif is_hovered:
                pygame.draw.rect(screen, (40, 50, 60), tech_rect, border_radius=4)

            # Store for click detection
            self.tech_tree_selection_rects.append((tech_rect, tech_id))

            # Tech name
            tech_text = self.small_font.render(f"{prefix}{tech_data['name']}", True, tech_color)
            screen.blit(tech_text, (left_panel_x + 15, tech_y + 3))

        # MAIN VIEW: Tech visualization
        main_panel_x = left_panel_x + left_panel_w + 20
        main_panel_y = left_panel_y
        main_panel_w = screen_w - main_panel_x - 20
        main_panel_h = left_panel_h

        # Main panel background
        main_panel_rect = pygame.Rect(main_panel_x, main_panel_y, main_panel_w, main_panel_h)
        pygame.draw.rect(screen, (20, 25, 30), main_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 100, 120), main_panel_rect, 2, border_radius=8)

        # Draw focused tech
        if self.tech_tree_focused_tech and self.tech_tree_focused_tech in game.tech_tree.technologies:
            self._draw_tech_visualization(screen, game, main_panel_rect)

        # OK button
        ok_button_w = 150
        ok_button_h = 50
        ok_button_x = (screen_w - ok_button_w) // 2
        ok_button_y = screen_h - ok_button_h - 20
        self.tech_tree_ok_rect = pygame.Rect(ok_button_x, ok_button_y, ok_button_w, ok_button_h)

        ok_hover = self.tech_tree_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, self.tech_tree_ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, self.tech_tree_ok_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.tech_tree_ok_rect.centerx - ok_text.get_width() // 2, self.tech_tree_ok_rect.centery - 10))

    def _draw_tech_visualization(self, screen, game, main_rect):
        """Draw the main tech visualization showing focused tech and connections."""
        focused_id = self.tech_tree_focused_tech
        focused_data = game.tech_tree.technologies[focused_id]

        # Storage for clickable prerequisite/unlock rectangles
        self.tech_tree_prereq_rects = []  # List of (rect, tech_id) tuples
        self.tech_tree_unlock_rects = []  # List of (rect, tech_id) tuples

        # Center tech box
        center_x = main_rect.centerx
        center_y = main_rect.centery
        tech_box_w = 240
        tech_box_h = 180

        # Draw center tech (focused)
        center_rect = pygame.Rect(center_x - tech_box_w // 2, center_y - tech_box_h // 2, tech_box_w, tech_box_h)

        # Color based on status
        status = game.tech_tree.get_tech_status(focused_id)
        if status == "Completed":
            bg_color = (40, 60, 40)
            border_color = (100, 220, 100)
            text_color = (255, 255, 255)
        elif status == "Researching":
            bg_color = (60, 60, 40)
            border_color = (200, 220, 100)
            text_color = (255, 255, 255)
        elif status == "Available":
            bg_color = (40, 50, 60)
            border_color = (120, 180, 220)
            text_color = (255, 255, 255)
        else:  # Locked
            bg_color = (30, 30, 30)
            border_color = (80, 80, 80)
            text_color = (120, 120, 120)

        pygame.draw.rect(screen, bg_color, center_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, center_rect, 3, border_radius=10)

        # Tech icon (simple placeholder)
        icon_size = 80
        icon_rect = pygame.Rect(center_rect.centerx - icon_size // 2, center_rect.top + 20, icon_size, icon_size)
        pygame.draw.circle(screen, border_color, icon_rect.center, icon_size // 2)
        pygame.draw.circle(screen, bg_color, icon_rect.center, icon_size // 2 - 3)

        # Tech ID abbreviation in icon
        abbrev_font = pygame.font.Font(None, 32)
        abbrev_text = abbrev_font.render(focused_id[:4], True, text_color)
        screen.blit(abbrev_text, (icon_rect.centerx - abbrev_text.get_width() // 2, icon_rect.centery - 12))

        # Tech name (wrapped)
        name_y = center_rect.top + 110
        name_lines = self._wrap_text(focused_data['name'], tech_box_w - 20, self.font)
        for i, line in enumerate(name_lines[:2]):
            line_surf = self.font.render(line, True, text_color)
            screen.blit(line_surf, (center_rect.centerx - line_surf.get_width() // 2, name_y + i * 24))

        # Cost and category info
        cost = focused_data['cost']
        category = focused_data.get('category', 'unknown')
        category_color = game.tech_tree.get_category_color(category)

        # Category badge
        category_names = {'explore': 'EXPLORE', 'discover': 'DISCOVER', 'build': 'BUILD', 'conquer': 'CONQUER'}
        category_name = category_names.get(category, 'UNKNOWN')
        category_text = self.small_font.render(category_name, True, category_color)
        category_badge_rect = pygame.Rect(center_rect.left + 10, center_rect.bottom - 45, category_text.get_width() + 10, 20)
        pygame.draw.rect(screen, (20, 25, 30), category_badge_rect, border_radius=4)
        pygame.draw.rect(screen, category_color, category_badge_rect, 2, border_radius=4)
        screen.blit(category_text, (category_badge_rect.x + 5, category_badge_rect.y + 2))

        # Cost text
        cost_text = self.small_font.render(f"Cost: {cost}", True, text_color)
        screen.blit(cost_text, (center_rect.centerx - cost_text.get_width() // 2, center_rect.bottom - 25))

        # PREREQUISITES (arrows from left)
        prereq1 = focused_data.get('prereq1')
        prereq2 = focused_data.get('prereq2')
        prereqs = [p for p in [prereq1, prereq2] if p is not None]

        arrow_spacing = 100
        prereq_x = center_x - tech_box_w // 2 - 200
        prereq_start_y = center_y - (len(prereqs) - 1) * arrow_spacing // 2

        for i, prereq_id in enumerate(prereqs):
            if prereq_id in game.tech_tree.technologies:
                prereq_data = game.tech_tree.technologies[prereq_id]
                prereq_y = prereq_start_y + i * arrow_spacing

                # Small prereq box
                prereq_w, prereq_h = 140, 60
                prereq_rect = pygame.Rect(prereq_x - prereq_w // 2, prereq_y - prereq_h // 2, prereq_w, prereq_h)

                # Store for click detection
                self.tech_tree_prereq_rects.append((prereq_rect, prereq_id))

                # Color based on status
                prereq_status = game.tech_tree.get_tech_status(prereq_id)
                if prereq_status == "Completed":
                    prereq_bg = (30, 50, 30)
                    prereq_border = (80, 180, 80)
                    prereq_text_color = (200, 220, 200)
                else:
                    prereq_bg = (25, 25, 25)
                    prereq_border = (60, 60, 60)
                    prereq_text_color = (100, 100, 100)

                # Highlight on hover
                is_hovered = prereq_rect.collidepoint(pygame.mouse.get_pos())
                if is_hovered:
                    prereq_border = tuple(min(255, c + 50) for c in prereq_border)

                pygame.draw.rect(screen, prereq_bg, prereq_rect, border_radius=6)
                pygame.draw.rect(screen, prereq_border, prereq_rect, 2, border_radius=6)

                # Prereq name (wrapped)
                prereq_lines = self._wrap_text(prereq_data['name'], prereq_w - 10, self.small_font)
                for j, line in enumerate(prereq_lines[:2]):
                    line_surf = self.small_font.render(line, True, prereq_text_color)
                    screen.blit(line_surf, (prereq_rect.centerx - line_surf.get_width() // 2, prereq_rect.top + 10 + j * 16))

                # Arrow from prereq to center
                arrow_start = (prereq_rect.right, prereq_y)
                arrow_end = (center_rect.left, center_y)
                pygame.draw.line(screen, prereq_border, arrow_start, arrow_end, 2)
                # Arrowhead
                pygame.draw.polygon(screen, prereq_border, [
                    arrow_end,
                    (arrow_end[0] - 10, arrow_end[1] - 5),
                    (arrow_end[0] - 10, arrow_end[1] + 5)
                ])

        # UNLOCKS (arrows to right - techs that require this one)
        unlocks = []
        for tech_id, tech_data in game.tech_tree.technologies.items():
            if tech_data.get('prereq1') == focused_id or tech_data.get('prereq2') == focused_id:
                unlocks.append((tech_id, tech_data))

        unlock_x = center_x + tech_box_w // 2 + 200
        unlock_start_y = center_y - (len(unlocks) - 1) * arrow_spacing // 2

        for i, (unlock_id, unlock_data) in enumerate(unlocks[:3]):  # Max 3 to avoid clutter
            unlock_y = unlock_start_y + i * arrow_spacing

            # Small unlock box
            unlock_w, unlock_h = 140, 60
            unlock_rect = pygame.Rect(unlock_x - unlock_w // 2, unlock_y - unlock_h // 2, unlock_w, unlock_h)

            # Store for click detection
            self.tech_tree_unlock_rects.append((unlock_rect, unlock_id))

            # Color based on status
            unlock_status = game.tech_tree.get_tech_status(unlock_id)
            if unlock_status == "Completed":
                unlock_bg = (30, 50, 30)
                unlock_border = (80, 180, 80)
                unlock_text_color = (200, 220, 200)
            elif unlock_status == "Available":
                unlock_bg = (30, 40, 50)
                unlock_border = (100, 150, 180)
                unlock_text_color = (180, 200, 220)
            else:
                unlock_bg = (25, 25, 25)
                unlock_border = (60, 60, 60)
                unlock_text_color = (100, 100, 100)

            # Highlight on hover
            is_hovered = unlock_rect.collidepoint(pygame.mouse.get_pos())
            if is_hovered:
                unlock_border = tuple(min(255, c + 50) for c in unlock_border)

            pygame.draw.rect(screen, unlock_bg, unlock_rect, border_radius=6)
            pygame.draw.rect(screen, unlock_border, unlock_rect, 2, border_radius=6)

            # Unlock name (wrapped)
            unlock_lines = self._wrap_text(unlock_data['name'], unlock_w - 10, self.small_font)
            for j, line in enumerate(unlock_lines[:2]):
                line_surf = self.small_font.render(line, True, unlock_text_color)
                screen.blit(line_surf, (unlock_rect.centerx - line_surf.get_width() // 2, unlock_rect.top + 10 + j * 16))

            # Arrow from center to unlock
            arrow_start = (center_rect.right, center_y)
            arrow_end = (unlock_rect.left, unlock_y)
            pygame.draw.line(screen, unlock_border, arrow_start, arrow_end, 2)
            # Arrowhead
            pygame.draw.polygon(screen, unlock_border, [
                arrow_end,
                (arrow_end[0] - 10, arrow_end[1] - 5),
                (arrow_end[0] - 10, arrow_end[1] + 5)
            ])

        # Show count if more unlocks exist
        if len(unlocks) > 3:
            more_text = self.small_font.render(f"+{len(unlocks) - 3} more", True, (150, 150, 150))
            screen.blit(more_text, (unlock_x - more_text.get_width() // 2, unlock_start_y + 3 * arrow_spacing - 20))

    def handle_tech_tree_click(self, pos, game):
        """Handle clicks in the Tech Tree screen. Returns 'close' if should exit, None otherwise."""
        # Check scroll arrows
        if hasattr(self, 'tech_tree_up_arrow') and self.tech_tree_up_arrow and self.tech_tree_up_arrow.collidepoint(pos):
            if self.tech_tree_scroll_offset > 0:
                self.tech_tree_scroll_offset -= 1
            return None

        if hasattr(self, 'tech_tree_down_arrow') and self.tech_tree_down_arrow and self.tech_tree_down_arrow.collidepoint(pos):
            all_techs_count = len(game.tech_tree.technologies)
            visible_lines = 25  # Approximate
            if self.tech_tree_scroll_offset < all_techs_count - visible_lines:
                self.tech_tree_scroll_offset += 1
            return None

        # Check prerequisite boxes (left side of visualization)
        if hasattr(self, 'tech_tree_prereq_rects'):
            for rect, tech_id in self.tech_tree_prereq_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id
                    game.set_status_message(f"Viewing: {game.tech_tree.technologies[tech_id]['name']}")
                    return None

        # Check unlock boxes (right side of visualization)
        if hasattr(self, 'tech_tree_unlock_rects'):
            for rect, tech_id in self.tech_tree_unlock_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id
                    # If it's available, also set it as current research
                    status = game.tech_tree.get_tech_status(tech_id)
                    if status == "Available":
                        game.tech_tree.set_current_research(tech_id)
                        category = game.tech_tree.technologies[tech_id].get('category', 'unknown')
                        category_name = {'explore': 'Explore', 'discover': 'Discover', 'build': 'Build', 'conquer': 'Conquer'}.get(category, 'Unknown')
                        game.set_status_message(f"Now researching a {category_name} technology")
                    else:
                        game.set_status_message(f"Viewing: {game.tech_tree.technologies[tech_id]['name']}")
                    return None

        # Check tech selection (clicking focuses the tech)
        if hasattr(self, 'tech_tree_selection_rects'):
            for rect, tech_id in self.tech_tree_selection_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id

                    # If it's available, also set it as current research
                    status = game.tech_tree.get_tech_status(tech_id)
                    if status == "Available":
                        game.tech_tree.set_current_research(tech_id)
                        category = game.tech_tree.technologies[tech_id].get('category', 'unknown')
                        category_name = {'explore': 'Explore', 'discover': 'Discover', 'build': 'Build', 'conquer': 'Conquer'}.get(category, 'Unknown')
                        game.set_status_message(f"Now researching a {category_name} technology")
                    return None

        # Check OK button
        if hasattr(self, 'tech_tree_ok_rect') and self.tech_tree_ok_rect.collidepoint(pos):
            self.tech_tree_open = False
            return 'close'
        return None

    def handle_design_workshop_click(self, pos):
        """Handle clicks in the Design Workshop screen. Returns 'close' if should exit, None otherwise."""
        # If component selection modal is open, handle those clicks first
        if self.dw_editing_panel:
            # Check scroll arrows for special abilities
            if self.dw_editing_panel in ['ability1', 'ability2']:
                if hasattr(self, 'dw_ability_up_arrow') and self.dw_ability_up_arrow and self.dw_ability_up_arrow.collidepoint(pos):
                    if self.dw_ability_scroll_offset > 0:
                        self.dw_ability_scroll_offset -= 1
                    return None
                if hasattr(self, 'dw_ability_down_arrow') and self.dw_ability_down_arrow and self.dw_ability_down_arrow.collidepoint(pos):
                    max_scroll = len(unit_components.SPECIAL_ABILITIES) - 9
                    if self.dw_ability_scroll_offset < max_scroll:
                        self.dw_ability_scroll_offset += 1
                    return None

            # Check cancel button in modal
            if hasattr(self, 'dw_component_cancel_rect') and self.dw_component_cancel_rect and self.dw_component_cancel_rect.collidepoint(pos):
                self.dw_editing_panel = None
                self.dw_ability_scroll_offset = 0
                return None

            # Check component selection
            if hasattr(self, 'dw_component_selection_rects'):
                for rect, component in self.dw_component_selection_rects:
                    if rect.collidepoint(pos):
                        # Select this component
                        if self.dw_editing_panel == 'chassis':
                            self.dw_selected_chassis = component['id']
                        elif self.dw_editing_panel == 'weapon':
                            self.dw_selected_weapon = component['id']
                        elif self.dw_editing_panel == 'armor':
                            self.dw_selected_armor = component['id']
                        elif self.dw_editing_panel == 'reactor':
                            self.dw_selected_reactor = component['id']
                        elif self.dw_editing_panel == 'ability1':
                            self.dw_selected_ability1 = component['id']
                        elif self.dw_editing_panel == 'ability2':
                            self.dw_selected_ability2 = component['id']
                        self.dw_editing_panel = None
                        self.dw_ability_scroll_offset = 0
                        return None

            # Click outside modal - close it
            return None

        # Check Done button
        if hasattr(self, 'dw_done_rect') and self.dw_done_rect.collidepoint(pos):
            self.design_workshop_open = False
            return 'close'

        # Check Cancel button
        if hasattr(self, 'dw_cancel_rect') and self.dw_cancel_rect.collidepoint(pos):
            self.design_workshop_open = False
            return 'close'

        # Check component panel clicks to open selection modal
        if hasattr(self, 'dw_chassis_rect') and self.dw_chassis_rect and self.dw_chassis_rect.collidepoint(pos):
            self.dw_editing_panel = 'chassis'
            return None

        if hasattr(self, 'dw_weapon_rect') and self.dw_weapon_rect and self.dw_weapon_rect.collidepoint(pos):
            self.dw_editing_panel = 'weapon'
            return None

        if hasattr(self, 'dw_armor_rect') and self.dw_armor_rect and self.dw_armor_rect.collidepoint(pos):
            self.dw_editing_panel = 'armor'
            return None

        if hasattr(self, 'dw_reactor_rect') and self.dw_reactor_rect and self.dw_reactor_rect.collidepoint(pos):
            self.dw_editing_panel = 'reactor'
            return None

        if hasattr(self, 'dw_ability1_rect') and self.dw_ability1_rect and self.dw_ability1_rect.collidepoint(pos):
            self.dw_editing_panel = 'ability1'
            return None

        if hasattr(self, 'dw_ability2_rect') and self.dw_ability2_rect and self.dw_ability2_rect.collidepoint(pos):
            self.dw_editing_panel = 'ability2'
            return None

        # Check Apply button (placeholder - does nothing for now)
        if hasattr(self, 'dw_apply_rect') and self.dw_apply_rect.collidepoint(pos):
            return None

        # Check Obsolete button (placeholder - does nothing for now)
        if hasattr(self, 'dw_obsolete_rect') and self.dw_obsolete_rect.collidepoint(pos):
            return None

        # Check Disband button (placeholder - does nothing for now)
        if hasattr(self, 'dw_disband_rect') and self.dw_disband_rect.collidepoint(pos):
            return None

        # Check left arrow
        if hasattr(self, 'dw_left_arrow_rect') and self.dw_left_arrow_rect.collidepoint(pos):
            if self.design_scroll_offset > 0:
                self.design_scroll_offset -= 1
            return None

        # Check right arrow
        if hasattr(self, 'dw_right_arrow_rect') and self.dw_right_arrow_rect.collidepoint(pos):
            if self.design_scroll_offset + self.designs_per_page < len(self.unit_designs):
                self.design_scroll_offset += 1
            return None

        # Check design squares (placeholder - selection not implemented yet)
        if hasattr(self, 'dw_design_rects'):
            for rect, design_idx in self.dw_design_rects:
                if rect.collidepoint(pos):
                    # TODO: Select this design for editing
                    return None

        return None
