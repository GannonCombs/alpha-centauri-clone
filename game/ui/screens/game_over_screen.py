"""Game over / victory screen."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                     COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)
from game.ui.components import draw_overlay


class GameOverScreen:
    """Draws the game over overlay and handles its two buttons.

    handle_click returns:
      'new_game'       — player clicked New Game
      'return_to_menu' — player clicked Main Menu (after retiring)
      'exit'           — player clicked Exit
      True             — click consumed but no action needed
    """

    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.title_font = pygame.font.Font(None, 48)
        self.score_font = pygame.font.Font(None, 42)
        self.new_game_rect = None
        self.exit_rect = None

    def draw(self, screen, game):
        from game.score import calculate_score

        draw_overlay(screen, alpha=200)

        dialog_w, dialog_h = 620, 560
        dialog_x = display.SCREEN_WIDTH  // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        pygame.draw.rect(screen, (30, 40, 50), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT, dialog_rect, 3, border_radius=12)

        # Title
        if getattr(game, 'resigned', False):
            title_text  = "RETIRED"
            title_color = (180, 160, 100)
        elif getattr(game, 'victory_type', None) is not None:
            title_text  = f"VICTORY! ({game.victory_type.capitalize()})"
            title_color = (100, 255, 100)
        else:
            title_text  = "DEFEAT"
            title_color = (255, 100, 100)

        title_surf = self.title_font.render(title_text, True, title_color)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 24))

        # Score
        try:
            sc = calculate_score(game)
        except Exception:
            sc = None

        y = dialog_y + 80

        if sc is not None:
            score_surf = self.score_font.render(f"SCORE:  {sc['total']}", True, (220, 200, 100))
            screen.blit(score_surf, (dialog_x + dialog_w // 2 - score_surf.get_width() // 2, y))
            y += 46

            pygame.draw.line(screen, (80, 100, 110),
                             (dialog_x + 30, y), (dialog_x + dialog_w - 30, y), 1)
            y += 10

            breakdown = [
                ("Citizens",                          sc['citizens'],        None),
                ("Diplo/Econ bonus",                  sc['diplo_bonus'],     None if sc['diplo_bonus'] else "(victory type only)"),
                ("Surrendered bases",                 sc['surrendered'],     None),
                ("Commerce income",                   sc['commerce'],        None),
                ("Technologies",                      sc['techs'],           None),
                ("Transcendent Thought",              sc['transcendent'],    None),
                (f"Secret Projects (×{sc['secret_count']})", sc['secret_projects'], None),
                ("Victory bonus",                     sc['victory_bonus'],   None),
            ]

            col_label_x = dialog_x + 40
            col_value_x = dialog_x + dialog_w - 80
            line_h = 24
            row_y = y
            for label, value, note in breakdown:
                if note and value == 0:
                    color    = (80, 90, 100)
                    row_surf = self.small_font.render(f"{label}:  —", True, color)
                else:
                    color    = (180, 200, 190) if value > 0 else (100, 110, 120)
                    row_surf = self.small_font.render(label + ":", True, color)
                    val_surf = self.small_font.render(str(value), True, color)
                    screen.blit(val_surf, (col_value_x - val_surf.get_width(), row_y + 2))
                screen.blit(row_surf, (col_label_x, row_y + 2))
                row_y += line_h

            y = row_y + 6
            pygame.draw.line(screen, (80, 100, 110),
                             (dialog_x + 30, y), (dialog_x + dialog_w - 30, y), 1)
            y += 8

            nl = sc['native_life']
            if nl != 'average':
                pct      = "+25%" if nl == 'abundant' else "-25%"
                nl_color = (100, 200, 100) if nl == 'abundant' else (200, 130, 80)
                nl_surf  = self.small_font.render(
                    f"Native Life ({nl.capitalize()}):  {pct}", True, nl_color)
                screen.blit(nl_surf, (col_label_x, y + 2))

        # Buttons
        button_y  = dialog_y + dialog_h - 80
        button_w  = 200
        button_h  = 50
        spacing   = 40

        new_game_x = dialog_x + dialog_w // 2 - button_w - spacing // 2
        new_game_rect = pygame.Rect(new_game_x, button_y, button_w, button_h)
        self.new_game_rect = new_game_rect

        exit_rect = pygame.Rect(dialog_x + dialog_w // 2 + spacing // 2, button_y, button_w, button_h)
        self.exit_rect = exit_rect

        mouse = pygame.mouse.get_pos()
        left_label = "Main Menu" if getattr(game, 'resigned', False) else "New Game"
        for rect, label in [(new_game_rect, left_label), (exit_rect, "Exit")]:
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(screen, COLOR_BUTTON_HOVER if hover else COLOR_BUTTON,
                             rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if hover else COLOR_BUTTON_BORDER,
                             rect, 2, border_radius=8)
            lbl_surf = self.font.render(label, True, COLOR_TEXT)
            screen.blit(lbl_surf, (rect.centerx - lbl_surf.get_width() // 2,
                                   rect.centery - lbl_surf.get_height() // 2))

    def handle_click(self, pos, game):
        if self.new_game_rect and self.new_game_rect.collidepoint(pos):
            if getattr(game, 'resigned', False):
                return 'return_to_menu'
            return 'new_game'
        if self.exit_rect and self.exit_rect.collidepoint(pos):
            return 'exit'
        return True  # consume but no action
