"""Pact-related dialogs: evacuation notification and pact-pronounce."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class PactEvacuationDialog(Dialog):
    """Notification popup after units are evacuated from former pact territory."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.count = 0
        self.pending_battle = None
        self.ok_rect = None

    def activate(self, count, pending_battle=None):
        self.active = True
        self.count = count
        self.pending_battle = pending_battle

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(700, 250)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(100, 140, 180))

        title_surf = self.font.render("PACT DISSOLVED", True, (200, 220, 255))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 30))

        unit_word = "unit" if self.count == 1 else "units"
        msg1 = self.small_font.render(
            f"With the pact dissolved, {self.count} {unit_word}", True, (180, 200, 220))
        msg2 = self.small_font.render("returned to your nearest base.", True, (180, 200, 220))
        screen.blit(msg1, (box_x + box_w // 2 - msg1.get_width() // 2, box_y + 85))
        screen.blit(msg2, (box_x + box_w // 2 - msg2.get_width() // 2, box_y + 115))

        ok_rect = pygame.Rect(box_x + box_w // 2 - 70, box_y + box_h - 80, 140, 50)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (70, 90, 110) if is_hover else (50, 70, 90), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 180), ok_rect, 3, border_radius=8)
        ok_s = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_s, (ok_rect.centerx - ok_s.get_width() // 2, ok_rect.centery - 10))

    def handle_click(self, pos, game):
        """Returns True if dismissed."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            if self.pending_battle:
                game.combat.pending_battle = self.pending_battle
                self.pending_battle = None
            self.count = 0
            return True
        return None


class PactPronounceDialog(Dialog):
    """Notification that a pact partner has declared Vendetta on a surprise attacker."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.current = None   # {'pactbro_id': int, 'attacker_id': int}
        self.ok_rect = None

    def activate(self, info):
        self.active = True
        self.current = info

    def draw(self, screen, game):
        if not self.active or not self.current:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(620, 230)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(200, 160, 80), bg_color=(35, 30, 20))

        title_surf = self.font.render("PACT RESPONSE", True, (240, 200, 100))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 24))

        bro_name = FACTION_DATA[self.current['pactbro_id']]['name']
        atk_name = FACTION_DATA[self.current['attacker_id']]['name']
        gender = FACTION_DATA[self.current['pactbro_id']].get('gender', 'M')
        sibling = 'Pact Sister' if gender == 'F' else 'Pact Brother'

        for i, line in enumerate([
            f"On behalf of your pact, {bro_name}",
            f"({sibling}) has pronounced Vendetta on {atk_name}!",
        ]):
            ls = self.small_font.render(line, True, (220, 210, 180))
            screen.blit(ls, (box_x + box_w // 2 - ls.get_width() // 2, box_y + 90 + i * 24))

        ok_rect = pygame.Rect(box_x + box_w // 2 - 70, box_y + box_h - 64, 140, 46)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (90, 70, 30) if is_hover else (65, 50, 20), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 160, 80), ok_rect, 3, border_radius=8)
        ok_s = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_s, (ok_rect.centerx - ok_s.get_width() // 2,
                            ok_rect.centery - ok_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns True if dismissed."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            self.current = None
            return True
        return None
