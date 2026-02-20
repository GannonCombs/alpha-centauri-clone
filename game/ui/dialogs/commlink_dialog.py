"""Commlink incoming-request dialog."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class CommLinkRequestDialog(Dialog):
    """Popup shown when an AI faction wants to open a commlink channel."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.other_faction_id = None
        self.player_id = None
        self.answer_rect = None
        self.ignore_rect = None

    def activate(self, other_faction_id, player_id):
        self.active = True
        self.other_faction_id = other_faction_id
        self.player_id = player_id

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(600, 250)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box)

        if self.other_faction_id is not None and self.other_faction_id < len(FACTION_DATA):
            faction = FACTION_DATA[self.other_faction_id]
            title_surf = self.font.render(
                f"{faction['leader']} is requesting to speak with you", True, (180, 220, 240))
            screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))
            msg_surf = self.small_font.render(
                "A representative wishes to open communications.", True, COLOR_TEXT)
            screen.blit(msg_surf, (box_x + box_w // 2 - msg_surf.get_width() // 2, box_y + 100))

        btn_w, btn_h = 180, 50
        btn_y = box_y + box_h - 80
        mouse = pygame.mouse.get_pos()

        answer_rect = pygame.Rect(box_x + box_w // 2 - btn_w - 10, btn_y, btn_w, btn_h)
        self.answer_rect = answer_rect
        hover = answer_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (65, 100, 85) if hover else (45, 75, 65), answer_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 180, 140), answer_rect, 3, border_radius=8)
        ans_s = self.font.render("Answer", True, COLOR_TEXT)
        screen.blit(ans_s, (answer_rect.centerx - ans_s.get_width() // 2, answer_rect.centery - 10))

        ignore_rect = pygame.Rect(box_x + box_w // 2 + 10, btn_y, btn_w, btn_h)
        self.ignore_rect = ignore_rect
        hover = ignore_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (100, 65, 65) if hover else (75, 45, 45), ignore_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 100, 100), ignore_rect, 3, border_radius=8)
        ign_s = self.font.render("Ignore", True, COLOR_TEXT)
        screen.blit(ign_s, (ignore_rect.centerx - ign_s.get_width() // 2, ignore_rect.centery - 10))

    def handle_click(self, pos, game):
        """Returns 'answer', 'ignore', or None."""
        if self.answer_rect and self.answer_rect.collidepoint(pos):
            self.active = False
            if game.pending_commlink_requests:
                game.pending_commlink_requests.pop(0)
            return 'answer'
        elif self.ignore_rect and self.ignore_rect.collidepoint(pos):
            self.active = False
            if game.pending_commlink_requests:
                game.pending_commlink_requests.pop(0)
            return 'ignore'
        return None
