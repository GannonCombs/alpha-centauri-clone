"""Reusable UI components."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)


# ---------------------------------------------------------------------------
# Module-level drawing helpers
# Usable by any screen or dialog without inheritance.
# ---------------------------------------------------------------------------

def draw_overlay(screen, alpha=180, color=(0, 0, 0)):
    """Draw a semi-transparent full-screen overlay."""
    overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
    overlay.set_alpha(alpha)
    overlay.fill(color)
    screen.blit(overlay, (0, 0))


def centered_rect(width, height):
    """Return a pygame.Rect centered on the screen."""
    x = display.SCREEN_WIDTH // 2 - width // 2
    y = display.SCREEN_HEIGHT // 2 - height // 2
    return pygame.Rect(x, y, width, height)


def draw_box(screen, rect, border_color=(100, 140, 160), bg_color=(30, 40, 50)):
    """Draw a rounded popup box with a border."""
    pygame.draw.rect(screen, bg_color, rect, border_radius=12)
    pygame.draw.rect(screen, border_color, rect, 3, border_radius=12)


def draw_button(screen, rect, label, font, normal_color=None, hover_color=None,
                border_color=None, text_color=None):
    """Draw a hover-aware button centered in rect. Returns True if hovered."""
    is_hover = rect.collidepoint(pygame.mouse.get_pos())
    bg = (hover_color or COLOR_BUTTON_HOVER) if is_hover else (normal_color or COLOR_BUTTON)
    pygame.draw.rect(screen, bg, rect, border_radius=6)
    pygame.draw.rect(screen, border_color or COLOR_BUTTON_BORDER, rect, 2, border_radius=6)
    text = font.render(label, True, text_color or COLOR_TEXT)
    screen.blit(text, (rect.centerx - text.get_width() // 2,
                       rect.centery - text.get_height() // 2))
    return is_hover


# ---------------------------------------------------------------------------
# Dialog base class
# ---------------------------------------------------------------------------

class Dialog:
    """Base class for modal dialogs that appear over the map view.

    Subclasses implement draw(screen, game) and handle_click(pos, game).
    All drawing helpers are available as self.* methods, delegating to the
    module-level functions above so non-Dialog code can also import them.
    """

    def __init__(self, font, small_font=None):
        self.font = font
        self.small_font = small_font

    def draw_overlay(self, screen, alpha=180, color=(0, 0, 0)):
        draw_overlay(screen, alpha, color)

    def centered_rect(self, width, height):
        return centered_rect(width, height)

    def draw_box(self, screen, rect, border_color=(100, 140, 160), bg_color=(30, 40, 50)):
        draw_box(screen, rect, border_color, bg_color)

    def draw_button(self, screen, rect, label, font=None, normal_color=None,
                    hover_color=None, border_color=None, text_color=None):
        return draw_button(screen, rect, label, font or self.font,
                           normal_color, hover_color, border_color, text_color)

    def draw(self, screen, game):
        raise NotImplementedError

    def handle_click(self, pos, game):
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Button component
# ---------------------------------------------------------------------------

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
