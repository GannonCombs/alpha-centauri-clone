"""Social Engineering screen for managing faction policies."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)
from game import social_engineering
from game.data.social_engineering_data import SE_DATA
from game.ui.components import draw_overlay


class SocialEngineeringScreen:
    """Manages the Social Engineering screen."""

    def __init__(self, font, small_font):
        """Initialize social engineering screen with fonts.

        Args:
            font: Main pygame font object
            small_font: Small pygame font object
        """
        self.font = font
        self.small_font = small_font

        # State
        self.social_engineering_open = False
        self.se_selections = None  # Temporary UI state, synced from game.se_selections

        # UI elements
        self.se_choice_rects = {}
        self.se_ok_rect = None
        self.se_cancel_rect = None

        # Energy allocation UI elements
        self.energy_left_arrows = {}  # {'economy': rect, 'psych': rect, 'labs': rect}
        self.energy_right_arrows = {}

        # Confirmation dialog
        self.se_confirm_dialog_open = False
        self.se_confirm_ok_rect = None
        self.se_confirm_cancel_rect = None

    def _calculate_se_cost(self, game):
        """Calculate the cost of social engineering changes.

        Cost values (from SMAC):
        - 1 change: 40
        - 2 changes: 135
        - 3 changes: 320
        - 4 changes: 625

        Args:
            game: Game instance for comparing current vs selected SE

        Returns:
            int: Total cost in energy credits
        """
        if self.se_selections is None:
            return 0

        # Count number of changes
        num_changes = 0
        for category in ['Politics', 'Economics', 'Values', 'Future Society']:
            if self.se_selections[category] != game.se_selections[category]:
                num_changes += 1

        # Use actual SMAC cost table
        cost_table = {0: 0, 1: 40, 2: 135, 3: 320, 4: 625}
        return cost_table.get(num_changes, 0)

    def draw_social_engineering(self, screen, game):
        """Draw the Social Engineering screen.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing tech tree and SE selections
        """
        # Sync selections from game (copy so we can cancel)
        if self.se_selections is None:
            self.se_selections = game.se_selections.copy()

        # Fill background
        screen.fill((20, 25, 30))

        screen_w = display.SCREEN_WIDTH
        screen_h = display.SCREEN_HEIGHT

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

        # Calculate cumulative effects from current selections + faction bonuses
        from game.data.faction_data import FACTION_DATA
        cumulative_effects = {}
        faction_bonuses = {}

        # Get faction bonuses
        faction = FACTION_DATA[game.player_faction_id]
        if 'bonuses' in faction:
            for stat_key, value in faction['bonuses'].items():
                # Map faction bonus keys to display names
                stat_map_keys = {
                    "ECONOMY": "Economy", "EFFIC": "Efficiency", "SUPPORT": "Support",
                    "MORALE": "Morale", "POLICE": "Police", "GROWTH": "Growth",
                    "PLANET": "Planet", "PROBE": "Probe", "INDUSTRY": "Industry",
                    "RESEARCH": "Research"
                }
                if stat_key in stat_map_keys and isinstance(value, int):
                    display_name = stat_map_keys[stat_key]
                    faction_bonuses[display_name] = value
                    cumulative_effects[display_name] = cumulative_effects.get(display_name, 0) + value

        choice_categories = [
            ("Politics", ["Frontier", "Police State", "Democratic", "Fundamentalist"]),
            ("Economics", ["Simple", "Free Market", "Planned", "Green"]),
            ("Values", ["Survival", "Power", "Knowledge", "Wealth"]),
            ("Future Society", ["None", "Cybernetic", "Eudaimonic", "Thought Control"])
        ]

        for category, choices in choice_categories:
            selected_idx = self.se_selections.get(category, 0)
            choice_name = choices[selected_idx]
            choice_data = next((c for c in SE_DATA.get(category, []) if c['name'] == choice_name), {})
            effects_list = list(choice_data.get('effects', {}).items())

            for stat_name, value in effects_list:
                # Normalize stat names to match display (e.g., "EFFIC" -> "Efficiency")
                stat_map = {
                    "ECONOMY": "Economy", "EFFIC": "Efficiency", "SUPPORT": "Support",
                    "MORALE": "Morale", "POLICE": "Police", "GROWTH": "Growth",
                    "PLANET": "Planet", "PROBE": "Probe", "INDUSTRY": "Industry",
                    "RESEARCH": "Research"
                }
                display_name = stat_map.get(stat_name, stat_name)
                cumulative_effects[display_name] = cumulative_effects.get(display_name, 0) + value

        # List of social effects
        effects = ["Economy", "Efficiency", "Support", "Morale", "Police",
                   "Growth", "Planet", "Probe", "Industry", "Research"]

        for i, effect in enumerate(effects):
            y_pos = effects_y + 50 + i * 30
            # Effect name
            effect_text = self.small_font.render(effect, True, COLOR_TEXT)
            screen.blit(effect_text, (effects_x + 15, y_pos))

            # Value from cumulative effects
            value = cumulative_effects.get(effect, 0)
            if value > 0:
                value_str = f"+{value}"
                value_color = (100, 200, 100)  # Green for positive
            elif value < 0:
                value_str = str(value)
                value_color = (200, 100, 100)  # Red for negative
            else:
                value_str = "0"
                value_color = (150, 150, 150)  # Gray for zero

            value_text = self.small_font.render(value_str, True, value_color)
            screen.blit(value_text, (effects_x + effects_w - 40, y_pos))

        # Show breakdown of bonuses (faction bonuses in a separate column)
        breakdown_y = effects_y + 50 + len(effects) * 30 + 20
        breakdown_title = self.small_font.render("Faction Bonuses:", True, (150, 170, 190))
        screen.blit(breakdown_title, (effects_x + 15, breakdown_y))

        breakdown_y += 25
        for effect in effects:
            if effect in faction_bonuses and faction_bonuses[effect] != 0:
                value = faction_bonuses[effect]
                if value > 0:
                    bonus_str = f"{effect} +{value}"
                    bonus_color = (100, 200, 100)
                else:
                    bonus_str = f"{effect} {value}"
                    bonus_color = (200, 100, 100)

                bonus_text = self.small_font.render(bonus_str, True, bonus_color)
                screen.blit(bonus_text, (effects_x + 20, breakdown_y))
                breakdown_y += 22

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
                player_tech_tree = game.factions[game.player_faction_id].tech_tree
                available_choices = social_engineering.get_available_choices(category, player_tech_tree)
                is_unlocked = any(c['name'] == choice_name for c in available_choices)

                # Only store unlocked choices for clicking
                if is_unlocked:
                    self.se_choice_rects[(category, col_idx)] = choice_rect

                is_selected = self.se_selections[category] == col_idx
                is_hover = choice_rect.collidepoint(pygame.mouse.get_pos()) and is_unlocked

                # Draw choice box
                if not is_unlocked:
                    # Locked - completely empty (no background, no text, no icon)
                    bg_color = (20, 25, 30)  # Match screen background
                    border_color = (40, 45, 50)  # Very subtle border
                    text_color = None  # Don't draw text
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

                # Only draw content if unlocked
                if is_unlocked and text_color:
                    # Choice name
                    name_surf = self.small_font.render(choice_name, True, text_color)
                    screen.blit(name_surf, (choice_rect.centerx - name_surf.get_width() // 2, choice_rect.y + 8))

                    # Show effect icons from real SE data
                    if col_idx > 0:
                        choice_data = next((c for c in SE_DATA.get(category, []) if c['name'] == choice_name), {})
                        effects = list(choice_data.get('effects', {}).items())

                        if effects:
                            icon_y = choice_rect.y + 30
                            # Calculate spacing based on number of effects
                            num_effects = len(effects)
                            icon_spacing = choice_w // max(num_effects, 1)

                            for effect_idx, (stat_name, value) in enumerate(effects):
                                icon_x = choice_rect.x + 5 + effect_idx * min(icon_spacing, 60)
                                icon_size = 10

                                # Determine color based on positive/negative value
                                if value > 0:
                                    icon_color = (100, 200, 100)  # Green for positive
                                else:
                                    icon_color = (200, 100, 100)  # Red for negative

                                # Draw small circle as icon
                                pygame.draw.circle(screen, icon_color,
                                                 (icon_x + icon_size // 2, icon_y + icon_size // 2),
                                                 icon_size // 2)

                                # Display value next to icon (with + or - sign)
                                value_str = f"+{value}" if value > 0 else str(value)
                                value_text = self.small_font.render(value_str, True, COLOR_TEXT)
                                screen.blit(value_text, (icon_x + icon_size + 2, icon_y - 2))

                                # Display abbreviated stat name below
                                stat_abbrev = stat_name[:3].upper()  # First 3 letters
                                stat_text = pygame.font.Font(None, 14).render(stat_abbrev, True, (150, 150, 150))
                                screen.blit(stat_text, (icon_x, icon_y + icon_size + 2))

        # ENERGY ALLOCATION METERS (bottom section, above buttons)
        energy_panel_y = screen_h - 180
        energy_panel_h = 100
        energy_panel_x = 20
        energy_panel_w = screen_w - 40

        # Draw energy allocation panel
        energy_rect = pygame.Rect(energy_panel_x, energy_panel_y, energy_panel_w, energy_panel_h)
        pygame.draw.rect(screen, (30, 35, 40), energy_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), energy_rect, 2, border_radius=8)

        # Title
        energy_title = self.font.render("ENERGY ALLOCATION", True, (180, 220, 240))
        screen.blit(energy_title, (energy_panel_x + energy_panel_w // 2 - energy_title.get_width() // 2, energy_panel_y + 5))

        # Get current allocation from game
        economy_pct = game.global_energy_allocation['economy']
        psych_pct = game.global_energy_allocation['psych']
        labs_pct = game.global_energy_allocation['labs']

        # Draw three meters side by side
        categories = [
            ('economy', 'Economy', economy_pct, (100, 200, 100)),
            ('psych', 'Psych', psych_pct, (200, 150, 200)),
            ('labs', 'Labs', labs_pct, (100, 200, 200))
        ]

        meter_w = 250
        meter_h = 30
        meter_spacing = (energy_panel_w - 60 - (meter_w * 3)) // 2
        meter_y = energy_panel_y + 40

        self.energy_left_arrows = {}
        self.energy_right_arrows = {}

        for i, (cat_id, cat_name, percent, color) in enumerate(categories):
            meter_x = energy_panel_x + 30 + i * (meter_w + meter_spacing)

            # Left arrow
            arrow_size = 20
            left_arrow_x = meter_x - arrow_size - 5
            left_arrow_rect = pygame.Rect(left_arrow_x, meter_y + (meter_h - arrow_size) // 2, arrow_size, arrow_size)
            self.energy_left_arrows[cat_id] = left_arrow_rect

            left_hover = left_arrow_rect.collidepoint(pygame.mouse.get_pos())
            arrow_color = COLOR_BUTTON_HOVER if left_hover else (80, 100, 120)
            pygame.draw.rect(screen, arrow_color, left_arrow_rect, border_radius=4)
            # Draw left arrow symbol
            pygame.draw.polygon(screen, COLOR_TEXT, [
                (left_arrow_rect.right - 5, left_arrow_rect.top + 5),
                (left_arrow_rect.left + 5, left_arrow_rect.centery),
                (left_arrow_rect.right - 5, left_arrow_rect.bottom - 5)
            ])

            # Category label and percentage
            label_text = self.small_font.render(f"{cat_name}: {percent}%", True, COLOR_TEXT)
            screen.blit(label_text, (meter_x, meter_y - 20))

            # Meter bar
            meter_rect = pygame.Rect(meter_x, meter_y, meter_w, meter_h)
            pygame.draw.rect(screen, (20, 25, 30), meter_rect, border_radius=4)

            # Fill based on percentage
            fill_w = int(meter_w * (percent / 100.0))
            if fill_w > 0:
                fill_rect = pygame.Rect(meter_x, meter_y, fill_w, meter_h)
                pygame.draw.rect(screen, color, fill_rect, border_radius=4)

            pygame.draw.rect(screen, (100, 140, 160), meter_rect, 2, border_radius=4)

            # Right arrow
            right_arrow_x = meter_x + meter_w + 5
            right_arrow_rect = pygame.Rect(right_arrow_x, meter_y + (meter_h - arrow_size) // 2, arrow_size, arrow_size)
            self.energy_right_arrows[cat_id] = right_arrow_rect

            right_hover = right_arrow_rect.collidepoint(pygame.mouse.get_pos())
            arrow_color = COLOR_BUTTON_HOVER if right_hover else (80, 100, 120)
            pygame.draw.rect(screen, arrow_color, right_arrow_rect, border_radius=4)
            # Draw right arrow symbol
            pygame.draw.polygon(screen, COLOR_TEXT, [
                (right_arrow_rect.left + 5, right_arrow_rect.top + 5),
                (right_arrow_rect.right - 5, right_arrow_rect.centery),
                (right_arrow_rect.left + 5, right_arrow_rect.bottom - 5)
            ])

        # INFO PANEL: Credits, Research, and Cost (between grid and buttons)
        info_panel_y = 580
        info_panel_h = 80
        info_panel_w = effects_x - 40
        info_panel_x = 20
        info_panel_rect = pygame.Rect(info_panel_x, info_panel_y, info_panel_w, info_panel_h)

        pygame.draw.rect(screen, (30, 35, 40), info_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), info_panel_rect, 2, border_radius=8)

        # Left side: Credits per turn and Research turns
        left_text_x = info_panel_x + 20
        credits_per_turn = game.credits_per_turn if hasattr(game, 'credits_per_turn') else 0
        research_turns = game.research_turns_remaining if hasattr(game, 'research_turns_remaining') else 0

        credits_text = self.font.render(f"Credits: {credits_per_turn} per turn", True, (180, 220, 240))
        screen.blit(credits_text, (left_text_x, info_panel_y + 15))

        research_text = self.font.render(f"Research: {research_turns} turns", True, (180, 220, 240))
        screen.blit(research_text, (left_text_x, info_panel_y + 45))

        # Right side: Cost (if there are changes)
        cost = self._calculate_se_cost(game)
        if cost > 0:
            cost_text = self.font.render(f"Cost: {cost} credits", True, (255, 100, 100))
            cost_x = info_panel_x + info_panel_w - cost_text.get_width() - 20
            screen.blit(cost_text, (cost_x, info_panel_y + 30))

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

        # Draw confirmation dialog if open
        if self.se_confirm_dialog_open:
            self._draw_confirmation_dialog(screen, game)

    def _draw_confirmation_dialog(self, screen, game):
        """Draw confirmation dialog for SE changes.

        Args:
            screen: Pygame screen surface
            game: Game instance for checking credits
        """
        draw_overlay(screen, alpha=150)

        # Dialog dimensions
        dialog_w, dialog_h = 500, 250
        dialog_x = display.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2

        # Draw dialog background
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Calculate cost
        cost = self._calculate_se_cost(game)
        has_credits = game.energy_credits >= cost

        # Title and message
        if has_credits:
            title_text = "Confirm Changes"
            title_color = (180, 220, 240)
            message = f"Change social engineering for {cost} credits?"
        else:
            title_text = "Insufficient Credits"
            title_color = (255, 150, 150)
            message = f"You need {cost} credits but only have {game.energy_credits}."

        title_surf = self.font.render(title_text, True, title_color)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 30))

        # Message
        msg_surf = self.small_font.render(message, True, COLOR_TEXT)
        screen.blit(msg_surf, (dialog_x + dialog_w // 2 - msg_surf.get_width() // 2, dialog_y + 90))

        # Buttons
        button_y = dialog_y + dialog_h - 70

        if has_credits:
            # OK and Cancel buttons
            ok_rect = pygame.Rect(dialog_x + dialog_w // 2 - 180, button_y, 150, 50)
            cancel_rect = pygame.Rect(dialog_x + dialog_w // 2 + 30, button_y, 150, 50)

            self.se_confirm_ok_rect = ok_rect
            self.se_confirm_cancel_rect = cancel_rect

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
        else:
            # Just OK button (to close dialog)
            ok_rect = pygame.Rect(dialog_x + dialog_w // 2 - 75, button_y, 150, 50)
            self.se_confirm_ok_rect = ok_rect
            self.se_confirm_cancel_rect = None

            ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
            pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
            ok_text = self.font.render("OK", True, COLOR_TEXT)
            screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - 10))

    def handle_social_engineering_click(self, pos, game):
        """Handle clicks in the Social Engineering screen.

        Args:
            pos: Mouse click position tuple (x, y)
            game: Game instance for saving selections and status messages

        Returns:
            'close' if should exit the screen, None otherwise
        """
        # Handle confirmation dialog clicks first
        if self.se_confirm_dialog_open:
            # Check OK button in confirmation dialog
            if hasattr(self, 'se_confirm_ok_rect') and self.se_confirm_ok_rect and self.se_confirm_ok_rect.collidepoint(pos):
                cost = self._calculate_se_cost(game)

                if game.energy_credits >= cost:
                    # Apply changes
                    game.se_selections = self.se_selections.copy()
                    game.energy_credits -= cost
                    game.set_status_message(f"Social Engineering updated (-{cost} credits)")

                    # Close everything
                    self.se_selections = None
                    self.se_confirm_dialog_open = False
                    self.social_engineering_open = False
                    return 'close'
                else:
                    # Just close the dialog (insufficient credits)
                    self.se_confirm_dialog_open = False
                return None

            # Check Cancel button in confirmation dialog
            if hasattr(self, 'se_confirm_cancel_rect') and self.se_confirm_cancel_rect and self.se_confirm_cancel_rect.collidepoint(pos):
                self.se_confirm_dialog_open = False
                return None

            # Click outside dialog - consume event
            return None

        # Check OK button (show confirmation dialog)
        if hasattr(self, 'se_ok_rect') and self.se_ok_rect.collidepoint(pos):
            cost = self._calculate_se_cost(game)
            if cost > 0:
                # Show confirmation dialog
                self.se_confirm_dialog_open = True
            else:
                # No changes, just close
                self.se_selections = None
                self.social_engineering_open = False
            return None

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

        # Check energy allocation arrows
        categories_order = ['economy', 'psych', 'labs']

        # Left arrows (decrease this category, increase next category)
        for cat_id, rect in self.energy_left_arrows.items():
            if rect.collidepoint(pos):
                current_idx = categories_order.index(cat_id)
                next_idx = (current_idx + 1) % 3
                next_cat = categories_order[next_idx]

                # Transfer 10% from current to next (wrapping)
                # If current is at 0%, pull from the next meter down the cycle instead
                if game.global_energy_allocation[cat_id] >= 10:
                    game.global_energy_allocation[cat_id] -= 10
                    game.global_energy_allocation[next_cat] += 10
                    game.set_status_message(f"Energy allocation: {cat_id.title()} -10%, {next_cat.title()} +10%")
                elif game.global_energy_allocation[cat_id] == 0:
                    # Current is at 0%, try to pull from next in cycle
                    next_next_idx = (next_idx + 1) % 3
                    next_next_cat = categories_order[next_next_idx]
                    if game.global_energy_allocation[next_next_cat] >= 10:
                        game.global_energy_allocation[next_next_cat] -= 10
                        game.global_energy_allocation[next_cat] += 10
                        game.set_status_message(f"Energy allocation: {next_next_cat.title()} -10%, {next_cat.title()} +10%")
                return None

        # Right arrows (increase this category, decrease next category)
        for cat_id, rect in self.energy_right_arrows.items():
            if rect.collidepoint(pos):
                current_idx = categories_order.index(cat_id)
                next_idx = (current_idx + 1) % 3
                next_cat = categories_order[next_idx]

                # Transfer 10% from next to current (wrapping)
                # If next is at 0%, pull from the one after it instead
                if game.global_energy_allocation[next_cat] >= 10:
                    game.global_energy_allocation[cat_id] += 10
                    game.global_energy_allocation[next_cat] -= 10
                    game.set_status_message(f"Energy allocation: {cat_id.title()} +10%, {next_cat.title()} -10%")
                elif game.global_energy_allocation[next_cat] == 0:
                    # Next is at 0%, try to pull from the one after
                    next_next_idx = (next_idx + 1) % 3
                    next_next_cat = categories_order[next_next_idx]
                    if game.global_energy_allocation[next_next_cat] >= 10:
                        game.global_energy_allocation[cat_id] += 10
                        game.global_energy_allocation[next_next_cat] -= 10
                        game.set_status_message(f"Energy allocation: {cat_id.title()} +10%, {next_next_cat.title()} -10%")
                return None

        return None

    def _wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width.

        Args:
            text: String to wrap
            max_width: Maximum width in pixels
            font: Pygame font to use for measuring text

        Returns:
            List of wrapped text lines
        """
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
