"""Alien Artifact / Network Node link dialog."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.ui.components import Dialog


class ArtifactLinkDialog(Dialog):
    """Yes/no popup asking the player whether to link an Alien Artifact to a Network Node."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.yes_rect = None
        self.no_rect = None

    def activate(self):
        self.active = True

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(620, 240)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(80, 180, 220), bg_color=(20, 35, 50))

        title_surf = self.font.render("ALIEN ARTIFACT", True, (120, 220, 255))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 30))

        link = game.pending_artifact_link
        base_name = link['base'].name if link else "this base"
        msg1 = self.small_font.render(f"An Alien Artifact is present at {base_name}.", True, (180, 210, 230))
        msg2 = self.small_font.render("What would you like to do with it?", True, (180, 210, 230))
        screen.blit(msg1, (box_x + box_w // 2 - msg1.get_width() // 2, box_y + 90))
        screen.blit(msg2, (box_x + box_w // 2 - msg2.get_width() // 2, box_y + 115))

        btn_w, btn_h = 180, 50
        btn_y = box_y + box_h - 75
        yes_rect = pygame.Rect(box_x + box_w // 2 - btn_w - 20, btn_y, btn_w, btn_h)
        no_rect  = pygame.Rect(box_x + box_w // 2 + 20,          btn_y, btn_w, btn_h)
        self.yes_rect = yes_rect
        self.no_rect  = no_rect

        for rect, label, bg_color in [
            (yes_rect, "Link to Network Node", (60, 120, 80)),
            (no_rect,  "Keep for later",        (60, 80, 80)),
        ]:
            hover = rect.collidepoint(pygame.mouse.get_pos())
            bg = tuple(min(c + 20, 255) for c in bg_color) if hover else bg_color
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            border = (120, 200, 140) if label.startswith("Link") else (200, 100, 100)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)
            lbl = self.font.render(label, True, COLOR_TEXT)
            screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - lbl.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns 'yes', 'no', or None."""
        if self.yes_rect and self.yes_rect.collidepoint(pos):
            self.active = False
            return 'yes'
        elif self.no_rect and self.no_rect.collidepoint(pos):
            game.pending_artifact_link = None
            self.active = False
            return 'no'
        return None
