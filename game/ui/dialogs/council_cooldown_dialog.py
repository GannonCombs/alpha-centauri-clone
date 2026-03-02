"""Dialog shown when a council proposal is still on cooldown."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_COUNCIL_BG, COLOR_COUNCIL_BOX)
from game.ui.components import Dialog


class CouncilCooldownDialog(Dialog):
    """Full-screen cooldown error for Planetary Council proposals.

    Set self.proposal before drawing.
    handle_click() returns True on OK click, None otherwise.
    """

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.proposal = None
        self.ok_rect = None

    def draw(self, screen, game):
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (40, 25, 25), (0, 180, display.SCREEN_WIDTH, 60))
        t = self.font.render("PLANETARY COUNCIL - MOTION DENIED", True, (255, 140, 120))
        screen.blit(t, (display.SCREEN_WIDTH // 2 - t.get_width() // 2, 200))

        box = pygame.Rect(display.SCREEN_WIDTH // 2 - 350, 280, 700, 180)
        pygame.draw.rect(screen, COLOR_COUNCIL_BOX, box, border_radius=10)
        pygame.draw.rect(screen, (255, 140, 120), box, 3, border_radius=10)

        rem = max(0, self.proposal['cooldown'] - (game.turn - self.proposal.get('last_voted', 0)))
        msgs = [f"Motion '{self.proposal['name']}' was recent.",
                f"Cooldown: {self.proposal['cooldown']} turns.", f"Remaining: {rem}"]
        for i, m in enumerate(msgs):
            s = self.font.render(m, True, COLOR_TEXT)
            screen.blit(s, (display.SCREEN_WIDTH // 2 - s.get_width() // 2, 310 + i * 40))

        self.ok_rect = pygame.Rect(display.SCREEN_WIDTH // 2 - 80, display.SCREEN_HEIGHT - 120, 160, 50)
        pygame.draw.rect(screen, (40, 30, 25), self.ok_rect, border_radius=8)
        ok_t = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_t, (self.ok_rect.centerx - ok_t.get_width() // 2,
                           self.ok_rect.centery - 10))

    def handle_click(self, pos, game):
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            return True
        return None
