"""Probe team action dialog — multi-stage espionage interface."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.data.faction_data import FACTION_DATA
from game.ui.components import Dialog

# Stage constants
STAGE_CONFIRM = 'confirm'   # #RISKEXCUSE — "probe team detected" risk warning (non-war only)
STAGE_MENU    = 'menu'      # #PROBEMENU  — action selection (8 options)
# Future stages: STAGE_SUB_OPTIONS, STAGE_RESULT


class ProbeDialog(Dialog):
    """Multi-stage probe team espionage dialog.

    Stage flow:
      Not at war:  STAGE_CONFIRM → STAGE_MENU → (sub-options) → result
      At war:      STAGE_MENU → (sub-options) → result

    Does not own an `active` flag — UIManager gates with `game.pending_probe_action`.

    handle_click returns:
      'abort'   — player aborted (any stage); UIManager cancels the probe move
      'proceed' — STAGE_CONFIRM confirmed; dialog advances to STAGE_MENU internally
      None      — click consumed but no stage transition
    """

    # --- Visual style constants ---
    _BG_COLOR     = (18, 24, 20)
    _BORDER_COLOR = (70, 110, 75)
    _TITLE_COLOR  = (110, 175, 115)
    _BODY_COLOR   = (185, 210, 185)

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.stage = STAGE_CONFIRM
        self._abort_rect   = None
        self._proceed_rect = None

    def _faction_data(self, faction_id):
        if 0 <= faction_id < len(FACTION_DATA):
            return FACTION_DATA[faction_id]
        return {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def activate(self, probe_unit, target_base, target_faction_id, at_war):
        """Called by UIManager when a probe unit enters an enemy base tile."""
        self.stage = STAGE_MENU if at_war else STAGE_CONFIRM

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, screen, game):
        probe_data = game.pending_probe_action
        if not probe_data:
            return

        if self.stage == STAGE_CONFIRM:
            self._draw_confirm(screen, probe_data)
        elif self.stage == STAGE_MENU:
            self._draw_menu_stub(screen, probe_data)

    def _draw_confirm(self, screen, probe_data):
        """#RISKEXCUSE — risk warning before probing a non-enemy faction."""
        self.draw_overlay(screen)

        box = self.centered_rect(580, 230)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=self._BORDER_COLOR, bg_color=self._BG_COLOR)

        # Header
        title_surf = self.font.render("OPERATIONS DIRECTOR", True, self._TITLE_COLOR)
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 18))

        # Separator
        sep_y = box_y + 42
        pygame.draw.line(screen, self._BORDER_COLOR, (box_x + 20, sep_y), (box_x + box_w - 20, sep_y), 1)

        # Body text — #RISKEXCUSE
        fd = self._faction_data(probe_data['faction_id'])
        title = fd.get('$TITLE', '')
        fullname = fd.get('$FULLNAME', fd.get('leader', 'the enemy leader'))
        leader = f"{title} {fullname}".strip()

        line1 = "If our probe team is detected, it will provide"
        line2 = f"{leader} with justification to move against us!"

        for i, line in enumerate([line1, line2]):
            surf = self.small_font.render(line, True, self._BODY_COLOR)
            screen.blit(surf, (box_x + box_w // 2 - surf.get_width() // 2, box_y + 65 + i * 24))

        # Buttons
        btn_w, btn_h = 200, 42
        btn_y = box_y + box_h - btn_h - 20
        mouse = pygame.mouse.get_pos()

        abort_rect   = pygame.Rect(box_x + box_w // 2 - btn_w - 10, btn_y, btn_w, btn_h)
        proceed_rect = pygame.Rect(box_x + box_w // 2 + 10,          btn_y, btn_w, btn_h)
        self._abort_rect   = abort_rect
        self._proceed_rect = proceed_rect

        for rect, label, base_color, border_color in [
            (abort_rect,   "Abort mission.",              (50, 45, 40),  (120, 100, 80)),
            (proceed_rect, "I am quite aware of that.",  (30, 55, 35),  self._BORDER_COLOR),
        ]:
            hover = rect.collidepoint(mouse)
            bg = tuple(min(c + 18, 255) for c in base_color) if hover else base_color
            pygame.draw.rect(screen, bg, rect, border_radius=6)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=6)
            lbl = self.small_font.render(label, True, COLOR_TEXT)
            screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                               rect.centery - lbl.get_height() // 2))

    def _draw_menu_stub(self, screen, probe_data):
        """Placeholder for STAGE_MENU — not yet implemented."""
        self.draw_overlay(screen)
        box = self.centered_rect(580, 230)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=self._BORDER_COLOR, bg_color=self._BG_COLOR)
        title_surf = self.font.render("OPERATIONS DIRECTOR", True, self._TITLE_COLOR)
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 18))
        stub = self.small_font.render("(Probe action menu — not yet implemented)", True, (120, 130, 120))
        screen.blit(stub, (box_x + box_w // 2 - stub.get_width() // 2, box_y + 100))

        btn_w, btn_h = 140, 42
        abort_rect = pygame.Rect(box_x + box_w // 2 - btn_w // 2, box_y + box_h - btn_h - 20, btn_w, btn_h)
        self._abort_rect = abort_rect
        self._proceed_rect = None
        hover = abort_rect.collidepoint(pygame.mouse.get_pos())
        bg = (68, 63, 58) if hover else (50, 45, 40)
        pygame.draw.rect(screen, bg, abort_rect, border_radius=6)
        pygame.draw.rect(screen, (120, 100, 80), abort_rect, 2, border_radius=6)
        lbl = self.small_font.render("Abort mission.", True, COLOR_TEXT)
        screen.blit(lbl, (abort_rect.centerx - lbl.get_width() // 2,
                           abort_rect.centery - lbl.get_height() // 2))

    # ------------------------------------------------------------------
    # Click handling
    # ------------------------------------------------------------------

    def handle_click(self, pos, game):
        """Returns 'abort', 'proceed', or None."""
        if self._abort_rect and self._abort_rect.collidepoint(pos):
            game.pending_probe_action = None
            self.stage = STAGE_CONFIRM
            return 'abort'

        if self._proceed_rect and self._proceed_rect.collidepoint(pos):
            self.stage = STAGE_MENU
            return 'proceed'

        return None
