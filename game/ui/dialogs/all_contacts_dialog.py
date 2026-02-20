"""Dialog shown when the player establishes contact with all living factions."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.ui.components import Dialog


class AllContactsDialog(Dialog):
    """Notification that the player has obtained commlinks with every faction.

    Gated on game.pending_all_contacts_popup.
    handle_click returns True when dismissed, None otherwise.
    """

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.continue_rect = None

    def draw(self, screen, game):
        if not game.pending_all_contacts_popup:
            return

        self.draw_overlay(screen)

        box = self.centered_rect(520, 280)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(100, 180, 220), bg_color=(40, 45, 50))

        title_surf = self.font.render("DIPLOMATIC MILESTONE", True, (100, 200, 255))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 20))

        msg_lines = [
            "You have established contact with",
            "all living factions on Planet!",
            "",
            "You may now call the Planetary Council",
            "to propose global resolutions.",
        ]
        y_offset = box_y + 70
        for line in msg_lines:
            surf = self.small_font.render(line, True, COLOR_TEXT)
            screen.blit(surf, (box_x + box_w // 2 - surf.get_width() // 2, y_offset))
            y_offset += 25

        btn_w, btn_h = 160, 45
        btn_x = box_x + box_w // 2 - btn_w // 2
        btn_y = box_y + box_h - 65
        self.continue_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        mouse = pygame.mouse.get_pos()
        hover = self.continue_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (65, 85, 100) if hover else (45, 55, 65),
                         self.continue_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), self.continue_rect, 3, border_radius=8)
        cont_surf = self.font.render("Continue", True, COLOR_TEXT)
        screen.blit(cont_surf, (self.continue_rect.centerx - cont_surf.get_width() // 2,
                                self.continue_rect.centery - cont_surf.get_height() // 2))

    def handle_click(self, pos, game):
        if self.continue_rect and self.continue_rect.collidepoint(pos):
            game.pending_all_contacts_popup = False
            return True
        return None
