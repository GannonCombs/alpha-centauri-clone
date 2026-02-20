"""Faction elimination notification dialog."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class EliminationDialog(Dialog):
    """Modal popup shown when a faction is completely eliminated."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.faction_id = None
        self.ok_rect = None

    def activate(self, faction_id):
        self.active = True
        self.faction_id = faction_id

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box_w, box_h = 600, 250
        box_x = pygame.display.get_surface().get_width() // 2 - box_w // 2
        box_y = pygame.display.get_surface().get_height() // 2 - box_h // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (40, 30, 30), box_rect, border_radius=12)
        pygame.draw.rect(screen, (180, 100, 100), box_rect, 3, border_radius=12)

        if self.faction_id is not None and self.faction_id < len(FACTION_DATA):
            faction = FACTION_DATA[self.faction_id]
            title_surf = self.font.render(f"{faction['name']} ELIMINATED", True, (240, 180, 180))
            screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))
            msg1 = self.small_font.render(f"{faction['leader']} has been defeated.", True, COLOR_TEXT)
            msg2 = self.small_font.render("All bases have been destroyed.", True, COLOR_TEXT)
            screen.blit(msg1, (box_x + box_w // 2 - msg1.get_width() // 2, box_y + 100))
            screen.blit(msg2, (box_x + box_w // 2 - msg2.get_width() // 2, box_y + 130))

        btn_w, btn_h = 180, 50
        btn_y = box_y + box_h - 80
        ok_rect = pygame.Rect(box_x + box_w // 2 - btn_w // 2, btn_y, btn_w, btn_h)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), ok_rect, 3, border_radius=8)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - 10))

    def handle_click(self, pos, game):
        """Dismiss popup. Returns True if clicked."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            if game.pending_faction_eliminations:
                game.pending_faction_eliminations.pop(0)
            return True
        return None
