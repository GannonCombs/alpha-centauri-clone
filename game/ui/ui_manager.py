"""Main UI coordinator - replaces UIPanel."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_UI_BACKGROUND, COLOR_UI_BORDER, COLOR_TEXT,
                                 COLOR_BLACK, COLOR_BUTTON_BORDER)
from .components import Button
from .dialogs.supply_pod_dialog import SupplyPodDialog
from .dialogs.artifact_dialog import ArtifactEventDialog
from .dialogs.combat_dialog import CombatDialog
from .dialogs.save_load_dialog import SaveLoadDialog
from .dialogs.secret_project_dialog import SecretProjectDialog
from .dialogs.elimination_dialog import EliminationDialog
from .dialogs.new_designs_dialog import NewDesignsDialog
from .dialogs.treaty_dialog import BreakTreatyDialog, SurpriseAttackDialog
from .dialogs.artifact_link_dialog import ArtifactLinkDialog
from .dialogs.raze_base_dialog import RazeBaseDialog
from .dialogs.commlink_dialog import CommLinkRequestDialog
from .dialogs.unit_dialog import BusyFormerDialog, MovementOverflowDialog, DebarkDialog
from .dialogs.terraform_dialog import TerraformCostDialog
from .dialogs.pact_dialog import PactEvacuationDialog, PactPronounceDialog
from .dialogs.atrocity_dialog import MajorAtrocityDialog
from .dialogs.renounce_pact_dialog import RenouncePactDialog
from .dialogs.encroachment_dialog import EncroachmentDialog
from .dialogs.upkeep_dialog import UpkeepEventDialog
from .dialogs.probe_dialog import ProbeDialog
from .screens.diplomacy_screen import DiplomacyScreen
from .screens.council_screen import CouncilScreen
from .screens.social_engineering_screen import SocialEngineeringScreen
from .screens.tech_tree_screen import TechTreeScreen
from .screens.design_workshop_screen import DesignWorkshopScreen
from .screens.base_screen import BaseScreen
from .screens.secret_project_screen import SecretProjectScreen
from .screens.game_over_screen import GameOverScreen
from .context_menu import ContextMenu
from game.data.faction_data import FACTION_DATA
from game.map import tile_base_nutrients, tile_base_energy, tile_base_minerals


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
        self.game_submenu_open = False

        # Initialize all screen managers
        self.supply_pod_dialog = SupplyPodDialog(self.font, self.small_font)
        self.artifact_dialog = ArtifactEventDialog(self.font, self.small_font)
        self.probe_dialog = ProbeDialog(self.font, self.small_font)
        self.combat_dialog = CombatDialog(self.font, self.small_font)
        self.diplomacy = DiplomacyScreen(self.font, self.small_font, self.mono_font)
        self.council = CouncilScreen(self.font, self.small_font)
        self.social_engineering_screen = SocialEngineeringScreen(self.font, self.small_font)
        self.tech_tree_screen = TechTreeScreen(self.font, self.small_font)
        self.design_workshop_screen = DesignWorkshopScreen(self.font, self.small_font)
        self.base_screen = BaseScreen(self.font, self.small_font)
        self.secret_project_screen = SecretProjectScreen(self.font, self.small_font)
        self.secret_project_dialog = SecretProjectDialog(self.font, self.small_font)
        self.elimination_dialog = EliminationDialog(self.font, self.small_font)
        self.new_designs_dialog = NewDesignsDialog(self.font, self.small_font)
        self.break_treaty_dialog = BreakTreatyDialog(self.font, self.small_font)
        self.surprise_attack_dialog = SurpriseAttackDialog(self.font, self.small_font)
        self.artifact_link_dialog = ArtifactLinkDialog(self.font, self.small_font)
        self.raze_base_dialog = RazeBaseDialog(self.font, self.small_font)
        self.commlink_request_dialog = CommLinkRequestDialog(self.font, self.small_font)
        self.busy_former_dialog = BusyFormerDialog(self.font, self.small_font)
        self.movement_overflow_dialog = MovementOverflowDialog(self.font, self.small_font)
        self.debark_dialog = DebarkDialog(self.font, self.small_font)
        self.terraform_cost_dialog = TerraformCostDialog(self.font, self.small_font)
        self.pact_evacuation_dialog = PactEvacuationDialog(self.font, self.small_font)
        self.pact_pronounce_dialog = PactPronounceDialog(self.font, self.small_font)
        self.major_atrocity_dialog = MajorAtrocityDialog(self.font, self.small_font)
        self.save_load_dialog = SaveLoadDialog(self.font, self.small_font)
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

        self.game_over_screen = GameOverScreen(self.font, self.small_font)

        self.upkeep_dialog = UpkeepEventDialog(self.font, self.small_font)

        # Encroachment popup (founding base on enemy territory)
        self.encroachment_dialog = EncroachmentDialog(self.font, self.small_font)

        # Renounce Pact popup (player initiates pact renouncement from commlink right-click)
        self.renounce_pact_dialog = RenouncePactDialog(self.font, self.small_font)

        # Pact pronounce queue (managed here; dialog shows one at a time)
        self.pact_pronounce_queue = []   # List of {'pactbro_id': int, 'attacker_id': int}

        # Session flag: always select busy formers without asking
        self.always_select_busy_formers = False


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

        # "Game" drop-right submenu (opens when "Game" is clicked)
        submenu_w, submenu_h = 200, 50
        submenu_x = self.main_menu_rect.right  # flush against the right edge
        submenu_y = self.main_menu_rect.y + 5  # aligned with the Game button
        self.game_submenu_rect = pygame.Rect(submenu_x, submenu_y, submenu_w, submenu_h)
        self.game_submenu_buttons = [
            Button(self.game_submenu_rect.x + 5, self.game_submenu_rect.y + 5, submenu_w - 10, 40, "Resign"),
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
                           faction["$FULLNAME"],
                           faction["color"],
                           COLOR_BLACK)
                btn.faction_id = faction_id
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
            # Enter/Return advances upkeep popups and dismisses new-designs popup
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if game.upkeep_phase_active:
                    game.turns.advance_upkeep_event()
                    return True
                if self.new_designs_dialog.active:
                    self.new_designs_dialog.active = False
                    game.new_designs_available = False
                    return True
                if self.renounce_pact_dialog.active:
                    self._resolve_renounce_pact(game)
                    return True
                if self.pact_pronounce_dialog.active:
                    self.pact_pronounce_dialog.active = False
                    self._advance_pact_pronounce()
                    return True
                if self.major_atrocity_dialog.active:
                    self.major_atrocity_dialog.handle_click(pygame.mouse.get_pos(), game)
                    return True
                if self.raze_base_dialog.active:
                    self._execute_raze_base(game)
                    return True

            # Block all game keys while modal popups are open
            if (self.busy_former_dialog.active or self.terraform_cost_dialog.active
                    or self.movement_overflow_dialog.active):
                return True

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
                result = self.base_screen.handle_base_naming_event(event, game)
                if result == 'close':
                    if self.base_screen.viewing_base:
                        self.active_screen = "BASE_VIEW"
                    else:
                        self.active_screen = "GAME"
                return True

            # Handle text input for base view (hurry production popup)
            if self.active_screen == "BASE_VIEW":
                _viewing = self.base_screen.viewing_base
                _enemy_base = _viewing and _viewing.owner != game.player_faction_id
                # Check for C (Change production) hotkey
                if not _enemy_base and event.key == pygame.K_c and not self.base_screen.hurry_production_open and not self.base_screen.queue_management_open:
                    self.base_screen.production_selection_mode = "change"
                    self.base_screen.production_selection_open = True
                    if self.base_screen.viewing_base:
                        self.base_screen.selected_production_item = self.base_screen.viewing_base.current_production
                    return True
                # Check for H (Hurry production) hotkey
                elif not _enemy_base and event.key == pygame.K_h and not self.base_screen.production_selection_open and not self.base_screen.queue_management_open:
                    self.base_screen.hurry_production_open = True
                    self.base_screen.hurry_input = ""
                    return True

                if self.base_screen.handle_base_view_event(event, game):
                    return True

            if event.key == pygame.K_e:
                # Toggle Social Engineering screen
                if self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_engineering_screen.social_engineering_open = False
                    # Reset selections to revert unsaved changes
                    self.social_engineering_screen.se_selections = None
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "SOCIAL_ENGINEERING"
                    self.social_engineering_screen.social_engineering_open = True
                    # Reset selections to load current game state
                    self.social_engineering_screen.se_selections = None
                    return True

            if event.key == pygame.K_u:
                # Toggle Design Workshop screen
                if self.active_screen == "DESIGN_WORKSHOP":
                    self.active_screen = "GAME"
                    self.design_workshop_screen.design_workshop_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "DESIGN_WORKSHOP"
                    self.design_workshop_screen.design_workshop_open = True
                    # Reset editing panel state when opening
                    self.design_workshop_screen.dw_editing_panel = None
                    # Load first empty slot when opening
                    workshop = self.design_workshop_screen
                    faction_designs = game.factions[game.player_faction_id].designs
                    first_empty = faction_designs.find_first_empty_slot()
                    workshop._load_slot_into_editor(first_empty, game)
                    # Rebuild designs if new tech was discovered (manual call, no specific tech)
                    if game.designs_need_rebuild:
                        player_tech_tree = game.factions[game.player_faction_id].tech_tree
                        self.design_workshop_screen.rebuild_available_designs(player_tech_tree, game, None)
                        game.designs_need_rebuild = False
                    return True

            if event.key == pygame.K_F2:
                # Toggle Tech Tree screen
                if self.active_screen == "TECH_TREE":
                    self.active_screen = "GAME"
                    self.tech_tree_screen.tech_tree_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "TECH_TREE"
                    self.tech_tree_screen.tech_tree_open = True
                    return True

            if event.key == pygame.K_F5:
                # Toggle Secret Projects view
                if self.active_screen == "SECRET_PROJECTS":
                    self.active_screen = "GAME"
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "SECRET_PROJECTS"
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
                    self.tech_tree_screen.tech_tree_open = False
                    return True
                elif self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_engineering_screen.social_engineering_open = False
                    # Reset selections to revert unsaved changes
                    self.social_engineering_screen.se_selections = None
                    self.social_engineering_screen.se_confirm_dialog_open = False
                    return True
                elif self.active_screen == "SECRET_PROJECTS":
                    self.active_screen = "GAME"
                    return True
                elif self.active_screen == "DESIGN_WORKSHOP":
                    # Check if a component selection panel is open
                    if self.design_workshop_screen.dw_editing_panel is not None:
                        # Close the component panel, stay in design workshop
                        self.design_workshop_screen.dw_editing_panel = None
                        return True
                    else:
                        # No panel open, exit design workshop
                        self.active_screen = "GAME"
                        self.design_workshop_screen.design_workshop_open = False
                        return True
                elif self.active_screen == "BASE_VIEW":
                    self.active_screen = "GAME"
                    self.base_screen.viewing_base = None
                    return True
                elif self.active_screen != "GAME" or self.commlink_open or self.main_menu_open:
                    self.active_screen = "GAME"
                    self.commlink_open = False
                    self.main_menu_open = False
                    self.game_submenu_open = False
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
                    if game.supply_pod_tech_event:
                        game.upkeep_events = [game.supply_pod_tech_event]
                        game.supply_pod_tech_event = None
                        game.current_upkeep_event_index = 0
                        game.upkeep_phase_active = True
                        game.mid_turn_upkeep = True
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
            # Commlink panel: right-click faction button → pact options
            if self.commlink_open and self.active_screen == "GAME":
                pos = event.pos
                for btn in self.faction_buttons:
                    if btn.rect.collidepoint(pos):
                        # Find which faction this button belongs to
                        fid = next((f for f in game.faction_contacts
                                    if f != game.player_faction_id
                                    and f not in game.eliminated_factions
                                    and FACTION_DATA[f]['$FULLNAME'] == btn.text), None)
                        if fid is not None:
                            relation = self.diplomacy.diplo_relations.get(fid, 'Uncommitted')
                            options = []
                            if relation == 'Pact':
                                def _make_renounce(faction_id):
                                    def _do():
                                        self.renounce_pact_dialog.activate(faction_id)
                                        self.commlink_open = False
                                    return _do
                                options.append(('Renounce Pact', _make_renounce(fid)))
                            if options:
                                self.context_menu.show(pos[0], pos[1], options)
                                return True

            # Handle garrison context menu in base view (read-only for enemy bases)
            if self.active_screen == "BASE_VIEW":
                _vb = self.base_screen.viewing_base
                _is_enemy = _vb and _vb.owner != game.player_faction_id
                if not _is_enemy and self.base_screen.handle_base_view_right_click(event.pos, game):
                    return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle upkeep event popup (highest priority)
            if game.upkeep_phase_active:
                result = self.upkeep_dialog.handle_click(event.pos, game)
                if isinstance(result, tuple) and result[0] == 'zoom':
                    base = result[1]
                    if base:
                        game.center_camera_on_tile = (base.x, base.y)
                        self.show_base_view(base)
                return True

            # Commlink request buttons
            if self.commlink_request_dialog.active:
                result = self.commlink_request_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result == 'answer':
                    fid = self.commlink_request_dialog.other_faction_id
                    pid = self.commlink_request_dialog.player_id
                    self.active_screen = "DIPLOMACY"
                    if fid is not None and fid < len(FACTION_DATA):
                        self.diplomacy.open_diplomacy(FACTION_DATA[fid], pid, game)
                    self.diplomacy.diplo_stage = "greeting"
                return True

            # Faction elimination popup buttons
            if self.elimination_dialog.active:
                self.elimination_dialog.handle_click(pygame.mouse.get_pos(), game)
                return True

            # New designs popup buttons
            if self.new_designs_dialog.active:
                result = self.new_designs_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result == 'view':
                    self.active_screen = "DESIGN_WORKSHOP"
                    self.design_workshop_screen.dw_editing_panel = None
                return True

            # Break treaty popup buttons
            if self.break_treaty_dialog.active:
                result = self.break_treaty_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result == 'ok':
                    target_faction = self.break_treaty_dialog.target_faction
                    pending_battle = self.break_treaty_dialog.pending_battle
                    had_pact = self.diplomacy.diplo_relations.get(target_faction, "Uncommitted") == "Pact"

                    self.diplomacy.diplo_relations[target_faction] = "Vendetta"
                    game.truce_expiry_turns.pop(target_faction, None)

                    from game.atrocity import drop_integrity
                    drop_integrity(game)

                    if had_pact:
                        player_evacuated = game.evacuate_units_from_former_pact(game.player_faction_id, target_faction)
                        game.evacuate_units_from_former_pact(target_faction, game.player_faction_id)

                        if player_evacuated > 0:
                            self.pact_evacuation_dialog.activate(player_evacuated, pending_battle)
                        else:
                            if pending_battle:
                                game.combat.pending_battle = pending_battle
                    else:
                        if pending_battle:
                            game.combat.pending_battle = pending_battle
                    self.break_treaty_dialog.pending_battle = None
                    self.break_treaty_dialog.target_faction = None
                return True

            # Pact evacuation popup button
            if self.pact_evacuation_dialog.active:
                self.pact_evacuation_dialog.handle_click(event.pos, game)
                return True

            # Renounce Pact popup
            if self.renounce_pact_dialog.active:
                result = self.renounce_pact_dialog.handle_click(event.pos, game)
                if result:
                    self._resolve_renounce_pact(game)
                return True

            # Pact pronounce popup (pact partner reacts to surprise attack)
            if self.pact_pronounce_dialog.active:
                result = self.pact_pronounce_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result:
                    self._advance_pact_pronounce()
                return True

            # Major atrocity popup (planet buster — all factions declare vendetta)
            if self.major_atrocity_dialog.active:
                self.major_atrocity_dialog.handle_click(pygame.mouse.get_pos(), game)
                return True

            # Raze base popup
            if self.raze_base_dialog.active:
                result = self.raze_base_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result == 'raze':
                    self._execute_raze_base(game)
                return True

            # Secret project started notification popup
            if getattr(game, 'secret_project_notifications', []):
                self.secret_project_dialog.handle_click(pygame.mouse.get_pos(), game)
                return True

            # Debark popup — unload a unit from a transport onto an adjacent land tile
            if self.debark_dialog.active:
                result = self.debark_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result == 'ok':
                    if self.debark_dialog.selected_unit is not None:
                        game.movement.unload_unit_from_transport(
                            self.debark_dialog.transport,
                            self.debark_dialog.selected_unit,
                            self.debark_dialog.target_x,
                            self.debark_dialog.target_y,
                        )
                    self.debark_dialog.transport = None
                    self.debark_dialog.selected_unit = None
                    self.debark_dialog.unit_rects = []
                elif result == 'cancel':
                    self.debark_dialog.transport = None
                    self.debark_dialog.selected_unit = None
                    self.debark_dialog.unit_rects = []
                return True

            # Encroachment popup — founding base on enemy territory
            if self.encroachment_dialog.active:
                result = self.encroachment_dialog.handle_click(event.pos, game)
                if result == 'build':
                    faction_id = self.encroachment_dialog.faction_id
                    unit = self.encroachment_dialog.unit
                    self.encroachment_dialog.faction_id = None
                    self.encroachment_dialog.unit = None
                    if faction_id is not None:
                        if self.diplomacy.diplo_relations.get(faction_id) != "Vendetta":
                            self.diplomacy.diplo_relations[faction_id] = "Vendetta"
                        game.integrity_level = max(0, game.integrity_level - 1)
                    if unit is not None:
                        self.show_base_naming_dialog(unit, game)
                return True

            # Surprise attack popup button
            if self.surprise_attack_dialog.active:
                result = self.surprise_attack_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result:
                    faction = self.surprise_attack_dialog.faction
                    self.diplomacy.diplo_relations[faction] = "Vendetta"
                    self._queue_pact_pronounce_popups(faction, game)
                    self.surprise_attack_dialog.faction = None
                return True

            # Artifact + Network Node link popup
            if self.artifact_link_dialog.active:
                result = self.artifact_link_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result == 'yes':
                    link = game.pending_artifact_link
                    if link:
                        import random
                        tech_tree = game.tech.get_faction_tree(game.player_faction_id)
                        researchable = tech_tree.get_researchable_techs()
                        if researchable:
                            tech_id = random.choice(researchable)
                            tech_name = tech_tree.technologies[tech_id]['name']
                            tech_tree.technologies[tech_id]['researched'] = True
                            tech_tree.researched_techs.add(tech_id)
                            if tech_tree.current_research == tech_id:
                                tech_tree.current_research = None
                                tech_tree.research_points = 0
                            game._auto_generate_unit_designs(tech_id)
                            game.upkeep_events.append({'type': 'tech_complete', 'tech_id': tech_id, 'tech_name': tech_name})
                        link['base'].network_node_linked = True
                        if link['artifact'] in game.units:
                            game._remove_unit(link['artifact'])
                        game.set_status_message("Artifact linked! Technology breakthrough achieved!")
                    game.pending_artifact_link = None
                return True  # Block clicks through popup (covers both 'yes' and 'no')

            # Movement overflow popup
            if self.movement_overflow_dialog.active:
                self.movement_overflow_dialog.handle_click(pygame.mouse.get_pos(), game)
                return True

            # Terrain cost confirmation popup (raise/lower land)
            if self.terraform_cost_dialog.active:
                result = self.terraform_cost_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result == 'approve':
                    pending = game.pending_terraform_cost
                    if pending and game.energy_credits >= pending['cost']:
                        game.energy_credits -= pending['cost']
                        from game.terraforming import start_terraforming
                        from game.data.terraforming_data import IMPROVEMENTS
                        start_terraforming(pending['unit'], pending['action'], game)
                        imp_name = IMPROVEMENTS[pending['action']]['name']
                        turns = pending['unit'].terraforming_turns_left
                        game.set_status_message(f"{pending['unit'].name}: {imp_name} ({turns} turns)")
                    elif pending:
                        game.set_status_message(f"Not enough energy. Need {pending['cost']} credits.")
                    game.pending_terraform_cost = None
                return True

            # Busy former popup buttons
            if self.busy_former_dialog.active:
                result = self.busy_former_dialog.handle_click(pygame.mouse.get_pos(), game)
                if result in ('select', 'always'):
                    if result == 'always':
                        self.always_select_busy_formers = True
                        game._always_select_busy_formers = True
                    unit = self.busy_former_dialog.unit
                    if unit:
                        from game.terraforming import cancel_terraforming
                        cancel_terraforming(unit)
                        game._select_unit(unit)
                        game.center_camera_on_tile = (unit.x, unit.y)
                    self.busy_former_dialog.unit = None
                elif result == 'ignore':
                    self.busy_former_dialog.unit = None
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
                result = self.game_over_screen.handle_click(event.pos, game)
                if result == 'return_to_menu':
                    return ('return_to_menu', None)
                elif result == 'new_game':
                    game.new_game()
                    self.active_screen = "GAME"
                    self.commlink_open = False
                    self.main_menu_open = False
                    self.game_submenu_open = False
                elif result == 'exit':
                    import sys
                    pygame.quit()
                    sys.exit()
                return True  # Consume all clicks when game over

            # Battle prediction takes highest priority
            if game.combat.pending_battle:
                result = self.combat_dialog.handle_battle_prediction_click(event.pos)
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
            if game.supply_pod_message and not self.commlink_request_dialog.active and self.active_screen != "DIPLOMACY":
                self.supply_pod_dialog.handle_click(event.pos, game)
                return True

            # Artifact event message (theft, capture, destruction)
            if game.artifact_message:
                self.artifact_dialog.handle_click(event.pos, game)
                return True

            # Probe team action dialog
            if game.pending_probe_action:
                self.probe_dialog.handle_click(event.pos, game)
                return True

            if self.active_screen == "SECRET_PROJECTS":
                if self.secret_project_screen.handle_click(event.pos) == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "TECH_TREE":
                result = self.tech_tree_screen.handle_tech_tree_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "SOCIAL_ENGINEERING":
                result = self.social_engineering_screen.handle_social_engineering_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "DESIGN_WORKSHOP":
                result = self.design_workshop_screen.handle_design_workshop_click(event.pos, game)
                if result == 'close':
                    self.active_screen = "GAME"
                return True
            elif self.active_screen == "BASE_VIEW":
                _vb = self.base_screen.viewing_base
                _is_enemy = bool(_vb and _vb.owner != game.player_faction_id)
                result = self.base_screen.handle_base_view_click(event.pos, game, is_enemy=_is_enemy)
                if result == 'close':
                    self.active_screen = "GAME"
                elif result == 'rename':
                    self.active_screen = "BASE_NAMING"
                return True
            elif self.active_screen == "BASE_NAMING":
                result = self.base_screen.handle_base_naming_click(event.pos, game)
                if result == 'close':
                    # Return to base view if we were renaming, otherwise back to game
                    if self.base_screen.viewing_base:
                        self.active_screen = "BASE_VIEW"
                    else:
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
                    self.game_submenu_open = False
                return True

            # Handle clicks inside Main Menu (and its Game submenu)
            if self.main_menu_open:
                # Check Game submenu first (it's layered on top)
                if self.game_submenu_open and self.game_submenu_rect.collidepoint(event.pos):
                    for btn in self.game_submenu_buttons:
                        if btn.handle_event(event):
                            if btn.text == "Resign":
                                self.main_menu_open = False
                                self.game_submenu_open = False
                                game.game_over = True
                                game.victory_type = None
                                game.resigned = True
                            return True
                    return True  # Consume click inside submenu
                elif self.main_menu_rect.collidepoint(event.pos):
                    for btn in self.main_menu_buttons:
                        if btn.handle_event(event):
                            if btn.text == "Game":
                                self.game_submenu_open = not self.game_submenu_open
                            else:
                                self.main_menu_open = False
                                self.game_submenu_open = False
                            return True
                    return True  # Consume click inside menu
                else:
                    self.main_menu_open = False
                    self.game_submenu_open = False

            # Handle clicks inside Commlink Menu
            if self.commlink_open:
                if self.commlink_menu_rect.collidepoint(event.pos):
                    for btn in self.faction_buttons:
                        if btn.handle_event(event):
                            # Get the faction for this player_id
                            faction_id = btn.faction_id
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
                if not game.combat.active_battle:
                    game.turns.end_turn()
                return True

        # 3. Mouse Button Up (for drag end)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Always end any scrollbar drag on mouse up, regardless of screen
            # This prevents the drag state from getting stuck
            if self.active_screen == "TECH_TREE":
                self.tech_tree_screen.handle_scrollbar_drag_end()
                # Don't return True here - let other handlers process the mouse up

        # 4. Mouse Wheel Scrolling
        if event.type == pygame.MOUSEWHEEL:
            # Handle scrolling in tech tree screen
            if self.active_screen == "TECH_TREE":
                self.tech_tree_screen.handle_tech_tree_scroll(event.y, game)
                return True

        # 5. Motion (Hover and Drag)
        if event.type == pygame.MOUSEMOTION:
            # Handle scrollbar drag in tech tree
            if self.active_screen == "TECH_TREE":
                if self.tech_tree_screen.handle_scrollbar_drag_motion(event.pos, game):
                    return True

            self.main_menu_button.handle_event(event)
            self.end_turn_button.handle_event(event)
            self.commlink_button.handle_event(event)
            if self.main_menu_open:
                for btn in self.main_menu_buttons:
                    btn.handle_event(event)
                if self.game_submenu_open:
                    for btn in self.game_submenu_buttons:
                        btn.handle_event(event)
            if self.commlink_open:
                for btn in self.faction_buttons:
                    btn.handle_event(event)
                self.council_btn.handle_event(event)

        return False

    def has_any_blocking_popup(self, game):
        """Return True if any modal popup or screen is currently blocking player turn flow.

        Single source of truth for auto-end-turn and auto-cycle blocking.
        Covers both dialog .active flags and game-state-gated dialogs.
        Adding a new blocking dialog requires ONE addition here only.
        """
        # --- Active non-game screens block auto-end ---
        if self.active_screen != "GAME":
            return True

        # --- Game-state-gated dialogs (no .active flag; gated by game field) ---
        if (game.supply_pod_message or
                game.supply_pod_tech_event or
                game.artifact_message or
                game.pending_probe_action or
                game.game_over):
            return True

        # --- Dialog .active flags ---
        return (self.commlink_request_dialog.active or
                self.commlink_open or
                self.elimination_dialog.active or
                self.new_designs_dialog.active or
                self.break_treaty_dialog.active or
                self.surprise_attack_dialog.active or
                self.artifact_link_dialog.active or
                self.pact_evacuation_dialog.active or
                self.busy_former_dialog.active or
                self.terraform_cost_dialog.active or
                self.movement_overflow_dialog.active or
                self.renounce_pact_dialog.active or
                self.pact_pronounce_dialog.active or
                self.major_atrocity_dialog.active or
                self.raze_base_dialog.active or
                self.encroachment_dialog.active or
                self.debark_dialog.active)

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

        # Integrity level
        from game.atrocity import get_integrity_label
        integrity_label = get_integrity_label(game)
        _INTEGRITY_COLORS = {
            'Noble':       (140, 210, 255),
            'Faithful':    (160, 220, 160),
            'Scrupulous':  (200, 220, 140),
            'Dependable':  (220, 200, 120),
            'Ruthless':    (220, 140,  80),
            'Treacherous': (220,  60,  60),
        }
        int_color = _INTEGRITY_COLORS.get(integrity_label, COLOR_TEXT)
        int_text = self.small_font.render(f"Integrity: {integrity_label}", True, int_color)
        screen.blit(int_text, (info_x, info_y + 36))

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

        # Unit info panel - left-center area (selected unit, or first unit at cursor tile)
        _cursor_unit = None
        if game.tile_cursor_mode and not game.selected_unit:
            _cursor_tile = game.game_map.get_tile(game.cursor_x, game.cursor_y)
            if _cursor_tile and _cursor_tile.units:
                _cursor_unit = _cursor_tile.units[0]
        if game.selected_unit or _cursor_unit:
            unit = game.selected_unit or _cursor_unit
            # Position left of battle panel
            info_x = 370
            info_y = display.UI_PANEL_Y + 20
            has_cargo = getattr(unit, 'transport_capacity', 0) > 0
            box_h = 155 if has_cargo else 135
            info_box = pygame.Rect(info_x - 10, info_y - 5, 280, box_h)
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
                _rem = unit.moves_remaining
                _rem_str = str(int(_rem)) if _rem == int(_rem) else f"{_rem:.2f}".rstrip('0')
                moves_text = self.small_font.render(f"Moves: {_rem_str}/{unit.max_moves()}", True, (200, 210, 220))
            screen.blit(moves_text, (info_x, info_y + 74))

            # Health percentage with color coding
            health_pct = unit.get_health_percentage()
            damage_percent_display = (unit.max_health - unit.current_health) * 100 // unit.max_health if unit.max_health > 0 else 0

            if damage_percent_display > 0:
                if health_pct >= 0.8:
                    health_color = (50, 255, 50)  # Green
                elif health_pct >= 0.5:
                    health_color = (255, 255, 50)  # Yellow
                else:
                    health_color = (255, 50, 50)  # Red

                health_text = self.small_font.render(f"Damage: {damage_percent_display}%", True, health_color)
                screen.blit(health_text, (info_x, info_y + 90))

            # Morale level
            morale_name = unit.get_morale_name()
            morale_text = self.small_font.render(f"Morale: {morale_name}", True, (150, 200, 255))
            screen.blit(morale_text, (info_x, info_y + 106))

            # Transport cargo (only for sea transports)
            if getattr(unit, 'transport_capacity', 0) > 0:
                cargo_count = len(getattr(unit, 'loaded_units', []))
                cargo_text = self.small_font.render(
                    f"Cargo: {cargo_count}/{unit.transport_capacity}", True, (160, 210, 160))
                screen.blit(cargo_text, (info_x, info_y + 122))

        # Terrain panel - far right of console
        # Show when a unit is selected OR when tile cursor mode is active
        _show_terrain = game.selected_unit or game.tile_cursor_mode
        if _show_terrain:
            terrain_x = 1080
            terrain_y = display.UI_PANEL_Y + 20
            terrain_box_w = 200
            terrain_box_h = 270
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
                        f"{rainfall_labels[tile.rainfall]}",
                        True, rainfall_colors[tile.rainfall])
                else:
                    rain_text = self.small_font.render("Rainfall: \u2014", True, (120, 150, 180))
                screen.blit(rain_text, (terrain_x, terrain_y + 46))

                # Rockiness (land: Flat/Rolling/Rocky; ocean: em dash)
                if tile.is_land():
                    rock_val = getattr(tile, 'rockiness', 0)
                    rock_labels = {0: "Flat", 1: "Rolling", 2: "Rocky"}
                    rock_colors = {0: (170, 180, 160), 1: (180, 160, 130), 2: (160, 140, 110)}
                    rock_text = self.small_font.render(
                        f"{rock_labels[rock_val]}",
                        True, rock_colors[rock_val])
                else:
                    rock_text = self.small_font.render("Rockiness: \u2014", True, (120, 150, 180))
                screen.blit(rock_text, (terrain_x, terrain_y + 62))

                # Elevation
                elev_text = self.small_font.render(f"Elev: {tile.altitude}m", True, (200, 200, 180))
                screen.blit(elev_text, (terrain_x, terrain_y + 78))

                # Nutrients (from rainfall for land; 1 for ocean)
                nutrients = tile_base_nutrients(tile)
                nut_text = self.small_font.render(f"Nutrients: {nutrients}", True, (150, 220, 150))
                screen.blit(nut_text, (terrain_x, terrain_y + 96))

                # Minerals (from rockiness for land; 0 for unimproved ocean)
                minerals = tile_base_minerals(tile)
                min_text = self.small_font.render(f"Minerals: {minerals}", True, (200, 180, 140))
                screen.blit(min_text, (terrain_x, terrain_y + 112))

                # Energy (from altitude band for land; 0 for unimproved ocean)
                energy = tile_base_energy(tile)
                ene_text = self.small_font.render(f"Energy: {energy}", True, (220, 220, 100))
                screen.blit(ene_text, (terrain_x, terrain_y + 128))

                # Terrain labels (Xenofungus, River, improvements) stacked from y+148
                _label_y = terrain_y + 148
                if getattr(tile, 'fungus', False):
                    xeno_text = self.small_font.render("Xenofungus", True, (255, 0, 200))
                    screen.blit(xeno_text, (terrain_x, _label_y))
                    _label_y += 16
                if getattr(tile, 'river_edges', None):
                    river_text = self.small_font.render("River", True, (100, 160, 220))
                    screen.blit(river_text, (terrain_x, _label_y))
                    _label_y += 16
                # Terrain improvements
                _IMP_NAMES = {
                    'farm': 'Farm', 'forest': 'Forest', 'mine': 'Mine',
                    'solar': 'Solar Collector', 'road': 'Road', 'mag_tube': 'Mag Tube',
                    'sensor_array': 'Sensor Array', 'borehole': 'Thermal Borehole',
                    'condenser': 'Condenser', 'echelon_mirror': 'Echelon Mirror',
                    'soil_enricher': 'Soil Enricher', 'bunker': 'Bunker',
                    'airbase': 'Air Base', 'kelp_farm': 'Kelp Farm',
                    'mining_platform': 'Mining Platform', 'tidal_harness': 'Tidal Harness',
                }
                _imp_labels = [
                    _IMP_NAMES.get(k, k.replace('_', ' ').title())
                    for k in sorted(getattr(tile, 'improvements', set()))
                    if k not in ('fungus', 'sea_fungus')
                ]
                if _imp_labels:
                    # Render comma-separated labels with line wrapping at ~175px
                    _imp_color = (180, 210, 160)
                    _max_w = 175
                    _full_text = ', '.join(_imp_labels)
                    # Word-wrap: split on ', ' boundaries
                    _tokens = _full_text.split(', ')
                    _current_line = ''
                    for _tok in _tokens:
                        _candidate = _tok if not _current_line else _current_line + ', ' + _tok
                        if self.small_font.size(_candidate)[0] <= _max_w:
                            _current_line = _candidate
                        else:
                            if _current_line:
                                screen.blit(self.small_font.render(_current_line, True, _imp_color),
                                            (terrain_x, _label_y))
                                _label_y += 14
                            _current_line = _tok
                    if _current_line:
                        screen.blit(self.small_font.render(_current_line, True, _imp_color),
                                    (terrain_x, _label_y))
                        _label_y += 14

        # Layer 4a: Main Menu Drop-up
        if self.main_menu_open and self.active_screen == "GAME":
            pygame.draw.rect(screen, (20, 25, 30), self.main_menu_rect)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.main_menu_rect, 3)
            for btn in self.main_menu_buttons:
                btn.draw(screen, self.font)

            # Game drop-right submenu
            if self.game_submenu_open:
                pygame.draw.rect(screen, (20, 25, 30), self.game_submenu_rect)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.game_submenu_rect, 3)
                for btn in self.game_submenu_buttons:
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
                    elif status == "Truce":
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
        if self.active_screen == "SECRET_PROJECTS":
            self.secret_project_screen.draw_secret_projects(screen, game)
        elif self.active_screen == "TECH_TREE":
            self.tech_tree_screen.draw_tech_tree(screen, game)
        elif self.active_screen == "SOCIAL_ENGINEERING":
            self.social_engineering_screen.draw_social_engineering(screen, game)
        elif self.active_screen == "DESIGN_WORKSHOP":
            self.design_workshop_screen.draw_design_workshop(screen, game)
        elif self.active_screen == "BASE_VIEW":
            self.base_screen.draw_base_view(screen, game)
        elif self.active_screen == "BASE_NAMING":
            if self.base_screen.rename_base_target:
                self.base_screen.draw_base_view(screen, game)
            self.base_screen.draw_base_naming(screen)
        elif self.active_screen == "DIPLOMACY":
            self.diplomacy.draw(screen)
        elif self.active_screen == "COUNCIL_VOTE":
            self.council.draw(screen, game)

        # Battle/info panel (always visible in game UI area)
        if self.active_screen == "GAME":
            self.combat_dialog.draw_battle_animation(screen, game)
            self._draw_unit_stack_panel(screen, game)

        # Supply pod message overlay (top priority, but not during diplomacy/commlink)
        # Don't show supply pod if we're in diplomacy or have a commlink request active
        if game.supply_pod_message and not self.commlink_request_dialog.active and self.active_screen != "DIPLOMACY":
            self.supply_pod_dialog.draw(screen, game)

        # Artifact event overlay (theft, capture, or destruction)
        if game.artifact_message:
            self.artifact_dialog.draw(screen, game)

        # Probe team action dialog
        if game.pending_probe_action:
            self.probe_dialog.draw(screen, game)

        # Check for treaty-breaking attacks (before battle prediction)
        if hasattr(game, 'pending_treaty_break') and game.pending_treaty_break and not self.break_treaty_dialog.active:
            attack_info = game.pending_treaty_break
            defender_faction = attack_info['defender'].owner
            relation = self.diplomacy.diplo_relations.get(defender_faction, "Uncommitted")

            if relation == "Pact":
                # Can't break pact by attacking
                game.set_status_message("You cannot attack your pact brother!")
                game.pending_treaty_break = None
            elif relation in ["Treaty", "Truce"]:
                # Show break treaty popup
                pending_battle = {
                    'attacker': attack_info['attacker'],
                    'defender': attack_info['defender'],
                    'target_x': attack_info['target_x'],
                    'target_y': attack_info['target_y']
                }
                self.break_treaty_dialog.activate(defender_faction, pending_battle, relation)
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
        if hasattr(game, 'pending_ai_attack') and game.pending_ai_attack and not self.surprise_attack_dialog.active:
            attack_info = game.pending_ai_attack
            ai_faction = attack_info['ai_faction']
            relation = self.diplomacy.diplo_relations.get(ai_faction, "Uncommitted")

            if relation in ["Treaty", "Truce", "Pact"]:
                # AI broke treaty - show surprise attack popup
                self.surprise_attack_dialog.activate(ai_faction)
            game.pending_ai_attack = None

        # Battle prediction overlay (highest priority)
        if game.combat.pending_battle:
            self.combat_dialog.draw_battle_prediction(screen, game)

        # Upkeep phase popup (high priority)
        if game.upkeep_phase_active:
            self.upkeep_dialog.draw(screen, game)

        # Artifact + Network Node link popup
        if game.pending_artifact_link and not self.artifact_link_dialog.active:
            self.artifact_link_dialog.activate()
        if self.artifact_link_dialog.active:
            self.artifact_link_dialog.draw(screen, game)

        # Busy former popup (player clicked a working former)
        if game.pending_busy_former and not self.busy_former_dialog.active:
            self.busy_former_dialog.activate(game.pending_busy_former)
            game.pending_busy_former = None
        if self.busy_former_dialog.active:
            self.busy_former_dialog.draw(screen, game)

        # Movement overflow popup
        if game.pending_movement_overflow_unit and not self.movement_overflow_dialog.active:
            self.movement_overflow_dialog.activate()
        if self.movement_overflow_dialog.active:
            self.movement_overflow_dialog.draw(screen, game)

        # Terrain cost confirmation popup
        if game.pending_terraform_cost and not self.terraform_cost_dialog.active:
            self.terraform_cost_dialog.activate()
        if self.terraform_cost_dialog.active:
            self.terraform_cost_dialog.draw(screen, game)

        # Check for pending commlink requests and show popup
        # Only activate next request if we're not in diplomacy (wait for screen to fully close)
        if not self.commlink_request_dialog.active and game.pending_commlink_requests and self.active_screen != "DIPLOMACY":
            request = game.pending_commlink_requests[0]
            self.commlink_request_dialog.activate(request['other_faction_id'], request['player_faction_id'])

        # Commlink request popup
        if self.commlink_request_dialog.active:
            self.commlink_request_dialog.draw(screen, game)

        # Check for pending faction eliminations and show popup
        if not self.elimination_dialog.active and game.pending_faction_eliminations:
            self.elimination_dialog.activate(game.pending_faction_eliminations[0])

        # Faction elimination popup
        if self.elimination_dialog.active:
            self.elimination_dialog.draw(screen, game)

        # Check for new designs available and show popup
        if not self.new_designs_dialog.active and game.new_designs_available:
            self.new_designs_dialog.activate()

        # New designs popup
        if self.new_designs_dialog.active:
            self.new_designs_dialog.draw(screen, game)

        # Treaty breaking popups
        if self.break_treaty_dialog.active:
            self.break_treaty_dialog.draw(screen, game)

        if self.surprise_attack_dialog.active:
            self.surprise_attack_dialog.draw(screen, game)

        if self.pact_evacuation_dialog.active:
            self.pact_evacuation_dialog.draw(screen, game)

        if self.renounce_pact_dialog.active:
            self.renounce_pact_dialog.draw(screen, game)

        if self.pact_pronounce_dialog.active:
            self.pact_pronounce_dialog.draw(screen, game)

        # Major atrocity popup (planet buster — all factions declare vendetta)
        if not self.major_atrocity_dialog.active and getattr(game, 'pending_major_atrocity_popup', False):
            self.major_atrocity_dialog.activate()

        if self.major_atrocity_dialog.active:
            self.major_atrocity_dialog.draw(screen, game)

        if self.raze_base_dialog.active:
            self.raze_base_dialog.draw(screen, game)

        if self.debark_dialog.active:
            self.debark_dialog.draw(screen, game)

        if self.encroachment_dialog.active:
            self.encroachment_dialog.draw(screen, game)

        if getattr(game, 'secret_project_notifications', []):
            self.secret_project_dialog.draw(screen, game)

        # Game over screen (highest priority)
        if game.game_over:
            self.game_over_screen.draw(screen, game)

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

    # ------------------------------------------------------------------
    # Pact renouncement helpers
    # ------------------------------------------------------------------

    def _resolve_renounce_pact(self, game):
        """Apply pact renouncement: drop to Treaty, evacuate units, close popup."""
        fid = self.renounce_pact_dialog.faction_id
        self.renounce_pact_dialog.active = False
        self.renounce_pact_dialog.faction_id = None
        if fid is None:
            return
        # Drop relation to Treaty
        self.diplomacy.diplo_relations[fid] = 'Treaty'
        # Renouncing a pact is breaking an agreement — integrity drops
        from game.atrocity import drop_integrity
        drop_integrity(game)
        # Evacuate units in each other's bases
        player_evac = game.evacuate_units_from_former_pact(game.player_faction_id, fid)
        game.evacuate_units_from_former_pact(fid, game.player_faction_id)
        if player_evac > 0:
            self.pact_evacuation_dialog.activate(player_evac)

    def _queue_pact_pronounce_popups(self, attacker_id, game):
        """Queue pact-pronounce popups for every current pact partner."""
        for fid, rel in self.diplomacy.diplo_relations.items():
            if rel == 'Pact' and fid != attacker_id:
                self.pact_pronounce_queue.append(
                    {'pactbro_id': fid, 'attacker_id': attacker_id}
                )
        self._advance_pact_pronounce()

    def _advance_pact_pronounce(self):
        """Show the next queued pact-pronounce popup, or close if queue empty."""
        self.pact_pronounce_dialog.active = False
        if self.pact_pronounce_queue:
            self.pact_pronounce_dialog.activate(self.pact_pronounce_queue.pop(0))

    def _execute_raze_base(self, game):
        """Destroy the base and apply atrocity consequences."""
        from game.atrocity import commit_atrocity
        base = self.raze_base_dialog.target
        if not base:
            self.raze_base_dialog.active = False
            return

        # Determine target faction (original owner if captured base)
        target_fid = None
        if base.original_owner != game.player_faction_id:
            target_fid = base.original_owner

        base_name = base.name

        # Remove the base from the map and game
        tile = game.game_map.get_tile(base.x, base.y)
        if tile:
            tile.base = None
        if base in game.bases:
            game.bases.remove(base)

        # Close base view if it was open
        if self.base_screen.viewing_base is base:
            self.base_screen.viewing_base = None

        game.territory.update_territory(game.bases)
        game.check_faction_elimination()
        game.check_victory()

        commit_atrocity(game, 'obliterate_base', target_faction_id=target_fid)

        sanction_turns = 10 * game.atrocity_count
        game.set_status_message(
            f"{base_name} razed. {sanction_turns}-turn commerce sanctions imposed."
        )

        self.raze_base_dialog.active = False
        self.raze_base_dialog.target = None

    def _draw_unit_stack_panel(self, screen, game):
        """Draw panel showing all units at the selected tile or cursor tile."""
        if game.tile_cursor_mode:
            tile = game.game_map.get_tile(game.cursor_x, game.cursor_y)
        elif game.selected_unit:
            tile = game.game_map.get_tile(game.selected_unit.x, game.selected_unit.y)
        else:
            return

        if not tile:
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
        if not units_to_show:
            empty_text = self.small_font.render("No units in tile", True, (120, 130, 140))
            screen.blit(empty_text, (panel_x + panel_w // 2 - empty_text.get_width() // 2, panel_y + 50))
            return
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

            unit_color = FACTION_DATA[unit.owner]['color'] if unit.owner < len(FACTION_DATA) else (255, 255, 255)

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
        self.base_screen.show_base_naming(unit, game)
        self.active_screen = "BASE_NAMING"

    def show_base_view(self, base):
        """Show the base management screen."""
        self.base_screen.show_base_view(base)
        self.active_screen = "BASE_VIEW"
