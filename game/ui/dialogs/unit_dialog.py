"""Unit-operation dialogs: busy former, movement overflow, debark."""

import pygame
from game.data.display_data import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                     COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)
from game.ui.components import Dialog


class BusyFormerDialog(Dialog):
    """Popup asking if the player wants to select a former that is currently terraforming."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.unit = None
        self.select_rect = None
        self.ignore_rect = None
        self.always_rect = None

    def activate(self, unit):
        self.active = True
        self.unit = unit

    def draw(self, screen, game):
        if not self.active or not self.unit:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(560, 230)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(180, 160, 80), bg_color=(30, 30, 20))

        title_surf = self.font.render("FORMER AT WORK", True, (220, 200, 100))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 30))

        action_name = ""
        if self.unit.terraforming_action:
            from game.data.terraforming_data import IMPROVEMENTS
            imp = IMPROVEMENTS.get(self.unit.terraforming_action)
            action_name = f" ({imp['name']})" if imp else ""
        msg1 = self.small_font.render("Would you like to select this unit?", True, (210, 200, 160))
        msg2 = self.small_font.render(
            f"Selecting will erase all work in progress{action_name}.", True, (180, 170, 130))
        screen.blit(msg1, (box_x + box_w // 2 - msg1.get_width() // 2, box_y + 85))
        screen.blit(msg2, (box_x + box_w // 2 - msg2.get_width() // 2, box_y + 110))

        btn_w, btn_h = 140, 46
        btn_y = box_y + box_h - 68
        gap = 14
        total_w = btn_w * 3 + gap * 2
        start_x = box_x + (box_w - total_w) // 2
        mouse = pygame.mouse.get_pos()

        self.select_rect = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        self.ignore_rect = pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h)
        self.always_rect = pygame.Rect(start_x + (btn_w + gap) * 2, btn_y, btn_w, btn_h)

        for rect, label, bg_color, border_color in [
            (self.select_rect, "Select",        (60, 100, 60),  (120, 200, 120)),
            (self.ignore_rect, "Ignore",        (60, 60, 100),  (120, 120, 200)),
            (self.always_rect, "Always Select", (80, 60, 40),   (180, 140, 80)),
        ]:
            hover = rect.collidepoint(mouse)
            bg = tuple(min(c + 20, 255) for c in bg_color) if hover else bg_color
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)
            lbl_s = self.small_font.render(label, True, COLOR_TEXT)
            screen.blit(lbl_s, (rect.centerx - lbl_s.get_width() // 2,
                                 rect.centery - lbl_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns 'select', 'ignore', 'always', or None."""
        if self.select_rect and self.select_rect.collidepoint(pos):
            self.active = False
            return 'select'
        elif self.ignore_rect and self.ignore_rect.collidepoint(pos):
            self.active = False
            return 'ignore'
        elif self.always_rect and self.always_rect.collidepoint(pos):
            self.active = False
            return 'always'
        return None


