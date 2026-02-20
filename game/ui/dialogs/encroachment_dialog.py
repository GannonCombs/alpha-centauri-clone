"""Encroachment warning dialog — founding a base on another faction's territory."""

import pygame
from game.data.display_data import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                     COLOR_BUTTON_BORDER)
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class EncroachmentDialog(Dialog):
    """Popup when the player tries to found a base on another faction's territory."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.faction_id = None
        self.unit = None
        self.leave_rect = None
        self.build_rect = None

    def activate(self, faction_id, unit):
        self.active = True
        self.faction_id = faction_id
        self.unit = unit

    def draw(self, screen, game):
        if not self.active or self.faction_id is None:
            return

        faction = FACTION_DATA[self.faction_id] if self.faction_id < len(FACTION_DATA) else {}
        faction_name = faction.get('name', 'Unknown')
        leader_name = faction.get('leader', faction_name)
        faction_color = faction.get('color', (180, 160, 100))

        self.draw_overlay(screen)

        popup_w, popup_h = 560, 240
        popup_rect = self.centered_rect(popup_w, popup_h)
        self.draw_box(screen, popup_rect, border_color=faction_color)

        px, py = popup_rect.x, popup_rect.y

        # Portrait box (top-left of dialog)
        portrait_size = 64
        portrait_rect = pygame.Rect(px + 12, py + 12, portrait_size, portrait_size)
        pygame.draw.rect(screen, (15, 20, 25), portrait_rect)
        pygame.draw.rect(screen, faction_color, portrait_rect, 3)
        inner = pygame.Rect(portrait_rect.x + 5, portrait_rect.y + 5,
                            portrait_size - 10, portrait_size - 10)
        pygame.draw.rect(screen, faction_color, inner, 1)
        lbl = self.small_font.render("[PORTRAIT]", True, (100, 110, 120))
        screen.blit(lbl, (portrait_rect.centerx - lbl.get_width() // 2,
                          portrait_rect.centery - lbl.get_height() // 2))

        # Faction name header to the right of the portrait
        header_x = portrait_rect.right + 12
        header_surf = self.font.render(f"{leader_name} ({faction_name})", True, faction_color)
        screen.blit(header_surf, (header_x, py + 16))

        # Message
        player_faction = FACTION_DATA[game.player_faction_id] if game.player_faction_id < len(FACTION_DATA) else {}
        player_name = player_faction.get('name', 'you')
        msg1 = f"This is our land, {player_name}, and we will"
        msg2 = "not have you building bases on it."
        screen.blit(self.small_font.render(msg1, True, COLOR_TEXT), (px + 20, py + 100))
        screen.blit(self.small_font.render(msg2, True, COLOR_TEXT), (px + 20, py + 120))

        # Buttons
        btn_w, btn_h = 200, 40
        btn_y = py + popup_h - 60
        leave_rect = pygame.Rect(px + popup_w // 2 - btn_w - 10, btn_y, btn_w, btn_h)
        build_rect = pygame.Rect(px + popup_w // 2 + 10,          btn_y, btn_w, btn_h)
        self.leave_rect = leave_rect
        self.build_rect = build_rect

        mouse_pos = pygame.mouse.get_pos()

        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if leave_rect.collidepoint(mouse_pos) else COLOR_BUTTON,
                         leave_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, leave_rect, 2, border_radius=6)
        leave_surf = self.small_font.render("Fine, we'll leave.", True, COLOR_TEXT)
        screen.blit(leave_surf, (leave_rect.centerx - leave_surf.get_width() // 2,
                                 leave_rect.centery - leave_surf.get_height() // 2))

        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if build_rect.collidepoint(mouse_pos) else (80, 30, 30),
                         build_rect, border_radius=6)
        pygame.draw.rect(screen, (180, 60, 60), build_rect, 2, border_radius=6)
        build_surf = self.small_font.render("We'll build here.", True, (255, 160, 160))
        screen.blit(build_surf, (build_rect.centerx - build_surf.get_width() // 2,
                                 build_rect.centery - build_surf.get_height() // 2))

        warn = self.small_font.render("(Vendetta + -1 Integrity)", True, (200, 100, 100))
        screen.blit(warn, (build_rect.centerx - warn.get_width() // 2, build_rect.bottom + 4))

    def handle_click(self, pos, game):
        """Returns 'leave', 'build', or None.

        On 'build', faction_id and unit remain set for UIManager to read before clearing.
        """
        if self.leave_rect and self.leave_rect.collidepoint(pos):
            self.active = False
            self.faction_id = None
            self.unit = None
            return 'leave'
        if self.build_rect and self.build_rect.collidepoint(pos):
            self.active = False
            return 'build'
        return None
