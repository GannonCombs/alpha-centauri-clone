"""Major atrocity (Planet Buster) notification dialog."""

import pygame
from game.ui.components import Dialog


class MajorAtrocityDialog(Dialog):
    """Full-screen notification when a Planet Buster is used, causing universal Vendetta."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.ok_rect = None

    def activate(self):
        self.active = True

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen, alpha=190)

        box = self.centered_rect(620, 280)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(200, 40, 40), bg_color=(60, 10, 10))

        title_surf = self.font.render("MAJOR ATROCITY COMMITTED", True, (255, 60, 60))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 20))

        sanction_turns = 10 * getattr(game, 'atrocity_count', 1)
        lines = [
            "The use of a Planet Buster is an unforgivable crime",
            "against all humanity on Chiron.",
            "ALL FACTIONS have declared Vendetta against us.",
            f"Commerce sanctions imposed for {sanction_turns} turns.",
            "Our votes in the Planetary Council are forfeit forever.",
        ]
        for i, line in enumerate(lines):
            col = (255, 120, 120) if i == 2 else (210, 180, 180)
            ls = self.small_font.render(line, True, col)
            screen.blit(ls, (box_x + box_w // 2 - ls.get_width() // 2, box_y + 72 + i * 22))

        ok_rect = pygame.Rect(box_x + box_w // 2 - 60, box_y + box_h - 60, 120, 40)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (100, 20, 20) if is_hover else (70, 15, 15), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 50, 50), ok_rect, 2, border_radius=8)
        ok_s = self.font.render("OK", True, (240, 200, 200))
        screen.blit(ok_s, (ok_rect.centerx - ok_s.get_width() // 2,
                            ok_rect.centery - ok_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns True if dismissed."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            game.pending_major_atrocity_popup = False
            self.active = False
            return True
        return None
