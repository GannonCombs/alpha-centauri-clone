"""Pact renouncement notification dialog."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class RenouncePactDialog(Dialog):
    """Popup shown when player renounces a pact — AI faction responds."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.faction_id = None
        self.ok_rect = None

    def activate(self, faction_id):
        self.active = True
        self.faction_id = faction_id

    def draw(self, screen, game):
        if not self.active or self.faction_id is None:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(660, 300)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(120, 140, 180), bg_color=(30, 35, 45))

        faction_data = FACTION_DATA[self.faction_id]
        faction_color = faction_data.get('color', (140, 160, 200))

        # Portrait box (top-left of dialog)
        portrait_size = 80
        portrait_rect = pygame.Rect(box_x + 14, box_y + 14, portrait_size, portrait_size)
        pygame.draw.rect(screen, (15, 20, 25), portrait_rect)
        pygame.draw.rect(screen, faction_color, portrait_rect, 3)
        inner = pygame.Rect(portrait_rect.x + 6, portrait_rect.y + 6,
                            portrait_size - 12, portrait_size - 12)
        pygame.draw.rect(screen, faction_color, inner, 1)
        lbl = self.small_font.render("[PORTRAIT]", True, (100, 110, 120))
        screen.blit(lbl, (portrait_rect.centerx - lbl.get_width() // 2,
                          portrait_rect.centery - lbl.get_height() // 2))

        # Title and leader name to the right of the portrait
        title_x = portrait_rect.right + 14
        title = f"PACT RENOUNCED — {faction_data['name'].upper()}"
        title_surf = self.font.render(title, True, (180, 200, 240))
        screen.blit(title_surf, (title_x, box_y + 24))

        leader = faction_data.get('leader', faction_data['name'])
        leader_surf = self.small_font.render(leader, True, faction_color)
        screen.blit(leader_surf, (title_x, box_y + 52))

        # Quote (word-wrapped), below the portrait
        player_fd = FACTION_DATA[game.player_faction_id]
        player_gender = player_fd.get('gender', 'M')
        pact_sibling = "Pact Sister" if player_gender == 'F' else "Pact Brother"
        player_title = player_fd.get('$TITLE', '')
        player_name  = player_fd.get('$FULLNAME', player_fd.get('leader', ''))
        player_display = f"{player_title} {player_name}".strip()
        raw_quote = (f'"I have little use for a false {pact_sibling}, '
                     f'{player_display}. '
                     f'Tread carefully when next we meet."')

        words = raw_quote.split()
        lines, current = [], ''
        max_w = box_w - 60
        for word in words:
            test = f"{current} {word}".strip()
            if self.small_font.size(test)[0] <= max_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        quote_y = portrait_rect.bottom + 14
        for i, line in enumerate(lines):
            ls = self.small_font.render(line, True, (200, 210, 230))
            screen.blit(ls, (box_x + box_w // 2 - ls.get_width() // 2, quote_y + i * 22))

        # OK button
        btn_w, btn_h = 140, 46
        ok_x = box_x + box_w // 2 - btn_w // 2
        btn_y = box_y + box_h - 68
        ok_rect = pygame.Rect(ok_x, btn_y, btn_w, btn_h)
        self.ok_rect = ok_rect
        is_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (60, 80, 110) if is_hover else (40, 55, 80), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 150, 200), ok_rect, 3, border_radius=8)
        ok_s = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_s, (ok_rect.centerx - ok_s.get_width() // 2,
                            ok_rect.centery - ok_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns True if dismissed."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            return True
        return None
