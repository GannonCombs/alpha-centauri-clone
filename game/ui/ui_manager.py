"""Main UI coordinator - replaces UIPanel."""

import pygame
from game.data import display
from game.data.display import (COLOR_UI_BACKGROUND, COLOR_UI_BORDER, COLOR_TEXT,
                                 COLOR_BLACK, COLOR_BUTTON_BORDER)
from .components import Button
from .dialogs import DialogManager
from .battle_ui import BattleUIManager
from .diplomacy import DiplomacyManager
from .council import CouncilManager
from .social_screens import SocialScreensManager
from .base_screens import BaseScreenManager
from .save_load_dialog import SaveLoadDialogManager
from .context_menu import ContextMenu
from game.data.data import FACTION_DATA
from game.map import tile_base_nutrients, tile_base_energy


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
        self.save_load_dialog = SaveLoadDialogManager(self.font, self.small_font)
        self.context_menu = ContextMenu(self.font)

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

        # Upkeep event popup buttons
        self.upkeep_zoom_rect = None
        self.upkeep_ignore_rect = None

        # Commlink request popup
        self.commlink_request_active = False
        self.commlink_request_other_faction_id = None
        self.commlink_request_player_id = None
        self.commlink_request_answer_rect = None
        self.commlink_request_ignore_rect = None

        # Faction elimination popup
        self.elimination_popup_active = False
        self.elimination_faction_id = None
        self.elimination_ok_rect = None

        # New designs popup
        self.new_designs_popup_active = False
        self.new_designs_view_rect = None
        self.new_designs_ignore_rect = None

        # Treaty breaking popups
        self.break_treaty_popup_active = False  # Player breaking treaty
        self.break_treaty_target_faction = None
        self.break_treaty_pending_battle = None  # Store battle info if player chooses to attack
        self.break_treaty_ok_rect = None
        self.break_treaty_cancel_rect = None

        self.surprise_attack_popup_active = False  # AI breaking treaty
        self.surprise_attack_faction = None
        self.surprise_attack_ok_rect = None

        # Pact evacuation popup
        self.pact_evacuation_popup_active = False
        self.pact_evacuation_count = 0
        self.pact_evacuation_ok_rect = None
        self.pact_evacuation_pending_battle = None  # Store battle to proceed after dismissing popup

        # Unit stack panel
        self.unit_stack_scroll_offset = 0
        self.unit_stack_left_arrow_rect = None
        self.unit_stack_right_arrow_rect = None

    def _init_layout(self):
        """Initialize layout after screen dimensions are known."""
        if self.main_menu_button is not None:
            return  # Already initialized

        button_y = display.UI_PANEL_Y + 20
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
        minimap_x = display.SCREEN_WIDTH - 320  # Left edge of right area
        minimap_y = display.UI_PANEL_Y + 25  # More spacing from top to fit label
        self.minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)

        # Commlink button to the RIGHT of the minimap
        self.commlink_button = Button(self.minimap_rect.right + 10, display.UI_PANEL_Y + 10, 180, 35, "Commlink")

        # Commlink Drop-up dimensions (increased height for votes summary)
        menu_w, menu_h = 320, 330
        self.commlink_menu_rect = pygame.Rect(self.commlink_button.rect.x - (menu_w - self.commlink_button.rect.width),
                                              self.commlink_button.rect.top - menu_h - 5, menu_w, menu_h)

        # Faction buttons will be created dynamically based on contacts
        self.faction_buttons = []

        self.council_btn = Button(self.commlink_menu_rect.x + 5, self.commlink_menu_rect.bottom - 45, menu_w - 10, 38,
                                  "Planetary Council")

    def _update_faction_buttons(self, game):
        """Update faction buttons based on current contacts (called when drawing commlink)."""
        # faction_contacts is a list preserving the order in which factions were met
        # Filter out the player's own faction and eliminated factions
        contacted_factions = [f for f in game.faction_contacts
                            if f != game.player_faction_id and f not in game.eliminated_factions]

        # Clear existing buttons
        self.faction_buttons = []

        # Create button for each contacted faction (in contact order)
        menu_w = self.commlink_menu_rect.width
        button_index = 0

        for faction_id in contacted_factions:
            # faction_id IS player_id in the new system
            if faction_id < len(FACTION_DATA):
                faction = FACTION_DATA[faction_id]
                btn = Button(self.commlink_menu_rect.x + 5,
                           self.commlink_menu_rect.y + 5 + (button_index * 38),
                           menu_w - 10, 32,
                           faction["full_name"],
                           faction["color"],
                           COLOR_BLACK)
                btn.player_id = faction_id  # Store faction_id (same as player_id now)
                btn.faction_id = faction_id  # Also store faction_id
                self.faction_buttons.append(btn)
                button_index += 1

    def handle_event(self, event, game):
        """Process input events for UI interactions and modal dialogs."""
        # Initialize layout if needed
        self._init_layout()

        # Handle context menu first (highest priority)
        if self.context_menu.handle_event(event):
            return True

        # 1. Handle Overlays First (Hotkeys)
        if event.type == pygame.KEYDOWN:
            # Check for Ctrl+S and Ctrl+L first (highest priority shortcuts)
            if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                if self.active_screen == "GAME" and not game.processing_ai:
                    self.save_load_dialog.show_save_dialog(game)
                return True
            elif event.key == pygame.K_l and (event.mod & pygame.KMOD_CTRL):
                if self.active_screen == "GAME" and not game.processing_ai:
                    self.save_load_dialog.show_load_dialog()
                return True

            # Handle save/load dialog events if open
            if self.save_load_dialog.mode is not None:
                result = self.save_load_dialog.handle_event(event, game)
                if result == 'save_complete':
                    # Game was saved successfully
                    game.set_status_message("Game saved successfully")
                    return True
                elif isinstance(result, tuple) and result[0] == 'load_complete':
                    # Game was loaded - return signal to main.py
                    return ('load_game', result[1])
                elif result == 'close':
                    # Dialog closed without action
                    return True
                return True  # Dialog consumed event

            # Handle text input for base naming
            if self.active_screen == "BASE_NAMING":
                result = self.base_screens.handle_base_naming_event(event, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True

            # Handle text input for base view (hurry production popup)
            if self.active_screen == "BASE_VIEW":
                # Check for C (Change production) hotkey
                if event.key == pygame.K_c and not self.base_screens.hurry_production_open and not self.base_screens.queue_management_open:
                    self.base_screens.production_selection_mode = "change"
                    self.base_screens.production_selection_open = True
                    if self.base_screens.viewing_base:
                        self.base_screens.selected_production_item = self.base_screens.viewing_base.current_production
                    return True
                # Check for H (Hurry production) hotkey
                elif event.key == pygame.K_h and not self.base_screens.production_selection_open and not self.base_screens.queue_management_open:
                    self.base_screens.hurry_production_open = True
                    self.base_screens.hurry_input = ""
                    return True

                if self.base_screens.handle_base_view_event(event, game):
                    return True

            if event.key == pygame.K_e:
                # Toggle Social Engineering screen
                if self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_screens.social_engineering_open = False
                    # Reset selections to revert unsaved changes
                    self.social_screens.social_engineering_screen.se_selections = None
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "SOCIAL_ENGINEERING"
                    self.social_screens.social_engineering_open = True
                    # Reset selections to load current game state
                    self.social_screens.social_engineering_screen.se_selections = None
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
                    # Reset editing panel state when opening
                    self.social_screens.design_workshop_screen.dw_editing_panel = None
                    # Load first empty slot when opening
                    workshop = self.social_screens.design_workshop_screen
                    faction_designs = game.factions[game.player_faction_id].designs
                    first_empty = faction_designs.find_first_empty_slot()
                    workshop._load_slot_into_editor(first_empty, game)
                    # Rebuild designs if new tech was discovered (manual call, no specific tech)
                    if game.designs_need_rebuild:
                        player_tech_tree = game.factions[game.player_faction_id].tech_tree
                        self.social_screens.design_workshop_screen.rebuild_available_designs(player_tech_tree, game, None)
                        game.designs_need_rebuild = False
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

            if event.key == pygame.K_c:
                # Center camera on selected unit
                if self.active_screen == "GAME" and game.selected_unit:
                    game.center_camera_on_tile = (game.selected_unit.x, game.selected_unit.y)
                    return True

            if event.key == pygame.K_ESCAPE:
                # Battle prediction popup - Esc = Cancel
                if game.combat.pending_battle:
                    game.combat.pending_battle = None
                    return True
                # Save/load dialog - Esc closes dialog
                elif self.save_load_dialog.mode is not None:
                    self.save_load_dialog.close()
                    return True
                elif self.active_screen == "TECH_TREE":
                    self.active_screen = "GAME"
                    self.social_screens.tech_tree_open = False
                    return True
                elif self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_screens.social_engineering_open = False
                    # Reset selections to revert unsaved changes
                    self.social_screens.social_engineering_screen.se_selections = None
                    self.social_screens.social_engineering_screen.se_confirm_dialog_open = False
                    return True
                elif self.active_screen == "DESIGN_WORKSHOP":
                    # Check if a component selection panel is open
                    if self.social_screens.design_workshop_screen.dw_editing_panel is not None:
                        # Close the component panel, stay in design workshop
                        self.social_screens.design_workshop_screen.dw_editing_panel = None
                        return True
                    else:
                        # No panel open, exit design workshop
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
                if game.combat.pending_battle:
                    # Enter key acts as OK button
                    attacker = game.combat.pending_battle['attacker']
                    defender = game.combat.pending_battle['defender']
                    target_x = game.combat.pending_battle['target_x']
                    target_y = game.combat.pending_battle['target_y']

                    # Clear pending battle
                    game.combat.pending_battle = None

                    # Resolve combat
                    game.combat.resolve_combat(attacker, defender, target_x, target_y)
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
        # Right-click handling (for context menus)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # Handle garrison context menu in base view
            if self.active_screen == "BASE_VIEW":
                if self.base_screens.handle_base_view_right_click(event.pos, game):
                    return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle upkeep event popup (highest priority)
            if game.upkeep_phase_active:
                pos = pygame.mouse.get_pos()

                # Zoom to view button
                if self.upkeep_zoom_rect and self.upkeep_zoom_rect.collidepoint(pos):
                    event_data = game.get_current_upkeep_event()
                    if event_data and 'base' in event_data:
                        # Center camera on the base
                        base = event_data['base']
                        game.center_camera_on_tile = (base.x, base.y)
                    # Advance to next event
                    game.advance_upkeep_event()
                    return True

                # Ignore/Continue button
                if self.upkeep_ignore_rect and self.upkeep_ignore_rect.collidepoint(pos):
                    game.advance_upkeep_event()
                    return True

                # Don't allow clicks through upkeep popup
                return True

            # Commlink request buttons
            if self.commlink_request_active:
                pos = pygame.mouse.get_pos()

                if self.commlink_request_answer_rect and self.commlink_request_answer_rect.collidepoint(pos):
                    # Answer - open diplomacy with this faction
                    self.commlink_request_active = False
                    # Remove the first request from pending requests
                    # Note: pending_commlink_requests is an array because a unit could meet multiple new factions in the same one move.
                    # While unlikely, it has happened to me.
                    if game.pending_commlink_requests:
                        game.pending_commlink_requests.pop(0)
                    self.active_screen = "DIPLOMACY"
                    # Use the other_faction_id we already have from the commlink request
                    if self.commlink_request_other_faction_id is not None and self.commlink_request_other_faction_id < len(FACTION_DATA):
                        # Player is always index 0
                        self.diplomacy.open_diplomacy(FACTION_DATA[self.commlink_request_other_faction_id], self.commlink_request_player_id, game)
                    self.diplomacy.diplo_stage = "greeting"
                    return True
                elif self.commlink_request_ignore_rect and self.commlink_request_ignore_rect.collidepoint(pos):
                    # Ignore - just close the popup
                    self.commlink_request_active = False
                    # Remove from pending requests
                    if game.pending_commlink_requests:
                        game.pending_commlink_requests.pop(0)
                    return True
                # Don't allow clicks through commlink request popup
                return True

            # Faction elimination popup buttons
            if self.elimination_popup_active:
                pos = pygame.mouse.get_pos()

                if self.elimination_ok_rect and self.elimination_ok_rect.collidepoint(pos):
                    # OK - close the popup
                    self.elimination_popup_active = False
                    # Remove from pending eliminations
                    if game.pending_faction_eliminations:
                        game.pending_faction_eliminations.pop(0)
                    return True
                # Don't allow clicks through elimination popup
                return True

            # New designs popup buttons
            if self.new_designs_popup_active:
                pos = pygame.mouse.get_pos()

                if self.new_designs_view_rect and self.new_designs_view_rect.collidepoint(pos):
                    # View - open design workshop
                    self.new_designs_popup_active = False
                    game.new_designs_available = False
                    self.active_screen = "DESIGN_WORKSHOP"
                    self.social_screens.design_workshop_screen.dw_editing_panel = None
                    return True
                elif self.new_designs_ignore_rect and self.new_designs_ignore_rect.collidepoint(pos):
                    # Ignore - just close the popup
                    self.new_designs_popup_active = False
                    game.new_designs_available = False
                    return True
                # Don't allow clicks through new designs popup
                return True

            # Break treaty popup buttons
            if self.break_treaty_popup_active:
                pos = pygame.mouse.get_pos()

                if self.break_treaty_ok_rect and self.break_treaty_ok_rect.collidepoint(pos):
                    # Player confirmed breaking treaty
                    # Check if there was a Pact (requires evacuation)
                    had_pact = self.diplomacy.diplo_relations.get(self.break_treaty_target_faction, "Uncommitted") == "Pact"

                    # Set relation to Vendetta
                    self.diplomacy.diplo_relations[self.break_treaty_target_faction] = "Vendetta"
                    self.break_treaty_popup_active = False

                    # If there was a pact, evacuate units and show popup
                    if had_pact:
                        # Evacuate both player's and AI's units
                        player_evacuated = game.evacuate_units_from_former_pact(game.player_faction_id, self.break_treaty_target_faction)
                        ai_evacuated = game.evacuate_units_from_former_pact(self.break_treaty_target_faction, game.player_faction_id)

                        # Show evacuation popup if any units were moved
                        if player_evacuated > 0:
                            self.pact_evacuation_popup_active = True
                            self.pact_evacuation_count = player_evacuated
                            self.pact_evacuation_pending_battle = self.break_treaty_pending_battle
                            self.break_treaty_pending_battle = None
                            self.break_treaty_target_faction = None
                        else:
                            # No evacuation needed, proceed with battle
                            if self.break_treaty_pending_battle:
                                game.combat.pending_battle = self.break_treaty_pending_battle
                                self.break_treaty_pending_battle = None
                            self.break_treaty_target_faction = None
                    else:
                        # No pact, just proceed with battle
                        if self.break_treaty_pending_battle:
                            game.combat.pending_battle = self.break_treaty_pending_battle
                            self.break_treaty_pending_battle = None
                        self.break_treaty_target_faction = None
                    return True
                elif self.break_treaty_cancel_rect and self.break_treaty_cancel_rect.collidepoint(pos):
                    # Cancel - no attack
                    self.break_treaty_popup_active = False
                    self.break_treaty_pending_battle = None
                    self.break_treaty_target_faction = None
                    return True
                # Don't allow clicks through popup
                return True

            # Pact evacuation popup button
            if self.pact_evacuation_popup_active:
                pos = pygame.mouse.get_pos()

                if self.pact_evacuation_ok_rect and self.pact_evacuation_ok_rect.collidepoint(pos):
                    # Dismiss popup and proceed with pending battle
                    self.pact_evacuation_popup_active = False

                    if self.pact_evacuation_pending_battle:
                        game.combat.pending_battle = self.pact_evacuation_pending_battle
                        self.pact_evacuation_pending_battle = None
                    self.pact_evacuation_count = 0
                    return True
                # Don't allow clicks through popup
                return True

            # Surprise attack popup button
            if self.surprise_attack_popup_active:
                pos = pygame.mouse.get_pos()

                if self.surprise_attack_ok_rect and self.surprise_attack_ok_rect.collidepoint(pos):
                    # Set both to Vendetta
                    self.diplomacy.diplo_relations[self.surprise_attack_faction] = "Vendetta"
                    self.surprise_attack_popup_active = False
                    self.surprise_attack_faction = None
                    return True
                # Don't allow clicks through popup
                return True

            # Handle save/load dialog clicks if open
            if self.save_load_dialog.mode is not None:
                result = self.save_load_dialog.handle_event(event, game)
                if result == 'save_complete':
                    game.set_status_message("Game saved successfully")
                    return True
                elif isinstance(result, tuple) and result[0] == 'load_complete':
                    # Game was loaded - return signal to main.py
                    return ('load_game', result[1])
                elif result == 'close':
                    return True
                return True  # Dialog consumed event

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
            if game.combat.pending_battle:
                result = self.battle_ui.handle_battle_prediction_click(event.pos)
                if result == 'ok':
                    # OK clicked - initiate combat
                    attacker = game.combat.pending_battle['attacker']
                    defender = game.combat.pending_battle['defender']
                    target_x = game.combat.pending_battle['target_x']
                    target_y = game.combat.pending_battle['target_y']

                    # Consume attacker's movement
                    if attacker.type in ['sea', 'air']:
                        # Sea and air units: attack ends turn
                        attacker.moves_remaining = 0
                    else:
                        # Land units: attack costs 1 move
                        attacker.moves_remaining -= 1

                    game.combat.resolve_combat(attacker, defender, target_x, target_y)
                    game.combat.pending_battle = None
                    return True
                elif result == 'cancel':
                    # Cancel clicked - abort attack
                    game.combat.pending_battle = None
                    return True
                # Block all other clicks when prediction is showing
                return True

            # Supply pod message takes priority (but only if not in diplomacy/commlink)
            if game.supply_pod_message and not self.commlink_request_active and self.active_screen != "DIPLOMACY":
                if self.dialogs.handle_supply_pod_click(event.pos):
                    game.supply_pod_message = None
                    return True
                # Block all other clicks when message is showing
                return True

            if self.active_screen == "TECH_TREE":
                result = self.social_screens.handle_tech_tree_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "SOCIAL_ENGINEERING":
                result = self.social_screens.handle_social_engineering_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "DESIGN_WORKSHOP":
                result = self.social_screens.handle_design_workshop_click(event.pos, game)
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
                    for btn in self.faction_buttons:
                        if btn.handle_event(event):
                            # Get the faction for this player_id
                            faction_id = btn.player_id  # player_id IS faction_id
                            if faction_id is not None and faction_id < len(FACTION_DATA):
                                # Open diplomacy with correct player faction ID
                                self.diplomacy.open_diplomacy(FACTION_DATA[faction_id], player_faction_index=game.player_faction_id, game=game)
                                self.active_screen = "DIPLOMACY"
                                self.commlink_open = False
                                return True
                    if self.council_btn.handle_event(event):
                        # Only allow if all contacts obtained
                        if game.all_contacts_obtained:
                            self.council.open_council()
                            self.active_screen = "COUNCIL_VOTE"
                            self.commlink_open = False
                            return True
                        else:
                            # Show message that council is locked
                            game.set_status_message("Contact all factions to unlock Planetary Council")
                            return True
                    return True
                else:
                    self.commlink_open = False  # Clicked outside

            # Handle minimap clicks - center camera on clicked location
            if self.minimap_rect and self.minimap_rect.collidepoint(event.pos):
                # Calculate which tile was clicked
                map_width = game.game_map.width
                map_height = game.game_map.height

                # Calculate scale and offset (same as in _draw_minimap)
                scale_x = self.minimap_rect.width / map_width
                scale_y = self.minimap_rect.height / map_height
                scale = min(scale_x, scale_y)

                scaled_width = int(map_width * scale)
                scaled_height = int(map_height * scale)
                offset_x = self.minimap_rect.x + (self.minimap_rect.width - scaled_width) // 2
                offset_y = self.minimap_rect.y + (self.minimap_rect.height - scaled_height) // 2

                # Convert click position to map coordinates
                click_x = event.pos[0] - offset_x
                click_y = event.pos[1] - offset_y

                # Check if click is within the scaled map area
                if 0 <= click_x < scaled_width and 0 <= click_y < scaled_height:
                    tile_x = int(click_x / scale)
                    tile_y = int(click_y / scale)

                    # Clamp to map bounds
                    tile_x = max(0, min(tile_x, map_width - 1))
                    tile_y = max(0, min(tile_y, map_height - 1))

                    # Center on this tile
                    game.center_camera_on_tile = (tile_x, tile_y)
                    return True

            if self.end_turn_button.handle_event(event):
                game.end_turn()
                return True

        # 3. Mouse Button Up (for drag end)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Always end any scrollbar drag on mouse up, regardless of screen
            # This prevents the drag state from getting stuck
            if self.active_screen == "TECH_TREE":
                self.social_screens.handle_tech_tree_drag_end()
                # Don't return True here - let other handlers process the mouse up

        # 4. Mouse Wheel Scrolling
        if event.type == pygame.MOUSEWHEEL:
            # Handle scrolling in tech tree screen
            if self.active_screen == "TECH_TREE":
                self.social_screens.handle_tech_tree_scroll(event.y, game)
                return True

        # 5. Motion (Hover and Drag)
        if event.type == pygame.MOUSEMOTION:
            # Handle scrollbar drag in tech tree
            if self.active_screen == "TECH_TREE":
                if self.social_screens.handle_tech_tree_drag_motion(event.pos, game):
                    return True

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

    def draw(self, screen, game, renderer=None):
        """Render the UI panel with game info, buttons, and active modals.

        Rendering layers (bottom to top):
        1. Background panel
        2. Minimap with viewport indicator
        3. Mission year, energy credits, turn counter
        4. Fixed buttons (Main Menu, End Turn, Commlink)
        5. Unit info panel (if unit selected)
        6. Active screen (BASE_VIEW, DIPLOMACY, etc.)
        7. Popups (highest priority first):
           - Battle prediction
           - Upkeep events (tech, milestones)
           - Commlink requests
           - New designs available
           - Faction elimination
        8. Context menus (highest priority)

        Args:
            screen: Pygame surface to draw on
            game: Game instance for state access
            renderer: Optional renderer for minimap drawing
        """
        self._init_layout()

        # Layer 1: Background
        pygame.draw.rect(screen, COLOR_UI_BACKGROUND,
                         (0, display.UI_PANEL_Y, display.SCREEN_WIDTH, display.UI_PANEL_HEIGHT))
        pygame.draw.line(screen, COLOR_UI_BORDER, (0, display.UI_PANEL_Y),
                         (display.SCREEN_WIDTH, display.UI_PANEL_Y), 3)

        # Layer 2: Minimap
        pygame.draw.rect(screen, COLOR_BLACK, self.minimap_rect)
        pygame.draw.rect(screen, COLOR_UI_BORDER, self.minimap_rect, 2)
        mm_label = self.small_font.render("Mini-Map", True, COLOR_TEXT)
        screen.blit(mm_label, (self.minimap_rect.x, self.minimap_rect.y - 18))

        # Draw minimap contents
        self._draw_minimap(screen, game, renderer)

        # Mission Year and Energy Credits - below minimap
        info_x = self.minimap_rect.x
        info_y = self.minimap_rect.bottom + 8
        year_text = self.small_font.render(f"MY: {game.mission_year}", True, COLOR_TEXT)
        screen.blit(year_text, (info_x, info_y))

        credits_text = self.small_font.render(f"Credits: {game.energy_credits}", True, (200, 220, 100))
        screen.blit(credits_text, (info_x, info_y + 18))

        # Layer 3: Fixed Buttons
        self.main_menu_button.draw(screen, self.font)

        # End Turn button with glow effect if all units have moved
        if game.all_friendly_units_moved() and not game.processing_ai:
            # Draw glowing border around button
            import math
            # Pulse effect based on time
            pulse = abs(math.sin(pygame.time.get_ticks() / 300.0))
            glow_color = (100 + int(155 * pulse), 200 + int(55 * pulse), 100)
            glow_rect = self.end_turn_button.rect.inflate(8, 8)
            pygame.draw.rect(screen, glow_color, glow_rect, 4, border_radius=8)

        self.end_turn_button.draw(screen, self.font)
        self.commlink_button.draw(screen, self.small_font)

        # Turn counter - below buttons
        turn_text = self.font.render(f"Turn: {game.turn}", True, COLOR_TEXT)
        screen.blit(turn_text, (20, display.UI_PANEL_Y + 75))

        # Unit info panel - left-center area (always visible if unit selected)
        if game.selected_unit:
            unit = game.selected_unit
            # Position left of battle panel
            info_x = 370
            info_y = display.UI_PANEL_Y + 20
            info_box = pygame.Rect(info_x - 10, info_y - 5, 280, 135)
            pygame.draw.rect(screen, (35, 40, 45), info_box)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, info_box, 2)
            screen.blit(self.font.render(f"Unit: {unit.name}", True, COLOR_TEXT), (info_x, info_y))

            # Capitalize unit type
            type_display = unit.type.capitalize()
            screen.blit(self.small_font.render(f"Type: {type_display}", True, (200, 210, 220)), (info_x, info_y + 30))

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

        # Terrain panel - far right of console
        # Show when a unit is selected OR when tile cursor mode is active
        _show_terrain = game.selected_unit or game.tile_cursor_mode
        if _show_terrain:
            terrain_x = 1080
            terrain_y = display.UI_PANEL_Y + 20
            terrain_box_w = 200
            terrain_box_h = 152
            terrain_box = pygame.Rect(terrain_x - 10, terrain_y - 5, terrain_box_w, terrain_box_h)
            pygame.draw.rect(screen, (30, 40, 35), terrain_box)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, terrain_box, 2)

            # Title
            screen.blit(self.font.render("Terrain", True, COLOR_TEXT), (terrain_x, terrain_y))

            # Get current tile info — cursor tile in cursor mode, else selected unit's tile
            if game.tile_cursor_mode:
                tile = game.game_map.get_tile(game.cursor_x, game.cursor_y)
            else:
                tile = game.game_map.get_tile(game.selected_unit.x, game.selected_unit.y)
            if tile:
                # Terrain type
                terrain_type = "Land" if tile.is_land() else "Ocean"
                terrain_text = self.small_font.render(terrain_type, True, (180, 200, 180))
                screen.blit(terrain_text, (terrain_x, terrain_y + 30))

                # Rainfall (land: Arid/Moderate/Rainy; ocean: em dash)
                if tile.is_land():
                    rainfall_labels = {0: "Arid", 1: "Moderate", 2: "Rainy"}
                    rainfall_colors = {0: (200, 170, 110), 1: (160, 200, 130), 2: (100, 210, 100)}
                    rain_text = self.small_font.render(
                        f"Rainfall: {rainfall_labels[tile.rainfall]}",
                        True, rainfall_colors[tile.rainfall])
                else:
                    rain_text = self.small_font.render("Rainfall: \u2014", True, (120, 150, 180))
                screen.blit(rain_text, (terrain_x, terrain_y + 46))

                # Elevation
                elev_text = self.small_font.render(f"Elev: {tile.altitude}m", True, (200, 200, 180))
                screen.blit(elev_text, (terrain_x, terrain_y + 62))

                # Nutrients (from rainfall for land; 1 for ocean)
                nutrients = tile_base_nutrients(tile)
                nut_text = self.small_font.render(f"Nutrients: {nutrients}", True, (150, 220, 150))
                screen.blit(nut_text, (terrain_x, terrain_y + 80))

                # Minerals (placeholder — Rockiness not yet implemented)
                min_text = self.small_font.render("Minerals: 1", True, (200, 180, 140))
                screen.blit(min_text, (terrain_x, terrain_y + 96))

                # Energy (from altitude band for land; 0 for unimproved ocean)
                energy = tile_base_energy(tile)
                ene_text = self.small_font.render(f"Energy: {energy}", True, (220, 220, 100))
                screen.blit(ene_text, (terrain_x, terrain_y + 112))

        # Layer 4a: Main Menu Drop-up
        if self.main_menu_open and self.active_screen == "GAME":
            pygame.draw.rect(screen, (20, 25, 30), self.main_menu_rect)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.main_menu_rect, 3)
            for btn in self.main_menu_buttons:
                btn.draw(screen, self.font)

        # Layer 4b: Commlink Drop-up
        if self.commlink_open and self.active_screen == "GAME":
            # Update faction buttons based on current contacts
            self._update_faction_buttons(game)

            pygame.draw.rect(screen, COLOR_BLACK, self.commlink_menu_rect)
            pygame.draw.rect(screen, COLOR_UI_BORDER, self.commlink_menu_rect, 2)

            # Draw faction list with proper formatting: "<number>. <faction name> <status>"
            # Status is right-justified
            line_height = 32
            y_offset = 5

            for i, btn in enumerate(self.faction_buttons):
                faction = FACTION_DATA[btn.faction_id]

                # Get diplomatic status
                status_text = ""
                if hasattr(self, 'diplomacy') and btn.faction_id in self.diplomacy.diplo_relations:
                    status = self.diplomacy.diplo_relations[btn.faction_id]
                    # Format status according to SMAC convention
                    if status == "Vendetta":
                        status_text = "VENDETTA"
                    elif status == "Pact":
                        status_text = "PACT"
                    elif status == "Treaty":
                        status_text = "TREATY"
                    elif status == "Truce" or status == "Formal Truce": #TODO: error?
                        status_text = "TRUCE"
                    # Informal Truce shows as blank (empty string)

                # Draw background on hover
                is_hover = btn.rect.collidepoint(pygame.mouse.get_pos())
                if is_hover:
                    pygame.draw.rect(screen, (40, 50, 60), btn.rect, border_radius=4)

                # Draw text: "<number>. <faction name>"
                contact_number = i + 1
                left_text = f"{contact_number}. {faction['leader']}"
                left_surf = self.small_font.render(left_text, True, faction['color'])
                screen.blit(left_surf, (btn.rect.x + 5, btn.rect.y + 8))

                # Draw status (right-justified)
                if status_text:
                    status_surf = self.small_font.render(status_text, True, faction['color'])
                    status_x = btn.rect.right - status_surf.get_width() - 5
                    screen.blit(status_surf, (status_x, btn.rect.y + 8))

            # Draw player's votes above council button
            player_faction = game.factions.get(game.player_faction_id)
            player_votes = player_faction.get_voting_power(game) if player_faction else 0

            votes_y = self.council_btn.rect.y - 25
            votes_text = f"Votes: {player_votes}"
            votes_surf = self.small_font.render(votes_text, True, (180, 200, 220))
            votes_x = self.commlink_menu_rect.x + (self.commlink_menu_rect.width - votes_surf.get_width()) // 2
            screen.blit(votes_surf, (votes_x, votes_y))

            # Draw council button (disabled if not all contacts obtained)
            if game.all_contacts_obtained:
                self.council_btn.draw(screen, self.small_font)
            else:
                # Draw disabled version
                pygame.draw.rect(screen, (30, 30, 30), self.council_btn.rect, border_radius=4)
                pygame.draw.rect(screen, (60, 60, 60), self.council_btn.rect, 2, border_radius=4)
                text_surf = self.small_font.render("Planetary Council", True, (80, 80, 80))
                screen.blit(text_surf, (self.council_btn.rect.centerx - text_surf.get_width() // 2,
                                       self.council_btn.rect.centery - text_surf.get_height() // 2))

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

        # Supply pod message overlay (top priority, but not during diplomacy/commlink)
        # Don't show supply pod if we're in diplomacy or have a commlink request active
        if game.supply_pod_message and not self.commlink_request_active and self.active_screen != "DIPLOMACY":
            self.dialogs.draw_supply_pod_message(screen, game.supply_pod_message)

        # Check for treaty-breaking attacks (before battle prediction)
        if hasattr(game, 'pending_treaty_break') and game.pending_treaty_break and not self.break_treaty_popup_active:
            attack_info = game.pending_treaty_break
            defender_faction = attack_info['defender'].owner
            relation = self.diplomacy.diplo_relations.get(defender_faction, "Uncommitted")

            if relation == "Pact":
                # Can't break pact by attacking
                game.set_status_message("You cannot attack your pact brother!")
                game.pending_treaty_break = None
            elif relation in ["Treaty", "Truce"]:
                # Show break treaty popup
                self.break_treaty_popup_active = True
                self.break_treaty_target_faction = defender_faction
                self.break_treaty_pending_battle = {
                    'attacker': attack_info['attacker'],
                    'defender': attack_info['defender'],
                    'target_x': attack_info['target_x'],
                    'target_y': attack_info['target_y']
                }
                game.pending_treaty_break = None
            else:
                # Vendetta or Uncommitted - proceed with combat
                game.combat.pending_battle = {
                    'attacker': attack_info['attacker'],
                    'defender': attack_info['defender'],
                    'target_x': attack_info['target_x'],
                    'target_y': attack_info['target_y']
                }
                game.pending_treaty_break = None

        # Check for AI surprise attacks
        if hasattr(game, 'pending_ai_attack') and game.pending_ai_attack and not self.surprise_attack_popup_active:
            attack_info = game.pending_ai_attack
            ai_faction = attack_info['ai_faction']
            relation = self.diplomacy.diplo_relations.get(ai_faction, "Uncommitted")

            if relation in ["Treaty", "Truce", "Pact"]:
                # AI broke treaty - show surprise attack popup
                self.surprise_attack_popup_active = True
                self.surprise_attack_faction = ai_faction
            game.pending_ai_attack = None

        # Battle prediction overlay (highest priority)
        if game.combat.pending_battle:
            self.battle_ui.draw_battle_prediction(screen, game)

        # Upkeep phase popup (high priority)
        if game.upkeep_phase_active:
            self._draw_upkeep_event(screen, game)

        # Check for pending commlink requests and show popup
        # Only activate next request if we're not in diplomacy (wait for screen to fully close)
        if not self.commlink_request_active and game.pending_commlink_requests and self.active_screen != "DIPLOMACY":
            # Activate the first pending request
            request = game.pending_commlink_requests[0]
            self.commlink_request_active = True
            self.commlink_request_other_faction_id = request['other_faction_id']
            self.commlink_request_player_id = request['player_faction_id']

        # Commlink request popup
        if self.commlink_request_active:
            self._draw_commlink_request(screen, game)

        # Check for pending faction eliminations and show popup
        if not self.elimination_popup_active and game.pending_faction_eliminations:
            # Activate the first pending elimination
            faction_id = game.pending_faction_eliminations[0]
            self.elimination_popup_active = True
            self.elimination_faction_id = faction_id

        # Faction elimination popup
        if self.elimination_popup_active:
            self._draw_faction_elimination(screen, game)

        # Check for new designs available and show popup
        if not self.new_designs_popup_active and game.new_designs_available:
            self.new_designs_popup_active = True

        # New designs popup
        if self.new_designs_popup_active:
            self._draw_new_designs_popup(screen, game)

        # Treaty breaking popups
        if self.break_treaty_popup_active:
            self._draw_break_treaty_popup(screen, game)

        if self.surprise_attack_popup_active:
            self._draw_surprise_attack_popup(screen, game)

        if self.pact_evacuation_popup_active:
            self._draw_pact_evacuation_popup(screen, game)

        # Game over screen (highest priority)
        if game.game_over:
            self._draw_game_over(screen, game)

        # Save/Load dialog (top of everything)
        if self.save_load_dialog.mode is not None:
            self.save_load_dialog.draw(screen)

        # Context menu (absolute top)
        self.context_menu.draw(screen)

    def _draw_minimap(self, screen, game, renderer=None):
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
                    color = display.COLOR_LAND if tile.is_land() else display.COLOR_OCEAN

                    # Draw tiny rectangle for this tile
                    tile_x = offset_x + int(x * scale)
                    tile_y = offset_y + int(y * scale)
                    tile_w = max(1, int(scale))
                    tile_h = max(1, int(scale))

                    pygame.draw.rect(screen, color, (tile_x, tile_y, tile_w, tile_h))

        # Draw bases as small dots
        base_colors = {
            0: (50, 205, 50),   # Player - Gaian green
            1: (255, 80, 80),   # AI - red
            2: (255, 255, 255), # AI - white
            3: (255, 215, 0),   # AI - gold
            4: (139, 69, 19),   # AI - brown
            5: (255, 165, 0),   # AI - orange
            6: (180, 140, 230)  # AI - purple
        }

        for base in game.bases:
            base_x = offset_x + int(base.x * scale)
            base_y = offset_y + int(base.y * scale)
            color = base_colors.get(base.owner, (150, 150, 150))

            # Draw a small circle for the base
            radius = max(2, int(scale * 0.5))
            pygame.draw.circle(screen, color, (base_x, base_y), radius)
            pygame.draw.circle(screen, COLOR_BLACK, (base_x, base_y), radius, 1)

        # Draw viewport indicator - transparent white-bordered rectangle
        # showing the currently visible section of the map (with wrapping support)
        if renderer:
            visible_tiles_x = display.SCREEN_WIDTH // display.TILE_SIZE
            visible_tiles_y = display.MAP_AREA_HEIGHT // display.TILE_SIZE

            # Get camera position from renderer
            camera_x = renderer.camera_offset_x % map_width  # Wrap horizontally
            camera_y = renderer.camera_offset_y

            # Check if viewport wraps around the horizontal edge
            viewport_end_x = camera_x + visible_tiles_x
            wraps = viewport_end_x > map_width

            if wraps:
                # Draw two rectangles: one from camera_x to map edge, one from 0 to overflow
                # First rectangle: right portion
                viewport_map_w1 = map_width - camera_x
                viewport_map_h = min(visible_tiles_y, map_height - camera_y)

                viewport_x1 = offset_x + int(camera_x * scale)
                viewport_y1 = offset_y + int(camera_y * scale)
                viewport_w1 = int(viewport_map_w1 * scale)
                viewport_h1 = int(viewport_map_h * scale)

                if viewport_w1 > 0 and viewport_h1 > 0:
                    viewport_rect1 = pygame.Rect(viewport_x1, viewport_y1, viewport_w1, viewport_h1)
                    viewport_surface1 = pygame.Surface((viewport_w1, viewport_h1), pygame.SRCALPHA)
                    viewport_surface1.fill((255, 255, 255, 50))
                    screen.blit(viewport_surface1, (viewport_x1, viewport_y1))
                    pygame.draw.rect(screen, (255, 255, 255), viewport_rect1, 2)

                # Second rectangle: left portion (wrapped)
                viewport_map_w2 = viewport_end_x - map_width
                viewport_x2 = offset_x
                viewport_y2 = offset_y + int(camera_y * scale)
                viewport_w2 = int(viewport_map_w2 * scale)
                viewport_h2 = int(viewport_map_h * scale)

                if viewport_w2 > 0 and viewport_h2 > 0:
                    viewport_rect2 = pygame.Rect(viewport_x2, viewport_y2, viewport_w2, viewport_h2)
                    viewport_surface2 = pygame.Surface((viewport_w2, viewport_h2), pygame.SRCALPHA)
                    viewport_surface2.fill((255, 255, 255, 50))
                    screen.blit(viewport_surface2, (viewport_x2, viewport_y2))
                    pygame.draw.rect(screen, (255, 255, 255), viewport_rect2, 2)
            else:
                # No wrapping - draw single rectangle
                viewport_map_x = camera_x
                viewport_map_y = camera_y
                viewport_map_w = min(visible_tiles_x, map_width - camera_x)
                viewport_map_h = min(visible_tiles_y, map_height - camera_y)

                viewport_x = offset_x + int(viewport_map_x * scale)
                viewport_y = offset_y + int(viewport_map_y * scale)
                viewport_w = int(viewport_map_w * scale)
                viewport_h = int(viewport_map_h * scale)

                if viewport_w > 0 and viewport_h > 0:
                    viewport_rect = pygame.Rect(viewport_x, viewport_y, viewport_w, viewport_h)
                    viewport_surface = pygame.Surface((viewport_w, viewport_h), pygame.SRCALPHA)
                    viewport_surface.fill((255, 255, 255, 50))
                    screen.blit(viewport_surface, (viewport_x, viewport_y))
                    pygame.draw.rect(screen, (255, 255, 255), viewport_rect, 2)

    def _draw_upkeep_event(self, screen, game):
        """Draw upkeep event popup with message and action buttons."""
        event = game.get_current_upkeep_event()
        if not event:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Event popup box
        box_w, box_h = 600, 300
        box_x = display.SCREEN_WIDTH // 2 - box_w // 2
        box_y = display.SCREEN_HEIGHT // 2 - box_h // 2

        # Draw box
        pygame.draw.rect(screen, (40, 45, 50), (box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(screen, (100, 180, 220), (box_x, box_y, box_w, box_h), 4, border_radius=10)

        # Event title based on type
        title_text = "UPKEEP REPORT"
        if event['type'] == 'tech_complete':
            title_text = "TECHNOLOGY BREAKTHROUGH"
            title_color = (100, 255, 100)
        elif event['type'] == 'all_contacts':
            title_text = "DIPLOMATIC MILESTONE"
            title_color = (100, 200, 255)
        elif event['type'] == 'drone_riot':
            title_text = "CIVIL UNREST"
            title_color = (255, 100, 100)
        elif event['type'] == 'starvation':
            title_text = "FOOD SHORTAGE"
            title_color = (255, 180, 100)
        elif event['type'] == 'ai_council':
            title_text = "PLANETARY COUNCIL VOTE"
            title_color = (180, 200, 255)
        else:
            title_color = (200, 220, 240)

        title = self.font.render(title_text, True, title_color)
        screen.blit(title, (box_x + box_w // 2 - title.get_width() // 2, box_y + 20))

        # Event message
        message = event.get('message', 'Event occurred.')
        msg_lines = []

        if event['type'] == 'tech_complete':
            msg_lines = [
                f"Your researchers have discovered:",
                f"",
                f"{event['tech_name']}",
                f"",
                "New units and facilities may be available."
            ]
        elif event['type'] == 'all_contacts':
            msg_lines = [
                "You have established contact with",
                "all living factions on Planet!",
                "",
                "You may now call the Planetary Council",
                "to propose global resolutions."
            ]
        elif event['type'] == 'drone_riot':
            msg_lines = [
                message,
                "",
                "Production has halted due to civil unrest.",
                "Increase psych allocation or build facilities",
                "to restore order."
            ]
        elif event['type'] == 'ai_council':
            msg_lines = [
                f"The Planetary Council has voted on:",
                f"{event['proposal_name']}",
                "",
                "Voting Results:"
            ]
            # Add vote results
            for vote_entry in event.get('results', [])[:5]:  # Show first 5
                msg_lines.append(f"  {vote_entry['name']}: {vote_entry['vote']}")
        else:
            msg_lines = [message]

        y_offset = box_y + 80
        for line in msg_lines:
            line_surf = self.small_font.render(line, True, COLOR_TEXT)
            screen.blit(line_surf, (box_x + box_w // 2 - line_surf.get_width() // 2, y_offset))
            y_offset += 25

        # Buttons
        btn_y = box_y + box_h - 70
        btn_w, btn_h = 180, 50

        # Zoom to view button (if event has a location)
        if 'base' in event:
            zoom_x = box_x + box_w // 2 - btn_w - 10
            self.upkeep_zoom_rect = pygame.Rect(zoom_x, btn_y, btn_w, btn_h)
            is_hover = self.upkeep_zoom_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65),
                           self.upkeep_zoom_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 140, 160), self.upkeep_zoom_rect, 3, border_radius=8)
            zoom_text = self.font.render("Zoom to Base", True, COLOR_TEXT)
            screen.blit(zoom_text, (self.upkeep_zoom_rect.centerx - zoom_text.get_width() // 2,
                                   self.upkeep_zoom_rect.centery - 10))
        else:
            self.upkeep_zoom_rect = None

        # Ignore/Continue button
        ignore_x = box_x + box_w // 2 + 10 if self.upkeep_zoom_rect else box_x + box_w // 2 - btn_w // 2
        self.upkeep_ignore_rect = pygame.Rect(ignore_x, btn_y, btn_w, btn_h)
        is_hover = self.upkeep_ignore_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65),
                       self.upkeep_ignore_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), self.upkeep_ignore_rect, 3, border_radius=8)
        ignore_text = self.font.render("Continue", True, COLOR_TEXT)
        screen.blit(ignore_text, (self.upkeep_ignore_rect.centerx - ignore_text.get_width() // 2,
                                 self.upkeep_ignore_rect.centery - 10))

    def _draw_commlink_request(self, screen, game):
        """Draw commlink request popup when AI wants to speak."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        box_w, box_h = 600, 250
        box_x = display.SCREEN_WIDTH // 2 - box_w // 2
        box_y = display.SCREEN_HEIGHT // 2 - box_h // 2

        pygame.draw.rect(screen, (30, 40, 50), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, (100, 140, 160), (box_x, box_y, box_w, box_h), 3, border_radius=12)

        # Get faction info
        if self.commlink_request_other_faction_id < len(FACTION_DATA):
            faction = FACTION_DATA[self.commlink_request_other_faction_id]
            faction_name = faction["leader"]

            # Title
            title_text = f"{faction_name} is requesting to speak with you"
            title_surf = self.font.render(title_text, True, (180, 220, 240))
            screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))

            # Message
            msg_text = "A representative wishes to open communications."
            msg_surf = self.small_font.render(msg_text, True, COLOR_TEXT)
            screen.blit(msg_surf, (box_x + box_w // 2 - msg_surf.get_width() // 2, box_y + 100))

        # Buttons
        btn_w, btn_h = 180, 50
        btn_y = box_y + box_h - 80

        # Answer button
        answer_x = box_x + box_w // 2 - btn_w - 10
        self.commlink_request_answer_rect = pygame.Rect(answer_x, btn_y, btn_w, btn_h)
        is_hover = self.commlink_request_answer_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (65, 100, 85) if is_hover else (45, 75, 65),
                       self.commlink_request_answer_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 180, 140), self.commlink_request_answer_rect, 3, border_radius=8)
        answer_text = self.font.render("Answer", True, COLOR_TEXT)
        screen.blit(answer_text, (self.commlink_request_answer_rect.centerx - answer_text.get_width() // 2,
                                 self.commlink_request_answer_rect.centery - 10))

        # Ignore button
        ignore_x = box_x + box_w // 2 + 10
        self.commlink_request_ignore_rect = pygame.Rect(ignore_x, btn_y, btn_w, btn_h)
        is_hover = self.commlink_request_ignore_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (100, 65, 65) if is_hover else (75, 45, 45),
                       self.commlink_request_ignore_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 100, 100), self.commlink_request_ignore_rect, 3, border_radius=8)
        ignore_text = self.font.render("Ignore", True, COLOR_TEXT)
        screen.blit(ignore_text, (self.commlink_request_ignore_rect.centerx - ignore_text.get_width() // 2,
                                 self.commlink_request_ignore_rect.centery - 10))

    def _draw_faction_elimination(self, screen, game):
        """Draw faction elimination notification popup."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        box_w, box_h = 600, 250
        box_x = display.SCREEN_WIDTH // 2 - box_w // 2
        box_y = display.SCREEN_HEIGHT // 2 - box_h // 2

        pygame.draw.rect(screen, (40, 30, 30), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, (180, 100, 100), (box_x, box_y, box_w, box_h), 3, border_radius=12)

        # Get faction info
        if self.elimination_faction_id < len(FACTION_DATA):
            faction = FACTION_DATA[self.elimination_faction_id]
            faction_name = faction["name"]
            leader_name = faction["leader"]

            # Title
            title_text = f"{faction_name} ELIMINATED"
            title_surf = self.font.render(title_text, True, (240, 180, 180))
            screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))

            # Message
            msg_text = f"{leader_name} has been defeated."
            msg_surf = self.small_font.render(msg_text, True, COLOR_TEXT)
            screen.blit(msg_surf, (box_x + box_w // 2 - msg_surf.get_width() // 2, box_y + 100))

            msg_text2 = "All bases have been destroyed."
            msg_surf2 = self.small_font.render(msg_text2, True, COLOR_TEXT)
            screen.blit(msg_surf2, (box_x + box_w // 2 - msg_surf2.get_width() // 2, box_y + 130))

        # OK button (centered)
        btn_w, btn_h = 180, 50
        btn_y = box_y + box_h - 80
        ok_x = box_x + box_w // 2 - btn_w // 2
        self.elimination_ok_rect = pygame.Rect(ok_x, btn_y, btn_w, btn_h)
        is_hover = self.elimination_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65),
                       self.elimination_ok_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), self.elimination_ok_rect, 3, border_radius=8)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.elimination_ok_rect.centerx - ok_text.get_width() // 2,
                             self.elimination_ok_rect.centery - 10))

    def _draw_new_designs_popup(self, screen, game):
        """Draw new unit designs available notification popup."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        box_w, box_h = 600, 250
        box_x = display.SCREEN_WIDTH // 2 - box_w // 2
        box_y = display.SCREEN_HEIGHT // 2 - box_h // 2

        pygame.draw.rect(screen, (30, 40, 50), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, (100, 180, 140), (box_x, box_y, box_w, box_h), 3, border_radius=12)

        # Title
        title_text = "NEW UNIT DESIGNS AVAILABLE"
        title_surf = self.font.render(title_text, True, (180, 240, 180))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))

        # Message
        msg_text = "New technology has unlocked improved unit designs."
        msg_surf = self.small_font.render(msg_text, True, COLOR_TEXT)
        screen.blit(msg_surf, (box_x + box_w // 2 - msg_surf.get_width() // 2, box_y + 100))

        msg_text2 = "Visit the Design Workshop to review them."
        msg_surf2 = self.small_font.render(msg_text2, True, COLOR_TEXT)
        screen.blit(msg_surf2, (box_x + box_w // 2 - msg_surf2.get_width() // 2, box_y + 130))

        # Buttons
        btn_w, btn_h = 180, 50
        btn_y = box_y + box_h - 80

        # View button
        view_x = box_x + box_w // 2 - btn_w - 10
        self.new_designs_view_rect = pygame.Rect(view_x, btn_y, btn_w, btn_h)
        is_hover = self.new_designs_view_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (65, 100, 85) if is_hover else (45, 75, 65),
                       self.new_designs_view_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 180, 140), self.new_designs_view_rect, 3, border_radius=8)
        view_text = self.font.render("View Designs", True, COLOR_TEXT)
        screen.blit(view_text, (self.new_designs_view_rect.centerx - view_text.get_width() // 2,
                               self.new_designs_view_rect.centery - 10))

        # Ignore button
        ignore_x = box_x + box_w // 2 + 10
        self.new_designs_ignore_rect = pygame.Rect(ignore_x, btn_y, btn_w, btn_h)
        is_hover = self.new_designs_ignore_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65),
                       self.new_designs_ignore_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), self.new_designs_ignore_rect, 3, border_radius=8)
        ignore_text = self.font.render("Ignore", True, COLOR_TEXT)
        screen.blit(ignore_text, (self.new_designs_ignore_rect.centerx - ignore_text.get_width() // 2,
                                 self.new_designs_ignore_rect.centery - 10))

    def _draw_break_treaty_popup(self, screen, game):
        """Draw popup asking player if they want to break a treaty."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        box_w, box_h = 600, 250
        box_x = display.SCREEN_WIDTH // 2 - box_w // 2
        box_y = display.SCREEN_HEIGHT // 2 - box_h // 2

        pygame.draw.rect(screen, (40, 30, 30), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, (220, 100, 100), (box_x, box_y, box_w, box_h), 3, border_radius=12)

        # Title - check if it's treaty or truce
        relation = self.diplomacy.diplo_relations.get(self.break_treaty_target_faction, "Uncommitted")
        if relation == "Truce":
            title_text = "BREAK TRUCE"
            relation_word = "truce"
        else:
            title_text = "BREAK TREATY"
            relation_word = "treaty"

        title_surf = self.font.render(title_text, True, (255, 150, 150))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))

        # Message
        faction_name = FACTION_DATA[self.break_treaty_target_faction]['name']
        msg_text = f"Are you sure you wish to attack {faction_name}?"
        msg_surf = self.small_font.render(msg_text, True, COLOR_TEXT)
        screen.blit(msg_surf, (box_x + box_w // 2 - msg_surf.get_width() // 2, box_y + 100))

        msg_text2 = f"This will break your {relation_word} and result in VENDETTA."
        msg_surf2 = self.small_font.render(msg_text2, True, (255, 200, 200))
        screen.blit(msg_surf2, (box_x + box_w // 2 - msg_surf2.get_width() // 2, box_y + 130))

        # Buttons
        btn_w, btn_h = 140, 50
        btn_y = box_y + box_h - 80

        # OK button
        ok_x = box_x + box_w // 2 - btn_w - 10
        self.break_treaty_ok_rect = pygame.Rect(ok_x, btn_y, btn_w, btn_h)
        is_hover = self.break_treaty_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (85, 60, 60) if is_hover else (65, 45, 45),
                       self.break_treaty_ok_rect, border_radius=8)
        pygame.draw.rect(screen, (220, 100, 100), self.break_treaty_ok_rect, 3, border_radius=8)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.break_treaty_ok_rect.centerx - ok_text.get_width() // 2,
                             self.break_treaty_ok_rect.centery - 10))

        # Cancel button
        cancel_x = box_x + box_w // 2 + 10
        self.break_treaty_cancel_rect = pygame.Rect(cancel_x, btn_y, btn_w, btn_h)
        is_hover = self.break_treaty_cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65),
                       self.break_treaty_cancel_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), self.break_treaty_cancel_rect, 3, border_radius=8)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_text, (self.break_treaty_cancel_rect.centerx - cancel_text.get_width() // 2,
                                 self.break_treaty_cancel_rect.centery - 10))

    def _draw_surprise_attack_popup(self, screen, game):
        """Draw popup notifying player that AI broke treaty."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        box_w, box_h = 600, 220
        box_x = display.SCREEN_WIDTH // 2 - box_w // 2
        box_y = display.SCREEN_HEIGHT // 2 - box_h // 2

        pygame.draw.rect(screen, (40, 30, 30), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, (220, 100, 100), (box_x, box_y, box_w, box_h), 3, border_radius=12)

        # Message
        faction_name = FACTION_DATA[self.surprise_attack_faction]['name']
        msg_text = f"{faction_name} has launched a surprise attack!"
        msg_surf = self.font.render(msg_text, True, (255, 150, 150))
        screen.blit(msg_surf, (box_x + box_w // 2 - msg_surf.get_width() // 2, box_y + 70))

        # OK button
        btn_w, btn_h = 140, 50
        btn_y = box_y + box_h - 80
        ok_x = box_x + box_w // 2 - btn_w // 2
        self.surprise_attack_ok_rect = pygame.Rect(ok_x, btn_y, btn_w, btn_h)
        is_hover = self.surprise_attack_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (85, 60, 60) if is_hover else (65, 45, 45),
                       self.surprise_attack_ok_rect, border_radius=8)
        pygame.draw.rect(screen, (220, 100, 100), self.surprise_attack_ok_rect, 3, border_radius=8)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.surprise_attack_ok_rect.centerx - ok_text.get_width() // 2,
                             self.surprise_attack_ok_rect.centery - 10))

    def _draw_pact_evacuation_popup(self, screen, game):
        """Draw popup notifying player of unit evacuation after pact ended."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        box_w, box_h = 700, 250
        box_x = display.SCREEN_WIDTH // 2 - box_w // 2
        box_y = display.SCREEN_HEIGHT // 2 - box_h // 2

        pygame.draw.rect(screen, (30, 40, 50), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, (100, 140, 180), (box_x, box_y, box_w, box_h), 3, border_radius=12)

        # Title
        title_text = "PACT DISSOLVED"
        title_surf = self.font.render(title_text, True, (200, 220, 255))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 30))

        # Message
        unit_word = "unit" if self.pact_evacuation_count == 1 else "units"
        msg_text = f"With the pact dissolved, {self.pact_evacuation_count} {unit_word}"
        msg_surf = self.small_font.render(msg_text, True, (180, 200, 220))
        screen.blit(msg_surf, (box_x + box_w // 2 - msg_surf.get_width() // 2, box_y + 85))

        msg_text2 = "returned to your nearest base."
        msg_surf2 = self.small_font.render(msg_text2, True, (180, 200, 220))
        screen.blit(msg_surf2, (box_x + box_w // 2 - msg_surf2.get_width() // 2, box_y + 115))

        # OK button
        btn_w, btn_h = 140, 50
        btn_y = box_y + box_h - 80
        ok_x = box_x + box_w // 2 - btn_w // 2
        self.pact_evacuation_ok_rect = pygame.Rect(ok_x, btn_y, btn_w, btn_h)
        is_hover = self.pact_evacuation_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if is_hover else (50, 70, 90),
                       self.pact_evacuation_ok_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 180), self.pact_evacuation_ok_rect, 3, border_radius=8)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.pact_evacuation_ok_rect.centerx - ok_text.get_width() // 2,
                             self.pact_evacuation_ok_rect.centery - 10))

    def _draw_game_over(self, screen, game):
        """Draw the game over screen with victory/defeat message and buttons."""
        from game.data.display import COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT

        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((10, 15, 20))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 600, 400
        dialog_x = display.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2
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
        panel_y = display.UI_PANEL_Y + 145  # Below battle panel (battle panel is 130px + 10px offset + 5px gap)

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

            #TODO: Examine this entire function. Code smell.
            # Determine unit color
            # if unit.owner == game.player_id:
            #     unit_color = COLOR_UNIT_FRIENDLY
            # else:
            #     unit_color = COLOR_UNIT_ENEMY

            unit_color = (255, 255, 255) #temp code

            # Highlight selected unit
            if unit == game.selected_unit:
                pygame.draw.circle(screen, (255, 255, 0), (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2 + 3)

            # Draw unit circle
            pygame.draw.circle(screen, unit_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2)
            pygame.draw.circle(screen, COLOR_BLACK, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2, 1)

            # Draw unit type indicator (first letter of unit type)
            # Show 'C' for colony pods, 'A' for artifacts, otherwise first letter of type
            if unit.weapon == 'colony_pod':
                type_letter = 'C'
            elif unit.weapon == 'artifact':
                type_letter = 'A'
            else:
                type_letter = unit.type[0].upper()  # 'L', 'S', 'A'
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

    def show_base_naming_dialog(self, unit, game):
        """Show the base naming dialog for a colony pod."""
        self.base_screens.show_base_naming(unit, game)
        self.active_screen = "BASE_NAMING"

    def show_base_view(self, base):
        """Show the base management screen."""
        self.base_screens.show_base_view(base)
        self.active_screen = "BASE_VIEW"
