"""New unit designs available notification dialog."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.ui.components import Dialog


class NewDesignsDialog(Dialog):
    """Modal popup shown when new technology unlocks improved unit designs."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.view_rect = None
        self.ignore_rect = None

    def activate(self):
        self.active = True

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(600, 250)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(100, 180, 140))

        title_surf = self.font.render("NEW UNIT DESIGNS AVAILABLE", True, (180, 240, 180))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 40))

        msg1 = self.small_font.render("New technology has unlocked improved unit designs.", True, COLOR_TEXT)
        msg2 = self.small_font.render("Visit the Design Workshop to review them.", True, COLOR_TEXT)
        screen.blit(msg1, (box_x + box_w // 2 - msg1.get_width() // 2, box_y + 100))
        screen.blit(msg2, (box_x + box_w // 2 - msg2.get_width() // 2, box_y + 130))

        btn_w, btn_h = 180, 50
        btn_y = box_y + box_h - 80
        mouse = pygame.mouse.get_pos()

        view_rect = pygame.Rect(box_x + box_w // 2 - btn_w - 10, btn_y, btn_w, btn_h)
        self.view_rect = view_rect
        is_hover = view_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (65, 100, 85) if is_hover else (45, 75, 65), view_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 180, 140), view_rect, 3, border_radius=8)
        vt = self.font.render("View Designs", True, COLOR_TEXT)
        screen.blit(vt, (view_rect.centerx - vt.get_width() // 2, view_rect.centery - 10))

        ignore_rect = pygame.Rect(box_x + box_w // 2 + 10, btn_y, btn_w, btn_h)
        self.ignore_rect = ignore_rect
        is_hover = ignore_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (65, 85, 100) if is_hover else (45, 55, 65), ignore_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), ignore_rect, 3, border_radius=8)
        it = self.font.render("Ignore", True, COLOR_TEXT)
        screen.blit(it, (ignore_rect.centerx - it.get_width() // 2, ignore_rect.centery - 10))

    def handle_click(self, pos, game):
        """Returns 'view', 'ignore', or None."""
        if self.view_rect and self.view_rect.collidepoint(pos):
            self.active = False
            game.new_designs_available = False
            return 'view'
        elif self.ignore_rect and self.ignore_rect.collidepoint(pos):
            self.active = False
            game.new_designs_available = False
            return 'ignore'
        return None