class MovementOverflowDialog(Dialog):
    """Warning popup when a unit exceeds the 100-move safety limit in one turn."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.ok_rect = None

    def activate(self):
        self.active = True

    def draw(self, screen, game):
        if not self.active:
            return
        self.draw_overlay(screen)

        box = self.centered_rect(520, 190)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(220, 80, 80), bg_color=(45, 20, 20))

        title_surf = self.font.render("MOVEMENT LIMIT REACHED", True, (255, 120, 120))
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 28))

        unit = game.pending_movement_overflow_unit
        name = unit.name if unit else "Unit"
        msg1 = self.small_font.render(
            f"{name} has been stopped after 100 moves this turn.", True, (210, 180, 180))
        msg2 = self.small_font.render(
            "Movement exhausted to prevent an infinite loop.", True, (170, 140, 140))
        screen.blit(msg1, (box_x + box_w // 2 - msg1.get_width() // 2, box_y + 80))
        screen.blit(msg2, (box_x + box_w // 2 - msg2.get_width() // 2, box_y + 104))

        ok_rect = pygame.Rect(box_x + box_w // 2 - 60, box_y + box_h - 60, 120, 44)
        self.ok_rect = ok_rect
        hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (80, 50, 50) if hover else (60, 35, 35), ok_rect, border_radius=8)
        pygame.draw.rect(screen, (220, 80, 80), ok_rect, 2, border_radius=8)
        ok_s = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_s, (ok_rect.centerx - ok_s.get_width() // 2,
                            ok_rect.centery - ok_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns True if dismissed."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            game.pending_movement_overflow_unit = None
            self.active = False
            return True
        return None


class DebarkDialog(Dialog):
    """Popup for selecting which unit to unload from a transport onto an adjacent land tile."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.active = False
        self.transport = None
        self.target_x = None
        self.target_y = None
        self.selected_unit = None
        self.unit_rects = []
        self.ok_rect = None
        self.cancel_rect = None

    def activate(self, transport, target_x, target_y):
        self.active = True
        self.transport = transport
        self.target_x = target_x
        self.target_y = target_y
        self.selected_unit = None
        self.unit_rects = []

    def draw(self, screen, game):
        if not self.active or not self.transport:
            return

        debarkable = [u for u in getattr(self.transport, 'loaded_units', [])
                      if u.moves_remaining > 0]

        popup_w = 400
        btn_h = 36
        popup_h = 80 + len(debarkable) * (btn_h + 6) + 60
        self.draw_overlay(screen)
        popup_rect = self.centered_rect(popup_w, popup_h)
        self.draw_box(screen, popup_rect)

        title = self.font.render(f"Debark from {self.transport.name}", True, (200, 220, 240))
        screen.blit(title, (popup_rect.x + 20, popup_rect.y + 16))
        sub = self.small_font.render("Select a unit to unload:", True, (160, 180, 190))
        screen.blit(sub, (popup_rect.x + 20, popup_rect.y + 44))

        self.unit_rects = []
        btn_x = popup_rect.x + 20
        btn_w = popup_w - 40
        mouse_pos = pygame.mouse.get_pos()
        y = popup_rect.y + 68

        for unit in debarkable:
            rect = pygame.Rect(btn_x, y, btn_w, btn_h)
            self.unit_rects.append((rect, unit))
            selected = (unit is self.selected_unit)
            if selected:
                bg = (50, 80, 110)
                border = COLOR_BUTTON_HIGHLIGHT
            elif rect.collidepoint(mouse_pos):
                bg = COLOR_BUTTON_HOVER
                border = COLOR_BUTTON_BORDER
            else:
                bg = COLOR_BUTTON
                border = COLOR_BUTTON_BORDER
            pygame.draw.rect(screen, bg, rect, border_radius=6)
            pygame.draw.rect(screen, border, rect, 2, border_radius=6)
            label = f"{unit.name}  (moves: {unit.moves_remaining:.0f}/{unit.max_moves()})"
            lbl_s = self.small_font.render(label, True, (220, 230, 240))
            screen.blit(lbl_s, (rect.x + 10, rect.centery - lbl_s.get_height() // 2))
            y += btn_h + 6

        ok_w = cancel_w = 120
        spacing = 16
        total = ok_w + spacing + cancel_w
        ok_x = popup_rect.centerx - total // 2
        cancel_x = ok_x + ok_w + spacing
        btn_y = popup_rect.bottom - 52

        ok_rect = pygame.Rect(ok_x, btn_y, ok_w, 40)
        cancel_rect = pygame.Rect(cancel_x, btn_y, cancel_w, 40)
        self.ok_rect = ok_rect
        self.cancel_rect = cancel_rect

        ok_enabled = self.selected_unit is not None
        ok_bg = (40, 80, 50) if ok_enabled else (35, 40, 45)
        ok_border = (80, 160, 80) if ok_enabled else (60, 70, 80)
        ok_hover_active = ok_rect.collidepoint(mouse_pos) and ok_enabled
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover_active else ok_bg,
                         ok_rect, border_radius=6)
        pygame.draw.rect(screen, ok_border, ok_rect, 2, border_radius=6)
        ok_s = self.font.render("OK", True, (220, 240, 220) if ok_enabled else (100, 110, 115))
        screen.blit(ok_s, (ok_rect.centerx - ok_s.get_width() // 2,
                            ok_rect.centery - ok_s.get_height() // 2))

        pygame.draw.rect(
            screen,
            COLOR_BUTTON_HOVER if cancel_rect.collidepoint(mouse_pos) else COLOR_BUTTON,
            cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_s = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_s, (cancel_rect.centerx - cancel_s.get_width() // 2,
                                cancel_rect.centery - cancel_s.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns ('select', unit), 'ok', 'cancel', or None."""
        for rect, unit in self.unit_rects:
            if rect.collidepoint(pos):
                self.selected_unit = unit
                return ('select', unit)
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            self.active = False
            return 'ok'
        if self.cancel_rect and self.cancel_rect.collidepoint(pos):
            self.active = False
            return 'cancel'
        return None
