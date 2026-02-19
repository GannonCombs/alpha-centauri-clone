"""SecretProjectDialog — modal popup for secret project started / 1-turn-away warning."""

import pygame
from game.data.display_data import COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_BORDER
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class SecretProjectDialog(Dialog):
    """Modal popup shown when an AI faction starts or is one turn from completing a secret project."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.ok_rect = None

    def draw(self, screen, game):
        """Draw the notification popup for the first queued secret project notification."""
        notifications = getattr(game, 'secret_project_notifications', [])
        if not notifications:
            return
        notif = notifications[0]
        notif_type = notif.get('type', 'started')
        project_name = notif['project_name']
        faction_id = notif['faction_id']
        faction = FACTION_DATA[faction_id] if faction_id < len(FACTION_DATA) else {}
        faction_name = faction.get('name', 'Unknown')
        faction_color = faction.get('color', (180, 160, 100))

        self.draw_overlay(screen, alpha=160)

        if notif_type == 'warning':
            player_also = notif.get('player_also_building', False)
            popup_h = 220 if player_also else 190
            popup_w = 500
            header_text = "SECRET PROJECT ALERT"
            header_color = (255, 180, 60)
            border_color = (200, 140, 40)
            line1 = f"{faction_name} is one turn away"
            line2 = f"from completing {project_name}."
            line3 = "You are also building it — rush production!" if player_also else None
        else:
            popup_h = 190
            popup_w = 480
            header_text = "SECRET PROJECT BEGUN"
            header_color = (200, 210, 255)
            border_color = faction_color
            line1 = f"{faction_name} has begun work on"
            line2 = project_name + "."
            line3 = None

        popup_rect = self.centered_rect(popup_w, popup_h)
        self.draw_box(screen, popup_rect, border_color=border_color)

        header = self.font.render(header_text, True, header_color)
        screen.blit(header, (popup_rect.centerx - header.get_width() // 2, popup_rect.y + 18))

        ty = popup_rect.y + 56
        l1 = self.small_font.render(line1, True, COLOR_TEXT)
        screen.blit(l1, (popup_rect.centerx - l1.get_width() // 2, ty))
        ty += 20
        l2 = self.small_font.render(line2, True, faction_color)
        screen.blit(l2, (popup_rect.centerx - l2.get_width() // 2, ty))
        if line3:
            ty += 22
            l3 = self.small_font.render(line3, True, (255, 220, 100))
            screen.blit(l3, (popup_rect.centerx - l3.get_width() // 2, ty))

        ok_w, ok_h = 90, 34
        ok_rect = pygame.Rect(popup_rect.centerx - ok_w // 2, popup_rect.y + popup_h - 50, ok_w, ok_h)
        self.ok_rect = ok_rect
        self.draw_button(screen, ok_rect, "OK")

    def handle_click(self, pos, game):
        """Dismiss the current notification if OK was clicked. Returns True if dismissed."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            game.secret_project_notifications.pop(0)
            return True
        return False
