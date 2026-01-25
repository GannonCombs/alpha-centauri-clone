"""Simple modal dialogs."""

import pygame
import constants
from constants import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                       COLOR_BUTTON_BORDER)


class DialogManager:
    """Manages simple modal dialogs like supply pod messages."""

    def __init__(self, font, small_font):
        """Initialize dialog manager with fonts."""
        self.font = font
        self.small_font = small_font
        self.supply_pod_ok_rect = None

    def draw_supply_pod_message(self, screen, message):
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
        msg_lines = message.split('\n')
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

    def handle_supply_pod_click(self, pos):
        """Handle click on supply pod message. Returns True if dismissed."""
        if self.supply_pod_ok_rect and self.supply_pod_ok_rect.collidepoint(pos):
            return True
        return False
