import pygame
import random
from constants import (COLOR_UI_BACKGROUND, COLOR_UI_BORDER, COLOR_BUTTON,
                       COLOR_BUTTON_HOVER, COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT,
                       COLOR_TEXT, COLOR_BLACK, COLOR_COUNCIL_BG, COLOR_COUNCIL_ACCENT,
                       COLOR_COUNCIL_BORDER, COLOR_COUNCIL_BOX, COLOR_BASE_FRIENDLY,
                       COLOR_BASE_BORDER, COLOR_UNIT_FRIENDLY, COLOR_UNIT_ENEMY, UNIT_SEA, UNIT_AIR)
import constants

# SMAC Factions
FACTIONS = [
    {"name": "Lady Deirdre Skye (Gaians)", "color": (50, 205, 50), "short": "Gaians", "votes": 45},
    {"name": "Chairman Yang (The Hive)", "color": (100, 100, 255), "short": "Hive", "votes": 78},
    {"name": "Provost Zakharov (University)", "color": (255, 255, 255), "short": "University", "votes": 52},
    {"name": "CEO Morgan (Morganites)", "color": (255, 215, 0), "short": "Morganites", "votes": 34},
    {"name": "Colonel Santiago (Spartans)", "color": (139, 69, 19), "short": "Spartans", "votes": 61},
    {"name": "Sister Miriam (Believers)", "color": (255, 165, 0), "short": "Believers", "votes": 28},
    {"name": "Commissioner Lal (Peacekeepers)", "color": (180, 140, 230), "short": "Peacekeepers", "votes": 89}
]

# Council Proposals
PROPOSALS = [
    {"id": "GOVERNOR", "name": "Elect Planetary Governor", "type": "candidate", "cooldown": 0},
    {"id": "SOLAR_SHADE", "name": "Launch Solar Shade", "desc": "(Sea levels drop)", "type": "yesno", "cooldown": 0},
    {"id": "ATROCITY", "name": "Remove Atrocity Prohibitions", "type": "yesno", "cooldown": 20, "last_voted": 1}
]

# Diplomacy conversation trees
DIPLOMACY_GREETINGS = [
    "Greetings. Our sensors indicate you wish to communicate. State your business.",
    "Ah, another transmission. I trust this will be more productive than our last exchange.",
    "You have reached my private channel. Make this brief.",
    "Welcome. Perhaps today we can find common ground where before there was only static."
]

DIPLOMACY_RESPONSES = [
    {"text": "Request pact of friendship", "next": "pact_request"},
    {"text": "Discuss technology exchange", "next": "tech_discuss"},
    {"text": "Propose trade agreement", "next": "trade_discuss"},
    {"text": "End transmission", "next": "exit"}
]


