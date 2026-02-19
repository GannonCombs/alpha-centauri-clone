"""SecretProjectScreen — full-screen list of in-progress and completed secret projects."""

import pygame
from game.data import display_data as display
from game.data.display_data import COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_BORDER
from game.data.facility_data import SECRET_PROJECTS
from game.data.faction_data import FACTION_DATA
from game.ui.components import draw_button


class SecretProjectScreen:
    """Full-screen view (F5) showing in-progress and completed secret projects."""

    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.ok_rect = None

    def draw_secret_projects(self, screen, game):
        """Full-screen view showing in-progress and completed secret projects."""
        sw, sh = display.SCREEN_WIDTH, display.SCREEN_HEIGHT
        mouse_pos = pygame.mouse.get_pos()

        screen.fill((12, 18, 28))

        title_surf = self.font.render("SECRET PROJECTS", True, (200, 210, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 20))
        pygame.draw.line(screen, (60, 80, 110), (40, 50), (sw - 40, 50), 1)

        # Build lookup: project name → faction_id currently building it
        in_progress_by_name = {}
        built_projects = getattr(game, 'built_projects', set())
        for base in game.bases:
            prod = getattr(base, 'current_production', None)
            if prod:
                for proj in SECRET_PROJECTS:
                    if proj['name'] == prod and proj['id'] not in built_projects:
                        if proj['name'] not in in_progress_by_name:
                            in_progress_by_name[proj['name']] = base.owner

        # Only in-progress and completed; in-progress first
        visible_projects = []
        for proj in SECRET_PROJECTS:
            if proj['name'] in in_progress_by_name:
                visible_projects.append((proj, True, False))
            elif proj['id'] in built_projects:
                visible_projects.append((proj, False, True))

        # Layout: 2 columns, cards sized to fill screen
        cols = 2
        col_spacing = 20
        row_spacing = 14
        pad_x = 80
        pad_top = 70
        pad_bottom = 70

        card_w = (sw - pad_x * 2 - (cols - 1) * col_spacing) // cols
        rows = max(1, (len(visible_projects) + cols - 1) // cols)
        available_h = sh - pad_top - pad_bottom
        card_h = max(80, (available_h - (rows - 1) * row_spacing) // rows)

        grid_x = pad_x
        grid_y = pad_top

        if not visible_projects:
            msg = self.font.render("No secret projects are in progress or completed.", True, (120, 130, 145))
            screen.blit(msg, (sw // 2 - msg.get_width() // 2, sh // 2 - msg.get_height() // 2))
        else:
            for i, (proj, is_inprogress, is_built) in enumerate(visible_projects):
                row = i // cols
                col = i % cols
                cx = grid_x + col * (card_w + col_spacing)
                cy = grid_y + row * (card_h + row_spacing)
                card_rect = pygame.Rect(cx, cy, card_w, card_h)

                if is_inprogress:
                    bg_color = (18, 38, 18)
                    border_color = (70, 150, 70)
                else:
                    bg_color = (28, 24, 14)
                    border_color = (110, 90, 35)

                pygame.draw.rect(screen, bg_color, card_rect, border_radius=6)
                pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=6)

                # Project name (word-wrapped, max 2 lines)
                name_words = proj['name'].split()
                name_lines = []
                cur = ""
                for word in name_words:
                    test = (cur + " " + word).strip()
                    if self.small_font.size(test)[0] <= card_w - 14:
                        cur = test
                    else:
                        if cur:
                            name_lines.append(cur)
                        cur = word
                if cur:
                    name_lines.append(cur)

                text_y = cy + 10
                for line in name_lines[:2]:
                    surf = self.small_font.render(line, True, COLOR_TEXT)
                    screen.blit(surf, (cx + 8, text_y))
                    text_y += 16

                # Status at bottom of card
                if is_inprogress:
                    fid = in_progress_by_name[proj['name']]
                    fname = FACTION_DATA[fid].get('name', 'Unknown') if fid < len(FACTION_DATA) else 'Unknown'
                    fcolor = FACTION_DATA[fid].get('color', (160, 200, 160)) if fid < len(FACTION_DATA) else (160, 200, 160)
                    faction_surf = self.small_font.render(fname, True, fcolor)
                    screen.blit(faction_surf, (cx + 8, cy + card_h - 34))
                    ip_surf = self.small_font.render("In Progress", True, (220, 80, 80))
                    screen.blit(ip_surf, (cx + 8, cy + card_h - 18))
                else:
                    done_surf = self.small_font.render("Completed", True, (160, 150, 60))
                    screen.blit(done_surf, (cx + 8, cy + card_h - 18))

        # OK button at bottom center
        ok_w, ok_h = 100, 36
        ok_rect = pygame.Rect(sw // 2 - ok_w // 2, sh - pad_bottom + 16, ok_w, ok_h)
        self.ok_rect = ok_rect
        ok_hover = ok_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2,
                               ok_rect.centery - ok_surf.get_height() // 2))

        hint = self.small_font.render("Press F5 or Esc to close", True, (80, 90, 100))
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - pad_bottom + 56))

    def handle_click(self, pos):
        """Returns 'close' if the OK button was clicked."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            return 'close'
        return None
