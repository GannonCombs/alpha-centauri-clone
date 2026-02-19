"""Exit confirmation dialog."""

import pygame
from game.ui.components import Dialog


class ExitDialog(Dialog):
    """Manages the exit confirmation dialog."""

    def __init__(self, font, message=None):
        super().__init__(font)
        self.show_dialog = False
        self.ok_button_rect = None
        self.cancel_button_rect = None
        self.message = message or "Are you sure you want to exit?"

    def show(self):
        """Show the exit confirmation dialog."""
        self.show_dialog = True

    def hide(self):
        """Hide the exit confirmation dialog."""
        self.show_dialog = False

    def draw(self, screen, screen_width, screen_height):
        """Draw the exit confirmation dialog."""
        if not self.show_dialog:
            return

        self.draw_overlay(screen, alpha=150)

        # Small dialog box
        dialog_w = 400
        dialog_h = 200
        dialog_x = screen_width // 2 - dialog_w // 2
        dialog_y = screen_height // 2 - dialog_h // 2

        # Dialog background
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 140, 160), dialog_rect, 3, border_radius=10)

        # Message
        message_surf = self.font.render(self.message, True, (220, 230, 240))
        screen.blit(message_surf, (dialog_x + dialog_w // 2 - message_surf.get_width() // 2, dialog_y + 50))

        # Buttons
        button_w = 120
        button_h = 50
        button_y = dialog_y + dialog_h - 80

        # OK button
        ok_x = dialog_x + dialog_w // 2 - button_w - 10
        self.ok_button_rect = pygame.Rect(ok_x, button_y, button_w, button_h)

        ok_hover = self.ok_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (110, 70, 70) if ok_hover else (90, 50, 50),
                        self.ok_button_rect, border_radius=6)
        pygame.draw.rect(screen, (180, 100, 100), self.ok_button_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, (220, 230, 240))
        screen.blit(ok_text, (self.ok_button_rect.centerx - ok_text.get_width() // 2,
                             self.ok_button_rect.centery - 10))

        # Cancel button
        cancel_x = dialog_x + dialog_w // 2 + 10
        self.cancel_button_rect = pygame.Rect(cancel_x, button_y, button_w, button_h)

        cancel_hover = self.cancel_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if cancel_hover else (50, 70, 90),
                        self.cancel_button_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 140, 180), self.cancel_button_rect, 2, border_radius=6)

        cancel_text = self.font.render("Cancel", True, (220, 230, 240))
        screen.blit(cancel_text, (self.cancel_button_rect.centerx - cancel_text.get_width() // 2,
                                 self.cancel_button_rect.centery - 10))

    def handle_event(self, event):
        """Handle events for the exit dialog.

        Returns:
            str: 'exit' if OK clicked, 'cancel' if Cancel clicked, None otherwise
        """
        if not self.show_dialog:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ok_button_rect and self.ok_button_rect.collidepoint(event.pos):
                return 'exit'
            elif self.cancel_button_rect and self.cancel_button_rect.collidepoint(event.pos):
                self.hide()
                return 'cancel'
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return 'cancel'
            elif event.key == pygame.K_RETURN:
                return 'exit'

        return None
