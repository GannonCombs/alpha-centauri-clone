"""Base-related screens (naming and management)."""

import pygame
from data import constants
import facilities
from data.constants import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                            COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT,
                            COLOR_UI_BORDER, COLOR_BLACK)


class BaseScreenManager:
    """Manages base naming and base management screens."""

    def __init__(self, font, small_font):
        """Initialize base screen manager with fonts."""
        self.font = font
        self.small_font = small_font

        # State
        self.base_naming_unit = None
        self.base_name_input = ""
        self.base_name_suggestions = []
        self.viewing_base = None
        self.hurry_production_open = False
        self.hurry_input = ""
        self.production_selection_open = False
        self.selected_production_item = None
        self.production_item_rects = []  # List of (rect, item_name) tuples
        self.production_selection_mode = "change"  # "change" or "queue"
        self.queue_management_open = False
        self.queue_item_rects = []  # List of (rect, item_index) tuples

        # UI elements
        self.base_naming_ok_rect = None
        self.base_naming_cancel_rect = None
        self.base_view_ok_rect = None
        self.base_view_rename_rect = None
        self.prod_change_rect = None
        self.prod_hurry_rect = None
        self.prod_queue_rect = None
        self.hurry_ok_rect = None
        self.hurry_cancel_rect = None
        self.hurry_all_rect = None
        self.prod_select_ok_rect = None
        self.prod_select_cancel_rect = None
        self.queue_add_rect = None
        self.queue_clear_rect = None
        self.queue_close_rect = None

    def show_base_naming(self, unit, game):
        """Show the base naming dialog for a colony pod."""
        self.base_naming_unit = unit
        # Use faction-specific base name from game
        self.base_name_input = game.generate_base_name(unit.owner)

    def show_base_view(self, base):
        """Show the base management screen."""
        self.viewing_base = base
        # Reset all popups when opening base view
        self._reset_base_popups()

    def _reset_base_popups(self):
        """Reset all base view popup states."""
        self.hurry_production_open = False
        self.hurry_input = ""
        self.production_selection_open = False
        self.selected_production_item = None
        self.queue_management_open = False

    def draw_base_naming(self, screen):
        """Draw the base naming dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((10, 15, 20))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 600, 400
        dialog_x = constants.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = constants.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_surf = self.font.render("Found New Base", True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Input field
        input_y = dialog_y + 80
        input_rect = pygame.Rect(dialog_x + 30, input_y, dialog_w - 60, 50)
        pygame.draw.rect(screen, (20, 25, 30), input_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, input_rect, 2, border_radius=6)

        # Draw input text
        input_surf = self.font.render(self.base_name_input, True, COLOR_TEXT)
        screen.blit(input_surf, (input_rect.x + 10, input_rect.y + 13))

        # Draw cursor
        cursor_x = input_rect.x + 10 + input_surf.get_width() + 2
        if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking cursor
            pygame.draw.line(screen, COLOR_TEXT, (cursor_x, input_rect.y + 10),
                           (cursor_x, input_rect.y + input_rect.height - 10), 2)

        # OK and Cancel buttons
        button_y = dialog_y + dialog_h - 70
        ok_rect = pygame.Rect(dialog_x + dialog_w // 2 - 180, button_y, 150, 50)
        cancel_rect = pygame.Rect(dialog_x + dialog_w // 2 + 30, button_y, 150, 50)

        self.base_naming_ok_rect = ok_rect
        self.base_naming_cancel_rect = cancel_rect

        # Draw OK button
        ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2, ok_rect.centery - 10))

        # Draw Cancel button
        cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if cancel_hover else COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_surf = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_surf, (cancel_rect.centerx - cancel_surf.get_width() // 2, cancel_rect.centery - 10))

    def handle_base_naming_event(self, event, game):
        """Handle keyboard and mouse events for base naming. Returns True if event consumed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.base_naming_unit = None
                self.base_name_input = ""
                return 'close'
            elif event.key == pygame.K_RETURN:
                if self.base_name_input.strip():
                    game.found_base(self.base_naming_unit, self.base_name_input.strip())
                    self.base_naming_unit = None
                    self.base_name_input = ""
                return 'close'
            elif event.key == pygame.K_BACKSPACE:
                self.base_name_input = self.base_name_input[:-1]
                return True
            else:
                # Add character to input
                if event.unicode and len(self.base_name_input) < 30:
                    self.base_name_input += event.unicode
                return True
        return False

    def handle_base_naming_click(self, pos, game):
        """Handle clicks in the base naming dialog. Returns 'close' if should exit, None otherwise."""
        # Check OK button
        if hasattr(self, 'base_naming_ok_rect') and self.base_naming_ok_rect.collidepoint(pos):
            if self.base_name_input.strip():
                game.found_base(self.base_naming_unit, self.base_name_input.strip())
                self.base_naming_unit = None
                self.base_name_input = ""
            return 'close'

        # Check Cancel button
        elif hasattr(self, 'base_naming_cancel_rect') and self.base_naming_cancel_rect.collidepoint(pos):
            self.base_naming_unit = None
            self.base_name_input = ""
            return 'close'

        return None

    def handle_base_view_event(self, event, game):
        """Handle keyboard events for base view (mainly popup input). Returns True if event consumed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Close any open popup, return to base view (don't exit base view)
                if self.hurry_production_open:
                    self.hurry_production_open = False
                    self.hurry_input = ""
                    return True
                elif self.production_selection_open:
                    self.production_selection_open = False
                    self.selected_production_item = None
                    return True
                elif self.queue_management_open:
                    self.queue_management_open = False
                    return True
                # If no popups open, let Escape close the base view
                return False

        # Only handle other keyboard input if hurry popup is open
        if not self.hurry_production_open:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Submit the hurry payment (same as OK button)
                base = self.viewing_base
                if base and base.current_production and self.hurry_input:
                    try:
                        credits_to_spend = int(self.hurry_input)
                        if credits_to_spend <= 0:
                            game.set_status_message("Must spend at least 1 credit")
                            return True

                        if credits_to_spend > game.energy_credits:
                            game.set_status_message(f"Not enough credits! You have {game.energy_credits}")
                            return True

                        # Perform the hurry
                        game.energy_credits -= credits_to_spend
                        production_added, completed = base.hurry_production(credits_to_spend)

                        if completed:
                            game.set_status_message(f"Rushed {base.current_production}! Will complete next turn.")
                        else:
                            turns_saved = production_added
                            game.set_status_message(f"Rushed production: {turns_saved} turns saved")

                        self.hurry_production_open = False
                        self.hurry_input = ""
                    except ValueError:
                        game.set_status_message("Invalid amount entered")
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.hurry_input = self.hurry_input[:-1]
                return True
            else:
                # Add character to input (only digits)
                if event.unicode.isdigit() and len(self.hurry_input) < 10:
                    self.hurry_input += event.unicode
                return True
        return False

    def draw_base_view(self, screen, game):
        """Draw the base management screen."""
        base = self.viewing_base
        if not base:
            return

        # Fill background
        screen.fill((15, 20, 25))

        # Calculate layout dimensions
        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # TOP BAR: Automation buttons (full width)
        top_bar_y = 10
        top_bar_h = 50
        button_w = 140
        button_spacing = 10

        automation_buttons = ["Explore", "Discover", "Build", "Conquer"]
        total_auto_w = len(automation_buttons) * button_w + (len(automation_buttons) - 1) * button_spacing
        governor_w = 120
        total_w = total_auto_w + governor_w + button_spacing * 2

        start_x = (screen_w - total_w) // 2

        # Draw automation buttons
        for i, label in enumerate(automation_buttons):
            if i < 2:
                btn_x = start_x + i * (button_w + button_spacing)
            else:
                btn_x = start_x + i * (button_w + button_spacing) + governor_w + button_spacing * 2

            btn_rect = pygame.Rect(btn_x, top_bar_y, button_w, top_bar_h)
            pygame.draw.rect(screen, COLOR_BUTTON, btn_rect, border_radius=6)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, btn_rect, 2, border_radius=6)
            btn_text = self.small_font.render(label, True, COLOR_TEXT)
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - 8))

        # Governor button in middle
        gov_x = start_x + 2 * (button_w + button_spacing)
        gov_rect = pygame.Rect(gov_x, top_bar_y, governor_w, top_bar_h)
        pygame.draw.rect(screen, (60, 80, 60), gov_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 140, 100), gov_rect, 2, border_radius=6)
        gov_text = self.small_font.render("Governor", True, COLOR_TEXT)
        screen.blit(gov_text, (gov_rect.centerx - gov_text.get_width() // 2, gov_rect.centery - 8))

        # TOP CENTER: Zoomed map view (below automation buttons)
        map_view_w = 200
        map_view_h = 200
        map_view_x = (screen_w - map_view_w) // 2
        map_view_y = top_bar_y + top_bar_h + 20
        map_view_rect = pygame.Rect(map_view_x, map_view_y, map_view_w, map_view_h)
        pygame.draw.rect(screen, (25, 35, 40), map_view_rect)
        pygame.draw.rect(screen, COLOR_UI_BORDER, map_view_rect, 2)

        # Show base and surrounding tiles as a grid (actual terrain)
        tile_size = 60
        start_tile_x = map_view_rect.centerx - (tile_size * 3) // 2
        start_tile_y = map_view_rect.centery - (tile_size * 3) // 2
        for dy in range(3):
            for dx in range(3):
                # Calculate actual map coordinates
                map_x = base.x - 1 + dx
                map_y = base.y - 1 + dy

                tile_rect = pygame.Rect(start_tile_x + dx * tile_size, start_tile_y + dy * tile_size, tile_size, tile_size)

                # Check if tile is within map bounds
                if game.game_map.is_valid_position(map_x, map_y):
                    actual_tile = game.game_map.get_tile(map_x, map_y)
                    # Draw actual terrain color
                    if actual_tile.is_land():
                        terrain_color = constants.COLOR_LAND
                    else:
                        terrain_color = constants.COLOR_OCEAN

                    # Center tile is the base
                    if dx == 1 and dy == 1:
                        # Use faction color for base square
                        from ui.data import FACTIONS
                        base_color = (255, 255, 255)  # Default to white
                        if hasattr(game, 'faction_assignments') and base.owner in game.faction_assignments:
                            faction_index = game.faction_assignments[base.owner]
                            base_color = FACTIONS[faction_index]['color']
                        pygame.draw.rect(screen, base_color, tile_rect, border_radius=4)
                    else:
                        pygame.draw.rect(screen, terrain_color, tile_rect)
                else:
                    # Outside map bounds - draw black
                    pygame.draw.rect(screen, COLOR_BLACK, tile_rect)

                pygame.draw.rect(screen, (60, 60, 60), tile_rect, 1)

        # RESOURCE ROWS: Below map inset
        resource_rows_y = map_view_y + map_view_h + 10
        resource_rows_w = map_view_w
        resource_rows_x = map_view_x
        row_h = 22

        # Nutrients row
        nut_row_y = resource_rows_y
        nut_label = self.small_font.render("Nutrients:", True, (150, 220, 150))
        screen.blit(nut_label, (resource_rows_x, nut_row_y))
        nut_values = self.small_font.render("5 - 2 = 3", True, (180, 200, 180))
        screen.blit(nut_values, (resource_rows_x + resource_rows_w - nut_values.get_width(), nut_row_y))

        # Minerals row
        min_row_y = nut_row_y + row_h
        min_label = self.small_font.render("Minerals:", True, (200, 180, 140))
        screen.blit(min_label, (resource_rows_x, min_row_y))
        min_values = self.small_font.render("4 - 1 = 3", True, (180, 180, 160))
        screen.blit(min_values, (resource_rows_x + resource_rows_w - min_values.get_width(), min_row_y))

        # Energy row
        ene_row_y = min_row_y + row_h
        ene_label = self.small_font.render("Energy:", True, (220, 220, 100))
        screen.blit(ene_label, (resource_rows_x, ene_row_y))
        ene_values = self.small_font.render("6 - 3 = 3", True, (200, 200, 120))
        screen.blit(ene_values, (resource_rows_x + resource_rows_w - ene_values.get_width(), ene_row_y))

        # Explainer row
        exp_row_y = ene_row_y + row_h + 5
        exp_text = self.small_font.render("INTAKE - CONSUMPTION = SURPLUS", True, (140, 140, 160))
        screen.blit(exp_text, (resource_rows_x + resource_rows_w // 2 - exp_text.get_width() // 2, exp_row_y))

        # Define content area (full width for layout)
        content_x = 20
        content_w = screen_w - 40

        # TOP LEFT: Nutrients pane
        nutrients_x = content_x
        nutrients_y = top_bar_y + top_bar_h + 20
        nutrients_w = 250
        nutrients_h = 120
        nutrients_rect = pygame.Rect(nutrients_x, nutrients_y, nutrients_w, nutrients_h)
        pygame.draw.rect(screen, (35, 45, 35), nutrients_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 140, 80), nutrients_rect, 2, border_radius=8)

        nut_title = self.small_font.render("NUTRIENTS & GROWTH", True, (150, 220, 150))
        screen.blit(nut_title, (nutrients_x + 10, nutrients_y + 8))

        # Growth progress bar
        progress_rect = pygame.Rect(nutrients_x + 10, nutrients_y + 35, nutrients_w - 20, 25)
        pygame.draw.rect(screen, (20, 25, 20), progress_rect, border_radius=4)

        # Fill progress
        progress_pct = base.nutrients_accumulated / base.nutrients_needed
        fill_w = int((nutrients_w - 20) * progress_pct)
        fill_rect = pygame.Rect(nutrients_x + 10, nutrients_y + 35, fill_w, 25)
        pygame.draw.rect(screen, (100, 200, 100), fill_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 140, 80), progress_rect, 2, border_radius=4)

        progress_text = self.small_font.render(f"{base.nutrients_accumulated}/{base.nutrients_needed}", True, COLOR_TEXT)
        screen.blit(progress_text, (progress_rect.centerx - progress_text.get_width() // 2, progress_rect.centery - 8))

        # Turns until growth
        growth_text = self.small_font.render(f"Growth in {base.growth_turns_remaining} turns", True, (180, 220, 180))
        screen.blit(growth_text, (nutrients_x + 10, nutrients_y + 70))

        pop_display = self.small_font.render(f"Population: {base.population}", True, COLOR_TEXT)
        screen.blit(pop_display, (nutrients_x + 10, nutrients_y + 92))

        # Commerce Panel (below nutrients panel)
        commerce_x = nutrients_x
        commerce_y = nutrients_y + nutrients_h + 10
        commerce_w = nutrients_w
        commerce_h = 80
        commerce_rect = pygame.Rect(commerce_x, commerce_y, commerce_w, commerce_h)
        pygame.draw.rect(screen, (35, 40, 45), commerce_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 120, 140), commerce_rect, 2, border_radius=8)

        commerce_title = self.small_font.render("COMMERCE", True, (180, 200, 220))
        screen.blit(commerce_title, (commerce_x + 10, commerce_y + 8))

        # Errata Panel (below commerce panel)
        errata_x = commerce_x
        errata_y = commerce_y + commerce_h + 10
        errata_w = commerce_w
        errata_h = 100
        errata_rect = pygame.Rect(errata_x, errata_y, errata_w, errata_h)
        pygame.draw.rect(screen, (40, 35, 35), errata_rect, border_radius=8)
        pygame.draw.rect(screen, (140, 120, 100), errata_rect, 2, border_radius=8)

        errata_title = self.small_font.render("INFO", True, (220, 200, 180))
        screen.blit(errata_title, (errata_x + 10, errata_y + 8))

        # Mission Year
        mission_year = 2100 + game.turn
        my_text = self.small_font.render(f"M.Y. {mission_year}", True, COLOR_TEXT)
        screen.blit(my_text, (errata_x + 10, errata_y + 35))

        # Energy credits
        credits_text = self.small_font.render(f"Credits: {game.energy_credits}", True, COLOR_TEXT)
        screen.blit(credits_text, (errata_x + 10, errata_y + 57))

        # Eco-damage (placeholder)
        ecodamage_text = self.small_font.render(f"Eco-damage: 0", True, COLOR_TEXT)
        screen.blit(ecodamage_text, (errata_x + 10, errata_y + 79))

        # TOP RIGHT: Base Facilities
        facilities_x = content_x + content_w - 280
        facilities_y = nutrients_y
        facilities_w = 280
        facilities_h = 300
        facilities_rect = pygame.Rect(facilities_x, facilities_y, facilities_w, facilities_h)
        pygame.draw.rect(screen, (40, 35, 50), facilities_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 100, 140), facilities_rect, 2, border_radius=8)

        fac_title = self.small_font.render("BASE FACILITIES", True, (200, 180, 220))
        screen.blit(fac_title, (facilities_x + 10, facilities_y + 8))

        # Get free facility from faction bonuses
        from ui.data import FACTIONS
        # Use faction_assignments to map player_id to faction_index
        if hasattr(game, 'faction_assignments') and base.owner in game.faction_assignments:
            faction_index = game.faction_assignments[base.owner]
            faction = FACTIONS[faction_index]
        else:
            faction = None
        free_facility = faction.get('bonuses', {}).get('free_facility') if faction else None

        # Combine regular facilities with free facility
        all_facilities = []
        if free_facility:
            all_facilities.append(f"* {free_facility}")  # Asterisk for free
        all_facilities.extend(base.facilities)

        # List facilities
        if all_facilities:
            for i, facility in enumerate(all_facilities):
                fac_text = self.small_font.render(facility, True, COLOR_TEXT)
                screen.blit(fac_text, (facilities_x + 15, facilities_y + 35 + i * 22))
        else:
            no_fac = self.small_font.render("No facilities yet", True, (120, 120, 140))
            screen.blit(no_fac, (facilities_x + 15, facilities_y + 40))

        # ENERGY ALLOCATION PANEL: Above civilians
        energy_alloc_y = screen_h - 380
        energy_alloc_h = 100
        energy_alloc_w = min(500, content_w - 40)
        energy_alloc_x = (screen_w - energy_alloc_w) // 2

        # Draw panel background
        energy_alloc_rect = pygame.Rect(energy_alloc_x, energy_alloc_y, energy_alloc_w, energy_alloc_h)
        pygame.draw.rect(screen, (35, 40, 45), energy_alloc_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 140, 100), energy_alloc_rect, 2, border_radius=8)

        # Title
        energy_title = self.small_font.render("ENERGY ALLOCATION", True, (200, 220, 180))
        screen.blit(energy_title, (energy_alloc_x + energy_alloc_w // 2 - energy_title.get_width() // 2, energy_alloc_y + 8))

        # Get energy allocation percentages from social engineering (default: Economy 50%, Labs 50%, Psych 0%)
        # TODO: Get these from game.social_engineering when implemented
        economy_pct = 50
        psych_pct = 0
        labs_pct = 50

        # Three rows: Economy, Psych, Labs
        row_y_start = energy_alloc_y + 35
        row_spacing = 20

        # Economy row
        econ_label = self.small_font.render(f"Economy: {economy_pct}%", True, (180, 200, 180))
        screen.blit(econ_label, (energy_alloc_x + 15, row_y_start))
        econ_calc = self.small_font.render("10 Energy + 5 Bonus = 15", True, (160, 180, 160))
        screen.blit(econ_calc, (energy_alloc_x + 160, row_y_start))

        # Psych row
        psych_label = self.small_font.render(f"Psych: {psych_pct}%", True, (200, 180, 200))
        screen.blit(psych_label, (energy_alloc_x + 15, row_y_start + row_spacing))
        psych_calc = self.small_font.render("0 Energy + 0 Bonus = 0", True, (180, 160, 180))
        screen.blit(psych_calc, (energy_alloc_x + 160, row_y_start + row_spacing))

        # Labs row
        labs_label = self.small_font.render(f"Labs: {labs_pct}%", True, (180, 200, 220))
        screen.blit(labs_label, (energy_alloc_x + 15, row_y_start + row_spacing * 2))
        labs_calc = self.small_font.render("10 Energy + 3 Bonus = 13", True, (160, 180, 200))
        screen.blit(labs_calc, (energy_alloc_x + 160, row_y_start + row_spacing * 2))

        # CENTER BOTTOM: Civilian icons in horizontal bar (1 per pop)
        civilian_y = screen_h - 250
        civilian_h = 70
        civilian_bar_w = min(600, content_w - 40)
        civilian_bar_x = (screen_w - civilian_bar_w) // 2

        # Draw bar background
        civilian_bar_rect = pygame.Rect(civilian_bar_x, civilian_y, civilian_bar_w, civilian_h)
        pygame.draw.rect(screen, (40, 45, 50), civilian_bar_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 110, 120), civilian_bar_rect, 2, border_radius=8)

        civ_label = self.small_font.render("CITIZENS", True, COLOR_TEXT)
        screen.blit(civ_label, (civilian_bar_x + civilian_bar_w // 2 - civ_label.get_width() // 2, civilian_y - 25))

        # Draw citizen icons inside the bar
        civ_icon_size = 40
        civ_spacing = 10
        total_civ_w = base.population * (civ_icon_size + civ_spacing) - civ_spacing
        civ_start_x = civilian_bar_x + (civilian_bar_w - total_civ_w) // 2

        for i in range(base.population):
            civ_x = civ_start_x + i * (civ_icon_size + civ_spacing)
            civ_y = civilian_y + (civilian_h - civ_icon_size) // 2
            civ_rect = pygame.Rect(civ_x, civ_y, civ_icon_size, civ_icon_size)
            pygame.draw.circle(screen, (200, 180, 140), civ_rect.center, civ_icon_size // 2)
            pygame.draw.circle(screen, (100, 90, 70), civ_rect.center, civ_icon_size // 2, 2)
            # Draw simple face
            eye_y = civ_rect.centery - 5
            pygame.draw.circle(screen, COLOR_BLACK, (civ_rect.centerx - 8, eye_y), 3)
            pygame.draw.circle(screen, COLOR_BLACK, (civ_rect.centerx + 8, eye_y), 3)

        # GARRISON BAR: Units in base (always show bar like citizens panel)
        garrison_y = civilian_y + civilian_h + 30  # Increased spacing to avoid overlap
        garrison_h = 60
        gar_label = self.small_font.render("GARRISON", True, COLOR_TEXT)
        screen.blit(gar_label, (screen_w // 2 - gar_label.get_width() // 2, garrison_y - 25))

        # Garrison bar with same styling as civilians
        garrison_bar_w = min(500, content_w - 200)
        garrison_bar_x = (screen_w - garrison_bar_w) // 2
        garrison_rect = pygame.Rect(garrison_bar_x, garrison_y, garrison_bar_w, garrison_h)

        # Always draw bar background and border (like citizens panel)
        pygame.draw.rect(screen, (40, 45, 50), garrison_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 110, 120), garrison_rect, 2, border_radius=8)

        # Draw garrison units or empty message inside the bar
        if base.garrison:
            for i, unit in enumerate(base.garrison):
                unit_x = garrison_rect.x + 10 + i * 50
                unit_circle = pygame.Rect(unit_x, garrison_rect.y + 10, 40, 40)
                pygame.draw.circle(screen, (255, 255, 255), unit_circle.center, 20)
                pygame.draw.circle(screen, COLOR_BLACK, unit_circle.center, 20, 2)
        else:
            empty_text = self.small_font.render("No units garrisoned", True, (120, 130, 140))
            screen.blit(empty_text, (garrison_rect.centerx - empty_text.get_width() // 2, garrison_rect.centery - 8))

        # BOTTOM LEFT: Current Production (expanded)
        prod_x = content_x
        prod_y = screen_h - 310
        prod_w = 500
        prod_h = 290
        prod_rect = pygame.Rect(prod_x, prod_y, prod_w, prod_h)
        pygame.draw.rect(screen, (45, 40, 35), prod_rect, border_radius=8)
        pygame.draw.rect(screen, (140, 120, 80), prod_rect, 2, border_radius=8)

        prod_title = self.small_font.render("PRODUCTION", True, (220, 200, 160))
        screen.blit(prod_title, (prod_x + 10, prod_y + 8))

        # Production item
        prod_name_text = base.current_production if base.current_production else "Nothing"
        prod_name = self.small_font.render(prod_name_text, True, COLOR_TEXT)
        screen.blit(prod_name, (prod_x + 15, prod_y + 35))

        # Progress bar
        prod_progress_rect = pygame.Rect(prod_x + 10, prod_y + 60, 200, 20)
        pygame.draw.rect(screen, (20, 20, 20), prod_progress_rect, border_radius=4)

        # Calculate actual fill percentage
        if base.current_production and base.production_cost > 0:
            progress_pct = base.production_progress / base.production_cost
            prod_fill = int(200 * progress_pct)
        else:
            prod_fill = 0

        if prod_fill > 0:
            pygame.draw.rect(screen, (140, 180, 100), pygame.Rect(prod_x + 10, prod_y + 60, prod_fill, 20), border_radius=4)
        pygame.draw.rect(screen, (140, 120, 80), prod_progress_rect, 2, border_radius=4)

        # Show turns remaining
        if base.current_production:
            turns_text = self.small_font.render(f"{base.production_turns_remaining} turns", True, (180, 180, 200))
            screen.blit(turns_text, (prod_x + 10, prod_y + 88))
        else:
            turns_text = self.small_font.render("No production", True, (180, 180, 200))
            screen.blit(turns_text, (prod_x + 10, prod_y + 88))

        # Production queue label
        queue_x = prod_x + 230
        queue_label = self.small_font.render("Queue:", True, (200, 180, 140))
        screen.blit(queue_label, (queue_x, prod_y + 35))

        # Queue items
        if base.production_queue:
            # Show first 10 items in queue
            y_offset = 55
            for i, item in enumerate(base.production_queue[:10]):  # Show max 10 items
                item_text = self.small_font.render(f"{i+1}. {item}", True, (180, 180, 180))
                screen.blit(item_text, (queue_x, prod_y + y_offset))
                y_offset += 18
            if len(base.production_queue) > 10:
                more_text = self.small_font.render(f"+{len(base.production_queue) - 10} more", True, (120, 120, 120))
                screen.blit(more_text, (queue_x, prod_y + y_offset))
        else:
            queue_text = self.small_font.render("(empty)", True, (120, 120, 120))
            screen.blit(queue_text, (queue_x, prod_y + 55))

        # Change, Hurry, and Queue buttons
        button_y = prod_y + 250
        change_rect = pygame.Rect(prod_x + 10, button_y, 90, 30)
        hurry_rect = pygame.Rect(prod_x + 110, button_y, 90, 30)
        queue_rect = pygame.Rect(prod_x + 210, button_y, 90, 30)

        self.prod_change_rect = change_rect
        self.prod_hurry_rect = hurry_rect
        self.prod_queue_rect = queue_rect

        # Change button
        change_hover = change_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if change_hover else COLOR_BUTTON, change_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, change_rect, 1, border_radius=4)
        change_text = self.small_font.render("Change", True, COLOR_TEXT)
        screen.blit(change_text, (change_rect.centerx - change_text.get_width() // 2, change_rect.centery - 7))

        # Hurry button
        hurry_hover = hurry_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if hurry_hover else COLOR_BUTTON, hurry_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, hurry_rect, 1, border_radius=4)
        hurry_text = self.small_font.render("Hurry", True, COLOR_TEXT)
        screen.blit(hurry_text, (hurry_rect.centerx - hurry_text.get_width() // 2, hurry_rect.centery - 7))

        # Queue button
        queue_hover = queue_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if queue_hover else COLOR_BUTTON, queue_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, queue_rect, 1, border_radius=4)
        queue_text = self.small_font.render("Queue", True, COLOR_TEXT)
        screen.blit(queue_text, (queue_rect.centerx - queue_text.get_width() // 2, queue_rect.centery - 7))

        # BOTTOM RIGHT: Supported Units
        support_x = content_x + content_w - 250
        support_y = prod_y
        support_w = 240
        support_h = 120
        support_rect = pygame.Rect(support_x, support_y, support_w, support_h)
        pygame.draw.rect(screen, (35, 40, 45), support_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 120, 140), support_rect, 2, border_radius=8)

        support_title = self.small_font.render("UNIT SUPPORT", True, (180, 200, 220))
        screen.blit(support_title, (support_x + 10, support_y + 8))

        # Show tiny unit icons
        if base.supported_units:
            for i, unit in enumerate(base.supported_units):
                u_x = support_x + 15 + (i % 6) * 35
                u_y = support_y + 35 + (i // 6) * 35
                pygame.draw.circle(screen, (255, 255, 255), (u_x + 12, u_y + 12), 12)
                pygame.draw.circle(screen, COLOR_BLACK, (u_x + 12, u_y + 12), 12, 1)
        else:
            support_text = self.small_font.render(f"0 units supported", True, (120, 140, 160))
            screen.blit(support_text, (support_x + 15, support_y + 40))

        # Base name title at top
        base_title = pygame.font.Font(None, 36).render(base.name, True, COLOR_TEXT)
        screen.blit(base_title, (content_x + content_w // 2 - base_title.get_width() // 2, nutrients_y - 50))

        # Rename and OK buttons at bottom center
        button_w = 150
        button_h = 50
        button_spacing = 20
        button_y = screen_h - button_h - 20

        # Calculate center position for both buttons
        total_button_w = button_w * 2 + button_spacing
        buttons_start_x = (screen_w - total_button_w) // 2

        # Rename button (disabled for now)
        rename_button_x = buttons_start_x
        self.base_view_rename_rect = pygame.Rect(rename_button_x, button_y, button_w, button_h)

        # Draw disabled Rename button (grayed out)
        pygame.draw.rect(screen, (50, 50, 50), self.base_view_rename_rect, border_radius=6)
        pygame.draw.rect(screen, (80, 80, 80), self.base_view_rename_rect, 2, border_radius=6)

        rename_text = self.font.render("Rename", True, (100, 100, 100))
        screen.blit(rename_text, (self.base_view_rename_rect.centerx - rename_text.get_width() // 2, self.base_view_rename_rect.centery - 10))

        # OK button
        ok_button_x = buttons_start_x + button_w + button_spacing
        self.base_view_ok_rect = pygame.Rect(ok_button_x, button_y, button_w, button_h)

        ok_hover = self.base_view_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, self.base_view_ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, self.base_view_ok_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.base_view_ok_rect.centerx - ok_text.get_width() // 2, self.base_view_ok_rect.centery - 10))

        # Hurry production popup (draw on top if open)
        if self.hurry_production_open:
            self._draw_hurry_production_popup(screen, base, game)

        # Production selection popup (draw on top if open)
        if self.production_selection_open:
            self._draw_production_selection_popup(screen, base, game)

        # Queue management popup (draw on top if open)
        if self.queue_management_open:
            self._draw_queue_management_popup(screen, base, game)

    def _draw_hurry_production_popup(self, screen, base, game):
        """Draw the hurry production popup dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 450, 280
        dialog_x = constants.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = constants.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_surf = self.font.render("Hurry Production", True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Production info
        info_y = dialog_y + 60
        prod_text = self.small_font.render(f"Current: {base.current_production}", True, COLOR_TEXT)
        screen.blit(prod_text, (dialog_x + 30, info_y))

        # Use the same turns calculation as production panel
        remaining_minerals = base.production_cost - base.production_progress
        credit_cost = remaining_minerals * 2  # 2 credits per mineral in SMAC
        turns_remaining = getattr(base, 'production_turns_remaining', 0) or 0
        cost_text = self.small_font.render(f"Remaining: {turns_remaining} turns ({credit_cost} credits)", True, (200, 220, 100))
        screen.blit(cost_text, (dialog_x + 30, info_y + 25))

        credits_text = self.small_font.render(f"Your credits: {game.energy_credits}", True, (200, 220, 100))
        screen.blit(credits_text, (dialog_x + 30, info_y + 50))

        # Input label
        input_label_y = dialog_y + 140
        label_surf = self.small_font.render("Credits to spend:", True, COLOR_TEXT)
        screen.blit(label_surf, (dialog_x + 30, input_label_y))

        # Input field
        input_y = input_label_y + 25
        input_rect = pygame.Rect(dialog_x + 30, input_y, dialog_w - 60, 40)
        pygame.draw.rect(screen, (20, 25, 30), input_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, input_rect, 2, border_radius=6)

        # Draw input text
        input_surf = self.font.render(self.hurry_input, True, COLOR_TEXT)
        screen.blit(input_surf, (input_rect.x + 10, input_rect.y + 10))

        # Draw cursor
        cursor_x = input_rect.x + 10 + input_surf.get_width() + 2
        if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking cursor
            pygame.draw.line(screen, COLOR_TEXT, (cursor_x, input_rect.y + 8),
                           (cursor_x, input_rect.y + input_rect.height - 8), 2)

        # Buttons
        button_y = dialog_y + dialog_h - 60
        button_w = 100
        button_spacing = 15

        # All button
        all_rect = pygame.Rect(dialog_x + 30, button_y, button_w, 40)
        self.hurry_all_rect = all_rect
        all_hover = all_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if all_hover else COLOR_BUTTON, all_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if all_hover else COLOR_BUTTON_BORDER, all_rect, 2, border_radius=6)
        all_surf = self.small_font.render("Pay All", True, COLOR_TEXT)
        screen.blit(all_surf, (all_rect.centerx - all_surf.get_width() // 2, all_rect.centery - 8))

        # OK button
        ok_rect = pygame.Rect(dialog_x + 30 + button_w + button_spacing, button_y, button_w, 40)
        self.hurry_ok_rect = ok_rect
        ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.small_font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2, ok_rect.centery - 8))

        # Cancel button
        cancel_rect = pygame.Rect(dialog_x + dialog_w - 30 - button_w, button_y, button_w, 40)
        self.hurry_cancel_rect = cancel_rect
        cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if cancel_hover else COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_surf = self.small_font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_surf, (cancel_rect.centerx - cancel_surf.get_width() // 2, cancel_rect.centery - 8))

    def _draw_production_selection_popup(self, screen, base, game):
        """Draw the production selection popup dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Get all production options (units from design workshop + facilities)
        # Calculate turns for each item based on cost and base population
        def get_turns(item_name):
            cost = base._get_production_cost(item_name)
            if cost == 0:
                return 0
            minerals_per_turn = base.population
            if minerals_per_turn == 0:
                return 999
            return (cost + minerals_per_turn - 1) // minerals_per_turn  # Ceiling division

        # Build production items list
        production_items = []

        # Units from design workshop
        if hasattr(game, 'ui_manager') and hasattr(game.ui_manager, 'social_screens'):
            workshop = game.ui_manager.social_screens.design_workshop_screen
            for design in workshop.unit_designs:
                unit_name = design['name']
                turns = get_turns(unit_name)
                # Show basic stats in description
                description = f"{design['chassis']}, {turns} turns"
                production_items.append({
                    "name": unit_name,
                    "type": "unit",
                    "description": description,
                    "design": design  # Store design data for stats display
                })
        else:
            # Fallback to hardcoded units if workshop not available
            production_items.append({"name": "Scout Patrol", "type": "unit", "description": f"Infantry unit, {get_turns('Scout Patrol')} turns"})
            production_items.append({"name": "Colony Pod", "type": "unit", "description": f"Found new base, {get_turns('Colony Pod')} turns"})

        # Facilities (filtered by tech and not already built)
        available_facilities = facilities.get_available_facilities(game.tech_tree)

        # Get free facility for this base's faction
        from ui.data import FACTIONS
        free_facility_name = None
        if hasattr(game, 'faction_assignments') and base.owner in game.faction_assignments:
            faction_index = game.faction_assignments[base.owner]
            faction = FACTIONS[faction_index]
            free_facility_name = faction.get('bonuses', {}).get('free_facility')

        for facility in available_facilities:
            # Skip Headquarters (auto-granted to first base)
            if facility['name'] == 'Headquarters':
                continue
            # Skip if already built in this base
            if facility['name'] in base.facilities:
                continue
            # Skip if this is the faction's free facility (automatically provided)
            if free_facility_name and facility['name'] == free_facility_name:
                continue
            turns = get_turns(facility['name'])
            description = f"{facility['effect']}, {turns} turns, {facility['maint']} energy/turn"
            production_items.append({"name": facility['name'], "type": "facility", "description": description})

        # Secret Projects (filtered by tech and global uniqueness)
        if not hasattr(game, 'built_projects'):
            game.built_projects = set()
        available_projects = facilities.get_available_projects(game.tech_tree, game.built_projects)
        for project in available_projects:
            turns = get_turns(project['name'])
            description = f"{project['effect']}, {turns} turns"
            production_items.append({"name": project['name'], "type": "project", "description": description})

        # Stockpile Energy (always available)
        production_items.append({"name": "Stockpile Energy", "type": "special", "description": f"Earn {1 + base.population} energy per turn"})

        # Calculate grid layout (5 items per row with bigger squares to prevent text overflow)
        items_per_row = 5
        item_size = 140
        item_spacing = 15
        rows = (len(production_items) + items_per_row - 1) // items_per_row

        # Dialog dimensions
        dialog_w = items_per_row * item_size + (items_per_row + 1) * item_spacing
        dialog_h = 100 + rows * item_size + (rows + 1) * item_spacing + 80  # Title + grid + buttons
        dialog_x = constants.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = constants.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_text = "Add to Queue" if self.production_selection_mode == "queue" else "Select Production"
        title_surf = self.font.render(title_text, True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Draw grid of production items
        self.production_item_rects = []
        grid_start_y = dialog_y + 70

        for i, item in enumerate(production_items):
            row = i // items_per_row
            col = i % items_per_row

            item_x = dialog_x + item_spacing + col * (item_size + item_spacing)
            item_y = grid_start_y + row * (item_size + item_spacing)
            item_rect = pygame.Rect(item_x, item_y, item_size, item_size)

            # Store rect for click detection
            self.production_item_rects.append((item_rect, item["name"]))

            # Check if this is the selected item
            is_selected = (self.selected_production_item == item["name"])
            is_hovered = item_rect.collidepoint(pygame.mouse.get_pos())

            # Draw item background
            if is_selected:
                pygame.draw.rect(screen, (60, 80, 60), item_rect, border_radius=6)
                pygame.draw.rect(screen, (100, 200, 100), item_rect, 3, border_radius=6)
            elif is_hovered:
                pygame.draw.rect(screen, (50, 55, 60), item_rect, border_radius=6)
                pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, item_rect, 2, border_radius=6)
            else:
                pygame.draw.rect(screen, (40, 45, 50), item_rect, border_radius=6)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, item_rect, 2, border_radius=6)

            # Draw icon
            icon_y = item_y + 15
            if item["type"] == "unit":
                # Draw simple unit icon (circle)
                pygame.draw.circle(screen, (255, 255, 255), (item_rect.centerx, icon_y + 15), 15)
                pygame.draw.circle(screen, COLOR_BLACK, (item_rect.centerx, icon_y + 15), 15, 2)
            else:  # facility
                # Draw facility icon (for Stockpile Energy: yellow square/diamond)
                icon_rect = pygame.Rect(item_rect.centerx - 12, icon_y + 3, 24, 24)
                pygame.draw.rect(screen, (220, 200, 80), icon_rect, border_radius=4)
                pygame.draw.rect(screen, (255, 220, 100), icon_rect, 2, border_radius=4)

            # Draw item name (wrap if too long)
            name_text = item["name"]
            name_words = name_text.split()
            name_lines = []
            current_line = ""
            for word in name_words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.small_font.render(test_line, True, COLOR_TEXT)
                if test_surf.get_width() <= item_size - 10:
                    current_line = test_line
                else:
                    if current_line:
                        name_lines.append(current_line)
                    current_line = word
            if current_line:
                name_lines.append(current_line)

            # Draw name lines (max 2 lines)
            name_y = icon_y + 35
            for line in name_lines[:2]:
                line_surf = self.small_font.render(line, True, COLOR_TEXT)
                line_rect = line_surf.get_rect(centerx=item_rect.centerx, top=name_y)
                screen.blit(line_surf, line_rect)
                name_y += 16

            # Draw description (word wrap)
            desc_lines = []
            words = item["description"].split()
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.small_font.render(test_line, True, (180, 190, 200))
                if test_surf.get_width() <= item_size - 10:
                    current_line = test_line
                else:
                    if current_line:
                        desc_lines.append(current_line)
                    current_line = word
            if current_line:
                desc_lines.append(current_line)

            # Draw description lines (start after name lines)
            desc_y = name_y + 5
            for line in desc_lines[:2]:  # Max 2 lines
                line_surf = self.small_font.render(line, True, (160, 170, 180))
                line_rect = line_surf.get_rect(centerx=item_rect.centerx, top=desc_y)
                screen.blit(line_surf, line_rect)
                desc_y += 16

            # Draw unit stats (weapon-armor-speed) for units
            if item["type"] == "unit" and "design" in item:
                design = item["design"]
                weapon_power = design.get('weapon_power', 0)
                armor_defense = design.get('armor_defense', 0)
                chassis_speed = design.get('chassis_speed', 1)
                stats_text = f"{weapon_power}-{armor_defense}-{chassis_speed}"
                stats_surf = self.small_font.render(stats_text, True, (200, 220, 100))
                stats_rect = stats_surf.get_rect(centerx=item_rect.centerx, bottom=item_rect.bottom - 5)
                screen.blit(stats_surf, stats_rect)

        # Buttons at bottom
        button_y = dialog_y + dialog_h - 60
        button_w = 120
        button_spacing = 20

        # OK button
        ok_x = dialog_x + dialog_w // 2 - button_w - button_spacing // 2
        ok_rect = pygame.Rect(ok_x, button_y, button_w, 40)
        self.prod_select_ok_rect = ok_rect
        ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2, ok_rect.centery - 10))

        # Cancel button
        cancel_x = dialog_x + dialog_w // 2 + button_spacing // 2
        cancel_rect = pygame.Rect(cancel_x, button_y, button_w, 40)
        self.prod_select_cancel_rect = cancel_rect
        cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if cancel_hover else COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_surf = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_surf, (cancel_rect.centerx - cancel_surf.get_width() // 2, cancel_rect.centery - 10))

    def _draw_queue_management_popup(self, screen, base, game):
        """Draw the production queue management popup dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 500, 450
        dialog_x = constants.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = constants.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_surf = self.font.render("Production Queue", True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Current production label
        current_y = dialog_y + 60
        current_label = self.small_font.render("Current Production:", True, (180, 180, 200))
        screen.blit(current_label, (dialog_x + 30, current_y))
        current_prod = self.small_font.render(base.current_production, True, (100, 200, 100))
        screen.blit(current_prod, (dialog_x + 200, current_y))

        # Queue list
        queue_y = current_y + 40
        queue_label = self.small_font.render("Queued Items:", True, (180, 180, 200))
        screen.blit(queue_label, (dialog_x + 30, queue_y))

        # Draw queue items
        self.queue_item_rects = []
        item_y = queue_y + 30
        max_visible = 8

        if base.production_queue:
            for i, item in enumerate(base.production_queue[:max_visible]):
                item_rect = pygame.Rect(dialog_x + 30, item_y, dialog_w - 60, 30)
                self.queue_item_rects.append((item_rect, i))

                # Highlight on hover
                is_hovered = item_rect.collidepoint(pygame.mouse.get_pos())
                if is_hovered:
                    pygame.draw.rect(screen, (60, 50, 50), item_rect, border_radius=4)
                    pygame.draw.rect(screen, (200, 100, 100), item_rect, 2, border_radius=4)
                else:
                    pygame.draw.rect(screen, (40, 45, 50), item_rect, border_radius=4)
                    pygame.draw.rect(screen, COLOR_BUTTON_BORDER, item_rect, 1, border_radius=4)

                # Draw item number and name
                item_text = self.small_font.render(f"{i+1}. {item}", True, COLOR_TEXT)
                screen.blit(item_text, (item_rect.x + 10, item_rect.y + 7))

                # Draw remove hint
                if is_hovered:
                    remove_hint = self.small_font.render("(click to remove)", True, (200, 150, 150))
                    screen.blit(remove_hint, (item_rect.right - remove_hint.get_width() - 10, item_rect.y + 7))

                item_y += 35

            if len(base.production_queue) > max_visible:
                more_text = self.small_font.render(f"+{len(base.production_queue) - max_visible} more items...", True, (120, 120, 140))
                screen.blit(more_text, (dialog_x + 30, item_y))
        else:
            empty_text = self.small_font.render("(empty - click Add to queue items)", True, (120, 120, 140))
            screen.blit(empty_text, (dialog_x + 30, item_y))

        # Buttons at bottom
        button_y = dialog_y + dialog_h - 60
        button_w = 110
        button_spacing = 15

        # Add button
        add_x = dialog_x + 30
        add_rect = pygame.Rect(add_x, button_y, button_w, 40)
        self.queue_add_rect = add_rect
        add_hover = add_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if add_hover else COLOR_BUTTON, add_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if add_hover else COLOR_BUTTON_BORDER, add_rect, 2, border_radius=6)
        add_surf = self.small_font.render("Add Item", True, COLOR_TEXT)
        screen.blit(add_surf, (add_rect.centerx - add_surf.get_width() // 2, add_rect.centery - 8))

        # Clear button
        clear_x = add_x + button_w + button_spacing
        clear_rect = pygame.Rect(clear_x, button_y, button_w, 40)
        self.queue_clear_rect = clear_rect
        clear_hover = clear_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if clear_hover else COLOR_BUTTON, clear_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if clear_hover else COLOR_BUTTON_BORDER, clear_rect, 2, border_radius=6)
        clear_surf = self.small_font.render("Clear All", True, COLOR_TEXT)
        screen.blit(clear_surf, (clear_rect.centerx - clear_surf.get_width() // 2, clear_rect.centery - 8))

        # Close button
        close_x = dialog_x + dialog_w - 30 - button_w
        close_rect = pygame.Rect(close_x, button_y, button_w, 40)
        self.queue_close_rect = close_rect
        close_hover = close_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if close_hover else COLOR_BUTTON, close_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if close_hover else COLOR_BUTTON_BORDER, close_rect, 2, border_radius=6)
        close_surf = self.small_font.render("Close", True, COLOR_TEXT)
        screen.blit(close_surf, (close_rect.centerx - close_surf.get_width() // 2, close_rect.centery - 8))

    def handle_base_view_click(self, pos, game):
        """Handle clicks in the base view screen. Returns 'close' if should exit, None otherwise."""
        base = self.viewing_base

        # If queue management popup is open, handle its clicks first
        if self.queue_management_open:
            # Check item clicks (remove from queue)
            for item_rect, item_index in self.queue_item_rects:
                if item_rect.collidepoint(pos):
                    removed_item = base.production_queue.pop(item_index)
                    game.set_status_message(f"Removed {removed_item} from queue")
                    return None

            # Check Add button
            if hasattr(self, 'queue_add_rect') and self.queue_add_rect.collidepoint(pos):
                # Open production selection to add to queue
                self.production_selection_mode = "queue"
                self.production_selection_open = True
                self.selected_production_item = None
                self.queue_management_open = False  # Close queue popup while selecting
                return None

            # Check Clear button
            if hasattr(self, 'queue_clear_rect') and self.queue_clear_rect.collidepoint(pos):
                if base.production_queue:
                    base.production_queue.clear()
                    game.set_status_message("Production queue cleared")
                return None

            # Check Close button
            if hasattr(self, 'queue_close_rect') and self.queue_close_rect.collidepoint(pos):
                self.queue_management_open = False
                return None

            # Click outside - consume event
            return None

        # If production selection popup is open, handle its clicks first
        if self.production_selection_open:
            # Check item clicks
            for item_rect, item_name in self.production_item_rects:
                if item_rect.collidepoint(pos):
                    self.selected_production_item = item_name
                    return None

            # Check OK button
            if hasattr(self, 'prod_select_ok_rect') and self.prod_select_ok_rect.collidepoint(pos):
                if self.selected_production_item:
                    if self.production_selection_mode == "queue":
                        # Add to queue
                        base.production_queue.append(self.selected_production_item)
                        game.set_status_message(f"Added {self.selected_production_item} to queue")
                        # Reopen queue management
                        self.production_selection_open = False
                        self.selected_production_item = None
                        self.queue_management_open = True
                    else:
                        # Change production (reset progress)
                        base.current_production = self.selected_production_item
                        base.production_progress = 0
                        base.production_cost = base._get_production_cost(self.selected_production_item)
                        base.production_turns_remaining = base._calculate_production_turns()
                        game.set_status_message(f"Now producing: {self.selected_production_item}")

                        self.production_selection_open = False
                        self.selected_production_item = None
                return None

            # Check Cancel button
            if hasattr(self, 'prod_select_cancel_rect') and self.prod_select_cancel_rect.collidepoint(pos):
                self.production_selection_open = False
                self.selected_production_item = None
                return None

            # Click outside - consume event
            return None

        # If hurry popup is open, handle its clicks first
        if self.hurry_production_open:
            # Check Cancel button
            if hasattr(self, 'hurry_cancel_rect') and self.hurry_cancel_rect.collidepoint(pos):
                self.hurry_production_open = False
                self.hurry_input = ""
                return None

            # Check Pay All button
            if hasattr(self, 'hurry_all_rect') and self.hurry_all_rect.collidepoint(pos):
                if base and base.current_production:
                    remaining_minerals = base.production_cost - base.production_progress
                    credit_cost = remaining_minerals * 2  # 2 credits per mineral (SMAC standard)
                    self.hurry_input = str(credit_cost)
                return None

            # Check OK button
            if hasattr(self, 'hurry_ok_rect') and self.hurry_ok_rect.collidepoint(pos):
                if base and base.current_production and self.hurry_input:
                    try:
                        credits_to_spend = int(self.hurry_input)
                        if credits_to_spend <= 0:
                            game.set_status_message("Must spend at least 1 credit")
                            return None

                        if credits_to_spend > game.energy_credits:
                            game.set_status_message(f"Not enough credits! You have {game.energy_credits}")
                            return None

                        # Perform the hurry
                        game.energy_credits -= credits_to_spend
                        production_added, completed = base.hurry_production(credits_to_spend)

                        if completed:
                            game.set_status_message(f"Rushed {base.current_production}! Will complete next turn.")
                        else:
                            turns_saved = production_added
                            game.set_status_message(f"Rushed production: {turns_saved} turns saved")

                        self.hurry_production_open = False
                        self.hurry_input = ""
                    except ValueError:
                        game.set_status_message("Invalid amount entered")
                return None

            # Click outside popup closes it
            return None

        # Check OK button
        if hasattr(self, 'base_view_ok_rect') and self.base_view_ok_rect.collidepoint(pos):
            self.viewing_base = None
            self._reset_base_popups()  # Reset all popups when closing
            return 'close'

        # Check Change button - open production selection
        if hasattr(self, 'prod_change_rect') and self.prod_change_rect.collidepoint(pos):
            if base:
                self.production_selection_mode = "change"
                self.production_selection_open = True
                self.selected_production_item = base.current_production  # Pre-select current
            return None

        # Check Hurry button - open popup
        if hasattr(self, 'prod_hurry_rect') and self.prod_hurry_rect.collidepoint(pos):
            if base and base.current_production:
                remaining_cost = base.production_cost - base.production_progress
                if remaining_cost <= 0:
                    game.set_status_message("Production already complete!")
                else:
                    self.hurry_production_open = True
                    self.hurry_input = ""
            return None

        # Check Queue button - open queue management
        if hasattr(self, 'prod_queue_rect') and self.prod_queue_rect.collidepoint(pos):
            if base:
                self.queue_management_open = True
            return None

        return None