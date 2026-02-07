"""Faction diplomacy interface."""

import pygame
from game.data import constants
from game.data.constants import COLOR_TEXT, COLOR_BUTTON_BORDER
from game.data.data import FACTIONS
from game.commlink_text import DialogSubstitution, select_greeting_dialog


class DiplomacyManager:
    """Manages the faction diplomacy interface."""

    def __init__(self, font, small_font, mono_font):
        """Initialize diplomacy manager with fonts."""
        self.font = font
        self.small_font = small_font
        self.mono_font = mono_font

        # State
        self.target_faction = None
        self.player_faction = None  # Will be set when opening diplomacy
        self.diplo_stage = "greeting"  # greeting, diplo, proposal, exit, etc.
        self.diplo_relations = {}  # faction_id -> status
        self.diplo_mood = "CORDIAL"  # CORDIAL, WARY, HOSTILE, FRIENDLY

        # Initialize relations (start with no formal relations)
        # Relations are established through dialog (Treaty, Pact)
        # or conflict (Vendetta, Truce)
        # Empty dict means "Uncommitted" - no formal relationship

        # Dialog system
        self.dialog_system = DialogSubstitution()
        self.current_dialog = None
        self.current_responses = []

        # UI elements
        self.diplo_option_rects = []
        self.diplo_ok_rect = None
        self._current_diplo_message = ""
        self._last_diplo_stage = None

    def open_diplomacy(self, faction, player_faction_index):
        """Initialize diplomacy with a faction.

        Args:
            faction: AI faction dictionary
            player_faction_index: Index of player's faction in FACTIONS list
        """
        self.target_faction = faction
        self.player_faction = FACTIONS[player_faction_index]  # Get actual player faction
        self.diplo_stage = "greeting"
        self._last_diplo_stage = None  # Force dialog refresh

    def draw(self, screen):
        """Render diplomacy screen with faction portrait and dialogue."""
        # Safety check - don't draw if target_faction not set
        if not self.target_faction or not isinstance(self.target_faction, dict):
            return

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

        name_surf = self.font.render(self.target_faction['full_name'], True, self.target_faction['color'])
        screen.blit(name_surf, (info_x, info_y))

        faction_id = next((i for i, f in enumerate(FACTIONS) if f['name'] == self.target_faction['name']), None)
        relation = self.diplo_relations.get(faction_id, "Uncommitted")

        info_lines = [f"STATUS: {relation}", f"MOOD: {self.diplo_mood}",
                      f"COUNCIL VOTES: {self.target_faction.get('votes', 0)}"]
        for i, line in enumerate(info_lines):
            screen.blit(self.mono_font.render(line, True, (180, 200, 190)), (info_x, info_y + 45 + i * 32))

        msg_rect = pygame.Rect(60, 300, constants.SCREEN_WIDTH - 120, 150)
        pygame.draw.rect(screen, (12, 18, 22), msg_rect)
        pygame.draw.rect(screen, self.target_faction['color'], msg_rect, 3)

        # Update dialog if stage changed
        if self._last_diplo_stage != self.diplo_stage:
            self._update_dialog(relation)
            self._last_diplo_stage = self.diplo_stage

        # Draw dialog text (if any)
        if self.current_dialog and self.current_dialog.get('text'):
            self._draw_wrapped_text(screen, self.current_dialog['text'], msg_rect, self.font, (210, 230, 220))

        # Draw response options (only if not exiting)
        if self.diplo_stage != "exit":
            options_y = msg_rect.bottom + 40
            self.diplo_option_rects = []

            # Filter responses based on requirements
            available_responses = self._filter_responses(self.current_responses, relation)

            for i, response in enumerate(available_responses):
                opt_rect = pygame.Rect(constants.SCREEN_WIDTH // 2 - 400, options_y + i * 60, 800, 50)
                action = response.get('action', 'diplo')
                self.diplo_option_rects.append((opt_rect, action))
                is_hover = opt_rect.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(screen, (50, 65, 75) if is_hover else (35, 45, 55), opt_rect)
                pygame.draw.rect(screen, self.target_faction['color'] if is_hover else COLOR_BUTTON_BORDER, opt_rect, 3)

                # Substitute variables in response text
                response_text = self.dialog_system.substitute(response['text'])
                screen.blit(self.font.render(response_text, True, COLOR_TEXT), (opt_rect.x + 30, opt_rect.centery - 10))

    def _update_dialog(self, relation):
        """Update current dialog based on stage.

        Args:
            relation: Current relationship status
        """
        # Map stage to dialog ID
        dialog_id = self._get_dialog_id_for_stage(relation)

        # On exit, there's no dialog - just close
        if dialog_id is None:
            self.current_dialog = {'text': '', 'responses': []}
            self.current_responses = []
            return

        # Get dialog with substitutions using actual player faction
        self.current_dialog = self.dialog_system.get_dialog(
            dialog_id,
            self.player_faction,
            self.target_faction
        )
        self.current_responses = self.current_dialog.get('responses', [])

    def _get_dialog_id_for_stage(self, relation):
        """Map conversation stage to dialog ID.

        Args:
            relation: Current relationship status

        Returns:
            String dialog ID or None for no dialog
        """
        if self.diplo_stage == "greeting":
            return select_greeting_dialog(relation)
        elif self.diplo_stage == "diplo":
            return 'DIPLO'
        elif self.diplo_stage == "proposal":
            return 'PROPOSAL'
        elif self.diplo_stage == "propose_pact":
            return 'SWEARAPACT'
        elif self.diplo_stage == "accept_pact":
            return 'MAKEPACT'
        elif self.diplo_stage == "reject_pact":
            return 'REJPACT'
        elif self.diplo_stage == "propose_treaty":
            return 'OFFERTREATY'
        elif self.diplo_stage == "accept_treaty":
            return 'MAKETREATY0'  # Use MAKETREATY0 from script.txt
        elif self.diplo_stage == "reject_treaty":
            return 'REJTREATY'
        elif self.diplo_stage == "propose_tech":
            return 'BUYTECH0'
        elif self.diplo_stage == "propose_loan":
            # TODO: Need correct dialog for player asking AI for loan
            # ASKFORLOAN1 is AI asking player, which is backwards
            return 'GENERIC'  # Placeholder until we have the right dialog
        elif self.diplo_stage == "exit":
            return None  # No dialog on exit, just close
        else:
            return 'GENERIC'

    def _filter_responses(self, responses, relation):
        """Filter responses based on requirements.

        Args:
            responses: List of response dictionaries
            relation: Current relationship status

        Returns:
            List of available responses
        """
        available = []
        for response in responses:
            requires = response.get('requires')

            # Can only offer pact if you already have a treaty
            if requires == 'has_treaty' and relation != 'Treaty':
                continue
            # Can only offer treaty if you don't already have one
            if requires == 'no_treaty' and relation in ['Treaty', 'Pact']:
                continue
            # Pact-specific options
            if requires == 'pact' and relation != 'Pact':
                continue

            available.append(response)
        return available

    def handle_click(self, pos):
        """Process clicks on diplomacy screen. Returns 'close' if should exit, None otherwise."""
        if hasattr(self, 'diplo_option_rects'):
            for rect, action in self.diplo_option_rects:
                if rect.collidepoint(pos):
                    result = self._handle_action(action)
                    if result == 'close':
                        self.diplo_stage = "greeting"
                        return 'close'
                    return None
        return None

    def _handle_action(self, action):
        """Handle a dialog action by transitioning to next stage.

        Player-initiated proposal flow:
        1. Player clicks proposal → propose_X stage (player's speech)
        2. Player clicks Continue → ai_decide_X action
        3. AI auto-decides → accept_X or reject_X stage (AI's response)
        4. Player clicks Continue → return to diplo menu

        Special behaviors:
        - 'exit': Establishes Truce on first meeting, then closes dialog
        - 'ai_decide_treaty'/'ai_decide_pact': Updates diplo_relations immediately
        - Other actions: Just change diplo_stage for next dialog

        Args:
            action (str): Action identifier from dialog response

        Returns:
            str: 'close' if dialog should close, None to stay in dialog

        Note:
            Player never responds to their own proposals - AI decides automatically.
        """
        # Map actions to stages
        if action == 'exit':
            # On exit, establish Truce if no formal relationship exists
            faction_id = next((i for i, f in enumerate(FACTIONS) if f['name'] == self.target_faction['name']), None)
            if faction_id is not None:
                current_relation = self.diplo_relations.get(faction_id, "Uncommitted")
                # If uncommitted (first meeting), establish Truce
                if current_relation == "Uncommitted":
                    self.diplo_relations[faction_id] = 'Truce'
            # Exit immediately - no dialog, just close
            return 'close'
        elif action == 'diplo':
            self.diplo_stage = 'diplo'
        elif action == 'proposal':
            self.diplo_stage = 'proposal'
        elif action == 'propose_pact':
            # Player proposes pact - show player's speech
            self.diplo_stage = 'propose_pact'
        elif action == 'ai_decide_pact':
            # AI decides whether to accept player's pact proposal
            # For now, always accept (later: base on relationship)
            faction_id = next((i for i, f in enumerate(FACTIONS) if f['name'] == self.target_faction['name']), None)
            if faction_id is not None:
                self.diplo_relations[faction_id] = 'Pact'
            self.diplo_stage = 'accept_pact'  # AI accepts
        elif action == 'accept_pact':
            # After showing AI's acceptance, return to diplo
            self.diplo_stage = 'diplo'
        elif action == 'reject_pact':
            # After showing AI's rejection, return to diplo
            self.diplo_stage = 'diplo'
        elif action == 'propose_treaty':
            # Player proposes treaty - show player's speech
            self.diplo_stage = 'propose_treaty'
        elif action == 'ai_decide_treaty':
            # AI decides whether to accept player's treaty proposal
            # For now, always accept (later: base on relationship)
            faction_id = next((i for i, f in enumerate(FACTIONS) if f['name'] == self.target_faction['name']), None)
            if faction_id is not None:
                self.diplo_relations[faction_id] = 'Treaty'
            self.diplo_stage = 'accept_treaty'  # AI accepts
        elif action == 'accept_treaty':
            # After showing AI's acceptance, return to diplo
            self.diplo_stage = 'diplo'
        elif action == 'reject_treaty':
            # After showing AI's rejection, return to diplo
            self.diplo_stage = 'diplo'
        elif action == 'propose_tech':
            self.diplo_stage = 'propose_tech'
        elif action == 'propose_loan':
            self.diplo_stage = 'propose_loan'
        elif action == 'battleplans':
            # TODO: Implement battle plans
            self.diplo_stage = 'diplo'
        else:
            # Default fallback
            self.diplo_stage = 'diplo'
        return None

    def _draw_wrapped_text(self, screen, text, rect, font, color):
        """Render text with word wrapping within a rectangle."""
        words = text.split(' ')
        lines, cur = [], []
        for w in words:
            if font.size(' '.join(cur + [w]))[0] < rect.width - 20:
                cur.append(w)
            else:
                lines.append(' '.join(cur))
                cur = [w]
        if cur:
            lines.append(' '.join(cur))
        for i, l in enumerate(lines):
            screen.blit(font.render(l, True, color), (rect.x + 10, rect.y + 10 + i * (font.get_height() + 2)))
