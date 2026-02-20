"""Supply pod discovery popup."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER)
from game.ui.components import Dialog


class SupplyPodDialog(Dialog):
    """Draws and handles the supply pod discovery popup.

    Does not own an `active` flag — UIManager gates with `game.supply_pod_message`.

    handle_click returns:
      True  — dismissed (OK clicked)
      None  — click did not hit OK (click blocked)
    """

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.ok_rect = None

    def draw(self, screen, game):
        message = game.supply_pod_message
        if not message:
            return

        self.draw_overlay(screen)

        box_w, box_h = 500, 250
        box_x = (display.SCREEN_WIDTH - box_w) // 2
        box_y = (display.SCREEN_HEIGHT - box_h) // 2

        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (30, 50, 40), box_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 200, 150), box_rect, 3, border_radius=10)

        title_text = self.font.render("UNITY SUPPLY POD", True, (150, 255, 200))
        title_rect = title_text.get_rect(centerx=box_x + box_w // 2, top=box_y + 20)
        screen.blit(title_text, title_rect)

        msg_y = box_y + 80
        for i, line in enumerate(message.split('\n')):
            line_text = self.small_font.render(line, True, COLOR_TEXT)
            line_rect = line_text.get_rect(centerx=box_x + box_w // 2, top=msg_y + i * 25)
            screen.blit(line_text, line_rect)

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

        self.ok_rect = ok_rect

    def handle_click(self, pos, game):
        """Returns True if dismissed, None if click did not hit OK."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            game.supply_pod_message = None
            if game.supply_pod_tech_event:
                game.upkeep_events = [game.supply_pod_tech_event]
                game.supply_pod_tech_event = None
                game.current_upkeep_event_index = 0
                game.upkeep_phase_active = True
                game.mid_turn_upkeep = True
            return True
        return None
