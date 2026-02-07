"""Reusable UI components."""

import pygame
from game.data.constants import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)


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
