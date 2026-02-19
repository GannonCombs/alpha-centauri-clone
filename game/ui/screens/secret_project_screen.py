"""SecretProjectScreen — full-screen list and notification popup for secret projects."""

import pygame
from game.data import display_data as display
from game.data.display_data import COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_BORDER
from game.data.facility_data import SECRET_PROJECTS
from game.data.faction_data import FACTION_DATA


class SecretProjectScreen:
    """Handles the secret projects full-screen view and the started/warning notification popup."""

    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.ok_rect = None           # Close button for the full-screen view
        self.notify_ok_rect = None    # Dismiss button for the notification popup

    # ------------------------------------------------------------------
    # Drawing helpers (shared by both views)
    # ------------------------------------------------------------------

    def _draw_overlay(self, screen, alpha=180):
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

    def _centered_popup_rect(self, width, height):
        x = display.SCREEN_WIDTH // 2 - width // 2
        y = display.SCREEN_HEIGHT // 2 - height // 2
        return pygame.Rect(x, y, width, height)

    def _draw_popup_box(self, screen, rect, border_color=(100, 140, 160), bg_color=(30, 40, 50)):
        pygame.draw.rect(screen, bg_color, rect, border_radius=12)
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=12)

    # ------------------------------------------------------------------
    # Full-screen view (F5)
    # ------------------------------------------------------------------

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
        """Handle click on the full-screen view. Returns 'close' if OK was clicked."""
        if self.ok_rect and self.ok_rect.collidepoint(pos):
            return 'close'
        return None

    # ------------------------------------------------------------------
    # Notification popup (secret project started / 1-turn warning)
    # ------------------------------------------------------------------

    def draw_notification(self, screen, game):
        """Modal popup for secret project started or 1-turn-away warning."""
        notifications = getattr(game, 'secret_project_notifications', [])
        if not notifications:
            return
        notif = notifications[0]
        notif_type = notif.get('type', 'started')
        project_name = notif['project_name']
        faction_id = notif['faction_id']
        faction = FACTION_DATA[faction_id] if faction_id < len(FACTION_DATA) else {}
        faction_name = faction.get('name', 'Unknown')
        faction_color = faction.get('color', (180, 160, 100))

        self._draw_overlay(screen, alpha=160)

        if notif_type == 'warning':
            player_also = notif.get('player_also_building', False)
            popup_h = 220 if player_also else 190
            popup_w = 500
            header_text = "SECRET PROJECT ALERT"
            header_color = (255, 180, 60)
            border_color = (200, 140, 40)
            line1 = f"{faction_name} is one turn away"
            line2 = f"from completing {project_name}."
            line3 = "You are also building it — rush production!" if player_also else None
        else:
            popup_h = 190
            popup_w = 480
            header_text = "SECRET PROJECT BEGUN"
            header_color = (200, 210, 255)
            border_color = faction_color
            line1 = f"{faction_name} has begun work on"
            line2 = project_name + "."
            line3 = None

        popup_rect = self._centered_popup_rect(popup_w, popup_h)
        self._draw_popup_box(screen, popup_rect, border_color=border_color)

        header = self.font.render(header_text, True, header_color)
        screen.blit(header, (popup_rect.centerx - header.get_width() // 2, popup_rect.y + 18))

        y = popup_rect.y + 56
        l1 = self.small_font.render(line1, True, COLOR_TEXT)
        screen.blit(l1, (popup_rect.centerx - l1.get_width() // 2, y))
        y += 20
        l2 = self.small_font.render(line2, True, faction_color)
        screen.blit(l2, (popup_rect.centerx - l2.get_width() // 2, y))
        if line3:
            y += 22
            l3 = self.small_font.render(line3, True, (255, 220, 100))
            screen.blit(l3, (popup_rect.centerx - l3.get_width() // 2, y))

        # OK button
        ok_w, ok_h = 90, 34
        ok_rect = pygame.Rect(popup_rect.centerx - ok_w // 2, popup_rect.y + popup_h - 50, ok_w, ok_h)
        self.notify_ok_rect = ok_rect
        mouse_pos = pygame.mouse.get_pos()
        ok_hover = ok_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_surf = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_surf, (ok_rect.centerx - ok_surf.get_width() // 2,
                               ok_rect.centery - ok_surf.get_height() // 2))

    def handle_notification_click(self, pos, game):
        """Handle click on the notification popup. Returns True if dismissed."""
        if self.notify_ok_rect and self.notify_ok_rect.collidepoint(pos):
            game.secret_project_notifications.pop(0)
            return True
        return False
