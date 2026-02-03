"""Faction diplomacy interface."""

import pygame
import random
import constants
from constants import COLOR_TEXT, COLOR_BUTTON_BORDER
from .data import FACTIONS, DIPLOMACY_GREETINGS, DIPLOMACY_RESPONSES


class DiplomacyManager:
    """Manages the faction diplomacy interface."""

    def __init__(self, font, small_font, mono_font):
        """Initialize diplomacy manager with fonts."""
        self.font = font
        self.small_font = small_font
        self.mono_font = mono_font

        # State
        self.target_faction = None
        self.diplo_stage = "greeting"  # greeting, pact_request, tech_discuss, trade_discuss, exit
        self.diplo_relations = {}  # faction_id -> status
        self.diplo_mood = "CORDIAL"  # CORDIAL, WARY, HOSTILE, FRIENDLY

        # Initialize relations (default to Truce for others)
        for i, f in enumerate(FACTIONS):
            if i == 0:
                continue  # Skip player
            status = random.choice(["Treaty", "Truce", "Informal Truce", "Vendetta"])
            self.diplo_relations[i] = status

        # UI elements
        self.diplo_option_rects = []
        self.diplo_ok_rect = None
        self._current_diplo_message = ""
        self._last_diplo_stage = None

    def open_diplomacy(self, faction):
        """Initialize diplomacy with a faction."""
        self.target_faction = faction
        self.diplo_stage = "greeting"

    def draw(self, screen):
        """Render diplomacy screen with faction portrait and dialogue."""
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

    def handle_click(self, pos):
        """Process clicks on diplomacy screen. Returns 'close' if should exit, None otherwise."""
        if hasattr(self, 'diplo_ok_rect') and self.diplo_ok_rect and self.diplo_ok_rect.collidepoint(pos):
            self.diplo_stage = "greeting"
            return 'close'
        if hasattr(self, 'diplo_option_rects'):
            for rect, next_s in self.diplo_option_rects:
                if rect.collidepoint(pos):
                    self.diplo_stage = next_s
                    return None
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
