"""Base-related screens (naming and management)."""

import math
import pygame
from game.data import display
from game import facilities
from game.data.display import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT,
                                 COLOR_UI_BORDER, COLOR_BLACK)


# ---------------------------------------------------------------------------
# Citizen icon helpers
# Each takes (screen, cx, cy, size) where (cx, cy) is the centre of the icon
# and size is the diameter.  All icons are designed for size=40 but scale OK.
# ---------------------------------------------------------------------------

def draw_worker_icon(screen, cx, cy, size):
    """Standard worker: warm tan, no mouth."""
    r = size // 2
    pygame.draw.circle(screen, (200, 180, 140), (cx, cy), r)
    pygame.draw.circle(screen, (100, 90, 70), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 13))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 13))


def draw_drone_icon(screen, cx, cy, size):
    """Drone: red skin, frowny face."""
    r = size // 2
    pygame.draw.circle(screen, (210, 80, 80), (cx, cy), r)
    pygame.draw.circle(screen, (130, 40, 40), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 13))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 13))
    # Frown: bottom arc drawn as the top half of a small ellipse
    mouth_w = size // 3
    mouth_h = size // 7
    mouth_rect = pygame.Rect(cx - mouth_w // 2, cy + size // 12, mouth_w, mouth_h)
    pygame.draw.arc(screen, COLOR_BLACK, mouth_rect, 0, math.pi, max(1, size // 20))


def draw_talent_icon(screen, cx, cy, size):
    """Talent: lavender skin, glasses, slight smile."""
    r = size // 2
    pygame.draw.circle(screen, (195, 175, 225), (cx, cy), r)
    pygame.draw.circle(screen, (110, 90, 140), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    # Eyes (small dots behind glasses)
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 15))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 15))
    # Glasses: two small rounded rects + bridge
    g = max(2, size // 20)
    gr = size // 7
    left_lens  = pygame.Rect(cx - eye_dx - gr, eye_y - gr, gr * 2, gr * 2)
    right_lens = pygame.Rect(cx + eye_dx - gr, eye_y - gr, gr * 2, gr * 2)
    pygame.draw.rect(screen, (60, 50, 80), left_lens,  g, border_radius=3)
    pygame.draw.rect(screen, (60, 50, 80), right_lens, g, border_radius=3)
    bridge_y = eye_y
    pygame.draw.line(screen, (60, 50, 80),
                     (left_lens.right, bridge_y), (right_lens.left, bridge_y), g)


def draw_doctor_icon(screen, cx, cy, size):
    """Doctor: pale skin, surgical mask with red cross."""
    r = size // 2
    pygame.draw.circle(screen, (240, 235, 225), (cx, cy), r)
    pygame.draw.circle(screen, (160, 155, 145), (cx, cy), r, 2)
    eye_y = cy - size // 6
    eye_dx = size // 5
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 14))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 14))
    # Surgical mask on lower face
    mask_w = r * 3 // 2
    mask_h = r * 3 // 5
    mask_rect = pygame.Rect(cx - mask_w // 2, cy - r // 6, mask_w, mask_h)
    pygame.draw.rect(screen, (210, 225, 248), mask_rect, border_radius=4)
    pygame.draw.rect(screen, (148, 170, 200), mask_rect, max(1, size // 22), border_radius=4)
    # Red cross on mask
    cs = max(2, size // 9)
    mc = (mask_rect.centerx, mask_rect.centery)
    lw = max(2, size // 18)
    pygame.draw.line(screen, (210, 50, 50), (mc[0] - cs, mc[1]), (mc[0] + cs, mc[1]), lw)
    pygame.draw.line(screen, (210, 50, 50), (mc[0], mc[1] - cs), (mc[0], mc[1] + cs), lw)


def draw_technician_icon(screen, cx, cy, size):
    """Technician: warm skin, yellow hard hat."""
    r = size // 2
    pygame.draw.circle(screen, (200, 170, 110), (cx, cy), r)
    pygame.draw.circle(screen, (130, 105, 65), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 13))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 13))
    # Hard hat dome sitting on top of head
    hat_w = r * 7 // 4
    hat_h = r // 2
    brim_y = cy - r + r // 5
    hat_rect = pygame.Rect(cx - hat_w // 2, brim_y - hat_h, hat_w, hat_h + r // 4)
    pygame.draw.ellipse(screen, (230, 185, 45), hat_rect)
    pygame.draw.ellipse(screen, (165, 128, 22), hat_rect, max(1, size // 20))
    pygame.draw.line(screen, (165, 128, 22),
                     (cx - hat_w // 2 - 2, brim_y), (cx + hat_w // 2 + 2, brim_y),
                     max(2, size // 16))


def draw_librarian_icon(screen, cx, cy, size):
    """Librarian: cool gray-purple skin, thick scholarly glasses."""
    r = size // 2
    pygame.draw.circle(screen, (175, 165, 190), (cx, cy), r)
    pygame.draw.circle(screen, (105, 95, 125), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 15))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 15))
    # Thick frames (heavier than talent's slim glasses)
    g = max(3, size // 11)
    gr = size // 5
    left_lens  = pygame.Rect(cx - eye_dx - gr, eye_y - gr, gr * 2, gr * 2)
    right_lens = pygame.Rect(cx + eye_dx - gr, eye_y - gr, gr * 2, gr * 2)
    pygame.draw.rect(screen, (45, 30, 70), left_lens,  g, border_radius=2)
    pygame.draw.rect(screen, (45, 30, 70), right_lens, g, border_radius=2)
    pygame.draw.line(screen, (45, 30, 70),
                     (left_lens.right, eye_y), (right_lens.left, eye_y), g)


def draw_empath_icon(screen, cx, cy, size):
    """Empath: ghostly pale skin, violet eyes, ESP rays from top of head."""
    r = size // 2
    pygame.draw.circle(screen, (238, 238, 248), (cx, cy), r)
    pygame.draw.circle(screen, (148, 138, 178), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    pygame.draw.circle(screen, (88, 62, 140), (cx - eye_dx, eye_y), max(2, size // 13))
    pygame.draw.circle(screen, (88, 62, 140), (cx + eye_dx, eye_y), max(2, size // 13))
    # Psychic rays fanning from the upper arc of the head outward
    ray_len = size * 2 // 5
    ray_w = max(1, size // 22)
    for i in range(5):
        angle = math.radians(75 + i * 15)   # 75°→135°, top-left to top-right
        sx = cx + int(math.cos(angle) * (r - 1))
        sy = cy - int(math.sin(angle) * (r - 1))
        ex = cx + int(math.cos(angle) * (r + ray_len))
        ey = cy - int(math.sin(angle) * (r + ray_len))
        pygame.draw.line(screen, (185, 145, 255), (sx, sy), (ex, ey), ray_w)


def draw_engineer_icon(screen, cx, cy, size):
    """Engineer: weathered skin, big gray beard."""
    r = size // 2
    pygame.draw.circle(screen, (190, 165, 135), (cx, cy), r)
    pygame.draw.circle(screen, (110, 85, 60), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 13))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 13))
    # Gray beard covering lower chin
    beard_w = r * 7 // 5
    beard_h = r * 4 // 5
    beard_rect = pygame.Rect(cx - beard_w // 2, cy + r // 8, beard_w, beard_h)
    pygame.draw.ellipse(screen, (165, 160, 158), beard_rect)
    pygame.draw.ellipse(screen, (112, 108, 106), beard_rect, max(1, size // 20))


def draw_thinker_icon(screen, cx, cy, size):
    """Thinker: cool teal skin, furrowed brow."""
    r = size // 2
    pygame.draw.circle(screen, (155, 195, 205), (cx, cy), r)
    pygame.draw.circle(screen, (85, 135, 148), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    pygame.draw.circle(screen, COLOR_BLACK, (cx - eye_dx, eye_y), max(2, size // 13))
    pygame.draw.circle(screen, COLOR_BLACK, (cx + eye_dx, eye_y), max(2, size // 13))
    # Furrowed brow: lines angling down toward centre
    brow_y = eye_y - max(3, size // 9)
    bw = max(2, size // 16)
    indent = max(2, size // 12)
    pygame.draw.line(screen, (58, 100, 118),
                     (cx - eye_dx - indent, brow_y),
                     (cx - eye_dx + indent // 2, brow_y + indent), bw)
    pygame.draw.line(screen, (58, 100, 118),
                     (cx + eye_dx - indent // 2, brow_y + indent),
                     (cx + eye_dx + indent, brow_y), bw)


def draw_transcend_icon(screen, cx, cy, size):
    """Transcend: golden glowing skin, sunburst rays, bright eyes."""
    r = size // 2
    # Alternating long/short sunburst rays drawn first (behind head)
    ray_long  = size * 3 // 5
    ray_short = size * 2 // 5
    ray_w = max(2, size // 14)
    for i in range(8):
        angle = math.radians(i * 45)
        length = ray_long if i % 2 == 0 else ray_short
        ex = cx + int(math.cos(angle) * (r + length))
        ey = cy + int(math.sin(angle) * (r + length))
        pygame.draw.line(screen, (255, 200, 40), (cx, cy), (ex, ey), ray_w)
    # Head drawn on top of rays
    pygame.draw.circle(screen, (255, 225, 88), (cx, cy), r)
    pygame.draw.circle(screen, (192, 148, 22), (cx, cy), r, 2)
    eye_y = cy - size // 8
    eye_dx = size // 5
    # Glowing eyes with bright core
    pygame.draw.circle(screen, (255, 255, 205), (cx - eye_dx, eye_y), max(3, size // 10))
    pygame.draw.circle(screen, (255, 255, 205), (cx + eye_dx, eye_y), max(3, size // 10))
    pygame.draw.circle(screen, (255, 195, 45), (cx - eye_dx, eye_y), max(1, size // 17))
    pygame.draw.circle(screen, (255, 195, 45), (cx + eye_dx, eye_y), max(1, size // 17))


# Map specialist/citizen type strings to their draw functions
_CITIZEN_ICON_FUNCS = {
    'worker':     draw_worker_icon,
    'drone':      draw_drone_icon,
    'talent':     draw_talent_icon,
    'doctor':     draw_doctor_icon,
    'technician': draw_technician_icon,
    'librarian':  draw_librarian_icon,
    'empath':     draw_empath_icon,
    'engineer':   draw_engineer_icon,
    'thinker':    draw_thinker_icon,
    'transcend':  draw_transcend_icon,
}


def draw_citizen_icon(screen, cx, cy, size, ctype):
    """Dispatch to the correct icon function by citizen/specialist type."""
    _CITIZEN_ICON_FUNCS.get(ctype, draw_worker_icon)(screen, cx, cy, size)


def _get_available_specialists(tech_tree, population):
    """Return list of specialist dicts the player can currently assign."""
    from game.data.unit_data import SPECIALISTS
    available = []
    for spec in SPECIALISTS:
        prereq = spec['prereq']
        if prereq is not None and not tech_tree.has_tech(prereq):
            continue
        if population < spec.get('min_pop', 1):
            continue
        available.append(spec)
    return available


class BaseScreenManager:
    """Manages base naming and base management screens."""

    def __init__(self, font, small_font):
        """Initialize base screen manager with fonts."""
        self.font = font
        self.small_font = small_font

        # State
        self.base_naming_unit = None
        self.rename_base_target = None      # Set when renaming (not founding)
        self.base_name_text_selected = False  # True = full text highlighted; backspace clears all
        self.base_name_input = ""
        self.base_name_suggestions = []
        self.viewing_base = None
        self.hurry_production_open = False
        self.hurry_input = ""
        self.production_selection_open = False
        self.selected_production_item = None
        self.production_item_rects = []  # List of (rect, item_name) tuples
        self.production_selection_mode = "change"  # "change" or "queue"
        self.queue_management_open = False
        self.queue_item_rects = []  # List of (rect, item_index) tuples

        # Garrison context menu
        self.garrison_context_menu_open = False
        self.garrison_context_unit = None  # Unit that was right-clicked
        self.garrison_context_menu_rect = None
        self.garrison_context_menu_x = 0  # Save menu position
        self.garrison_context_menu_y = 0
        self.garrison_activate_rect = None
        self.garrison_unit_rects = []  # List of (rect, unit) tuples
        self.civ_icon_rects = []       # List of (rect, ctype, spec_idx) for citizen right-clicks

        # Citizen specialist context menu
        self.citizen_context_open = False
        self.citizen_context_menu_x = 0
        self.citizen_context_menu_y = 0
        self.citizen_context_type = None    # 'worker' or a specialist id string
        self.citizen_context_spec_idx = None  # index into base.specialists, or None
        self.citizen_context_item_rects = []  # list of (rect, action, data)

        # UI elements
        self.base_naming_ok_rect = None
        self.base_naming_cancel_rect = None
        self.base_view_ok_rect = None
        self.base_view_rename_rect = None
        self.prod_change_rect = None
        self.prod_hurry_rect = None
        self.prod_queue_rect = None
        self.hurry_ok_rect = None
        self.hurry_cancel_rect = None
        self.hurry_all_rect = None
        self.governor_button_rect = None
        self.mode_button_rects = []  # List of (rect, mode_name) tuples
        self.map_tile_rects = []     # List of (rect, map_x, map_y) for domain tile clicks
        self.hurry_error_message = ""
        self.hurry_error_time = 0
        self.prod_select_ok_rect = None
        self.prod_select_cancel_rect = None
        self.queue_add_rect = None
        self.queue_clear_rect = None
        self.queue_close_rect = None

    def show_base_naming(self, unit, game):
        """Show the base naming dialog for a colony pod."""
        self.base_naming_unit = unit
        # Use faction-specific base name from game
        self.base_name_input = game.generate_base_name(unit.owner)

    def show_base_view(self, base):
        """Show the base management screen."""
        self.viewing_base = base
        # Reset all popups when opening base view
        self._reset_base_popups()

    def _reset_base_popups(self):
        """Reset all base view popup states."""
        self.hurry_production_open = False
        self.hurry_input = ""
        self.production_selection_open = False
        self.selected_production_item = None
        self.queue_management_open = False
        self.citizen_context_open = False

    def draw_base_naming(self, screen):
        """Draw the base naming dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((10, 15, 20))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 600, 400
        dialog_x = display.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_text = "Rename Base" if self.rename_base_target else "Found New Base"
        title_surf = self.font.render(title_text, True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Input field
        input_y = dialog_y + 80
        input_rect = pygame.Rect(dialog_x + 30, input_y, dialog_w - 60, 50)
        pygame.draw.rect(screen, (20, 25, 30), input_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, input_rect, 2, border_radius=6)

        # Draw selection highlight or normal text
        input_surf = self.font.render(self.base_name_input, True, COLOR_TEXT)
        if self.base_name_text_selected and self.base_name_input:
            # Draw yellow highlight behind text
            highlight_rect = pygame.Rect(input_rect.x + 8, input_rect.y + 8,
                                         input_surf.get_width() + 4, input_rect.height - 16)
            pygame.draw.rect(screen, (180, 150, 30), highlight_rect, border_radius=3)
            # Draw text in dark color over highlight
            sel_surf = self.font.render(self.base_name_input, True, (20, 15, 5))
            screen.blit(sel_surf, (input_rect.x + 10, input_rect.y + 13))
        else:
            screen.blit(input_surf, (input_rect.x + 10, input_rect.y + 13))
            # Draw cursor
            cursor_x = input_rect.x + 10 + input_surf.get_width() + 2
            if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking cursor
                pygame.draw.line(screen, COLOR_TEXT, (cursor_x, input_rect.y + 10),
                               (cursor_x, input_rect.y + input_rect.height - 10), 2)

        # OK and Cancel buttons
        button_y = dialog_y + dialog_h - 70
        ok_rect = pygame.Rect(dialog_x + dialog_w // 2 - 180, button_y, 150, 50)
        cancel_rect = pygame.Rect(dialog_x + dialog_w // 2 + 30, button_y, 150, 50)

        self.base_naming_ok_rect = ok_rect
        self.base_naming_cancel_rect = cancel_rect

        # Draw OK button
        ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2, ok_rect.centery - 10))

        # Draw Cancel button
        cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if cancel_hover else COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_surf = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_surf, (cancel_rect.centerx - cancel_surf.get_width() // 2, cancel_rect.centery - 10))

    def handle_base_naming_event(self, event, game):
        """Handle keyboard and mouse events for base naming. Returns True if event consumed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._close_naming_dialog()
                return 'close'
            elif event.key == pygame.K_RETURN:
                if self.base_name_input.strip():
                    self._commit_naming(game)
                self._close_naming_dialog()
                return 'close'
            elif event.key == pygame.K_BACKSPACE:
                if self.base_name_text_selected:
                    self.base_name_input = ""
                    self.base_name_text_selected = False
                else:
                    self.base_name_input = self.base_name_input[:-1]
                return True
            else:
                if event.unicode:
                    if self.base_name_text_selected:
                        # Replace entire selection with the typed character
                        self.base_name_input = event.unicode
                        self.base_name_text_selected = False
                    elif len(self.base_name_input) < 30:
                        self.base_name_input += event.unicode
                return True
        return False

    def _commit_naming(self, game):
        """Apply the name — either found a new base or rename an existing one."""
        name = self.base_name_input.strip()
        if not name:
            return
        if self.rename_base_target:
            self.rename_base_target.name = name
        else:
            game.found_base(self.base_naming_unit, name)

    def _close_naming_dialog(self):
        """Reset all naming state."""
        self.base_naming_unit = None
        self.rename_base_target = None
        self.base_name_input = ""
        self.base_name_text_selected = False

    def handle_base_naming_click(self, pos, game):
        """Handle clicks in the base naming dialog. Returns 'close' if should exit, None otherwise."""
        # Check OK button
        if hasattr(self, 'base_naming_ok_rect') and self.base_naming_ok_rect.collidepoint(pos):
            self._commit_naming(game)
            self._close_naming_dialog()
            return 'close'

        # Check Cancel button
        elif hasattr(self, 'base_naming_cancel_rect') and self.base_naming_cancel_rect.collidepoint(pos):
            self._close_naming_dialog()
            return 'close'

        return None

    def handle_base_view_event(self, event, game):
        """Handle keyboard events for base view (mainly popup input). Returns True if event consumed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Close any open popup, return to base view (don't exit base view)
                if self.hurry_production_open:
                    self.hurry_production_open = False
                    self.hurry_input = ""
                    return True
                elif self.production_selection_open:
                    self.production_selection_open = False
                    self.selected_production_item = None
                    return True
                elif self.queue_management_open:
                    self.queue_management_open = False
                    return True
                # If no popups open, let Escape close the base view
                return False

        # Only handle other keyboard input if hurry popup is open
        if not self.hurry_production_open:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Submit the hurry payment (same as OK button)
                base = self.viewing_base
                if base and base.current_production and self.hurry_input:
                    try:
                        # Check if base has already hurried this turn
                        if base.hurried_this_turn:
                            import time
                            self.hurry_error_message = "Already hurried this turn!"
                            self.hurry_error_time = time.time()
                            return True

                        credits_to_spend = int(self.hurry_input)
                        if credits_to_spend <= 0:
                            import time
                            self.hurry_error_message = "Must spend at least 1 credit"
                            self.hurry_error_time = time.time()
                            return True

                        if credits_to_spend > game.energy_credits:
                            import time
                            self.hurry_error_message = "Not enough funds!"
                            self.hurry_error_time = time.time()
                            return True

                        # Perform the hurry
                        game.energy_credits -= credits_to_spend
                        production_added, completed = base.hurry_production(credits_to_spend)

                        # Mark base as hurried this turn
                        base.hurried_this_turn = True

                        if completed:
                            game.set_status_message(f"Rushed {base.current_production}! Will complete next turn.")
                        else:
                            turns_saved = production_added
                            game.set_status_message(f"Rushed production: {turns_saved} turns saved")

                        self.hurry_production_open = False
                        self.hurry_input = ""
                    except ValueError:
                        game.set_status_message("Invalid amount entered")
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.hurry_input = self.hurry_input[:-1]
                return True
            else:
                # Add character to input (only digits)
                if event.unicode.isdigit() and len(self.hurry_input) < 10:
                    self.hurry_input += event.unicode
                return True
        return False

    def draw_base_view(self, screen, game):
        """Draw the base management screen."""
        base = self.viewing_base
        if not base:
            return

        # Refresh resource output from worked tiles so display is always current
        if hasattr(game, 'game_map'):
            base.calculate_resource_output(game.game_map)
            base.energy_production = base.energy_per_turn  # sync for allocate_energy
            base.growth_turns_remaining = base._calculate_growth_turns()
            # Apply inefficiency before splitting so economy/labs reflect true net
            if hasattr(game, '_calc_inefficiency_loss'):
                ineff = game._calc_inefficiency_loss(base, base.owner)
                base.inefficiency_loss = min(base.energy_production, max(0, ineff))
                base.energy_production = max(0, base.energy_production - base.inefficiency_loss)
            alloc = getattr(game, 'global_energy_allocation', {'economy': 50, 'labs': 50, 'psych': 0})
            base.allocate_energy(alloc['economy'], alloc['labs'], alloc['psych'])

        # Fill background
        screen.fill((15, 20, 25))

        # Calculate layout dimensions
        screen_w = display.SCREEN_WIDTH
        screen_h = display.SCREEN_HEIGHT

        # TOP BAR: Automation buttons (full width)
        top_bar_y = 10
        top_bar_h = 50
        button_w = 140
        button_spacing = 10

        automation_buttons = ["Explore", "Discover", "Build", "Conquer"]
        total_auto_w = len(automation_buttons) * button_w + (len(automation_buttons) - 1) * button_spacing
        governor_w = 120
        total_w = total_auto_w + governor_w + button_spacing * 2

        start_x = (screen_w - total_w) // 2

        # Draw automation mode buttons
        mode_names = ["explore", "discover", "build", "conquer"]
        self.mode_button_rects = []
        for i, label in enumerate(automation_buttons):
            if i < 2:
                btn_x = start_x + i * (button_w + button_spacing)
            else:
                btn_x = start_x + i * (button_w + button_spacing) + governor_w + button_spacing * 2

            btn_rect = pygame.Rect(btn_x, top_bar_y, button_w, top_bar_h)
            mode_name = mode_names[i]

            # Highlight if this mode is active
            is_active = base.governor_enabled and base.governor_mode == mode_name
            if is_active:
                pygame.draw.rect(screen, (100, 140, 100), btn_rect, border_radius=6)
                pygame.draw.rect(screen, (140, 180, 140), btn_rect, 3, border_radius=6)
            else:
                pygame.draw.rect(screen, COLOR_BUTTON, btn_rect, border_radius=6)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, btn_rect, 2, border_radius=6)

            btn_text = self.small_font.render(label, True, COLOR_TEXT)
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - 8))
            self.mode_button_rects.append((btn_rect, mode_name))

        # Governor button in middle
        gov_x = start_x + 2 * (button_w + button_spacing)
        self.governor_button_rect = pygame.Rect(gov_x, top_bar_y, governor_w, top_bar_h)

        # Governor button appearance based on state
        if base.governor_enabled:
            pygame.draw.rect(screen, (80, 120, 80), self.governor_button_rect, border_radius=6)
            pygame.draw.rect(screen, (120, 180, 120), self.governor_button_rect, 3, border_radius=6)
            gov_text = self.small_font.render("Governor", True, (220, 255, 220))
        else:
            pygame.draw.rect(screen, (60, 60, 70), self.governor_button_rect, border_radius=6)
            pygame.draw.rect(screen, (100, 100, 120), self.governor_button_rect, 2, border_radius=6)
            gov_text = self.small_font.render("Governor", True, (160, 160, 180))

        screen.blit(gov_text, (self.governor_button_rect.centerx - gov_text.get_width() // 2, self.governor_button_rect.centery - 8))

        # Base name title — sits between the top bar and the mini-map
        base_title_font = pygame.font.Font(None, 32)
        is_enemy_base = base.owner != game.player_faction_id
        if is_enemy_base:
            from game.data.data import FACTION_DATA
            faction_name = FACTION_DATA[base.owner]['name'] if base.owner < len(FACTION_DATA) else "Unknown"
            title_str = f"{base.name} ({faction_name})"
        else:
            title_str = base.name
        base_title_surf = base_title_font.render(title_str, True, COLOR_TEXT)
        base_title_y = top_bar_y + top_bar_h + 6
        screen.blit(base_title_surf,
                    (screen_w // 2 - base_title_surf.get_width() // 2, base_title_y))

        # TOP CENTER: Zoomed map view — fat cross domain (5×5 minus corners)
        map_view_w = 220
        map_view_h = 220
        map_view_x = (screen_w - map_view_w) // 2
        map_view_y = top_bar_y + top_bar_h + 38  # room for title above
        map_view_rect = pygame.Rect(map_view_x, map_view_y, map_view_w, map_view_h)
        pygame.draw.rect(screen, (25, 35, 40), map_view_rect)
        pygame.draw.rect(screen, COLOR_UI_BORDER, map_view_rect, 2)

        from game.map import tile_base_nutrients, tile_base_minerals, tile_base_energy
        from game.terraforming import get_tile_yields
        from game.data.data import FACTION_DATA

        tile_size = 44  # 5 × 44 = 220
        start_tile_x = map_view_x
        start_tile_y = map_view_y

        # Build set of currently-worked tile coords for highlighting
        worked_tiles = base.get_worked_tiles(game.game_map)
        worked_coords = {(t.x, t.y) for t in worked_tiles}

        # Resource colors
        COLOR_NUT = (100, 220, 100)       # green
        COLOR_MIN = (100, 160, 210)       # steel blue
        COLOR_ENE = (230, 220, 80)        # yellow

        self.map_tile_rects = []

        for grid_dy in range(5):
            for grid_dx in range(5):
                tdx = grid_dx - 2  # offset from base: -2 to +2
                tdy = grid_dy - 2
                is_corner = abs(tdx) == 2 and abs(tdy) == 2
                is_base = tdx == 0 and tdy == 0

                map_x = (base.x + tdx) % game.game_map.width
                map_y = base.y + tdy

                tile_rect = pygame.Rect(
                    start_tile_x + grid_dx * tile_size,
                    start_tile_y + grid_dy * tile_size,
                    tile_size, tile_size
                )

                if not (0 <= map_y < game.game_map.height):
                    pygame.draw.rect(screen, COLOR_BLACK, tile_rect)
                    pygame.draw.rect(screen, (40, 40, 40), tile_rect, 1)
                    continue

                actual_tile = game.game_map.get_tile(map_x, map_y)
                if actual_tile is None:
                    pygame.draw.rect(screen, COLOR_BLACK, tile_rect)
                    continue

                # Void tiles count as empty (off-map) — draw black like out-of-bounds
                if getattr(actual_tile, 'void', False):
                    pygame.draw.rect(screen, COLOR_BLACK, tile_rect)
                    pygame.draw.rect(screen, (40, 40, 40), tile_rect, 1)
                    continue

                # Terrain base color — mirrors main renderer rainfall/fungus logic
                if actual_tile.is_ocean():
                    terrain_color = display.COLOR_OCEAN
                else:
                    _rainfall_colors = [
                        display.COLOR_LAND_ARID,
                        display.COLOR_LAND_MODERATE,
                        display.COLOR_LAND_RAINY,
                    ]
                    terrain_color = _rainfall_colors[getattr(actual_tile, 'rainfall', 1)]

                # Fungus overrides terrain color (same tones as main renderer)
                if getattr(actual_tile, 'fungus', False):
                    terrain_color = (200, 50, 120) if actual_tile.is_land() else (80, 130, 210)

                if is_base:
                    # Base tile: faction color background
                    base_color = (255, 255, 255)
                    if base.owner < len(FACTION_DATA):
                        base_color = FACTION_DATA[base.owner]['color']
                    pygame.draw.rect(screen, base_color, tile_rect, border_radius=3)
                elif is_corner:
                    # Outside domain: pure black
                    pygame.draw.rect(screen, COLOR_BLACK, tile_rect)
                else:
                    pygame.draw.rect(screen, terrain_color, tile_rect)
                    # Rocks: draw a subtle darker overlay on rocky land tiles
                    if actual_tile.is_land() and getattr(actual_tile, 'rockiness', 0) == 2:
                        rock_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                        rock_surf.fill((0, 0, 0, 60))
                        screen.blit(rock_surf, tile_rect.topleft)
                    # Store rect for click detection (domain tiles only, not base)
                    self.map_tile_rects.append((pygame.Rect(tile_rect), map_x, map_y))

                # Border: bright if worked, dim if unworked domain, faint if corner/out
                coord = (map_x, map_y)
                if is_base:
                    pygame.draw.rect(screen, (255, 255, 255), tile_rect, 2, border_radius=3)
                elif is_corner:
                    pygame.draw.rect(screen, (40, 40, 40), tile_rect, 1)
                elif coord in worked_coords:
                    pygame.draw.rect(screen, (200, 200, 200), tile_rect, 2)
                else:
                    pygame.draw.rect(screen, (55, 65, 55), tile_rect, 1)

                # Resource number overlays for worked tiles (including base tile)
                if coord in worked_coords:
                    imp_yields = get_tile_yields(actual_tile)
                    if imp_yields['fixed']:
                        nut, min_, ene = imp_yields['fixed']
                    else:
                        mult = imp_yields['nutrients_multiplier']
                        nut  = int((tile_base_nutrients(actual_tile) + imp_yields['nutrients']) * mult)
                        min_ = tile_base_minerals(actual_tile) + imp_yields['minerals']
                        ene  = tile_base_energy(actual_tile)   + imp_yields['energy']

                    # Draw small colored numbers at bottom of tile, left to right
                    num_x = tile_rect.x + 2
                    num_y = tile_rect.bottom - 12
                    for val, color in ((nut, COLOR_NUT), (min_, COLOR_MIN), (ene, COLOR_ENE)):
                        num_surf = self.small_font.render(str(val), True, color)
                        screen.blit(num_surf, (num_x, num_y))
                        num_x += num_surf.get_width() + 3

        # RESOURCE ROWS: Below map inset
        resource_rows_y = map_view_y + map_view_h + 10
        resource_rows_w = map_view_w
        resource_rows_x = map_view_x
        row_h = 22

        # Nutrients row
        nut_row_y = resource_rows_y
        nut_label = self.small_font.render("Nutrients:", True, (150, 220, 150))
        screen.blit(nut_label, (resource_rows_x, nut_row_y))
        nut_intake = getattr(base, 'nutrients_per_turn', 0)
        nut_consumption = base.population * 2
        nut_surplus = nut_intake - nut_consumption
        if nut_surplus < 0:
            seg_nut_main = self.small_font.render(f"{nut_intake} - {nut_consumption} = ", True, (180, 200, 180))
            seg_nut_surp = self.small_font.render(str(nut_surplus), True, (210, 70, 70))
            nut_total_w = seg_nut_main.get_width() + seg_nut_surp.get_width()
            nut_blit_x = resource_rows_x + resource_rows_w - nut_total_w
            screen.blit(seg_nut_main, (nut_blit_x, nut_row_y))
            screen.blit(seg_nut_surp, (nut_blit_x + seg_nut_main.get_width(), nut_row_y))
        else:
            nut_values = self.small_font.render(f"{nut_intake} - {nut_consumption} = {nut_surplus}", True, (180, 200, 180))
            screen.blit(nut_values, (resource_rows_x + resource_rows_w - nut_values.get_width(), nut_row_y))

        # Minerals row
        min_row_y = nut_row_y + row_h
        min_label = self.small_font.render("Minerals:", True, (200, 180, 140))
        screen.blit(min_label, (resource_rows_x, min_row_y))
        min_intake = getattr(base, 'minerals_per_turn', 0)
        min_consumption = getattr(base, 'support_cost_paid', 0)
        min_surplus = min_intake - min_consumption
        min_values = self.small_font.render(f"{min_intake} - {min_consumption} = {min_surplus}", True, (180, 180, 160))
        screen.blit(min_values, (resource_rows_x + resource_rows_w - min_values.get_width(), min_row_y))

        # Energy row (multi-color: inefficiency shown in red when non-zero)
        ene_row_y = min_row_y + row_h
        ene_label = self.small_font.render("Energy:", True, (220, 220, 100))
        screen.blit(ene_label, (resource_rows_x, ene_row_y))
        ene_intake = getattr(base, 'energy_per_turn', base.energy_production)
        ene_ineff = getattr(base, 'inefficiency_loss', 0)
        ene_consumption = 0  # placeholder — inefficiency is the only energy consumption
        ene_surplus = ene_intake - ene_ineff
        ene_color = (200, 200, 120)
        ene_red = (210, 70, 70)
        if ene_ineff > 0:
            seg_ene_main = self.small_font.render(f"{ene_intake} - {ene_consumption}", True, ene_color)
            seg_ene_ineff_surf = self.small_font.render(f" (-{ene_ineff})", True, ene_red)
            seg_ene_eq = self.small_font.render(f" = {ene_surplus}", True, ene_color)
            ene_total_w = seg_ene_main.get_width() + seg_ene_ineff_surf.get_width() + seg_ene_eq.get_width()
            ene_blit_x = resource_rows_x + resource_rows_w - ene_total_w
            screen.blit(seg_ene_main, (ene_blit_x, ene_row_y))
            screen.blit(seg_ene_ineff_surf, (ene_blit_x + seg_ene_main.get_width(), ene_row_y))
            screen.blit(seg_ene_eq, (ene_blit_x + seg_ene_main.get_width() + seg_ene_ineff_surf.get_width(), ene_row_y))
        else:
            seg_ene = self.small_font.render(f"{ene_intake} - {ene_consumption} = {ene_surplus}", True, ene_color)
            screen.blit(seg_ene, (resource_rows_x + resource_rows_w - seg_ene.get_width(), ene_row_y))

        # Explainer row: form changes depending on whether inefficiency is present and/or nutrient shortfall
        exp_row_y = ene_row_y + row_h + 5
        exp_color = (140, 140, 160)
        exp_red = (210, 70, 70)
        surplus_label = "SHORTFALL" if nut_surplus < 0 else "SURPLUS"
        surplus_label_color = exp_red if nut_surplus < 0 else exp_color
        if ene_ineff > 0:
            seg_exp1 = self.small_font.render("INTAKE - (CONSUMPTION + ", True, exp_color)
            seg_exp_ineff = self.small_font.render("INEFFICIENCY", True, exp_red)
            seg_exp2 = self.small_font.render(") = ", True, exp_color)
            seg_exp_surp = self.small_font.render(surplus_label, True, surplus_label_color)
            exp_total_w = seg_exp1.get_width() + seg_exp_ineff.get_width() + seg_exp2.get_width() + seg_exp_surp.get_width()
            exp_blit_x = resource_rows_x + resource_rows_w // 2 - exp_total_w // 2
            screen.blit(seg_exp1, (exp_blit_x, exp_row_y))
            screen.blit(seg_exp_ineff, (exp_blit_x + seg_exp1.get_width(), exp_row_y))
            screen.blit(seg_exp2, (exp_blit_x + seg_exp1.get_width() + seg_exp_ineff.get_width(), exp_row_y))
            screen.blit(seg_exp_surp, (exp_blit_x + seg_exp1.get_width() + seg_exp_ineff.get_width() + seg_exp2.get_width(), exp_row_y))
        else:
            seg_exp_main = self.small_font.render("INTAKE - CONSUMPTION = ", True, exp_color)
            seg_exp_surp = self.small_font.render(surplus_label, True, surplus_label_color)
            exp_total_w = seg_exp_main.get_width() + seg_exp_surp.get_width()
            exp_blit_x = resource_rows_x + resource_rows_w // 2 - exp_total_w // 2
            screen.blit(seg_exp_main, (exp_blit_x, exp_row_y))
            screen.blit(seg_exp_surp, (exp_blit_x + seg_exp_main.get_width(), exp_row_y))

        # Define content area (full width for layout)
        content_x = 20
        content_w = screen_w - 40

        # TOP LEFT: Nutrients pane
        nutrients_x = content_x
        nutrients_y = top_bar_y + top_bar_h + 20
        nutrients_w = 250
        nutrients_h = 120
        nutrients_rect = pygame.Rect(nutrients_x, nutrients_y, nutrients_w, nutrients_h)
        pygame.draw.rect(screen, (35, 45, 35), nutrients_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 140, 80), nutrients_rect, 2, border_radius=8)

        nut_title = self.small_font.render("NUTRIENTS & GROWTH", True, (150, 220, 150))
        screen.blit(nut_title, (nutrients_x + 10, nutrients_y + 8))

        # Growth progress bar
        progress_rect = pygame.Rect(nutrients_x + 10, nutrients_y + 35, nutrients_w - 20, 25)
        pygame.draw.rect(screen, (20, 25, 20), progress_rect, border_radius=4)

        # Fill progress
        progress_pct = base.nutrients_accumulated / base.nutrients_needed
        fill_w = int((nutrients_w - 20) * progress_pct)
        fill_rect = pygame.Rect(nutrients_x + 10, nutrients_y + 35, fill_w, 25)
        pygame.draw.rect(screen, (100, 200, 100), fill_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 140, 80), progress_rect, 2, border_radius=4)

        progress_text = self.small_font.render(f"{base.nutrients_accumulated}/{base.nutrients_needed}", True, COLOR_TEXT)
        screen.blit(progress_text, (progress_rect.centerx - progress_text.get_width() // 2, progress_rect.centery - 8))

        # Turns until growth (or hunger warning if net negative nutrients)
        if nut_surplus < 0:
            growth_text = self.small_font.render("Hunger!", True, (210, 70, 70))
        elif base.growth_turns_remaining >= 999:
            growth_text = self.small_font.render("No growth", True, (140, 160, 140))
        else:
            growth_text = self.small_font.render(f"Growth in {base.growth_turns_remaining} turns", True, (180, 220, 180))
        screen.blit(growth_text, (nutrients_x + 10, nutrients_y + 70))

        pop_display = self.small_font.render(f"Population: {base.population}", True, COLOR_TEXT)
        screen.blit(pop_display, (nutrients_x + 10, nutrients_y + 92))

        # Commerce Panel (below nutrients panel)
        commerce_x = nutrients_x
        commerce_y = nutrients_y + nutrients_h + 10
        commerce_w = nutrients_w
        commerce_h = 80
        commerce_rect = pygame.Rect(commerce_x, commerce_y, commerce_w, commerce_h)
        pygame.draw.rect(screen, (35, 40, 45), commerce_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 120, 140), commerce_rect, 2, border_radius=8)

        commerce_title = self.small_font.render("COMMERCE", True, (180, 200, 220))
        screen.blit(commerce_title, (commerce_x + 10, commerce_y + 8))

        # Display commerce breakdown (if commerce system exists)
        if hasattr(game, 'commerce'):
            commerce_data = game.commerce.get_commerce_display_data()
            y_offset = commerce_y + 30
            total_commerce = 0

            # Show all commerce relationships (even if 0)
            if commerce_data:
                for partner_name, your_amount, their_amount in commerce_data:
                    text = f"{partner_name}: +{your_amount} (they get +{their_amount})"
                    commerce_line = self.small_font.render(text, True, (200, 220, 200))
                    screen.blit(commerce_line, (commerce_x + 10, y_offset))
                    y_offset += 16
                    total_commerce += your_amount

                # Show total (even if 0)
                total_text = f"Total: +{total_commerce}"
                total_line = self.small_font.render(total_text, True, (180, 220, 180))
                screen.blit(total_line, (commerce_x + 10, y_offset))
            else:
                # No treaties/pacts
                no_commerce = self.small_font.render("No trade agreements", True, (150, 150, 150))
                screen.blit(no_commerce, (commerce_x + 10, y_offset))

        # Errata Panel (below commerce panel)
        errata_x = commerce_x
        errata_y = commerce_y + commerce_h + 10
        errata_w = commerce_w
        errata_h = 100
        errata_rect = pygame.Rect(errata_x, errata_y, errata_w, errata_h)
        pygame.draw.rect(screen, (40, 35, 35), errata_rect, border_radius=8)
        pygame.draw.rect(screen, (140, 120, 100), errata_rect, 2, border_radius=8)

        errata_title = self.small_font.render("INFO", True, (220, 200, 180))
        screen.blit(errata_title, (errata_x + 10, errata_y + 8))

        # Mission Year
        mission_year = 2100 + game.turn
        my_text = self.small_font.render(f"M.Y. {mission_year}", True, COLOR_TEXT)
        screen.blit(my_text, (errata_x + 10, errata_y + 35))

        # Energy credits
        credits_text = self.small_font.render(f"Credits: {game.energy_credits}", True, COLOR_TEXT)
        screen.blit(credits_text, (errata_x + 10, errata_y + 57))

        # Eco-damage (placeholder)
        ecodamage_text = self.small_font.render(f"Eco-damage: 0", True, COLOR_TEXT)
        screen.blit(ecodamage_text, (errata_x + 10, errata_y + 79))

        # TOP RIGHT: Base Facilities
        facilities_x = content_x + content_w - 280
        facilities_y = nutrients_y
        facilities_w = 280
        facilities_h = 300
        facilities_rect = pygame.Rect(facilities_x, facilities_y, facilities_w, facilities_h)
        pygame.draw.rect(screen, (40, 35, 50), facilities_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 100, 140), facilities_rect, 2, border_radius=8)

        fac_title = self.small_font.render("BASE FACILITIES", True, (200, 180, 220))
        screen.blit(fac_title, (facilities_x + 10, facilities_y + 8))

        # Display facilities (convert IDs to names, add * for free facilities)
        from game.facilities import get_facility_by_id
        if base.facilities:
            for i, facility_id in enumerate(base.facilities):
                facility_data = get_facility_by_id(facility_id)
                if facility_data:
                    # Add asterisk for free facilities
                    prefix = "* " if facility_id in base.free_facilities else ""
                    facility_name = prefix + facility_data['name']
                    fac_text = self.small_font.render(facility_name, True, COLOR_TEXT)
                    screen.blit(fac_text, (facilities_x + 15, facilities_y + 35 + i * 22))
        else:
            no_fac = self.small_font.render("No facilities yet", True, (120, 120, 140))
            screen.blit(no_fac, (facilities_x + 15, facilities_y + 40))

        # ENERGY ALLOCATION PANEL: Above civilians
        energy_alloc_y = screen_h - 380
        energy_alloc_h = 100
        energy_alloc_w = min(500, content_w - 40)
        energy_alloc_x = (screen_w - energy_alloc_w) // 2

        # Draw panel background
        energy_alloc_rect = pygame.Rect(energy_alloc_x, energy_alloc_y, energy_alloc_w, energy_alloc_h)
        pygame.draw.rect(screen, (35, 40, 45), energy_alloc_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 140, 100), energy_alloc_rect, 2, border_radius=8)

        # Title
        energy_title = self.small_font.render("ENERGY ALLOCATION", True, (200, 220, 180))
        screen.blit(energy_title, (energy_alloc_x + energy_alloc_w // 2 - energy_title.get_width() // 2, energy_alloc_y + 8))

        # Get energy allocation percentages (TODO: from social engineering)
        economy_pct = 50
        psych_pct = 0
        labs_pct = 50

        # Real values from base (freshly calculated in refresh above)
        econ_energy = base.economy_output
        labs_energy = base.labs_output
        psych_energy = base.psych_output
        econ_bonus = 0  # TODO: commerce income + faction bonuses
        labs_bonus = 0  # TODO: research facility bonuses
        psych_bonus = 0  # TODO: psych facility bonuses

        # Three rows: Economy, Psych, Labs
        row_y_start = energy_alloc_y + 35
        row_spacing = 20

        # Economy row
        econ_label = self.small_font.render(f"Economy: {economy_pct}%", True, (180, 200, 180))
        screen.blit(econ_label, (energy_alloc_x + 15, row_y_start))
        econ_calc = self.small_font.render(
            f"{econ_energy} Energy + {econ_bonus} Bonus = {econ_energy + econ_bonus}", True, (160, 180, 160))
        screen.blit(econ_calc, (energy_alloc_x + 160, row_y_start))

        # Psych row
        psych_label = self.small_font.render(f"Psych: {psych_pct}%", True, (200, 180, 200))
        screen.blit(psych_label, (energy_alloc_x + 15, row_y_start + row_spacing))
        psych_calc = self.small_font.render(
            f"{psych_energy} Energy + {psych_bonus} Bonus = {psych_energy + psych_bonus}", True, (180, 160, 180))
        screen.blit(psych_calc, (energy_alloc_x + 160, row_y_start + row_spacing))

        # Labs row
        labs_label = self.small_font.render(f"Labs: {labs_pct}%", True, (180, 200, 220))
        screen.blit(labs_label, (energy_alloc_x + 15, row_y_start + row_spacing * 2))
        labs_calc = self.small_font.render(
            f"{labs_energy} Energy + {labs_bonus} Bonus = {labs_energy + labs_bonus}", True, (160, 180, 200))
        screen.blit(labs_calc, (energy_alloc_x + 160, row_y_start + row_spacing * 2))

        # CENTER BOTTOM: Civilian icons in horizontal bar (1 per pop)
        civilian_y = screen_h - 250
        civilian_h = 70
        civilian_bar_w = min(600, content_w - 40)
        civilian_bar_x = (screen_w - civilian_bar_w) // 2

        # Draw bar background
        civilian_bar_rect = pygame.Rect(civilian_bar_x, civilian_y, civilian_bar_w, civilian_h)
        pygame.draw.rect(screen, (40, 45, 50), civilian_bar_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 110, 120), civilian_bar_rect, 2, border_radius=8)

        civ_label = self.small_font.render("CITIZENS", True, COLOR_TEXT)
        screen.blit(civ_label, (civilian_bar_x + civilian_bar_w // 2 - civ_label.get_width() // 2, civilian_y - 25))

        # Draw citizen icons inside the bar — talents | specialists | workers | drones
        civ_icon_size = 40
        civ_spacing = 10
        total_civ_w = base.population * (civ_icon_size + civ_spacing) - civ_spacing
        civ_start_x = civilian_bar_x + (civilian_bar_w - total_civ_w) // 2
        civ_cy = civilian_y + civilian_h // 2

        # Build ordered list of (ctype, spec_idx) tuples, capped to population slots
        # ctype is a citizen/specialist type string; spec_idx is index into base.specialists or None
        citizen_list = []
        for _ in range(min(base.talents, base.population)):
            citizen_list.append(('talent', None))
        for idx, spec_id in enumerate(getattr(base, 'specialists', [])):
            if len(citizen_list) < base.population:
                citizen_list.append((spec_id, idx))
        remaining = base.population - len(citizen_list)
        for _ in range(min(base.workers, remaining)):
            citizen_list.append(('worker', None))
        remaining = base.population - len(citizen_list)
        for _ in range(min(base.drones, remaining)):
            citizen_list.append(('drone', None))

        self.civ_icon_rects = []
        for i, (ctype, spec_idx) in enumerate(citizen_list):
            cx = civ_start_x + i * (civ_icon_size + civ_spacing) + civ_icon_size // 2
            rect = pygame.Rect(cx - civ_icon_size // 2,
                               civ_cy - civ_icon_size // 2,
                               civ_icon_size, civ_icon_size)
            draw_citizen_icon(screen, cx, civ_cy, civ_icon_size, ctype)
            self.civ_icon_rects.append((rect, ctype, spec_idx))

        # GARRISON BAR: Units in base (always show bar like citizens panel)
        garrison_y = civilian_y + civilian_h + 30  # Increased spacing to avoid overlap
        garrison_h = 60
        gar_label = self.small_font.render("GARRISON", True, COLOR_TEXT)
        screen.blit(gar_label, (screen_w // 2 - gar_label.get_width() // 2, garrison_y - 25))

        # Garrison bar with same styling as civilians
        garrison_bar_w = min(500, content_w - 200)
        garrison_bar_x = (screen_w - garrison_bar_w) // 2
        garrison_rect = pygame.Rect(garrison_bar_x, garrison_y, garrison_bar_w, garrison_h)

        # Always draw bar background and border (like citizens panel)
        pygame.draw.rect(screen, (40, 45, 50), garrison_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 110, 120), garrison_rect, 2, border_radius=8)

        # Draw garrison units or empty message inside the bar
        # Use dynamic garrison to ensure we show all units actually at the base
        garrison_units = base.get_garrison_units(game)
        self.garrison_unit_rects = []  # Reset for click detection

        if garrison_units:
            for i, unit in enumerate(garrison_units):
                unit_x = garrison_rect.x + 10 + i * 50
                unit_circle = pygame.Rect(unit_x, garrison_rect.y + 10, 40, 40)
                pygame.draw.circle(screen, (255, 255, 255), unit_circle.center, 20)
                pygame.draw.circle(screen, COLOR_BLACK, unit_circle.center, 20, 2)

                # Draw H indicator for held units
                if unit.held:
                    held_text = self.small_font.render("H", True, (255, 100, 100))
                    screen.blit(held_text, (unit_circle.centerx - held_text.get_width() // 2,
                                           unit_circle.centery - held_text.get_height() // 2))

                # Store rect for click detection
                self.garrison_unit_rects.append((unit_circle, unit))
        else:
            empty_text = self.small_font.render("No units garrisoned", True, (120, 130, 140))
            screen.blit(empty_text, (garrison_rect.centerx - empty_text.get_width() // 2, garrison_rect.centery - 8))

        # Draw garrison context menu if open
        if self.garrison_context_menu_open and self.garrison_context_unit:
            menu_w = 120
            menu_h = 40

            # Use saved position from when menu was opened
            menu_x = self.garrison_context_menu_x
            menu_y = self.garrison_context_menu_y

            self.garrison_context_menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
            pygame.draw.rect(screen, (50, 50, 55), self.garrison_context_menu_rect, border_radius=4)
            pygame.draw.rect(screen, (120, 120, 130), self.garrison_context_menu_rect, 2, border_radius=4)

            # Activate button
            self.garrison_activate_rect = pygame.Rect(menu_x + 5, menu_y + 5, menu_w - 10, 30)
            pygame.draw.rect(screen, COLOR_BUTTON, self.garrison_activate_rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.garrison_activate_rect, 2, border_radius=4)

            activate_text = self.small_font.render("Activate", True, COLOR_TEXT)
            screen.blit(activate_text, (self.garrison_activate_rect.centerx - activate_text.get_width() // 2,
                                       self.garrison_activate_rect.centery - activate_text.get_height() // 2))

        # Draw citizen specialist context menu if open
        if self.citizen_context_open:
            self._draw_citizen_context_menu(screen, game)

        # BOTTOM LEFT: Current Production (expanded)
        prod_x = content_x
        prod_y = screen_h - 310
        prod_w = 500
        prod_h = 290
        prod_rect = pygame.Rect(prod_x, prod_y, prod_w, prod_h)
        pygame.draw.rect(screen, (45, 40, 35), prod_rect, border_radius=8)
        pygame.draw.rect(screen, (140, 120, 80), prod_rect, 2, border_radius=8)

        prod_title = self.small_font.render("PRODUCTION", True, (220, 200, 160))
        screen.blit(prod_title, (prod_x + 10, prod_y + 8))

        # Production item
        prod_name_text = base.current_production if base.current_production else "Nothing"
        prod_name = self.small_font.render(prod_name_text, True, COLOR_TEXT)
        screen.blit(prod_name, (prod_x + 15, prod_y + 35))

        # Progress bar
        prod_progress_rect = pygame.Rect(prod_x + 10, prod_y + 60, 200, 20)
        pygame.draw.rect(screen, (20, 20, 20), prod_progress_rect, border_radius=4)

        # Calculate actual fill percentage
        if base.current_production and base.production_cost > 0:
            progress_pct = base.production_progress / base.production_cost
            prod_fill = int(200 * progress_pct)
        else:
            prod_fill = 0

        if prod_fill > 0:
            pygame.draw.rect(screen, (140, 180, 100), pygame.Rect(prod_x + 10, prod_y + 60, prod_fill, 20), border_radius=4)
        pygame.draw.rect(screen, (140, 120, 80), prod_progress_rect, 2, border_radius=4)

        # Show turns remaining
        if base.current_production:
            turns_text = self.small_font.render(f"{base.production_turns_remaining} turns", True, (180, 180, 200))
            screen.blit(turns_text, (prod_x + 10, prod_y + 88))
        else:
            turns_text = self.small_font.render("No production", True, (180, 180, 200))
            screen.blit(turns_text, (prod_x + 10, prod_y + 88))

        # Production queue label
        queue_x = prod_x + 230
        queue_label = self.small_font.render("Queue:", True, (200, 180, 140))
        screen.blit(queue_label, (queue_x, prod_y + 35))

        # Queue items
        if base.production_queue:
            # Show first 10 items in queue
            y_offset = 55
            for i, item in enumerate(base.production_queue[:10]):  # Show max 10 items
                item_text = self.small_font.render(f"{i+1}. {item}", True, (180, 180, 180))
                screen.blit(item_text, (queue_x, prod_y + y_offset))
                y_offset += 18
            if len(base.production_queue) > 10:
                more_text = self.small_font.render(f"+{len(base.production_queue) - 10} more", True, (120, 120, 120))
                screen.blit(more_text, (queue_x, prod_y + y_offset))
        else:
            queue_text = self.small_font.render("(empty)", True, (120, 120, 120))
            screen.blit(queue_text, (queue_x, prod_y + 55))

        # Change, Hurry, and Queue buttons
        button_y = prod_y + 250
        change_rect = pygame.Rect(prod_x + 10, button_y, 90, 30)
        hurry_rect = pygame.Rect(prod_x + 110, button_y, 90, 30)
        queue_rect = pygame.Rect(prod_x + 210, button_y, 90, 30)

        self.prod_change_rect = change_rect
        self.prod_hurry_rect = hurry_rect
        self.prod_queue_rect = queue_rect

        # Change button
        change_hover = change_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if change_hover else COLOR_BUTTON, change_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, change_rect, 1, border_radius=4)
        change_text = self.small_font.render("Change", True, COLOR_TEXT)
        screen.blit(change_text, (change_rect.centerx - change_text.get_width() // 2, change_rect.centery - 7))

        # Hurry button (grayed out if already hurried this turn)
        hurry_disabled = base.hurried_this_turn
        if hurry_disabled:
            # Gray out the button
            pygame.draw.rect(screen, (40, 40, 40), hurry_rect, border_radius=4)
            pygame.draw.rect(screen, (80, 80, 80), hurry_rect, 1, border_radius=4)
            hurry_text = self.small_font.render("Hurry", True, (100, 100, 100))
        else:
            hurry_hover = hurry_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, COLOR_BUTTON_HOVER if hurry_hover else COLOR_BUTTON, hurry_rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, hurry_rect, 1, border_radius=4)
            hurry_text = self.small_font.render("Hurry", True, COLOR_TEXT)
        screen.blit(hurry_text, (hurry_rect.centerx - hurry_text.get_width() // 2, hurry_rect.centery - 7))

        # Queue button
        queue_hover = queue_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if queue_hover else COLOR_BUTTON, queue_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, queue_rect, 1, border_radius=4)
        queue_text = self.small_font.render("Queue", True, COLOR_TEXT)
        screen.blit(queue_text, (queue_rect.centerx - queue_text.get_width() // 2, queue_rect.centery - 7))

        # BOTTOM RIGHT: Supported Units
        support_x = content_x + content_w - 250
        support_y = prod_y
        support_w = 240
        support_h = 120
        support_rect = pygame.Rect(support_x, support_y, support_w, support_h)
        pygame.draw.rect(screen, (35, 40, 45), support_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 120, 140), support_rect, 2, border_radius=8)

        support_title = self.small_font.render("UNIT SUPPORT", True, (180, 200, 220))
        screen.blit(support_title, (support_x + 10, support_y + 8))

        # Show tiny unit icons
        if base.supported_units:
            for i, unit in enumerate(base.supported_units):
                u_x = support_x + 15 + (i % 6) * 35
                u_y = support_y + 35 + (i // 6) * 35
                pygame.draw.circle(screen, (255, 255, 255), (u_x + 12, u_y + 12), 12)
                pygame.draw.circle(screen, COLOR_BLACK, (u_x + 12, u_y + 12), 12, 1)
        else:
            support_text = self.small_font.render(f"0 units supported", True, (120, 140, 160))
            screen.blit(support_text, (support_x + 15, support_y + 40))

        # Base name title is drawn above the mini-map (see earlier in this function)

        # Rename and OK buttons at bottom center
        button_w = 150
        button_h = 50
        button_spacing = 20
        button_y = screen_h - button_h - 20

        # Calculate center position for both buttons
        total_button_w = button_w * 2 + button_spacing
        buttons_start_x = (screen_w - total_button_w) // 2

        # Rename button
        rename_button_x = buttons_start_x
        self.base_view_rename_rect = pygame.Rect(rename_button_x, button_y, button_w, button_h)

        rename_hover = self.base_view_rename_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if rename_hover else COLOR_BUTTON, self.base_view_rename_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if rename_hover else COLOR_BUTTON_BORDER, self.base_view_rename_rect, 2, border_radius=6)

        rename_text = self.font.render("Rename", True, COLOR_TEXT)
        screen.blit(rename_text, (self.base_view_rename_rect.centerx - rename_text.get_width() // 2, self.base_view_rename_rect.centery - 10))

        # OK button
        ok_button_x = buttons_start_x + button_w + button_spacing
        self.base_view_ok_rect = pygame.Rect(ok_button_x, button_y, button_w, button_h)

        ok_hover = self.base_view_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, self.base_view_ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, self.base_view_ok_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.base_view_ok_rect.centerx - ok_text.get_width() // 2, self.base_view_ok_rect.centery - 10))

        # Hurry production popup (draw on top if open)
        if self.hurry_production_open:
            self._draw_hurry_production_popup(screen, base, game)

        # Production selection popup (draw on top if open)
        if self.production_selection_open:
            self._draw_production_selection_popup(screen, base, game)

        # Queue management popup (draw on top if open)
        if self.queue_management_open:
            self._draw_queue_management_popup(screen, base, game)

    def _draw_hurry_production_popup(self, screen, base, game):
        """Draw the hurry production popup dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 450, 280
        dialog_x = display.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_surf = self.font.render("Hurry Production", True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Production info
        info_y = dialog_y + 60
        prod_text = self.small_font.render(f"Current: {base.current_production}", True, COLOR_TEXT)
        screen.blit(prod_text, (dialog_x + 30, info_y))

        # Use the same turns calculation as production panel
        remaining_minerals = base.production_cost - base.production_progress
        credit_cost = remaining_minerals * 2  # 2 credits per mineral in SMAC
        turns_remaining = getattr(base, 'production_turns_remaining', 0) or 0
        cost_text = self.small_font.render(f"Remaining: {turns_remaining} turns ({credit_cost} credits)", True, (200, 220, 100))
        screen.blit(cost_text, (dialog_x + 30, info_y + 25))

        credits_text = self.small_font.render(f"Your credits: {game.energy_credits}", True, (200, 220, 100))
        screen.blit(credits_text, (dialog_x + 30, info_y + 50))

        # Error message (shown for 3 seconds)
        import time
        if self.hurry_error_message and (time.time() - self.hurry_error_time) < 3.0:
            error_surf = self.font.render(self.hurry_error_message, True, (255, 50, 50))
            screen.blit(error_surf, (dialog_x + dialog_w // 2 - error_surf.get_width() // 2, dialog_y + 100))
        elif self.hurry_error_message:
            # Clear error after 3 seconds
            self.hurry_error_message = ""

        # Input label
        input_label_y = dialog_y + 140
        label_surf = self.small_font.render("Credits to spend:", True, COLOR_TEXT)
        screen.blit(label_surf, (dialog_x + 30, input_label_y))

        # Input field
        input_y = input_label_y + 25
        input_rect = pygame.Rect(dialog_x + 30, input_y, dialog_w - 60, 40)
        pygame.draw.rect(screen, (20, 25, 30), input_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, input_rect, 2, border_radius=6)

        # Draw input text
        input_surf = self.font.render(self.hurry_input, True, COLOR_TEXT)
        screen.blit(input_surf, (input_rect.x + 10, input_rect.y + 10))

        # Draw cursor
        cursor_x = input_rect.x + 10 + input_surf.get_width() + 2
        if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking cursor
            pygame.draw.line(screen, COLOR_TEXT, (cursor_x, input_rect.y + 8),
                           (cursor_x, input_rect.y + input_rect.height - 8), 2)

        # Buttons
        button_y = dialog_y + dialog_h - 60
        button_w = 100
        button_spacing = 15

        # All button
        all_rect = pygame.Rect(dialog_x + 30, button_y, button_w, 40)
        self.hurry_all_rect = all_rect
        all_hover = all_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if all_hover else COLOR_BUTTON, all_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if all_hover else COLOR_BUTTON_BORDER, all_rect, 2, border_radius=6)
        all_surf = self.small_font.render("Pay All", True, COLOR_TEXT)
        screen.blit(all_surf, (all_rect.centerx - all_surf.get_width() // 2, all_rect.centery - 8))

        # OK button
        ok_rect = pygame.Rect(dialog_x + 30 + button_w + button_spacing, button_y, button_w, 40)
        self.hurry_ok_rect = ok_rect
        ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.small_font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2, ok_rect.centery - 8))

        # Cancel button
        cancel_rect = pygame.Rect(dialog_x + dialog_w - 30 - button_w, button_y, button_w, 40)
        self.hurry_cancel_rect = cancel_rect
        cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if cancel_hover else COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_surf = self.small_font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_surf, (cancel_rect.centerx - cancel_surf.get_width() // 2, cancel_rect.centery - 8))

    def _draw_production_selection_popup(self, screen, base, game):
        """Draw the production selection popup dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Get all production options (units from design workshop + facilities)
        # Calculate turns for each item based on cost and base population
        def get_turns(item_name):
            cost = base._get_production_cost(item_name)
            if cost == 0:
                return 0
            minerals_per_turn = max(1, getattr(base, 'minerals_per_turn', base.population)
                                    - getattr(base, 'support_cost_paid', 0))
            if minerals_per_turn == 0:
                return 999
            return (cost + minerals_per_turn - 1) // minerals_per_turn  # Ceiling division

        # Build production items list
        production_items = []

        # Units from faction designs (use base owner's faction)
        from game.unit_components import generate_unit_name, get_chassis_by_id
        faction_designs = game.factions[base.owner].designs
        for design in faction_designs.get_designs():
            # Skip artifacts - they can't be built, only found
            if design['weapon'] == 'artifact':
                continue

            # Generate unit name from component IDs
            unit_name = generate_unit_name(
                design['weapon'], design['chassis'], design['armor'], design['reactor'],
                design.get('ability1', 'none'), design.get('ability2', 'none')
            )
            turns = get_turns(unit_name)
            # Show basic stats in description
            chassis_data = get_chassis_by_id(design['chassis'])
            chassis_display = chassis_data['name'] if chassis_data else design['chassis']
            description = f"{chassis_display}, {turns} turns"
            production_items.append({
                "name": unit_name,
                "type": "unit",
                "description": description,
                "design": design  # Store design data for stats display
            })

        # Facilities (filtered by tech and not already built)
        player_tech_tree = game.factions[game.player_faction_id].tech_tree
        available_facilities = facilities.get_available_facilities(player_tech_tree)

        # Get free facility for this base's faction
        from game.data.data import FACTION_DATA
        free_facility_name = None
        faction_index = base.owner  # owner IS faction_id
        if faction_index < len(FACTION_DATA):
            faction = FACTION_DATA[faction_index]
            free_facility_name = faction.get('bonuses', {}).get('free_facility')

        for facility in available_facilities:
            # Skip Headquarters (auto-granted to first base)
            if facility['id'] == 'headquarters':
                continue
            # Skip if already built in this base (check by ID)
            if facility['id'] in base.facilities:
                continue
            turns = get_turns(facility['name'])
            description = f"{facility['effect']}, {turns} turns, {facility['maint']} energy/turn"
            production_items.append({"name": facility['name'], "type": "facility", "description": description})

        # Secret Projects (filtered by tech and global uniqueness)
        if not hasattr(game, 'built_projects'):
            game.built_projects = set()
        available_projects = facilities.get_available_projects(player_tech_tree, game.built_projects)
        for project in available_projects:
            turns = get_turns(project['name'])
            description = f"{project['effect']}, {turns} turns"
            production_items.append({"name": project['name'], "type": "project", "description": description})

        # (Stockpile Energy is already included via facility_data.py and the loop above)

        # Calculate grid layout (5 items per row with bigger squares to prevent text overflow)
        items_per_row = 5
        item_size = 140
        item_spacing = 15
        rows = (len(production_items) + items_per_row - 1) // items_per_row

        # Dialog dimensions
        dialog_w = items_per_row * item_size + (items_per_row + 1) * item_spacing
        dialog_h = 100 + rows * item_size + (rows + 1) * item_spacing + 80  # Title + grid + buttons
        dialog_x = display.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_text = "Add to Queue" if self.production_selection_mode == "queue" else "Select Production"
        title_surf = self.font.render(title_text, True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Draw grid of production items
        self.production_item_rects = []
        grid_start_y = dialog_y + 70

        for i, item in enumerate(production_items):
            row = i // items_per_row
            col = i % items_per_row

            item_x = dialog_x + item_spacing + col * (item_size + item_spacing)
            item_y = grid_start_y + row * (item_size + item_spacing)
            item_rect = pygame.Rect(item_x, item_y, item_size, item_size)

            # Store rect for click detection
            self.production_item_rects.append((item_rect, item["name"]))

            # Check if this is the selected item
            is_selected = (self.selected_production_item == item["name"])
            is_hovered = item_rect.collidepoint(pygame.mouse.get_pos())

            # Draw item background
            if is_selected:
                pygame.draw.rect(screen, (60, 80, 60), item_rect, border_radius=6)
                pygame.draw.rect(screen, (100, 200, 100), item_rect, 3, border_radius=6)
            elif is_hovered:
                pygame.draw.rect(screen, (50, 55, 60), item_rect, border_radius=6)
                pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, item_rect, 2, border_radius=6)
            else:
                pygame.draw.rect(screen, (40, 45, 50), item_rect, border_radius=6)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, item_rect, 2, border_radius=6)

            # Draw icon
            icon_y = item_y + 15
            if item["type"] == "unit":
                # Draw simple unit icon (circle)
                pygame.draw.circle(screen, (255, 255, 255), (item_rect.centerx, icon_y + 15), 15)
                pygame.draw.circle(screen, COLOR_BLACK, (item_rect.centerx, icon_y + 15), 15, 2)
            else:  # facility
                # Draw facility icon (for Stockpile Energy: yellow square/diamond)
                icon_rect = pygame.Rect(item_rect.centerx - 12, icon_y + 3, 24, 24)
                pygame.draw.rect(screen, (220, 200, 80), icon_rect, border_radius=4)
                pygame.draw.rect(screen, (255, 220, 100), icon_rect, 2, border_radius=4)

            # Draw item name (wrap if too long)
            name_text = item["name"]
            name_words = name_text.split()
            name_lines = []
            current_line = ""
            for word in name_words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.small_font.render(test_line, True, COLOR_TEXT)
                if test_surf.get_width() <= item_size - 10:
                    current_line = test_line
                else:
                    if current_line:
                        name_lines.append(current_line)
                    current_line = word
            if current_line:
                name_lines.append(current_line)

            # Draw name lines (max 2 lines)
            name_y = icon_y + 35
            for line in name_lines[:2]:
                line_surf = self.small_font.render(line, True, COLOR_TEXT)
                line_rect = line_surf.get_rect(centerx=item_rect.centerx, top=name_y)
                screen.blit(line_surf, line_rect)
                name_y += 16

            # Draw description (word wrap)
            desc_lines = []
            words = item["description"].split()
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.small_font.render(test_line, True, (180, 190, 200))
                if test_surf.get_width() <= item_size - 10:
                    current_line = test_line
                else:
                    if current_line:
                        desc_lines.append(current_line)
                    current_line = word
            if current_line:
                desc_lines.append(current_line)

            # Draw description lines (start after name lines)
            desc_y = name_y + 5
            for line in desc_lines[:2]:  # Max 2 lines
                line_surf = self.small_font.render(line, True, (160, 170, 180))
                line_rect = line_surf.get_rect(centerx=item_rect.centerx, top=desc_y)
                screen.blit(line_surf, line_rect)
                desc_y += 16

            # Draw unit stats (weapon-armor-speed) for units
            if item["type"] == "unit" and "design" in item:
                from game.unit_components import get_weapon_by_id, get_armor_by_id, get_chassis_by_id
                design = item["design"]
                # Look up stats from component IDs
                weapon_data = get_weapon_by_id(design['weapon'])
                armor_data = get_armor_by_id(design['armor'])
                chassis_data = get_chassis_by_id(design['chassis'])
                weapon_power = weapon_data['attack'] if weapon_data else 0
                armor_defense = armor_data['defense'] if armor_data else 0
                chassis_speed = chassis_data['speed'] if chassis_data else 1
                stats_text = f"{weapon_power}-{armor_defense}-{chassis_speed}"
                stats_surf = self.small_font.render(stats_text, True, (200, 220, 100))
                stats_rect = stats_surf.get_rect(centerx=item_rect.centerx, bottom=item_rect.bottom - 5)
                screen.blit(stats_surf, stats_rect)

        # Buttons at bottom
        button_y = dialog_y + dialog_h - 60
        button_w = 120
        button_spacing = 20

        # OK button
        ok_x = dialog_x + dialog_w // 2 - button_w - button_spacing // 2
        ok_rect = pygame.Rect(ok_x, button_y, button_w, 40)
        self.prod_select_ok_rect = ok_rect
        ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2, ok_rect.centery - 10))

        # Cancel button
        cancel_x = dialog_x + dialog_w // 2 + button_spacing // 2
        cancel_rect = pygame.Rect(cancel_x, button_y, button_w, 40)
        self.prod_select_cancel_rect = cancel_rect
        cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if cancel_hover else COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_surf = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_surf, (cancel_rect.centerx - cancel_surf.get_width() // 2, cancel_rect.centery - 10))

    def _draw_queue_management_popup(self, screen, base, game):
        """Draw the production queue management popup dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 500, 450
        dialog_x = display.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        title_surf = self.font.render("Production Queue", True, COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        # Current production label
        current_y = dialog_y + 60
        current_label = self.small_font.render("Current Production:", True, (180, 180, 200))
        screen.blit(current_label, (dialog_x + 30, current_y))
        current_prod = self.small_font.render(base.current_production, True, (100, 200, 100))
        screen.blit(current_prod, (dialog_x + 200, current_y))

        # Queue list
        queue_y = current_y + 40
        queue_label = self.small_font.render("Queued Items:", True, (180, 180, 200))
        screen.blit(queue_label, (dialog_x + 30, queue_y))

        # Draw queue items
        self.queue_item_rects = []
        item_y = queue_y + 30
        max_visible = 8

        if base.production_queue:
            for i, item in enumerate(base.production_queue[:max_visible]):
                item_rect = pygame.Rect(dialog_x + 30, item_y, dialog_w - 60, 30)
                self.queue_item_rects.append((item_rect, i))

                # Highlight on hover
                is_hovered = item_rect.collidepoint(pygame.mouse.get_pos())
                if is_hovered:
                    pygame.draw.rect(screen, (60, 50, 50), item_rect, border_radius=4)
                    pygame.draw.rect(screen, (200, 100, 100), item_rect, 2, border_radius=4)
                else:
                    pygame.draw.rect(screen, (40, 45, 50), item_rect, border_radius=4)
                    pygame.draw.rect(screen, COLOR_BUTTON_BORDER, item_rect, 1, border_radius=4)

                # Draw item number and name
                item_text = self.small_font.render(f"{i+1}. {item}", True, COLOR_TEXT)
                screen.blit(item_text, (item_rect.x + 10, item_rect.y + 7))

                # Draw remove hint
                if is_hovered:
                    remove_hint = self.small_font.render("(click to remove)", True, (200, 150, 150))
                    screen.blit(remove_hint, (item_rect.right - remove_hint.get_width() - 10, item_rect.y + 7))

                item_y += 35

            if len(base.production_queue) > max_visible:
                more_text = self.small_font.render(f"+{len(base.production_queue) - max_visible} more items...", True, (120, 120, 140))
                screen.blit(more_text, (dialog_x + 30, item_y))
        else:
            empty_text = self.small_font.render("(empty - click Add to queue items)", True, (120, 120, 140))
            screen.blit(empty_text, (dialog_x + 30, item_y))

        # Buttons at bottom
        button_y = dialog_y + dialog_h - 60
        button_w = 110
        button_spacing = 15

        # Add button
        add_x = dialog_x + 30
        add_rect = pygame.Rect(add_x, button_y, button_w, 40)
        self.queue_add_rect = add_rect
        add_hover = add_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if add_hover else COLOR_BUTTON, add_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if add_hover else COLOR_BUTTON_BORDER, add_rect, 2, border_radius=6)
        add_surf = self.small_font.render("Add Item", True, COLOR_TEXT)
        screen.blit(add_surf, (add_rect.centerx - add_surf.get_width() // 2, add_rect.centery - 8))

        # Clear button
        clear_x = add_x + button_w + button_spacing
        clear_rect = pygame.Rect(clear_x, button_y, button_w, 40)
        self.queue_clear_rect = clear_rect
        clear_hover = clear_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if clear_hover else COLOR_BUTTON, clear_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if clear_hover else COLOR_BUTTON_BORDER, clear_rect, 2, border_radius=6)
        clear_surf = self.small_font.render("Clear All", True, COLOR_TEXT)
        screen.blit(clear_surf, (clear_rect.centerx - clear_surf.get_width() // 2, clear_rect.centery - 8))

        # Close button
        close_x = dialog_x + dialog_w - 30 - button_w
        close_rect = pygame.Rect(close_x, button_y, button_w, 40)
        self.queue_close_rect = close_rect
        close_hover = close_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if close_hover else COLOR_BUTTON, close_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if close_hover else COLOR_BUTTON_BORDER, close_rect, 2, border_radius=6)
        close_surf = self.small_font.render("Close", True, COLOR_TEXT)
        screen.blit(close_surf, (close_rect.centerx - close_surf.get_width() // 2, close_rect.centery - 8))

    def _draw_citizen_context_menu(self, screen, game):
        """Draw the specialist assignment context menu."""
        base = self.viewing_base
        if not base:
            return

        faction = game.factions[base.owner]
        available = _get_available_specialists(faction.tech_tree, base.population)

        # Build item list
        items = []
        if self.citizen_context_type == 'worker':
            for spec in available:
                items.append((spec['id'], spec['name']))
        else:
            # It's a specialist — offer revert + switch to other specialists
            items.append(('__revert__', 'Revert to Auto'))
            for spec in available:
                if spec['id'] != self.citizen_context_type:
                    items.append((spec['id'], spec['name']))

        item_h = 30
        menu_w = 160
        menu_h = len(items) * item_h + 8
        mx = min(self.citizen_context_menu_x, display.SCREEN_WIDTH - menu_w - 4)
        my = min(self.citizen_context_menu_y, display.SCREEN_HEIGHT - menu_h - 4)

        pygame.draw.rect(screen, (45, 45, 52), pygame.Rect(mx, my, menu_w, menu_h), border_radius=4)
        pygame.draw.rect(screen, (120, 120, 135), pygame.Rect(mx, my, menu_w, menu_h), 2, border_radius=4)

        self.citizen_context_item_rects = []
        mouse_pos = pygame.mouse.get_pos()
        for i, (action, label) in enumerate(items):
            item_rect = pygame.Rect(mx + 4, my + 4 + i * item_h, menu_w - 8, item_h - 2)
            hover = item_rect.collidepoint(mouse_pos)
            if hover:
                pygame.draw.rect(screen, (70, 70, 90), item_rect, border_radius=3)
            if action != '__revert__':
                draw_citizen_icon(screen, item_rect.x + 16, item_rect.centery, 22, action)
            label_surf = self.small_font.render(label, True, (220, 215, 200) if hover else COLOR_TEXT)
            screen.blit(label_surf, (item_rect.x + (34 if action != '__revert__' else 8),
                                     item_rect.centery - label_surf.get_height() // 2))
            self.citizen_context_item_rects.append((item_rect, action))

    def handle_base_view_right_click(self, pos, game):
        """Handle right-clicks in the base view screen (for garrison context menu)."""
        # Check if right-clicking on a garrison unit
        for unit_rect, unit in self.garrison_unit_rects:
            if unit_rect.collidepoint(pos):
                # Open context menu for this unit and save position
                self.garrison_context_menu_open = True
                self.garrison_context_unit = unit

                # Save menu position (with screen boundary checks)
                menu_w = 120
                menu_h = 40
                screen_w = 1280  # From display.py
                screen_h = 720

                self.garrison_context_menu_x = min(pos[0], screen_w - menu_w)
                self.garrison_context_menu_y = min(pos[1], screen_h - menu_h)

                return True

        # Check citizen icons — only for player's own base
        base = self.viewing_base
        if base and base.owner == game.player_faction_id:
            for rect, ctype, spec_idx in self.civ_icon_rects:
                if rect.collidepoint(pos):
                    if ctype == 'worker':
                        self.citizen_context_open = True
                        self.citizen_context_type = 'worker'
                        self.citizen_context_spec_idx = None
                        self.citizen_context_menu_x = pos[0]
                        self.citizen_context_menu_y = pos[1]
                        self.garrison_context_menu_open = False
                        return True
                    elif ctype not in ('talent', 'drone'):
                        # It's a specialist
                        self.citizen_context_open = True
                        self.citizen_context_type = ctype
                        self.citizen_context_spec_idx = spec_idx
                        self.citizen_context_menu_x = pos[0]
                        self.citizen_context_menu_y = pos[1]
                        self.garrison_context_menu_open = False
                        return True
        return False

    def handle_base_view_click(self, pos, game, is_enemy=False):
        """Handle clicks in the base view screen. Returns 'close' if should exit, None otherwise."""
        base = self.viewing_base
        is_enemy_base = base and base.owner != game.player_faction_id

        # If garrison context menu is open, handle it first
        if self.garrison_context_menu_open:
            # Check if clicking Activate button
            if self.garrison_activate_rect and self.garrison_activate_rect.collidepoint(pos):
                unit = self.garrison_context_unit
                if unit:
                    # Unhold the unit
                    unit.held = False
                    # Select the unit
                    game.selected_unit = unit
                    # Close context menu and base view
                    self.garrison_context_menu_open = False
                    self.garrison_context_unit = None
                    return 'close'  # Exit base view
            # Close menu on any other click
            self.garrison_context_menu_open = False
            self.garrison_context_unit = None
            return None

        # Citizen specialist context menu
        if self.citizen_context_open:
            for item_rect, action in self.citizen_context_item_rects:
                if item_rect.collidepoint(pos):
                    if action == '__revert__':
                        # Remove this specialist; recalculate will reassign as worker/talent/drone
                        if self.citizen_context_spec_idx is not None:
                            base.specialists.pop(self.citizen_context_spec_idx)
                        base.calculate_population_happiness()
                        base.calculate_resource_output(game.game_map)
                        base.growth_turns_remaining = base._calculate_growth_turns()
                        game.set_status_message("Specialist reverted to auto citizen")
                    else:
                        # Assign worker as specialist, or replace existing specialist
                        if self.citizen_context_type == 'worker':
                            base.specialists.append(action)
                        elif self.citizen_context_spec_idx is not None:
                            base.specialists[self.citizen_context_spec_idx] = action
                        base.calculate_population_happiness()
                        base.calculate_resource_output(game.game_map)
                        base.growth_turns_remaining = base._calculate_growth_turns()
                        from game.data.unit_data import SPECIALISTS
                        name = next((s['name'] for s in SPECIALISTS if s['id'] == action), action)
                        game.set_status_message(f"Citizen assigned as {name}")
                    self.citizen_context_open = False
                    return None
            # Click outside menu closes it
            self.citizen_context_open = False
            return None

        # If queue management popup is open, handle its clicks first
        if self.queue_management_open:
            # Check item clicks (remove from queue)
            for item_rect, item_index in self.queue_item_rects:
                if item_rect.collidepoint(pos):
                    removed_item = base.production_queue.pop(item_index)
                    game.set_status_message(f"Removed {removed_item} from queue")
                    return None

            # Check Add button
            if hasattr(self, 'queue_add_rect') and self.queue_add_rect.collidepoint(pos):
                # Open production selection to add to queue
                self.production_selection_mode = "queue"
                self.production_selection_open = True
                self.selected_production_item = None
                self.queue_management_open = False  # Close queue popup while selecting
                return None

            # Check Clear button
            if hasattr(self, 'queue_clear_rect') and self.queue_clear_rect.collidepoint(pos):
                if base.production_queue:
                    base.production_queue.clear()
                    game.set_status_message("Production queue cleared")
                return None

            # Check Close button
            if hasattr(self, 'queue_close_rect') and self.queue_close_rect.collidepoint(pos):
                self.queue_management_open = False
                return None

            # Click outside - consume event
            return None

        # If production selection popup is open, handle its clicks first
        if self.production_selection_open:
            # Check item clicks
            for item_rect, item_name in self.production_item_rects:
                if item_rect.collidepoint(pos):
                    self.selected_production_item = item_name
                    return None

            # Check OK button
            if hasattr(self, 'prod_select_ok_rect') and self.prod_select_ok_rect.collidepoint(pos):
                if self.selected_production_item:
                    if self.production_selection_mode == "queue":
                        # Add to queue
                        base.production_queue.append(self.selected_production_item)
                        game.set_status_message(f"Added {self.selected_production_item} to queue")
                        # Reopen queue management
                        self.production_selection_open = False
                        self.selected_production_item = None
                        self.queue_management_open = True
                    else:
                        # Change production (reset progress)
                        base.current_production = self.selected_production_item
                        base.production_progress = 0
                        base.production_cost = base._get_production_cost(self.selected_production_item)
                        base.production_turns_remaining = base._calculate_production_turns()
                        game.set_status_message(f"Now producing: {self.selected_production_item}")

                        self.production_selection_open = False
                        self.selected_production_item = None
                return None

            # Check Cancel button
            if hasattr(self, 'prod_select_cancel_rect') and self.prod_select_cancel_rect.collidepoint(pos):
                self.production_selection_open = False
                self.selected_production_item = None
                return None

            # Click outside - consume event
            return None

        # If hurry popup is open, handle its clicks first
        if self.hurry_production_open:
            # Check Cancel button
            if hasattr(self, 'hurry_cancel_rect') and self.hurry_cancel_rect.collidepoint(pos):
                self.hurry_production_open = False
                self.hurry_input = ""
                self.hurry_error_message = ""
                return None

            # Check Pay All button
            if hasattr(self, 'hurry_all_rect') and self.hurry_all_rect.collidepoint(pos):
                if base and base.current_production:
                    remaining_minerals = base.production_cost - base.production_progress
                    credit_cost = remaining_minerals * 2  # 2 credits per mineral (SMAC standard)
                    self.hurry_input = str(credit_cost)
                return None

            # Check OK button
            if hasattr(self, 'hurry_ok_rect') and self.hurry_ok_rect.collidepoint(pos):
                if base and base.current_production and self.hurry_input:
                    try:
                        # Check if base has already hurried this turn
                        if base.hurried_this_turn:
                            import time
                            self.hurry_error_message = "Already hurried this turn!"
                            self.hurry_error_time = time.time()
                            return None  # Keep popup open

                        credits_to_spend = int(self.hurry_input)
                        if credits_to_spend <= 0:
                            import time
                            self.hurry_error_message = "Must spend at least 1 credit"
                            self.hurry_error_time = time.time()
                            return None  # Keep popup open

                        if credits_to_spend > game.energy_credits:
                            import time
                            self.hurry_error_message = "Not enough funds!"
                            self.hurry_error_time = time.time()
                            return None  # Keep popup open

                        # Perform the hurry
                        game.energy_credits -= credits_to_spend
                        production_added, completed = base.hurry_production(credits_to_spend)

                        # Mark base as hurried this turn
                        base.hurried_this_turn = True

                        if completed:
                            game.set_status_message(f"Rushed {base.current_production}! Will complete next turn.")
                        else:
                            turns_saved = production_added
                            game.set_status_message(f"Rushed production: {turns_saved} turns saved")

                        # Only close popup on success
                        self.hurry_production_open = False
                        self.hurry_input = ""
                        self.hurry_error_message = ""  # Clear any error
                    except ValueError:
                        import time
                        self.hurry_error_message = "Invalid amount entered"
                        self.hurry_error_time = time.time()
                        return None  # Keep popup open
                else:
                    # No input - just close
                    self.hurry_production_open = False
                    self.hurry_input = ""
                    self.hurry_error_message = ""
                return None

            # Click outside popup closes it
            return None

        # Check map tile clicks (toggle worked/unworked) — only for own bases
        if not is_enemy_base:
            for tile_rect, map_x, map_y in self.map_tile_rects:
                if tile_rect.collidepoint(pos):
                    base.toggle_worked_tile(map_x, map_y, game.game_map)
                    base.calculate_resource_output(game.game_map)
                    base.growth_turns_remaining = base._calculate_growth_turns()
                    return None

        # Check OK button
        if hasattr(self, 'base_view_ok_rect') and self.base_view_ok_rect.collidepoint(pos):
            self.viewing_base = None
            self._reset_base_popups()  # Reset all popups when closing
            return 'close'

        # Check Rename button (player's own bases only)
        if not is_enemy_base and hasattr(self, 'base_view_rename_rect') and self.base_view_rename_rect and self.base_view_rename_rect.collidepoint(pos):
            if base:
                self.rename_base_target = base
                self.base_name_input = base.name
                self.base_name_text_selected = True
            return 'rename'

        # All remaining interactive controls are player-only
        if is_enemy_base:
            return None

        # Check Change button - open production selection
        if hasattr(self, 'prod_change_rect') and self.prod_change_rect.collidepoint(pos):
            if base:
                self.production_selection_mode = "change"
                self.production_selection_open = True
                self.selected_production_item = base.current_production  # Pre-select current
            return None

        # Check Hurry button - open popup
        if hasattr(self, 'prod_hurry_rect') and self.prod_hurry_rect.collidepoint(pos):
            if base and base.current_production:
                if base.hurried_this_turn:
                    game.set_status_message("Base has already hurried this turn!")
                else:
                    remaining_cost = base.production_cost - base.production_progress
                    if remaining_cost <= 0:
                        game.set_status_message("Production already complete!")
                    else:
                        self.hurry_production_open = True
                        self.hurry_input = ""
            return None

        # Check Queue button - open queue management
        if hasattr(self, 'prod_queue_rect') and self.prod_queue_rect.collidepoint(pos):
            if base:
                self.queue_management_open = True
            return None

        # Check Governor button - toggle governor
        if hasattr(self, 'governor_button_rect') and self.governor_button_rect and self.governor_button_rect.collidepoint(pos):
            if base:
                base.governor_enabled = not base.governor_enabled
                if base.governor_enabled:
                    # Set default mode if none set (generalist mode uses 'build')
                    if not base.governor_mode:
                        base.governor_mode = 'build'

                    # Immediately change production based on governor
                    from game.governor import select_production
                    faction = game.factions[base.owner]
                    new_production = select_production(base, faction, game)
                    if new_production:
                        if new_production != base.current_production:
                            base.current_production = new_production
                            base.production_progress = 0
                            base.production_cost = base._get_production_cost(new_production)
                            base.production_turns_remaining = base._calculate_production_turns()
                            game.set_status_message(f"Governor activated: Now producing {new_production}")
                        else:
                            game.set_status_message(f"Governor activated for {base.name}")
                    else:
                        game.set_status_message(f"Governor activated for {base.name}")
                else:
                    game.set_status_message(f"Governor deactivated for {base.name}")
            return None

        # Check mode buttons - set governor mode
        if hasattr(self, 'mode_button_rects') and self.mode_button_rects:
            for btn_rect, mode_name in self.mode_button_rects:
                if btn_rect.collidepoint(pos):
                    if base:
                        if base.governor_enabled and base.governor_mode == mode_name:
                            # Clicking active mode switches to generalist (no specific mode)
                            base.governor_mode = None
                            game.set_status_message(f"Governor mode cleared (generalist)")
                        else:
                            # Activate governor with this mode
                            base.governor_enabled = True
                            base.governor_mode = mode_name

                            # Immediately change production based on new mode
                            from game.governor import select_production
                            faction = game.factions[base.owner]
                            new_production = select_production(base, faction, game)
                            if new_production:
                                if new_production != base.current_production:
                                    base.current_production = new_production
                                    base.production_progress = 0
                                    base.production_cost = base._get_production_cost(new_production)
                                    base.production_turns_remaining = base._calculate_production_turns()
                                    game.set_status_message(f"Governor: {mode_name.upper()} mode - Now producing {new_production}")
                                else:
                                    game.set_status_message(f"Governor: {mode_name.upper()} mode - Continuing {new_production}")
                            else:
                                game.set_status_message(f"Governor set to {mode_name.upper()} mode")
                    return None

        return None