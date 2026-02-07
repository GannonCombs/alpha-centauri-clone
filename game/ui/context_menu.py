# ui/context_menu.py
"""Context menu for unit actions.

This module provides a right-click context menu for performing unit actions
like long range fire (artillery), unit actions, etc.
"""

import pygame


class ContextMenu:
    """Manages right-click context menus for unit actions."""

    def __init__(self, font):
        """Initialize context menu.

        Args:
            font: Pygame font for menu text
        """
        self.font = font
        self.visible = False
        self.x = 0
        self.y = 0
        self.options = []  # List of (label, callback) tuples
        self.width = 200
        self.option_height = 30
        self.hover_index = -1

    def show(self, x, y, options):
        """Show context menu at position with given options.

        Args:
            x (int): Screen X coordinate
            y (int): Screen Y coordinate
            options (list): List of (label, callback) tuples
        """
        self.visible = True
        self.x = x
        self.y = y
        self.options = options
        self.hover_index = -1

        # Adjust position if menu would go off screen
        menu_height = len(options) * self.option_height
        if self.y + menu_height > pygame.display.get_surface().get_height():
            self.y = pygame.display.get_surface().get_height() - menu_height

        if self.x + self.width > pygame.display.get_surface().get_width():
            self.x = pygame.display.get_surface().get_width() - self.width

    def hide(self):
        """Hide the context menu."""
        self.visible = False
        self.options = []
        self.hover_index = -1

    def handle_event(self, event):
        """Handle mouse events for the context menu.

        Args:
            event: Pygame event

        Returns:
            bool: True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            # Check if mouse is over menu
            if (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + len(self.options) * self.option_height):
                # Calculate which option is hovered
                relative_y = mouse_y - self.y
                self.hover_index = relative_y // self.option_height
                return True
            else:
                self.hover_index = -1
            return False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check if clicked on menu
            if (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + len(self.options) * self.option_height):
                # Calculate which option was clicked
                relative_y = mouse_y - self.y
                clicked_index = relative_y // self.option_height

                if 0 <= clicked_index < len(self.options):
                    # Execute callback
                    label, callback = self.options[clicked_index]
                    self.hide()
                    callback()
                    return True
            else:
                # Clicked outside menu - close it
                self.hide()
                return True

        return False

    def draw(self, screen):
        """Draw the context menu.

        Args:
            screen: Pygame screen surface
        """
        if not self.visible or not self.options:
            return

        menu_height = len(self.options) * self.option_height

        # Draw background
        background_rect = pygame.Rect(self.x, self.y, self.width, menu_height)
        pygame.draw.rect(screen, (40, 40, 40), background_rect)
        pygame.draw.rect(screen, (200, 200, 200), background_rect, 2)

        # Draw options
        for i, (label, callback) in enumerate(self.options):
            option_y = self.y + i * self.option_height

            # Highlight hovered option
            if i == self.hover_index:
                highlight_rect = pygame.Rect(self.x, option_y, self.width, self.option_height)
                pygame.draw.rect(screen, (70, 70, 70), highlight_rect)

            # Draw text
            text_surface = self.font.render(label, True, (255, 255, 255))
            text_rect = text_surface.get_rect(midleft=(self.x + 10, option_y + self.option_height // 2))
            screen.blit(text_surface, text_rect)

            # Draw separator line between options
            if i < len(self.options) - 1:
                pygame.draw.line(screen, (100, 100, 100),
                               (self.x, option_y + self.option_height),
                               (self.x + self.width, option_y + self.option_height), 1)
