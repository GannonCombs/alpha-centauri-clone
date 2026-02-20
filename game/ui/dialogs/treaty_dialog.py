"""Treaty-related dialogs: player breaking a treaty, and AI surprise attack notification."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class BreakTreatyDialog(Dialog):
    """Confirmation popup when the player tries to attack a faction they have a treaty/truce with."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.target_faction = None
        self.pending_battle = None
        self.relation = "Truce"   # 'Truce' or anything else (displayed as 'Treaty')
        self.ok_rect = None
        self.cancel_rect = None

    def activate(self, target_faction, pending_battle=None, relation="Truce"):
        self.active = True
        self.target_faction = target_faction
        self.pending_battle = pending_battle
        self.relation = relation

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(600, 250)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(220, 100, 100), bg_color=(40, 30, 30))

        if self.relation == "Truce":
            title_text, relation_word = "BREAK TRUCE", "truce"
        else:
            title_text, relation_word = "BREAK TREATY", "treaty"

        title_surf = self.font.render(title_text, True, (255, 150, 150))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))

        faction_name = FACTION_DATA[self.target_faction]['name']
        msg1 = self.small_font.render(f"Are you sure you wish to attack {faction_name}?", True, COLOR_TEXT)
        msg2 = self.small_font.render(f"This will break your {relation_word} and result in VENDETTA.",
                                      True, (255, 200, 200))
        screen.blit(msg1, (box_x + box_w // 2 - msg1.get_width() // 2, box_y + 100))
        screen.blit(msg2, (box_x + box_w // 2 - msg2.get_width() // 2, box_y + 130))

        btn_w, btn_h = 140, 50
        btn_y = box_y + box_h - 80
        mouse = pygame.mouse.get_pos()

        ok_rect = pygame.Rect(box_x + box_w // 2 - btn_w - 10, btn_y, btn_w, btn_h)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (85, 60, 60) if is_hover else (65, 45, 45), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (220, 100, 100), ok_rect, 3, border_radius=8)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - 10))

        cancel_rect = pygame.Rect(box_x + box_w // 2 + 10, btn_y, btn_w, btn_h)
        self.cancel_rect = cancel_rect
        is_hover = cancel_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65), cancel_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), cancel_rect, 3, border_radius=8)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_text, (cancel_rect.centerx - cancel_text.get_width() // 2, cancel_rect.centery - 10))

    def handle_click(self, pos, game):
        """Returns 'ok', 'cancel', or None."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            return 'ok'
        elif self.cancel_rect and self.cancel_rect.collidepoint(pos):
            self.active = False
            self.pending_battle = None
            self.target_faction = None
            return 'cancel'
        return None


class SurpriseAttackDialog(Dialog):
    """Notification popup when an AI faction breaks a treaty and launches a surprise attack."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.faction = None
        self.ok_rect = None

    def activate(self, faction_id):
        self.active = True
        self.faction = faction_id

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(600, 220)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(220, 100, 100), bg_color=(40, 30, 30))

        faction_name = FACTION_DATA[self.faction]['name'] if self.faction is not None else "Unknown"
        msg = self.font.render(f"{faction_name} has launched a surprise attack!", True, (255, 150, 150))
        screen.blit(msg, (box_x + box_w // 2 - msg.get_width() // 2, box_y + 70))

        btn_w, btn_h = 140, 50
        btn_y = box_y + box_h - 80
        ok_rect = pygame.Rect(box_x + box_w // 2 - btn_w // 2, btn_y, btn_w, btn_h)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (85, 60, 60) if is_hover else (65, 45, 45), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (220, 100, 100), ok_rect, 3, border_radius=8)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - 10))

    def handle_click(self, pos, game):
        """Returns True if dismissed."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            return True
        return None
