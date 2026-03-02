"""Dialog shown when an AI faction convenes the Planetary Council."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog


class CouncilCalledDialog(Dialog):
    """Announcement that an AI faction has called a council vote.

    Gated on game.pending_council_call (a dict with 'faction_id' and 'proposal').
    Only an OK button — no cancel, no ESC dismiss.
    handle_click returns True when dismissed, None otherwise.
    """

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.ok_rect = None

    def draw(self, screen, game):
        if not game.pending_council_call:
            return

        self.draw_overlay(screen)

        box = self.centered_rect(520, 260)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(100, 180, 220), bg_color=(40, 45, 50))

        title_surf = self.font.render("Protocol Director", True, (100, 200, 255))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 20))

        faction_id = game.pending_council_call['faction_id']
        proposal = game.pending_council_call['proposal']
        faction = FACTION_DATA[faction_id]

        msg_lines = [
            f"{faction['$TITLE']} {faction['leader']}",
            "convenes the Planetary Council!",
            "",
            "Agenda:",
            "",
            proposal['name'],
        ]
        y_offset = box_y + 60
        for line in msg_lines:
            surf = self.small_font.render(line, True, COLOR_TEXT)
            screen.blit(surf, (box_x + box_w // 2 - surf.get_width() // 2, y_offset))
            y_offset += 22

        btn_w, btn_h = 120, 40
        btn_x = box_x + box_w // 2 - btn_w // 2
        btn_y = box_y + box_h - 55
        self.ok_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.draw_button(screen, self.ok_rect, "OK",
                         normal_color=(45, 55, 65), hover_color=(65, 85, 100),
                         border_color=(100, 140, 160))

    def handle_click(self, pos, game):
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            return True
        return None
