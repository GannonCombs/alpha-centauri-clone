"""Raze base confirmation dialog."""

import pygame
from game.ui.components import Dialog


class RazeBaseDialog(Dialog):
    """Confirmation popup before a player razes (obliterates) one of their own bases."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.target = None   # Base object
        self.ok_rect = None
        self.cancel_rect = None

    def activate(self, base):
        self.active = True
        self.target = base

    def draw(self, screen, game):
        if not self.active or not self.target:
            return
        base = self.target
        self.draw_overlay(screen, alpha=170)

        box = self.centered_rect(560, 230)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(200, 100, 40), bg_color=(45, 20, 10))

        title_surf = self.font.render("RAZE BASE", True, (240, 140, 60))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 20))

        atrocity_count = getattr(game, 'atrocity_count', 0)
        sanction_turns = 10 * (atrocity_count + 1)
        lines = [
            f'Raze "{base.name}" and kill all {base.population} citizen(s)?',
            "This is an ATROCITY against civilian populations.",
            f"Commerce sanctions will last {sanction_turns} turns.",
        ]
        for i, line in enumerate(lines):
            col = (255, 160, 80) if i == 1 else (210, 190, 170)
            ls = self.small_font.render(line, True, col)
            screen.blit(ls, (box_x + box_w // 2 - ls.get_width() // 2, box_y + 75 + i * 24))

        btn_w, btn_h = 140, 40
        btn_y = box_y + box_h - 58
        mouse = pygame.mouse.get_pos()

        ok_rect = pygame.Rect(box_x + box_w // 2 - btn_w - 15, btn_y, btn_w, btn_h)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (140, 50, 20) if is_hover else (100, 35, 10), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (220, 100, 40), ok_rect, 2, border_radius=8)
        ok_s = self.font.render("RAZE", True, (255, 210, 170))
        screen.blit(ok_s, (ok_rect.centerx - ok_s.get_width() // 2, ok_rect.centery - ok_s.get_height() // 2))

        cancel_rect = pygame.Rect(box_x + box_w // 2 + 15, btn_y, btn_w, btn_h)
        self.cancel_rect = cancel_rect
        is_hover = cancel_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (60, 70, 80) if is_hover else (40, 50, 60), cancel_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 140, 160), cancel_rect, 2, border_radius=8)
        cancel_s = self.font.render("CANCEL", True, (200, 210, 220))
        screen.blit(cancel_s, (cancel_rect.centerx - cancel_s.get_width() // 2,
                                cancel_rect.centery - cancel_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns 'raze', 'cancel', or None."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            return 'raze'
        elif self.cancel_rect and self.cancel_rect.collidepoint(pos):
            self.active = False
            self.target = None
            return 'cancel'
        return None
