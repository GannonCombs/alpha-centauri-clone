"""Terraform cost confirmation dialog."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.ui.components import Dialog


class TerraformCostDialog(Dialog):
    """Confirmation popup showing the energy cost for raise/lower land terrain operations."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.approve_rect = None
        self.reject_rect = None

    def activate(self):
        self.active = True

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(500, 210)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(100, 160, 220), bg_color=(25, 35, 45))

        pending = game.pending_terraform_cost
        action_name = ""
        if pending:
            from game.data.terraforming_data import IMPROVEMENTS
            imp = IMPROVEMENTS.get(pending['action'])
            action_name = imp['name'] if imp else pending['action']
        cost = pending['cost'] if pending else 0
        can_afford = game.energy_credits >= cost

        title_surf = self.font.render(action_name.upper(), True, (140, 200, 255))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 28))

        msg1_surf = self.small_font.render(
            f"This operation costs {cost} energy credits.", True, (200, 210, 220))
        color2 = (120, 220, 120) if can_afford else (220, 100, 100)
        msg2_surf = self.small_font.render(
            f"Current balance: {game.energy_credits} credits.", True, color2)
        screen.blit(msg1_surf, (box_x + box_w // 2 - msg1_surf.get_width() // 2, box_y + 80))
        screen.blit(msg2_surf, (box_x + box_w // 2 - msg2_surf.get_width() // 2, box_y + 105))

        btn_w, btn_h = 150, 46
        btn_y = box_y + box_h - 64
        gap = 20
        approve_rect = pygame.Rect(box_x + box_w // 2 - btn_w - gap // 2, btn_y, btn_w, btn_h)
        reject_rect  = pygame.Rect(box_x + box_w // 2 + gap // 2,          btn_y, btn_w, btn_h)
        self.approve_rect = approve_rect
        self.reject_rect  = reject_rect

        approve_bg     = (40, 90, 50)    if can_afford else (50, 50, 50)
        approve_border = (100, 200, 120) if can_afford else (100, 100, 100)
        approve_label  = "Approve"       if can_afford else "Approve (no funds)"
        mouse = pygame.mouse.get_pos()

        for rect, label, bg, border in [
            (approve_rect, approve_label, approve_bg,   approve_border),
            (reject_rect,  "Reject",      (80, 50, 50), (200, 100, 100)),
        ]:
            hover = rect.collidepoint(mouse)
            draw_bg = tuple(min(c + 20, 255) for c in bg) if hover else bg
            pygame.draw.rect(screen, draw_bg, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)
            lbl_s = self.small_font.render(label, True, COLOR_TEXT)
            screen.blit(lbl_s, (rect.centerx - lbl_s.get_width() // 2,
                                 rect.centery - lbl_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns 'approve', 'reject', or None."""
        if self.approve_rect and self.approve_rect.collidepoint(pos):
            self.active = False
            return 'approve'
        elif self.reject_rect and self.reject_rect.collidepoint(pos):
            game.pending_terraform_cost = None
            self.active = False
            return 'reject'
        return None