class Button:
    """Clickable UI button with hover effects and gradient shading."""

    def __init__(self, x, y, width, height, text, text_color=COLOR_TEXT, bg_color=None):
        """Initialize button with position, size, and appearance."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False
        self.text_color = text_color
        self.bg_color = bg_color or COLOR_BUTTON

    def handle_event(self, event):
        """Process mouse events for hover and click detection."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen, font):
        """Render button with gradient effects and text."""
        # Create gradient effect
        if self.hovered:
            base_color = COLOR_BUTTON_HOVER
            border_color = COLOR_BUTTON_HIGHLIGHT
            border_width = 3
        else:
            base_color = self.bg_color
            border_color = COLOR_BUTTON_BORDER
            border_width = 2

        # Draw main button rectangle
        pygame.draw.rect(screen, base_color, self.rect, border_radius=6)

        # Gradient shading effect - top highlight
        for i in range(self.rect.height // 3):
            alpha = int(30 * (1 - i / (self.rect.height // 3)))
            shade = self._lighten(base_color, alpha)
            highlight_rect = pygame.Rect(self.rect.x + 3, self.rect.y + i,
                                         self.rect.width - 6, 1)
            if i < 3:
                pygame.draw.rect(screen, shade, highlight_rect)

        # Bottom shadow
        shadow_start = self.rect.height * 2 // 3
        for i in range(shadow_start, self.rect.height - 3):
            alpha = int(20 * ((i - shadow_start) / (self.rect.height - shadow_start)))
            shade = self._darken(base_color, alpha)
            shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + i,
                                      self.rect.width - 6, 1)
            if i > self.rect.height - 6:
                pygame.draw.rect(screen, shade, shadow_rect)

        # Border
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=6)

        # Draw text with better handling for long text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Clip text if too wide
        if text_surface.get_width() > self.rect.width - 10:
            # Scale down font or clip
            text_rect.left = self.rect.left + 5

        screen.blit(text_surface, text_rect)

    def _lighten(self, color, amount):
        """Lighten an RGB color by adding to each channel."""
        return tuple(min(255, c + amount) for c in color)

    def _darken(self, color, amount):
        """Darken an RGB color by subtracting from each channel."""
        return tuple(max(0, c - amount) for c in color)


class UIPanel:
    """Main UI panel displaying game information and modal dialogs."""

    def __init__(self):
        """Initialize UI panel with fonts and layout state."""
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.mono_font = pygame.font.Font(None, 20)  # Console-like font

        # State
        self.active_screen = "GAME"
        self.target_faction = None
        self.commlink_open = False
        self.main_menu_open = False
        self.council_votes = []

        # Base naming state
        self.base_naming_unit = None
        self.base_name_input = ""
        self.base_name_suggestions = []

        # Base view state
        self.viewing_base = None

        # Social Engineering state
        self.social_engineering_open = False
        self.se_selections = {
            'Politics': 0,      # 0=Frontier, 1=Police State, 2=Democratic, 3=Fundamentalist
            'Economics': 0,     # 0=Simple, 1=Free Market, 2=Planned, 3=Green
            'Values': 0,        # 0=Survival, 1=Power, 2=Knowledge, 3=Wealth
            'Future Society': 0 # 0=None, 1=Cybernetic, 2=Eudaimonic, 3=Thought Control
        }

        self.design_workshop_open = False

        # Tech tree state
        self.tech_tree_open = False

        # Diplomacy state
        self.diplo_stage = "greeting"  # greeting, pact_request, tech_discuss, trade_discuss
        self.diplo_relations = {}  # faction_id -> status
        self.diplo_mood = "CORDIAL"  # CORDIAL, WARY, HOSTILE, FRIENDLY

        # Initialize relations (default to Truce for others)
        for i, f in enumerate(FACTIONS):
            if i == 0:
                continue  # Skip player
            status = random.choice(["Treaty", "Truce", "Informal Truce", "Vendetta"])
            self.diplo_relations[i] = status

        # Council state
        self.council_stage = "select_proposal"  # select_proposal, too_recent, voting, results
        self.selected_proposal = None
        self.player_vote = None
        self.proposal_history = {}  # {proposal_id: last_voted_turn}

        # Layout - will be initialized properly after screen size is known
        self.main_menu_button = None
        self.end_turn_button = None
        self.commlink_button = None
        self.minimap_rect = None
        self.main_menu_rect = None
        self.commlink_menu_rect = None
        self.faction_buttons = []
        self.council_btn = None

    def show_base_naming_dialog(self, unit):
        """Show the base naming dialog for a colony pod."""
        self.base_naming_unit = unit
        self.active_screen = "BASE_NAMING"
        self.base_name_suggestions = self._generate_base_names()
        self.base_name_input = random.choice(self.base_name_suggestions)

    def show_base_view(self, base):
        """Show the base management screen."""
        self.viewing_base = base
        self.active_screen = "BASE_VIEW"

    def _generate_base_names(self):
        """Generate random base name suggestions."""
        prefixes = ["New", "Fort", "Port", "Station", "Base", "Colony", "Outpost", "Settlement"]
        suffixes = ["Alpha", "Beta", "Gamma", "Delta", "Prime", "Omega", "Nexus", "Haven",
                    "Hope", "Unity", "Prosperity", "Liberty", "Freedom", "Victory", "Vanguard"]

        # SMAC-style names
        smac_names = ["Morgan Industries", "Gaia's Landing", "UN Headquarters", "Hive Territory",
                      "University Base", "Sparta Command", "Believer's Hope", "Data Haven",
                      "Solar Collective", "Merchant Exchange", "Research Station", "Psi Gate",
                      "Manifold Nexus", "Planetary Transit", "Ascent to Transcendence"]

        suggestions = []
        # Generate compound names
        for _ in range(3):
            suggestions.append(f"{random.choice(prefixes)} {random.choice(suffixes)}")

        # Add SMAC-style names
        suggestions.extend(random.sample(smac_names, min(2, len(smac_names))))

        return suggestions

    def _init_layout(self):
        """Initialize layout after screen dimensions are known"""
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
                if event.key == pygame.K_ESCAPE:
                    self.active_screen = "GAME"
                    self.base_naming_unit = None
                    self.base_name_input = ""
                    return True
                elif event.key == pygame.K_RETURN:
                    # Found the base with the entered name
                    if self.base_name_input.strip():
                        game.found_base(self.base_naming_unit, self.base_name_input.strip())
                        self.active_screen = "GAME"
                        self.base_naming_unit = None
                        self.base_name_input = ""
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.base_name_input = self.base_name_input[:-1]
                    return True
                else:
                    # Add character to input
                    if event.unicode and len(self.base_name_input) < 30:
                        self.base_name_input += event.unicode
                    return True

            if event.key == pygame.K_e:
                # Toggle Social Engineering screen
                if self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_engineering_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "SOCIAL_ENGINEERING"
                    self.social_engineering_open = True
                    return True

            if event.key == pygame.K_u:
                # Toggle Social Engineering screen
                if self.active_screen == "DESIGN_WORKSHOP":
                    self.active_screen = "GAME"
                    self.design_workshop_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "DESIGN_WORKSHOP"
                    self.design_workshop_open = True
                    return True

            if event.key == pygame.K_F2:
                # Toggle Tech Tree screen
                if self.active_screen == "TECH_TREE":
                    self.active_screen = "GAME"
                    self.tech_tree_open = False
                    return True
                elif self.active_screen == "GAME" and not self.commlink_open and not self.main_menu_open:
                    self.active_screen = "TECH_TREE"
                    self.tech_tree_open = True
                    return True

            if event.key == pygame.K_ESCAPE:
                if self.active_screen == "TECH_TREE":
                    self.active_screen = "GAME"
                    self.tech_tree_open = False
                    return True
                elif self.active_screen == "SOCIAL_ENGINEERING":
                    self.active_screen = "GAME"
                    self.social_engineering_open = False
                    return True
                elif self.active_screen == "DESIGN_WORKSHOP":
                    self.active_screen = "GAME"
                    self.design_workshop_open = False
                    return True
                elif self.active_screen == "BASE_VIEW":
                    self.active_screen = "GAME"
                    self.viewing_base = None
                    return True
                elif self.active_screen != "GAME" or self.commlink_open or self.main_menu_open:
                    self.active_screen = "GAME"
                    self.commlink_open = False
                    self.main_menu_open = False
                    self.diplo_stage = "greeting"
                    self.council_stage = "select_proposal"
                    self.selected_proposal = None
                    self.player_vote = None
                    return True
                else:
                    return False

            elif event.key == pygame.K_RETURN:
                if self.active_screen == "DIPLOMACY":
                    if self.diplo_stage == "exit":
                        self.active_screen = "GAME"
                        self.diplo_stage = "greeting"
                        return True
                elif self.active_screen == "COUNCIL_VOTE":
                    if self.council_stage == "too_recent":
                        self.council_stage = "select_proposal"
                        self.selected_proposal = None
                        return True
                    elif self.council_stage == "results":
                        self.active_screen = "GAME"
                        self.council_stage = "select_proposal"
                        self.selected_proposal = None
                        self.player_vote = None
                        return True
                return False

        # 2. Mouse Logic
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Battle prediction takes highest priority
            if game.pending_battle:
                if hasattr(self, 'battle_prediction_ok_rect') and self.battle_prediction_ok_rect.collidepoint(event.pos):
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
                elif hasattr(self, 'battle_prediction_cancel_rect') and self.battle_prediction_cancel_rect.collidepoint(event.pos):
                    # Cancel clicked - abort attack
                    game.pending_battle = None
                    return True
                # Block all other clicks when prediction is showing
                return True

            # Supply pod message takes priority
            if game.supply_pod_message:
                if hasattr(self, 'supply_pod_ok_rect') and self.supply_pod_ok_rect.collidepoint(event.pos):
                    game.supply_pod_message = None
                    return True
                # Block all other clicks when message is showing
                return True

            if self.active_screen == "TECH_TREE":
                self._handle_tech_tree_click(event.pos, game)
                return True
            elif self.active_screen == "SOCIAL_ENGINEERING":
                self._handle_social_engineering_click(event.pos, game)
                return True
            elif self.active_screen == "BASE_VIEW":
                self._handle_base_view_click(event.pos, game)
                return True
            elif self.active_screen == "BASE_NAMING":
                self._handle_base_naming_click(event.pos, game)
                return True
            elif self.active_screen == "DIPLOMACY":
                self._handle_diplomacy_click(event.pos)
                return True
            elif self.active_screen == "COUNCIL_VOTE":
                self._handle_council_click(event.pos, game)
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
                            self.target_faction = FACTIONS[i + 1]
                            self.active_screen = "DIPLOMACY"
                            self.diplo_stage = "greeting"
                            self.commlink_open = False
                            return True
                    if self.council_btn.handle_event(event):
                        self.active_screen = "COUNCIL_VOTE"
                        self.council_stage = "select_proposal"
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

        turn_text = self.font.render(f"Turn: {game.turn}", True, COLOR_TEXT)
        screen.blit(turn_text, (350, constants.UI_PANEL_Y + 25))

        # Show AI status if processing
        ai_status = game.get_ai_status_text()
        if ai_status:
            ai_text = self.font.render(ai_status, True, (255, 200, 100))
            screen.blit(ai_text, (350, constants.UI_PANEL_Y + 50))

        # Unit info
        if game.selected_unit:
            unit = game.selected_unit
            info_x, info_y = 550, constants.UI_PANEL_Y + 20
            info_box = pygame.Rect(info_x - 10, info_y - 5, 300, 110)
            pygame.draw.rect(screen, (35, 40, 45), info_box)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, info_box, 2)
            screen.blit(self.font.render(f"Unit: {unit.name}", True, COLOR_TEXT), (info_x, info_y))
            screen.blit(self.small_font.render(f"Type: {unit.unit_type}", True, (200, 210, 220)), (info_x, info_y + 30))
            # Stats: weapon-armor-moves*health
            stats_str = unit.get_stats_string()
            screen.blit(self.small_font.render(f"Stats: {stats_str}", True, (200, 210, 220)), (info_x, info_y + 52))
            screen.blit(self.small_font.render(f"Position: ({unit.x}, {unit.y})", True, (200, 210, 220)),
                        (info_x, info_y + 74))

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
            self._draw_tech_tree(screen, game)
        elif self.active_screen == "SOCIAL_ENGINEERING":
            self._draw_social_engineering(screen, game)
        elif self.active_screen == "BASE_VIEW":
            self._draw_base_view(screen, game)
        elif self.active_screen == "BASE_NAMING":
            self._draw_base_naming(screen)
        elif self.active_screen == "DIPLOMACY":
            self._draw_diplomacy(screen)
        elif self.active_screen == "COUNCIL_VOTE":
            if self.council_stage == "select_proposal":
                self._draw_council_selection(screen)
            elif self.council_stage == "too_recent":
                self._draw_council_too_recent(screen, game)
            elif self.council_stage == "voting":
                self._draw_council_voting(screen, game)
            elif self.council_stage == "results":
                self._draw_council_results(screen)

        # Battle animation panel (in game UI area)
        if game.active_battle and self.active_screen == "GAME":
            self._draw_battle_animation(screen, game)

        # Supply pod message overlay (top priority)
        if game.supply_pod_message:
            self._draw_supply_pod_message(screen, game)

        # Battle prediction overlay (highest priority)
        if game.pending_battle:
            self._draw_battle_prediction(screen, game)

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

    def _draw_diplomacy(self, screen):
        """Draw diplomacy screen with faction portrait and dialogue."""
        screen.fill((8, 12, 18))

        face_size = 200
        face_rect = pygame.Rect(60, 60, face_size, face_size)
        pygame.draw.rect(screen, (15, 20, 25), face_rect)
        pygame.draw.rect(screen, self.target_faction['color'], face_rect, 4)
        inner_face = pygame.Rect(face_rect.x + 8, face_rect.y + 8, face_rect.width - 16, face_rect.height - 16)
        pygame.draw.rect(screen, self.target_faction['color'], inner_face, 1)

        face_label = self.small_font.render("[PORTRAIT]", True, (100, 110, 120))
        screen.blit(face_label, (face_rect.centerx - face_label.get_width() // 2, face_rect.centery - 10))

        info_x = face_rect.right + 40
        info_y = face_rect.top
        info_panel = pygame.Rect(info_x - 10, info_y - 10, 500, 220)
        pygame.draw.rect(screen, (15, 22, 28), info_panel)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, info_panel, 2)

        name_surf = self.font.render(self.target_faction['name'], True, self.target_faction['color'])
        screen.blit(name_surf, (info_x, info_y))

        faction_id = next((i for i, f in enumerate(FACTIONS) if f['name'] == self.target_faction['name']), None)
        relation = self.diplo_relations.get(faction_id, "Truce")

        info_lines = [f"STATUS: {relation}", f"MOOD: {self.diplo_mood}",
                      f"COUNCIL VOTES: {self.target_faction.get('votes', 0)}"]
        for i, line in enumerate(info_lines):
            screen.blit(self.mono_font.render(line, True, (180, 200, 190)), (info_x, info_y + 45 + i * 32))

        msg_rect = pygame.Rect(60, 300, constants.SCREEN_WIDTH - 120, 150)
        pygame.draw.rect(screen, (12, 18, 22), msg_rect)
        pygame.draw.rect(screen, self.target_faction['color'], msg_rect, 3)

        if not hasattr(self, '_current_diplo_message') or self._last_diplo_stage != self.diplo_stage:
            if self.diplo_stage == "greeting":
                self._current_diplo_message = random.choice(DIPLOMACY_GREETINGS)
            elif self.diplo_stage == "pact_request":
                self._current_diplo_message = "A pact? Interesting. But trust must be earned."
            elif self.diplo_stage == "tech_discuss":
                self._current_diplo_message = "Our researchers guard their findings jealously."
            elif self.diplo_stage == "trade_discuss":
                self._current_diplo_message = "Trade routes could benefit us both."
            elif self.diplo_stage == "exit":
                self._current_diplo_message = "Very well. End transmission."
            self._last_diplo_stage = self.diplo_stage

        self._draw_wrapped_text(screen, self._current_diplo_message, msg_rect, self.font, (210, 230, 220))

        options_y = msg_rect.bottom + 40
        options = DIPLOMACY_RESPONSES if self.diplo_stage == "greeting" else ([{"text": "Return", "next": "greeting"},
                                                                               {"text": "End",
                                                                                "next": "exit"}] if self.diplo_stage != "exit" else [])

        self.diplo_option_rects = []
        for i, opt in enumerate(options):
            opt_rect = pygame.Rect(constants.SCREEN_WIDTH // 2 - 400, options_y + i * 60, 800, 50)
            self.diplo_option_rects.append((opt_rect, opt["next"]))
            is_hover = opt_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (50, 65, 75) if is_hover else (35, 45, 55), opt_rect)
            pygame.draw.rect(screen, self.target_faction['color'] if is_hover else COLOR_BUTTON_BORDER, opt_rect, 3)
            screen.blit(self.font.render(opt["text"], True, COLOR_TEXT), (opt_rect.x + 30, opt_rect.centery - 10))

        if self.diplo_stage == "exit":
            self.diplo_ok_rect = pygame.Rect(constants.SCREEN_WIDTH // 2 - 100, constants.SCREEN_HEIGHT - 100, 200, 55)
            is_hover = self.diplo_ok_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (50, 65, 75) if is_hover else (35, 45, 55), self.diplo_ok_rect)
            pygame.draw.rect(screen, self.target_faction['color'], self.diplo_ok_rect, 3)
            ok_t = self.font.render("OK", True, COLOR_TEXT)
            screen.blit(ok_t, (self.diplo_ok_rect.centerx - ok_t.get_width() // 2, self.diplo_ok_rect.centery - 10))

    def _draw_council_selection(self, screen):
        """Draw Planetary Council proposal selection screen."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (20, 40, 30), (0, 40, constants.SCREEN_WIDTH, 60))
        t = self.font.render("PLANETARY COUNCIL - SELECT PROPOSAL", True, COLOR_COUNCIL_ACCENT)
        screen.blit(t, (constants.SCREEN_WIDTH // 2 - t.get_width() // 2, 60))

        self.proposal_rects = []
        for i, prop in enumerate(PROPOSALS):
            rect = pygame.Rect(constants.SCREEN_WIDTH // 2 - 400, 150 + i * 90, 800, 75)
            self.proposal_rects.append((rect, prop))
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (35, 55, 45) if is_hover else COLOR_COUNCIL_BOX, rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_COUNCIL_BORDER if is_hover else COLOR_COUNCIL_ACCENT, rect, 3,
                             border_radius=8)
            screen.blit(self.font.render(prop["name"], True, COLOR_COUNCIL_ACCENT), (rect.x + 25, rect.y + 18))
            if "desc" in prop:
                screen.blit(self.small_font.render(prop["desc"], True, (180, 220, 200)), (rect.x + 25, rect.y + 45))

    def _draw_council_too_recent(self, screen, game):
        """Draw error screen when trying to vote on proposal in cooldown."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (40, 25, 25), (0, 180, constants.SCREEN_WIDTH, 60))
        t = self.font.render("PLANETARY COUNCIL - MOTION DENIED", True, (255, 140, 120))
        screen.blit(t, (constants.SCREEN_WIDTH // 2 - t.get_width() // 2, 200))

        box = pygame.Rect(constants.SCREEN_WIDTH // 2 - 350, 280, 700, 180)
        pygame.draw.rect(screen, COLOR_COUNCIL_BOX, box, border_radius=10)
        pygame.draw.rect(screen, (255, 140, 120), box, 3, border_radius=10)

        rem = max(0, self.selected_proposal['cooldown'] - (game.turn - self.selected_proposal.get('last_voted', 0)))
        msgs = [f"Motion '{self.selected_proposal['name']}' was recent.",
                f"Cooldown: {self.selected_proposal['cooldown']} turns.", f"Remaining: {rem}"]
        for i, m in enumerate(msgs):
            s = self.font.render(m, True, COLOR_TEXT)
            screen.blit(s, (constants.SCREEN_WIDTH // 2 - s.get_width() // 2, 310 + i * 40))

        self.council_too_recent_ok_rect = pygame.Rect(constants.SCREEN_WIDTH // 2 - 80, constants.SCREEN_HEIGHT - 120,
                                                      160, 50)
        pygame.draw.rect(screen, (40, 30, 25), self.council_too_recent_ok_rect, border_radius=8)
        ok_t = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_t, (self.council_too_recent_ok_rect.centerx - ok_t.get_width() // 2,
                           self.council_too_recent_ok_rect.centery - 10))

    def _draw_council_voting(self, screen, game):
        """Draw voting interface for selected council proposal."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (20, 40, 30), (0, 20, constants.SCREEN_WIDTH, 60))
        t = self.font.render(f"COUNCIL - {self.selected_proposal['name'].upper()}", True, COLOR_COUNCIL_ACCENT)
        screen.blit(t, (constants.SCREEN_WIDTH // 2 - t.get_width() // 2, 40))

        box_w, box_h = 180, 100
        start_x = constants.SCREEN_WIDTH // 2 - (4 * box_w + 3 * 20) // 2
        for i, f in enumerate(FACTIONS):
            x = start_x + (i % 4) * (box_w + 20)
            y = 120 + (i // 4) * (box_h + 25)
            rect = pygame.Rect(x, y, box_w, box_h)
            pygame.draw.rect(screen, COLOR_COUNCIL_BOX, rect, border_radius=6)
            pygame.draw.rect(screen, f['color'], rect, 3, border_radius=6)
            screen.blit(self.small_font.render(f['short'], True, f['color']), (x + 68, y + 12))

        vote_y = 400
        if not self.player_vote:
            self.vote_option_rects = []
            opts = ["YES", "NO", "ABSTAIN"] if self.selected_proposal['type'] == 'yesno' else self._get_top_candidates()
            for i, opt in enumerate(opts):
                rect = pygame.Rect(constants.SCREEN_WIDTH // 2 - (len(opts) * 100) + i * 210, vote_y, 180, 55)
                self.vote_option_rects.append((rect, opt))
                pygame.draw.rect(screen, (25, 50, 35), rect, border_radius=8)
                txt = self.font.render(opt, True, COLOR_TEXT)
                screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - 10))
        else:
            self._show_vote_tally(screen, vote_y)

    def _draw_council_results(self, screen):
        """Draw final voting results with all faction votes tallied."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (20, 40, 30), (0, 20, constants.SCREEN_WIDTH, 60))
        t = self.font.render("COUNCIL VOTE - RESULTS", True, COLOR_COUNCIL_ACCENT)
        screen.blit(t, (constants.SCREEN_WIDTH // 2 - t.get_width() // 2, 40))

        for i, entry in enumerate(self.council_votes):
            x = constants.SCREEN_WIDTH // 2 + (-400 if i < 4 else 50)
            y = 160 + (i % 4) * 40
            rect = pygame.Rect(x, y - 5, 400, 35)
            pygame.draw.rect(screen, COLOR_COUNCIL_BOX, rect, border_radius=5)
            pygame.draw.rect(screen, entry["color"], rect, 2, border_radius=5)
            screen.blit(self.small_font.render(f"{entry['name']} → {entry['vote']}", True, entry["color"]), (x + 10, y))

        self.council_ok_rect = pygame.Rect(constants.SCREEN_WIDTH // 2 - 80, constants.SCREEN_HEIGHT - 80, 160, 50)
        pygame.draw.rect(screen, (25, 50, 35), self.council_ok_rect, border_radius=8)
        ok_t = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_t, (self.council_ok_rect.centerx - ok_t.get_width() // 2, self.council_ok_rect.centery - 10))

    def _show_vote_tally(self, screen, y):
        """Display player's vote and calculating message."""
        screen.blit(self.font.render(f"You voted: {self.player_vote}", True, (0, 255, 255)), (50, y))
        screen.blit(self.small_font.render("Calculating results...", True, (100, 150, 100)), (50, y + 40))

    def _generate_ai_votes(self):
        """Generate random votes for all AI factions."""
        self.council_votes = []
        is_yesno = self.selected_proposal['type'] == 'yesno'
        opts = ["YES", "NO", "ABSTAIN"] if is_yesno else self._get_top_candidates()
        for f in FACTIONS[1:]:
            v = random.choice(opts)
            self.council_votes.append(
                {"name": f["name"].split('(')[0].strip(), "color": f["color"], "vote": v, "votes": f["votes"]})

    def _get_top_candidates(self):
        """Get top two faction candidates for leader elections."""
        sorted_f = sorted(FACTIONS, key=lambda x: x['votes'], reverse=True)
        return [sorted_f[0]['short'], sorted_f[1]['short']]

    def _handle_diplomacy_click(self, pos):
        """Process clicks on diplomacy screen buttons and options."""
        if hasattr(self, 'diplo_ok_rect') and self.diplo_ok_rect and self.diplo_ok_rect.collidepoint(pos):
            self.active_screen, self.diplo_stage = "GAME", "greeting"
        if hasattr(self, 'diplo_option_rects'):
            for rect, next_s in self.diplo_option_rects:
                if rect.collidepoint(pos): self.diplo_stage = next_s

    def _handle_council_click(self, pos, game):
        """Process clicks on Planetary Council interface."""
        if self.council_stage == "select_proposal":
            for rect, prop in self.proposal_rects:
                if rect.collidepoint(pos):
                    self.selected_proposal = prop
                    self.council_stage = "voting" if game.turn - prop.get('last_voted', -99) >= prop[
                        'cooldown'] else "too_recent"
                    if self.council_stage == "voting": self._generate_ai_votes()
        elif self.council_stage in ["too_recent", "results"]:
            rect = self.council_too_recent_ok_rect if self.council_stage == "too_recent" else self.council_ok_rect
            if rect.collidepoint(pos):
                self.active_screen, self.council_stage = (
                    "GAME" if self.council_stage == "results" else "COUNCIL_VOTE"), "select_proposal"
        elif self.council_stage == "voting" and not self.player_vote:
            for rect, val in self.vote_option_rects:
                if rect.collidepoint(pos):
                    self.player_vote = val
                    self.council_votes.insert(0, {"name": "You", "color": FACTIONS[0]['color'], "vote": val,
                                                  "votes": FACTIONS[0]['votes']})
                    pygame.time.wait(300)
                    self.council_stage = "results"

    def _draw_base_naming(self, screen):
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

    def _handle_base_naming_click(self, pos, game):
        """Handle clicks in the base naming dialog."""
        # Check OK button
        if hasattr(self, 'base_naming_ok_rect') and self.base_naming_ok_rect.collidepoint(pos):
            if self.base_name_input.strip():
                game.found_base(self.base_naming_unit, self.base_name_input.strip())
                self.active_screen = "GAME"
                self.base_naming_unit = None
                self.base_name_input = ""

        # Check Cancel button
        elif hasattr(self, 'base_naming_cancel_rect') and self.base_naming_cancel_rect.collidepoint(pos):
            self.active_screen = "GAME"
            self.base_naming_unit = None
            self.base_name_input = ""

    def _draw_base_view(self, screen, game):
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
                        pygame.draw.rect(screen, COLOR_BASE_FRIENDLY, tile_rect, border_radius=4)
                    else:
                        pygame.draw.rect(screen, terrain_color, tile_rect)
                else:
                    # Outside map bounds - draw black
                    pygame.draw.rect(screen, COLOR_BLACK, tile_rect)

                pygame.draw.rect(screen, (60, 60, 60), tile_rect, 1)

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

        # List facilities (placeholders for now)
        if base.facilities:
            for i, facility in enumerate(base.facilities):
                fac_text = self.small_font.render(f"- {facility}", True, COLOR_TEXT)
                screen.blit(fac_text, (facilities_x + 15, facilities_y + 35 + i * 22))
        else:
            no_fac = self.small_font.render("No facilities yet", True, (120, 120, 140))
            screen.blit(no_fac, (facilities_x + 15, facilities_y + 40))

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

        # GARRISON BAR: Units in base
        garrison_y = civilian_y + civilian_h + 10
        garrison_h = 60
        gar_label = self.small_font.render("GARRISON", True, COLOR_TEXT)
        screen.blit(gar_label, (screen_w // 2 - gar_label.get_width() // 2, garrison_y - 25))

        # Narrower garrison bar to avoid overlap
        garrison_bar_w = min(500, content_w - 200)
        garrison_bar_x = (screen_w - garrison_bar_w) // 2
        garrison_rect = pygame.Rect(garrison_bar_x, garrison_y, garrison_bar_w, garrison_h)
        pygame.draw.rect(screen, (30, 35, 40), garrison_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_UI_BORDER, garrison_rect, 2, border_radius=6)

        if base.garrison:
            # Draw garrison units
            for i, unit in enumerate(base.garrison):
                unit_x = garrison_rect.x + 10 + i * 50
                unit_circle = pygame.Rect(unit_x, garrison_rect.y + 10, 40, 40)
                pygame.draw.circle(screen, COLOR_UNIT_FRIENDLY, unit_circle.center, 20)
                pygame.draw.circle(screen, COLOR_BLACK, unit_circle.center, 20, 2)
        else:
            empty_text = self.small_font.render("No units garrisoned", True, (120, 130, 140))
            screen.blit(empty_text, (garrison_rect.centerx - empty_text.get_width() // 2, garrison_rect.centery - 8))

        # BOTTOM LEFT: Current Production (expanded)
        prod_x = content_x
        prod_y = screen_h - 160
        prod_w = 500
        prod_h = 140
        prod_rect = pygame.Rect(prod_x, prod_y, prod_w, prod_h)
        pygame.draw.rect(screen, (45, 40, 35), prod_rect, border_radius=8)
        pygame.draw.rect(screen, (140, 120, 80), prod_rect, 2, border_radius=8)

        prod_title = self.small_font.render("PRODUCTION", True, (220, 200, 160))
        screen.blit(prod_title, (prod_x + 10, prod_y + 8))

        # Production item (placeholder)
        if base.current_production:
            prod_name = self.small_font.render(base.current_production, True, COLOR_TEXT)
            screen.blit(prod_name, (prod_x + 15, prod_y + 35))
        else:
            prod_name = self.small_font.render("Scout Patrol", True, COLOR_TEXT)
            screen.blit(prod_name, (prod_x + 15, prod_y + 35))

        # Progress bar
        prod_progress_rect = pygame.Rect(prod_x + 10, prod_y + 60, 200, 20)
        pygame.draw.rect(screen, (20, 20, 20), prod_progress_rect, border_radius=4)

        # Fill (placeholder 60%)
        prod_fill = int(200 * 0.6)
        pygame.draw.rect(screen, (140, 180, 100), pygame.Rect(prod_x + 10, prod_y + 60, prod_fill, 20), border_radius=4)
        pygame.draw.rect(screen, (140, 120, 80), prod_progress_rect, 2, border_radius=4)

        turns_text = self.small_font.render(f"{base.production_turns_remaining} turns", True, (180, 180, 200))
        screen.blit(turns_text, (prod_x + 10, prod_y + 88))

        # Production queue label
        queue_x = prod_x + 230
        queue_label = self.small_font.render("Queue:", True, (200, 180, 140))
        screen.blit(queue_label, (queue_x, prod_y + 35))

        # Queue items (placeholder - empty for now)
        queue_text = self.small_font.render("(empty)", True, (120, 120, 120))
        screen.blit(queue_text, (queue_x, prod_y + 55))

        # Change and Hurry buttons
        button_y = prod_y + 100
        change_rect = pygame.Rect(prod_x + 10, button_y, 90, 30)
        hurry_rect = pygame.Rect(prod_x + 110, button_y, 90, 30)

        self.prod_change_rect = change_rect
        self.prod_hurry_rect = hurry_rect

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
                pygame.draw.circle(screen, COLOR_UNIT_FRIENDLY, (u_x + 12, u_y + 12), 12)
                pygame.draw.circle(screen, COLOR_BLACK, (u_x + 12, u_y + 12), 12, 1)
        else:
            support_text = self.small_font.render(f"0 units supported", True, (120, 140, 160))
            screen.blit(support_text, (support_x + 15, support_y + 40))

        # Base name title at top
        base_title = pygame.font.Font(None, 36).render(base.name, True, COLOR_TEXT)
        screen.blit(base_title, (content_x + content_w // 2 - base_title.get_width() // 2, nutrients_y - 50))

        # OK button at bottom center
        ok_button_w = 150
        ok_button_h = 50
        ok_button_x = (screen_w - ok_button_w) // 2
        ok_button_y = screen_h - ok_button_h - 20
        self.base_view_ok_rect = pygame.Rect(ok_button_x, ok_button_y, ok_button_w, ok_button_h)

        ok_hover = self.base_view_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, self.base_view_ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, self.base_view_ok_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.base_view_ok_rect.centerx - ok_text.get_width() // 2, self.base_view_ok_rect.centery - 10))

    def _handle_base_view_click(self, pos, game):
        """Handle clicks in the base view screen."""
        # Check OK button
        if hasattr(self, 'base_view_ok_rect') and self.base_view_ok_rect.collidepoint(pos):
            self.active_screen = "GAME"
            self.viewing_base = None
            return

        # Check Change button (placeholder - does nothing for now)
        if hasattr(self, 'prod_change_rect') and self.prod_change_rect.collidepoint(pos):
            game.set_status_message("Change production: Not yet implemented")
            return

        # Check Hurry button (placeholder - shows cost estimate)
        if hasattr(self, 'prod_hurry_rect') and self.prod_hurry_rect.collidepoint(pos):
            game.set_status_message("Hurry production: Costs energy credits (not yet implemented)")
            return

    def _draw_social_engineering(self, screen, game):
        """Draw the Social Engineering screen."""
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
                self.se_choice_rects[(category, col_idx)] = choice_rect

                is_selected = self.se_selections[category] == col_idx
                is_hover = choice_rect.collidepoint(pygame.mouse.get_pos())

                # Draw choice box
                if is_selected:
                    bg_color = (60, 80, 100)
                    border_color = (120, 180, 200)
                elif is_hover:
                    bg_color = (50, 60, 70)
                    border_color = (100, 140, 160)
                else:
                    bg_color = (40, 45, 50)
                    border_color = (80, 100, 120)

                pygame.draw.rect(screen, bg_color, choice_rect, border_radius=6)
                pygame.draw.rect(screen, border_color, choice_rect, 2, border_radius=6)

                # Choice name
                name_surf = self.small_font.render(choice_name, True, COLOR_TEXT)
                screen.blit(name_surf, (choice_rect.centerx - name_surf.get_width() // 2, choice_rect.y + 8))

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

    def _handle_social_engineering_click(self, pos, game):
        """Handle clicks in the Social Engineering screen."""
        # Check OK button
        if hasattr(self, 'se_ok_rect') and self.se_ok_rect.collidepoint(pos):
            self.active_screen = "GAME"
            self.social_engineering_open = False
            return

        # Check Cancel button
        if hasattr(self, 'se_cancel_rect') and self.se_cancel_rect.collidepoint(pos):
            # Reset selections to defaults (all leftmost)
            self.se_selections = {
                'Politics': 0,
                'Economics': 0,
                'Values': 0,
                'Future Society': 0
            }
            self.active_screen = "GAME"
            self.social_engineering_open = False
            return

        # Check choice selections
        if hasattr(self, 'se_choice_rects'):
            for (category, col_idx), rect in self.se_choice_rects.items():
                if rect.collidepoint(pos):
                    self.se_selections[category] = col_idx
                    break

    def _draw_design_workshop(self, screen, game):
        """Draw the Design Workshop screen."""
        # Fill background
        screen.fill((20, 25, 30))

        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("DESIGN WORKSHOP", True, (180, 220, 240))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 20))

    def _draw_tech_tree(self, screen, game):
        """Draw the Technology Tree screen."""
        # Fill background
        screen.fill((15, 20, 25))

        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("TECHNOLOGY TREE", True, (180, 220, 240))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 20))

        # Current research info
        current_tech = game.tech_tree.get_current_tech()
        info_y = 100

        current_label = self.font.render("Current Research:", True, (150, 180, 200))
        screen.blit(current_label, (50, info_y))

        tech_name = pygame.font.Font(None, 36).render(current_tech, True, (200, 220, 240))
        screen.blit(tech_name, (50, info_y + 35))

        # Progress bar
        progress_y = info_y + 80
        progress_w = 600
        progress_h = 40
        progress_x = 50

        progress_rect = pygame.Rect(progress_x, progress_y, progress_w, progress_h)
        pygame.draw.rect(screen, (30, 35, 40), progress_rect, border_radius=6)

        # Fill based on progress
        if current_tech != "Complete":
            progress_pct = game.tech_tree.get_progress_percentage()
            fill_w = int(progress_w * progress_pct)
            fill_rect = pygame.Rect(progress_x, progress_y, fill_w, progress_h)
            pygame.draw.rect(screen, (80, 150, 200), fill_rect, border_radius=6)

        pygame.draw.rect(screen, (100, 140, 180), progress_rect, 2, border_radius=6)

        # Progress text
        if current_tech != "Complete":
            turns_left = game.tech_tree.get_turns_remaining()
            progress_text = self.font.render(f"{turns_left} turns remaining", True, COLOR_TEXT)
            screen.blit(progress_text, (progress_rect.centerx - progress_text.get_width() // 2, progress_rect.centery - 10))
        else:
            complete_text = self.font.render("Research Complete!", True, (100, 220, 100))
            screen.blit(complete_text, (progress_rect.centerx - complete_text.get_width() // 2, progress_rect.centery - 10))

        # Tech list (linear progression)
        list_y = progress_y + 80
        list_title = self.font.render("Technology Progression:", True, (150, 180, 200))
        screen.blit(list_title, (50, list_y))

        # Display all 20 techs in a grid
        tech_start_y = list_y + 40
        tech_spacing_y = 35
        cols = 2
        col_width = (screen_w - 100) // cols

        for i, tech in enumerate(game.tech_tree.techs):
            col = i % cols
            row = i // cols

            tech_x = 50 + col * col_width
            tech_y = tech_start_y + row * tech_spacing_y

            status = game.tech_tree.get_tech_status(tech)

            # Color based on status
            if status == "Completed":
                tech_color = (100, 220, 100)
                status_symbol = "✓"
            elif status == "Researching":
                tech_color = (200, 220, 100)
                status_symbol = "→"
            else:
                tech_color = (120, 130, 140)
                status_symbol = " "

            tech_text = self.small_font.render(f"{status_symbol} {tech}", True, tech_color)
            screen.blit(tech_text, (tech_x, tech_y))

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

    def _handle_tech_tree_click(self, pos, game):
        """Handle clicks in the Tech Tree screen."""
        # Check OK button
        if hasattr(self, 'tech_tree_ok_rect') and self.tech_tree_ok_rect.collidepoint(pos):
            self.active_screen = "GAME"
            self.tech_tree_open = False

    def _draw_wrapped_text(self, screen, text, rect, font, color):
        """Render text with word wrapping within a rectangle."""
        words = text.split(' ')
        lines, cur = [], []
        for w in words:
            if font.size(' '.join(cur + [w]))[0] < rect.width - 20:
                cur.append(w)
            else:
                lines.append(' '.join(cur)); cur = [w]
        if cur: lines.append(' '.join(cur))
        for i, l in enumerate(lines):
            screen.blit(font.render(l, True, color), (rect.x + 10, rect.y + 10 + i * (font.get_height() + 2)))

    def _draw_supply_pod_message(self, screen, game):
        """Draw supply pod discovery message."""
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Message box
        box_w, box_h = 500, 250
        box_x = (constants.SCREEN_WIDTH - box_w) // 2
        box_y = (constants.SCREEN_HEIGHT - box_h) // 2

        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (30, 50, 40), box_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 200, 150), box_rect, 3, border_radius=10)

        # Title
        title_text = self.font.render("UNITY SUPPLY POD", True, (150, 255, 200))
        title_rect = title_text.get_rect(centerx=box_x + box_w // 2, top=box_y + 20)
        screen.blit(title_text, title_rect)

        # Message
        msg_y = box_y + 80
        msg_lines = game.supply_pod_message.split('\n')
        for i, line in enumerate(msg_lines):
            line_text = self.small_font.render(line, True, COLOR_TEXT)
            line_rect = line_text.get_rect(centerx=box_x + box_w // 2, top=msg_y + i * 25)
            screen.blit(line_text, line_rect)

        # OK button
        ok_w, ok_h = 120, 40
        ok_x = box_x + (box_w - ok_w) // 2
        ok_y = box_y + box_h - ok_h - 20
        ok_rect = pygame.Rect(ok_x, ok_y, ok_w, ok_h)

        mouse_pos = pygame.mouse.get_pos()
        ok_hover = ok_rect.collidepoint(mouse_pos)

        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, COLOR_TEXT)
        ok_text_rect = ok_text.get_rect(center=ok_rect.center)
        screen.blit(ok_text, ok_text_rect)

        # Store rect for clicking
        self.supply_pod_ok_rect = ok_rect

    def _draw_battle_prediction(self, screen, game):
        """Draw battle prediction dialog before combat."""
        if not game.pending_battle:
            return

        attacker = game.pending_battle['attacker']
        defender = game.pending_battle['defender']

        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Prediction box
        box_w, box_h = 500, 300
        box_x = (constants.SCREEN_WIDTH - box_w) // 2
        box_y = (constants.SCREEN_HEIGHT - box_h) // 2

        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (40, 30, 30), box_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 100, 100), box_rect, 3, border_radius=10)

        # Title
        title_text = self.font.render("BATTLE PREDICTION", True, (255, 200, 200))
        title_rect = title_text.get_rect(centerx=box_x + box_w // 2, top=box_y + 20)
        screen.blit(title_text, title_rect)

        # Attacker info (left side)
        att_x = box_x + 40
        att_y = box_y + 80
        att_name = self.font.render(f"{attacker.name}", True, COLOR_UNIT_FRIENDLY)
        screen.blit(att_name, (att_x, att_y))

        att_stats = self.small_font.render(f"{attacker.get_stats_string()}", True, COLOR_TEXT)
        screen.blit(att_stats, (att_x, att_y + 30))

        att_hp = self.small_font.render(f"HP: {attacker.current_health}/{attacker.max_health}", True, COLOR_TEXT)
        screen.blit(att_hp, (att_x, att_y + 55))

        # VS in center
        vs_text = self.font.render("VS", True, (255, 255, 255))
        vs_rect = vs_text.get_rect(center=(box_x + box_w // 2, att_y + 40))
        screen.blit(vs_text, vs_rect)

        # Defender info (right side)
        def_x = box_x + box_w - 200
        def_y = box_y + 80
        def_name = self.font.render(f"{defender.name}", True, COLOR_UNIT_ENEMY)
        screen.blit(def_name, (def_x, def_y))

        def_stats = self.small_font.render(f"{defender.get_stats_string()}", True, COLOR_TEXT)
        screen.blit(def_stats, (def_x, def_y + 30))

        def_hp = self.small_font.render(f"HP: {defender.current_health}/{defender.max_health}", True, COLOR_TEXT)
        screen.blit(def_hp, (def_x, def_y + 55))

        # Combat odds
        odds = game.calculate_combat_odds(attacker, defender)
        odds_text = self.font.render(f"Win Chance: {int(odds * 100)}%", True, (255, 255, 100))
        odds_rect = odds_text.get_rect(centerx=box_x + box_w // 2, top=box_y + 160)
        screen.blit(odds_text, odds_rect)

        # OK and Cancel buttons
        button_y = box_y + box_h - 60
        ok_w, ok_h = 100, 40
        cancel_w, cancel_h = 100, 40

        ok_x = box_x + box_w // 2 - ok_w - 10
        cancel_x = box_x + box_w // 2 + 10

        ok_rect = pygame.Rect(ok_x, button_y, ok_w, ok_h)
        cancel_rect = pygame.Rect(cancel_x, button_y, cancel_w, cancel_h)

        mouse_pos = pygame.mouse.get_pos()
        ok_hover = ok_rect.collidepoint(mouse_pos)
        cancel_hover = cancel_rect.collidepoint(mouse_pos)

        # OK button
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        ok_text_rect = ok_text.get_rect(center=ok_rect.center)
        screen.blit(ok_text, ok_text_rect)

        # Cancel button
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        screen.blit(cancel_text, cancel_text_rect)

        # Store rects for clicking
        self.battle_prediction_ok_rect = ok_rect
        self.battle_prediction_cancel_rect = cancel_rect

    def _draw_battle_animation(self, screen, game):
        """Draw ongoing battle animation in bottom center of screen."""
        if not game.active_battle:
            return

        battle = game.active_battle
        attacker = battle['attacker']
        defender = battle['defender']

        # Battle panel - bottom center, 1/3 of UI panel width
        panel_w = constants.SCREEN_WIDTH // 3
        panel_h = constants.UI_PANEL_HEIGHT - 20
        panel_x = (constants.SCREEN_WIDTH - panel_w) // 2
        panel_y = constants.UI_PANEL_Y + 10

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (30, 20, 20), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 50, 50), panel_rect, 3, border_radius=8)

        # Title
        title = self.small_font.render("BATTLE IN PROGRESS", True, (255, 200, 200))
        title_rect = title.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 10)
        screen.blit(title, title_rect)

        # Show current round HP
        current_round_idx = battle['current_round'] - 1
        if current_round_idx >= 0 and current_round_idx < len(battle['rounds']):
            round_data = battle['rounds'][current_round_idx]
            att_hp = round_data['attacker_hp']
            def_hp = round_data['defender_hp']
        else:
            att_hp = attacker.current_health
            def_hp = defender.current_health

        # Attacker HP (left)
        att_y = panel_y + 50
        att_text = self.small_font.render(f"{attacker.name}", True, COLOR_UNIT_FRIENDLY)
        screen.blit(att_text, (panel_x + 10, att_y))
        att_hp_text = self.small_font.render(f"HP: {att_hp}/{attacker.max_health}", True, COLOR_TEXT)
        screen.blit(att_hp_text, (panel_x + 10, att_y + 20))

        # Defender HP (right)
        def_text = self.small_font.render(f"{defender.name}", True, COLOR_UNIT_ENEMY)
        def_text_rect = def_text.get_rect(right=panel_x + panel_w - 10, top=att_y)
        screen.blit(def_text, def_text_rect)
        def_hp_text = self.small_font.render(f"HP: {def_hp}/{defender.max_health}", True, COLOR_TEXT)
        def_hp_rect = def_hp_text.get_rect(right=panel_x + panel_w - 10, top=att_y + 20)
        screen.blit(def_hp_text, def_hp_rect)

        # Round counter
        round_text = self.small_font.render(
            f"Round {battle['current_round']}/{len(battle['rounds'])}",
            True, (200, 200, 200)
        )
        round_rect = round_text.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 110)
        screen.blit(round_text, round_rect)

        # Show latest hit
        if current_round_idx >= 0 and current_round_idx < len(battle['rounds']):
            round_data = battle['rounds'][current_round_idx]
            if round_data['winner'] == 'attacker':
                hit_text = f"{attacker.name} hits for {round_data['damage']}!"
                hit_color = COLOR_UNIT_FRIENDLY
            else:
                hit_text = f"{defender.name} hits for {round_data['damage']}!"
                hit_color = COLOR_UNIT_ENEMY

            hit_surface = self.small_font.render(hit_text, True, hit_color)
            hit_rect = hit_surface.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 140)
            screen.blit(hit_surface, hit_rect)