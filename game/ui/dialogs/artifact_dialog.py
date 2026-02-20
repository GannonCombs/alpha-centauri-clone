"""Alien Artifact event notification dialog."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.ui.components import Dialog


class ArtifactEventDialog(Dialog):
    """Notification popup for artifact theft, capture, or destruction events.

    Does not own an `active` flag — UIManager gates with `game.artifact_message`.

    handle_click returns:
      True  — dismissed (OK clicked)
      None  — click did not hit OK (click blocked)
    """

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.ok_rect = None

    def draw(self, screen, game):
        message = game.artifact_message
        if not message:
            return

        self.draw_overlay(screen)

        box = self.centered_rect(520, 230)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(80, 180, 220), bg_color=(20, 35, 50))

        title_surf = self.font.render("ALIEN ARTIFACT", True, (120, 220, 255))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 24))

        msg_y = box_y + 80
        for i, line in enumerate(message.split('\n')):
            line_surf = self.small_font.render(line, True, (180, 210, 230))
            screen.blit(line_surf, (box_x + box_w // 2 - line_surf.get_width() // 2,
                                    msg_y + i * 25))

        btn_w, btn_h = 120, 40
        ok_x = box_x + (box_w - btn_w) // 2
        ok_y = box_y + box_h - btn_h - 18
        ok_rect = pygame.Rect(ok_x, ok_y, btn_w, btn_h)
        self.ok_rect = ok_rect

        hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (60, 100, 130) if hover else (40, 70, 95), ok_rect, border_radius=6)
        pygame.draw.rect(screen, (80, 180, 220), ok_rect, 2, border_radius=6)
        ok_surf = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2,
                               ok_rect.centery - ok_surf.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns True if dismissed, None if click did not hit OK."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            game.artifact_message = None
            return True
        return None
