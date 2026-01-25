"""Main UI coordinator - replaces UIPanel."""

import pygame
import constants
from constants import (COLOR_UI_BACKGROUND, COLOR_UI_BORDER, COLOR_TEXT,
                       COLOR_BLACK, COLOR_BUTTON_BORDER, UNIT_SEA, UNIT_AIR, COLOR_UNIT_FRIENDLY, COLOR_UNIT_ENEMY)
from .components import Button
from .dialogs import DialogManager
from .battle_ui import BattleUIManager
from .diplomacy import DiplomacyManager
from .council import CouncilManager
from .social_screens import SocialScreensManager
from .base_screens import BaseScreenManager
from .data import FACTIONS


class UIManager:
    """Main UI coordinator that manages all screen managers and UI state."""

    def __init__(self):
        """Initialize UI manager with fonts and all screen managers."""
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.mono_font = pygame.font.Font(None, 20)  # Console-like font

        # Active screen state
        self.active_screen = "GAME"
        self.commlink_open = False
        self.main_menu_open = False

        # Initialize all screen managers
        self.dialogs = DialogManager(self.font, self.small_font)
        self.battle_ui = BattleUIManager(self.font, self.small_font)
        self.diplomacy = DiplomacyManager(self.font, self.small_font, self.mono_font)
        self.council = CouncilManager(self.font, self.small_font)
        self.social_screens = SocialScreensManager(self.font, self.small_font)
        self.base_screens = BaseScreenManager(self.font, self.small_font)

        # Layout - will be initialized properly after screen size is known
        self.main_menu_button = None
        self.end_turn_button = None
        self.commlink_button = None
        self.minimap_rect = None
        self.main_menu_rect = None
        self.commlink_menu_rect = None
        self.faction_buttons = []
        self.council_btn = None

        # Game over screen buttons
        self.game_over_new_game_rect = None
        self.game_over_exit_rect = None

        # Unit stack panel
        self.unit_stack_scroll_offset = 0
        self.unit_stack_left_arrow_rect = None
        self.unit_stack_right_arrow_rect = None

    def _init_layout(self):
        """Initialize layout after screen dimensions are known."""
        if self.main_menu_button is not None:
            return  # Already initialized

        button_y = constants.UI_PANEL_Y + 20
        self.main_menu_button = Button(20, button_y, 160, 45, "Main Menu")
        self.end_turn_button = Button(200, button_y, 140, 45, "End Turn")

        # Main menu drop-up
        main_menu_w, main_menu_h = 200, 150
        self.main_menu_rect = pygame.Rect(20, button_y - main_menu_h - 5, main_menu_w, main_menu_h)
        self.main_menu_buttons = [
            Button(self.main_menu_rect.x + 5, self.main_menu_rect.y + 5, main_menu_w - 10, 40, "Game"),
            Button(self.main_menu_rect.x + 5, self.main_menu_rect.y + 50, main_menu_w - 10, 40, "Help"),
            Button(self.main_menu_rect.x + 5, self.main_menu_rect.y + 95, main_menu_w - 10, 40, "Exit")
        ]

        # Minimap & Commlink Positioning - right side of UI panel
        minimap_size = 120
        minimap_x = constants.SCREEN_WIDTH - 320  # Left edge of right area
        minimap_y = constants.UI_PANEL_Y + 10
        self.minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)

        # Commlink button to the RIGHT of the minimap
        self.commlink_button = Button(self.minimap_rect.right + 10, constants.UI_PANEL_Y + 10, 180, 35, "Commlink")

        # Commlink Drop-up dimensions
        menu_w, menu_h = 320, 300
        self.commlink_menu_rect = pygame.Rect(self.commlink_button.rect.x - (menu_w - self.commlink_button.rect.width),
                                              self.commlink_button.rect.top - menu_h - 5, menu_w, menu_h)

        self.faction_buttons = []
        for i, f in enumerate(FACTIONS[1:]):  # Factions 1-6
            btn = Button(self.commlink_menu_rect.x + 5, self.commlink_menu_rect.y + 5 + (i * 38),
                         menu_w - 10, 32, f["name"], f["color"], COLOR_BLACK)
            self.faction_buttons.append(btn)

        self.council_btn = Button(self.commlink_menu_rect.x + 5, self.commlink_menu_rect.bottom - 45, menu_w - 10, 38,
                                  "Planetary Council")

    def handle_event(self, event, game):
        """Process input events for UI interactions and modal dialogs."""
        # Initialize layout if needed
        self._init_layout()

        # 1. Handle Overlays First (Hotkeys)
        if event.type == pygame.KEYDOWN:
            # Handle text input for base naming
            if self.active_screen == "BASE_NAMING":
                result = self.base_screens.handle_base_naming_event(event, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True

            # Handle text input for base view (hurry production popup)
            if self.active_screen == "BASE_VIEW":
                if self.base_screens.handle_base_view_event(event, game):
                    return True

            if event.key == pygame.K_e:
                # Toggle Social Engineering screen
                if self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_screens.social_engineering_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "SOCIAL_ENGINEERING"
                    self.social_screens.social_engineering_open = True
                    return True

            if event.key == pygame.K_u:
                # Toggle Design Workshop screen
                if self.active_screen == "DESIGN_WORKSHOP":
                    self.active_screen = "GAME"
                    self.social_screens.design_workshop_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "DESIGN_WORKSHOP"
                    self.social_screens.design_workshop_open = True
                    return True

            if event.key == pygame.K_F2:
                # Toggle Tech Tree screen
                if self.active_screen == "TECH_TREE":
                    self.active_screen = "GAME"
                    self.social_screens.tech_tree_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "TECH_TREE"
                    self.social_screens.tech_tree_open = True
                    return True

            if event.key == pygame.K_ESCAPE:
                if self.active_screen == "TECH_TREE":
                    self.active_screen = "GAME"
                    self.social_screens.tech_tree_open = False
                    return True
                elif self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_screens.social_engineering_open = False
                    return True
                elif self.active_screen == "DESIGN_WORKSHOP":
                    self.active_screen = "GAME"
                    self.social_screens.design_workshop_open = False
                    return True
                elif self.active_screen == "BASE_VIEW":
                    self.active_screen = "GAME"
                    self.base_screens.viewing_base = None
                    return True
                elif self.active_screen != "GAME" or self.commlink_open or self.main_menu_open:
                    self.active_screen = "GAME"
                    self.commlink_open = False
                    self.main_menu_open = False
                    self.diplomacy.diplo_stage = "greeting"
                    self.council.council_stage = "select_proposal"
                    self.council.selected_proposal = None
                    self.council.player_vote = None
                    return True
                else:
                    return False

            elif event.key == pygame.K_RETURN:
                # Battle prediction takes highest priority
                if game.pending_battle:
                    # Enter key acts as OK button
                    attacker = game.pending_battle['attacker']
                    defender = game.pending_battle['defender']
                    target_x = game.pending_battle['target_x']
                    target_y = game.pending_battle['target_y']

                    # Clear pending battle
                    game.pending_battle = None

                    # Resolve combat
                    game.resolve_combat(attacker, defender, target_x, target_y)
                    return True

                # Supply pod message takes priority
                if game.supply_pod_message:
                    game.supply_pod_message = None
                    return True

                if self.active_screen == "DIPLOMACY":
                    if self.diplomacy.diplo_stage == "exit":
                        self.active_screen = "GAME"
                        self.diplomacy.diplo_stage = "greeting"
                        return True
                elif self.active_screen == "COUNCIL_VOTE":
                    if self.council.council_stage == "too_recent":
                        self.council.council_stage = "select_proposal"
                        self.council.selected_proposal = None
                        return True
                    elif self.council.council_stage == "results":
                        self.active_screen = "GAME"
                        self.council.council_stage = "select_proposal"
                        self.council.selected_proposal = None
                        self.council.player_vote = None
                        return True
                return False

        # 2. Mouse Logic
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Game over screen takes highest priority
            if game.game_over:
                if self.game_over_new_game_rect and self.game_over_new_game_rect.collidepoint(event.pos):
                    # New Game clicked
                    game.new_game()
                    self.active_screen = "GAME"
                    self.commlink_open = False
                    self.main_menu_open = False
                    return True
                elif self.game_over_exit_rect and self.game_over_exit_rect.collidepoint(event.pos):
                    # Exit clicked
                    import sys
                    pygame.quit()
                    sys.exit()
                return True  # Consume all clicks when game over

            # Battle prediction takes highest priority
            if game.pending_battle:
                result = self.battle_ui.handle_battle_prediction_click(event.pos)
                if result == 'ok':
                    # OK clicked - initiate combat
                    attacker = game.pending_battle['attacker']
                    defender = game.pending_battle['defender']
                    target_x = game.pending_battle['target_x']
                    target_y = game.pending_battle['target_y']

                    # Consume attacker's movement
                    if attacker.unit_type in [UNIT_SEA, UNIT_AIR]:
                        # Sea and air units: attack ends turn
                        attacker.moves_remaining = 0
                    else:
                        # Land units: attack costs 1 move
                        attacker.moves_remaining -= 1

                    game.resolve_combat(attacker, defender, target_x, target_y)
                    game.pending_battle = None
                    return True
                elif result == 'cancel':
                    # Cancel clicked - abort attack
                    game.pending_battle = None
                    return True
                # Block all other clicks when prediction is showing
                return True

            # Supply pod message takes priority
            if game.supply_pod_message:
                if self.dialogs.handle_supply_pod_click(event.pos):
                    game.supply_pod_message = None
                    return True
                # Block all other clicks when message is showing
                return True

            if self.active_screen == "TECH_TREE":
                result = self.social_screens.handle_tech_tree_click(event.pos)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "SOCIAL_ENGINEERING":
                result = self.social_screens.handle_social_engineering_click(event.pos)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "DESIGN_WORKSHOP":
                result = self.social_screens.handle_design_workshop_click(event.pos)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "BASE_VIEW":
                result = self.base_screens.handle_base_view_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "BASE_NAMING":
                result = self.base_screens.handle_base_naming_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "DIPLOMACY":
                result = self.diplomacy.handle_click(event.pos)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "COUNCIL_VOTE":
                result = self.council.handle_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True

            if self.active_screen != "GAME":
                return True

            # Toggle Main Menu
            if self.main_menu_button.handle_event(event):
                self.main_menu_open = not self.main_menu_open
                if self.main_menu_open:
                    self.commlink_open = False  # Exclusivity
                return True

            # Toggle Commlink
            if self.commlink_button.handle_event(event):
                self.commlink_open = not self.commlink_open
                if self.commlink_open:
                    self.main_menu_open = False  # Exclusivity
                return True

            # Handle clicks inside Main Menu
            if self.main_menu_open:
                if self.main_menu_rect.collidepoint(event.pos):
                    for btn in self.main_menu_buttons:
                        if btn.handle_event(event):
                            self.main_menu_open = False
                            return True
                    return True  # Consume click inside menu
                else:
                    self.main_menu_open = False  # Clicked outside

            # Handle clicks inside Commlink Menu
            if self.commlink_open:
                if self.commlink_menu_rect.collidepoint(event.pos):
                    for i, btn in enumerate(self.faction_buttons):
                        if btn.handle_event(event):
                            self.diplomacy.open_diplomacy(FACTIONS[i + 1])
                            self.active_screen = "DIPLOMACY"
                            self.commlink_open = False
                            return True
                    if self.council_btn.handle_event(event):
                        self.council.open_council()
                        self.active_screen = "COUNCIL_VOTE"
                        self.commlink_open = False
                        return True
                    return True
                else:
                    self.commlink_open = False  # Clicked outside

            if self.end_turn_button.handle_event(event):
                game.end_turn()
                return True

        # 3. Motion (Hover)
        if event.type == pygame.MOUSEMOTION:
            self.main_menu_button.handle_event(event)
            self.end_turn_button.handle_event(event)
            self.commlink_button.handle_event(event)
            if self.main_menu_open:
                for btn in self.main_menu_buttons:
                    btn.handle_event(event)
            if self.commlink_open:
                for btn in self.faction_buttons:
                    btn.handle_event(event)
                self.council_btn.handle_event(event)

        return False

    def draw(self, screen, game):
        """Render the UI panel with game info, buttons, and active modals."""
        self._init_layout()

        # Layer 1: Background
        pygame.draw.rect(screen, COLOR_UI_BACKGROUND,
                         (0, constants.UI_PANEL_Y, constants.SCREEN_WIDTH, constants.UI_PANEL_HEIGHT))
        pygame.draw.line(screen, COLOR_UI_BORDER, (0, constants.UI_PANEL_Y),
                         (constants.SCREEN_WIDTH, constants.UI_PANEL_Y), 3)

        # Layer 2: Minimap
        pygame.draw.rect(screen, COLOR_BLACK, self.minimap_rect)
        pygame.draw.rect(screen, COLOR_UI_BORDER, self.minimap_rect, 2)
        mm_label = self.small_font.render("Mini-Map", True, COLOR_TEXT)
        screen.blit(mm_label, (self.minimap_rect.x, self.minimap_rect.y - 18))

        # Draw minimap contents
        self._draw_minimap(screen, game)

        # Mission Year and Energy Credits - below minimap
        info_x = self.minimap_rect.x
        info_y = self.minimap_rect.bottom + 8
        year_text = self.small_font.render(f"MY: {game.mission_year}", True, COLOR_TEXT)
        screen.blit(year_text, (info_x, info_y))

        credits_text = self.small_font.render(f"Credits: {game.energy_credits}", True, (200, 220, 100))
        screen.blit(credits_text, (info_x, info_y + 18))

        # Layer 3: Fixed Buttons
        self.main_menu_button.draw(screen, self.font)
        self.end_turn_button.draw(screen, self.font)
        self.commlink_button.draw(screen, self.small_font)

        # Turn counter - below buttons
        turn_text = self.font.render(f"Turn: {game.turn}", True, COLOR_TEXT)
        screen.blit(turn_text, (20, constants.UI_PANEL_Y + 75))

        # Unit info panel - left-center area (always visible if unit selected)
        if game.selected_unit:
            unit = game.selected_unit
            # Position left of battle panel
            info_x = 370
            info_y = constants.UI_PANEL_Y + 20
            info_box = pygame.Rect(info_x - 10, info_y - 5, 280, 135)
            pygame.draw.rect(screen, (35, 40, 45), info_box)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, info_box, 2)
            screen.blit(self.font.render(f"Unit: {unit.name}", True, COLOR_TEXT), (info_x, info_y))

            # Capitalize unit type
            unit_type_display = unit.unit_type.capitalize()
            screen.blit(self.small_font.render(f"Type: {unit_type_display}", True, (200, 210, 220)), (info_x, info_y + 30))

            # Stats: weapon-armor-moves*health
            stats_str = unit.get_stats_string()
            screen.blit(self.small_font.render(f"Stats: {stats_str}", True, (200, 210, 220)), (info_x, info_y + 52))

            # Moves remaining
            if unit.moves_remaining == 0:
                moves_text = self.small_font.render("ALREADY MOVED", True, (255, 100, 100))
            else:
                moves_text = self.small_font.render(f"Moves: {unit.moves_remaining}/{unit.max_moves()}", True, (200, 210, 220))
            screen.blit(moves_text, (info_x, info_y + 74))

            # Health percentage with color coding
            health_pct = unit.get_health_percentage()
            health_percent_display = int(health_pct * 100)

            # Color based on health percentage
            if health_pct >= 0.8:
                health_color = (50, 255, 50)  # Green
            elif health_pct >= 0.5:
                health_color = (255, 255, 50)  # Yellow
            else:
                health_color = (255, 50, 50)  # Red

            health_text = self.small_font.render(f"Health: {health_percent_display}%", True, health_color)
            screen.blit(health_text, (info_x, info_y + 90))

            # Morale level
            morale_name = unit.get_morale_name()
            morale_text = self.small_font.render(f"Morale: {morale_name}", True, (150, 200, 255))
            screen.blit(morale_text, (info_x, info_y + 106))

        # Layer 4a: Main Menu Drop-up
        if self.main_menu_open and self.active_screen == "GAME":
            pygame.draw.rect(screen, (20, 25, 30), self.main_menu_rect)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.main_menu_rect, 3)
            for btn in self.main_menu_buttons:
                btn.draw(screen, self.font)

        # Layer 4b: Commlink Drop-up
        if self.commlink_open and self.active_screen == "GAME":
            pygame.draw.rect(screen, COLOR_BLACK, self.commlink_menu_rect)
            pygame.draw.rect(screen, COLOR_UI_BORDER, self.commlink_menu_rect, 2)
            for btn in self.faction_buttons:
                btn.draw(screen, self.small_font)
            self.council_btn.draw(screen, self.small_font)

        # Layer 5: Overlays
        if self.active_screen == "TECH_TREE":
            self.social_screens.draw_tech_tree(screen, game)
        elif self.active_screen == "SOCIAL_ENGINEERING":
            self.social_screens.draw_social_engineering(screen, game)
        elif self.active_screen == "DESIGN_WORKSHOP":
            self.social_screens.draw_design_workshop(screen, game)
        elif self.active_screen == "BASE_VIEW":
            self.base_screens.draw_base_view(screen, game)
        elif self.active_screen == "BASE_NAMING":
            self.base_screens.draw_base_naming(screen)
        elif self.active_screen == "DIPLOMACY":
            self.diplomacy.draw(screen)
        elif self.active_screen == "COUNCIL_VOTE":
            self.council.draw(screen, game)

        # Battle/info panel (always visible in game UI area)
        if self.active_screen == "GAME":
            self.battle_ui.draw_battle_animation(screen, game)
            self._draw_unit_stack_panel(screen, game)

        # Supply pod message overlay (top priority)
        if game.supply_pod_message:
            self.dialogs.draw_supply_pod_message(screen, game.supply_pod_message)

        # Battle prediction overlay (highest priority)
        if game.pending_battle:
            self.battle_ui.draw_battle_prediction(screen, game)

        # Game over screen (highest priority)
        if game.game_over:
            self._draw_game_over(screen, game)

    def _draw_minimap(self, screen, game):
        """Draw a miniature version of the map showing terrain and bases."""
        # Calculate scale to fit entire map in minimap
        map_width = game.game_map.width
        map_height = game.game_map.height

        scale_x = self.minimap_rect.width / map_width
        scale_y = self.minimap_rect.height / map_height
        scale = min(scale_x, scale_y)

        # Calculate centered offset within minimap
        scaled_width = int(map_width * scale)
        scaled_height = int(map_height * scale)
        offset_x = self.minimap_rect.x + (self.minimap_rect.width - scaled_width) // 2
        offset_y = self.minimap_rect.y + (self.minimap_rect.height - scaled_height) // 2

        # Draw terrain
        for y in range(map_height):
            for x in range(map_width):
                tile = game.game_map.get_tile(x, y)
                if tile:
                    # Determine color
                    color = constants.COLOR_LAND if tile.is_land() else constants.COLOR_OCEAN

                    # Draw tiny rectangle for this tile
                    tile_x = offset_x + int(x * scale)
                    tile_y = offset_y + int(y * scale)
                    tile_w = max(1, int(scale))
                    tile_h = max(1, int(scale))

                    pygame.draw.rect(screen, color, (tile_x, tile_y, tile_w, tile_h))

        # Draw bases as small dots
        base_colors = {
            0: (50, 205, 50),   # Player - Gaian green
            1: (255, 80, 80)    # AI - red
        }

        for base in game.bases:
            base_x = offset_x + int(base.x * scale)
            base_y = offset_y + int(base.y * scale)
            color = base_colors.get(base.owner, (150, 150, 150))

            # Draw a small circle for the base
            radius = max(2, int(scale * 0.5))
            pygame.draw.circle(screen, color, (base_x, base_y), radius)
            pygame.draw.circle(screen, COLOR_BLACK, (base_x, base_y), radius, 1)

    def _draw_game_over(self, screen, game):
        """Draw the game over screen with victory/defeat message and buttons."""
        from constants import COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT

        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(200)
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
        title_font = pygame.font.Font(None, 48)
        if game.winner == game.player_id:
            title_text = "VICTORY!"
            title_color = (100, 255, 100)
            message = "You have conquered all enemy bases!"
        else:
            title_text = "DEFEAT"
            title_color = (255, 100, 100)
            message = "All your bases have been destroyed."

        title_surf = title_font.render(title_text, True, title_color)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 40))

        # Message
        message_surf = self.font.render(message, True, COLOR_TEXT)
        screen.blit(message_surf, (dialog_x + dialog_w // 2 - message_surf.get_width() // 2, dialog_y + 120))

        # Buttons
        button_y = dialog_y + dialog_h - 100
        button_w = 200
        button_h = 60
        button_spacing = 40

        # New Game button
        new_game_x = dialog_x + dialog_w // 2 - button_w - button_spacing // 2
        new_game_rect = pygame.Rect(new_game_x, button_y, button_w, button_h)
        self.game_over_new_game_rect = new_game_rect

        new_game_hover = new_game_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if new_game_hover else COLOR_BUTTON, new_game_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if new_game_hover else COLOR_BUTTON_BORDER, new_game_rect, 2, border_radius=8)
        new_game_surf = self.font.render("New Game", True, COLOR_TEXT)
        screen.blit(new_game_surf, (new_game_rect.centerx - new_game_surf.get_width() // 2, new_game_rect.centery - 10))

        # Exit button
        exit_x = dialog_x + dialog_w // 2 + button_spacing // 2
        exit_rect = pygame.Rect(exit_x, button_y, button_w, button_h)
        self.game_over_exit_rect = exit_rect

        exit_hover = exit_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if exit_hover else COLOR_BUTTON, exit_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if exit_hover else COLOR_BUTTON_BORDER, exit_rect, 2, border_radius=8)
        exit_surf = self.font.render("Exit", True, COLOR_TEXT)
        screen.blit(exit_surf, (exit_rect.centerx - exit_surf.get_width() // 2, exit_rect.centery - 10))

    def _draw_unit_stack_panel(self, screen, game):
        """Draw panel showing all units at the selected tile."""
        if not game.selected_unit:
            return

        # Get all units at selected unit's tile
        tile = game.game_map.get_tile(game.selected_unit.x, game.selected_unit.y)
        if not tile or len(tile.units) == 0:
            return

        # Panel dimensions - below battle panel, same width as battle panel
        panel_w = 360  # Match battle panel width
        panel_h = 120
        panel_x = 680  # Same x as battle panel
        panel_y = constants.UI_PANEL_Y + 145  # Below battle panel (battle panel is 130px + 10px offset + 5px gap)

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (25, 30, 35), panel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, panel_rect, 2, border_radius=6)

        # Title
        title = self.small_font.render("UNITS IN TILE", True, COLOR_TEXT)
        screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 5))

        # Draw unit icons (up to 8 visible at once)
        units_to_show = tile.units
        max_visible = 8
        icon_size = 20
        icon_spacing = 40  # Horizontal spacing between icons
        row_spacing = 50   # Vertical spacing between rows

        # Calculate visible range with scroll
        total_units = len(units_to_show)
        if total_units <= max_visible:
            # All units fit, no scrolling needed
            visible_units = units_to_show
            self.unit_stack_scroll_offset = 0
        else:
            # Need scrolling
            visible_units = units_to_show[self.unit_stack_scroll_offset:self.unit_stack_scroll_offset + max_visible]

        # Draw unit icons in 2 rows of 4
        start_x = panel_x + 20
        start_y = panel_y + 35

        for i, unit in enumerate(visible_units):
            col = i % 4
            row = i // 4
            icon_x = start_x + col * icon_spacing
            icon_y = start_y + row * row_spacing

            # Determine unit color
            if unit.owner == game.player_id:
                unit_color = COLOR_UNIT_FRIENDLY
            else:
                unit_color = COLOR_UNIT_ENEMY

            # Highlight selected unit
            if unit == game.selected_unit:
                pygame.draw.circle(screen, (255, 255, 0), (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2 + 3)

            # Draw unit circle
            pygame.draw.circle(screen, unit_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2)
            pygame.draw.circle(screen, COLOR_BLACK, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2, 1)

            # Draw unit type indicator (first letter of unit type)
            type_letter = unit.unit_type[0].upper()
            letter_font = pygame.font.Font(None, 16)
            letter_surf = letter_font.render(type_letter, True, COLOR_BLACK)
            letter_rect = letter_surf.get_rect(center=(icon_x + icon_size // 2, icon_y + icon_size // 2))
            screen.blit(letter_surf, letter_rect)

        # Draw scroll arrows and count if needed
        if total_units > max_visible:
            arrow_y = panel_y + panel_h - 20
            arrow_size = 15

            # Left arrow
            left_arrow_rect = pygame.Rect(panel_x + 10, arrow_y, arrow_size, arrow_size)
            self.unit_stack_left_arrow_rect = left_arrow_rect
            if self.unit_stack_scroll_offset > 0:
                pygame.draw.polygon(screen, COLOR_TEXT, [
                    (left_arrow_rect.right, left_arrow_rect.top),
                    (left_arrow_rect.left, left_arrow_rect.centery),
                    (left_arrow_rect.right, left_arrow_rect.bottom)
                ])

            # Right arrow
            right_arrow_rect = pygame.Rect(panel_x + panel_w - 25, arrow_y, arrow_size, arrow_size)
            self.unit_stack_right_arrow_rect = right_arrow_rect
            if self.unit_stack_scroll_offset + max_visible < total_units:
                pygame.draw.polygon(screen, COLOR_TEXT, [
                    (right_arrow_rect.left, right_arrow_rect.top),
                    (right_arrow_rect.right, right_arrow_rect.centery),
                    (right_arrow_rect.left, right_arrow_rect.bottom)
                ])

            # Unit count
            count_text = self.small_font.render(f"{self.unit_stack_scroll_offset + 1}-{min(self.unit_stack_scroll_offset + max_visible, total_units)}/{total_units}", True, (180, 180, 180))
            screen.blit(count_text, (panel_x + panel_w // 2 - count_text.get_width() // 2, arrow_y + 2))
        else:
            # Show total count even when not scrolling
            if total_units > 1:
                count_text = self.small_font.render(f"{total_units} units", True, (180, 180, 180))
                screen.blit(count_text, (panel_x + panel_w // 2 - count_text.get_width() // 2, panel_y + panel_h - 20))

    def show_base_naming_dialog(self, unit):
        """Show the base naming dialog for a colony pod."""
        self.base_screens.show_base_naming(unit)
        self.active_screen = "BASE_NAMING"

    def show_base_view(self, base):
        """Show the base management screen."""
        self.base_screens.show_base_view(base)
        self.active_screen = "BASE_VIEW"
