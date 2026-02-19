"""Save/Load dialog UI components."""

import os
import pygame
from game import save_load
from game.data import display_data as display


class SaveLoadDialog:
    """Manages the save and load dialog UI."""

    def __init__(self, font, small_font):
        """Initialize the dialog manager.

        Args:
            font: Regular pygame font
            small_font: Small pygame font
        """
        self.font = font
        self.small_font = small_font

        # Dialog state
        self.mode = None  # 'save' or 'load' or None
        self.save_files = []  # List of available saves
        self.selected_file_index = None
        self.save_name_input = ""  # For save dialog text input
        self.cursor_visible = True  # For blinking cursor
        self.cursor_timer = 0
        self.error_message = ""  # For displaying errors
        self.scroll_offset = 0  # For scrolling file list

        # UI elements (initialized when dialog opens)
        self.dialog_rect = None
        self.save_button_rect = None
        self.cancel_button_rect = None
        self.input_rect = None
        self.file_list_rects = []

        # Confirmation dialog state
        self.confirmation_mode = None  # 'overwrite' when showing overwrite warning
        self.pending_filepath = None  # File to save after confirmation
        self.confirm_ok_rect = None
        self.confirm_cancel_rect = None

        # Scrollbar button rects (load dialog)
        self.scroll_up_rect = None
        self.scroll_down_rect = None

    def show_save_dialog(self, game):
        """Open the save dialog with suggested filename.

        Args:
            game: Current game instance
        """
        self.mode = 'save'
        self.save_name_input = save_load.generate_save_filename(game)
        self.error_message = ""
        self.selected_file_index = None
        self.scroll_offset = 0

        # Load existing save files for reference
        self.save_files = save_load.list_save_files()

    def show_load_dialog(self):
        """Open the load dialog with file list."""
        self.mode = 'load'
        self.save_name_input = ""
        self.error_message = ""
        self.selected_file_index = None
        self.scroll_offset = 0

        # Load save files
        self.save_files = save_load.list_save_files()

        if not self.save_files:
            self.error_message = "No save files found"

    def draw(self, screen):
        """Render the active dialog.

        Args:
            screen: Pygame screen surface
        """
        if self.mode is None:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((10, 15, 20))
        screen.blit(overlay, (0, 0))

        # Dialog box dimensions
        if self.mode == 'save':
            dialog_w, dialog_h = 600, 400
        else:  # load
            dialog_w, dialog_h = 600, 500

        dialog_x = display.SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = display.SCREEN_HEIGHT // 2 - dialog_h // 2
        self.dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        # Draw dialog background
        pygame.draw.rect(screen, (30, 40, 50), self.dialog_rect, border_radius=12)
        pygame.draw.rect(screen, display.COLOR_BUTTON_HIGHLIGHT, self.dialog_rect, 3, border_radius=12)

        # Title
        title_text = "Save Game" if self.mode == 'save' else "Load Game"
        title_surf = self.font.render(title_text, True, display.COLOR_TEXT)
        screen.blit(title_surf, (dialog_x + dialog_w // 2 - title_surf.get_width() // 2, dialog_y + 20))

        if self.mode == 'save':
            self._draw_save_dialog(screen, dialog_x, dialog_y, dialog_w, dialog_h)
        else:
            self._draw_load_dialog(screen, dialog_x, dialog_y, dialog_w, dialog_h)

        # Error message at bottom (if any)
        if self.error_message:
            error_surf = self.small_font.render(self.error_message, True, (255, 100, 100))
            screen.blit(error_surf, (dialog_x + dialog_w // 2 - error_surf.get_width() // 2, dialog_y + dialog_h - 100))

        # Draw confirmation popup if active
        if self.confirmation_mode == 'overwrite':
            self._draw_confirmation_popup(screen)

    def _draw_save_dialog(self, screen, dialog_x, dialog_y, dialog_w, dialog_h):
        """Draw save dialog contents."""

        # Label
        label_y = dialog_y + 70
        label_surf = self.small_font.render("Filename:", True, display.COLOR_TEXT)
        screen.blit(label_surf, (dialog_x + 40, label_y))

        # Text input field
        input_y = label_y + 25
        input_w = dialog_w - 80
        input_h = 40
        self.input_rect = pygame.Rect(dialog_x + 40, input_y, input_w, input_h)

        pygame.draw.rect(screen, (50, 60, 70), self.input_rect, border_radius=4)
        pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, self.input_rect, 2, border_radius=4)

        # Text content
        text_surf = self.font.render(self.save_name_input, True, display.COLOR_TEXT)
        text_x = self.input_rect.x + 10
        text_y = self.input_rect.centery - text_surf.get_height() // 2
        screen.blit(text_surf, (text_x, text_y))

        # Blinking cursor
        if self.cursor_visible:
            cursor_x = text_x + text_surf.get_width() + 2
            pygame.draw.line(screen, display.COLOR_TEXT,
                             (cursor_x, text_y), (cursor_x, text_y + text_surf.get_height()), 2)

        # Info text
        info_y = input_y + 60
        info_text = "Enter filename without extension (.sav will be added)"
        info_surf = self.small_font.render(info_text, True, (150, 150, 150))
        screen.blit(info_surf, (dialog_x + 40, info_y))

        # Existing saves list (for reference, not clickable)
        if self.save_files:
            list_y = info_y + 40
            list_label = self.small_font.render("Existing saves:", True, (150, 150, 150))
            screen.blit(list_label, (dialog_x + 40, list_y))

            for i, save_file in enumerate(self.save_files[:5]):  # Show first 5
                item_y = list_y + 20 + i * 20
                filename_surf = self.small_font.render(save_file['filename'], True, (120, 120, 120))
                screen.blit(filename_surf, (dialog_x + 60, item_y))

        # Buttons
        self._draw_dialog_buttons(screen, dialog_x, dialog_y, dialog_w, dialog_h, "Save")

    def _draw_load_dialog(self, screen, dialog_x, dialog_y, dialog_w, dialog_h):
        """Draw load dialog contents with a scrollable file list."""

        if not self.save_files:
            no_saves_surf = self.font.render("No save files found", True, (150, 150, 150))
            screen.blit(no_saves_surf, (dialog_x + dialog_w // 2 - no_saves_surf.get_width() // 2, dialog_y + 150))
            self._draw_dialog_buttons(screen, dialog_x, dialog_y, dialog_w, dialog_h, "Load")
            return

        # ── layout constants ──────────────────────────────────────────────
        scrollbar_w = 18
        list_x      = dialog_x + 20
        list_y      = dialog_y + 60
        list_w      = dialog_w - 40 - scrollbar_w - 6   # leave room for scrollbar
        list_h      = dialog_h - 145                    # stop above buttons
        item_h      = 62
        item_gap    = 4
        item_stride = item_h + item_gap
        max_visible = list_h // item_stride
        max_scroll  = max(0, len(self.save_files) - max_visible)

        # Clamp scroll offset (handles list shrinking between opens)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        # ── list background ───────────────────────────────────────────────
        list_bg = pygame.Rect(list_x, list_y, list_w, list_h)
        pygame.draw.rect(screen, (22, 30, 38), list_bg, border_radius=4)
        pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, list_bg, 1, border_radius=4)

        # ── clip so items can never bleed outside the list area ───────────
        old_clip = screen.get_clip()
        screen.set_clip(list_bg)

        self.file_list_rects = []
        for i in range(max_visible):
            actual_index = self.scroll_offset + i
            if actual_index >= len(self.save_files):
                break
            save_file = self.save_files[actual_index]

            item_y    = list_y + i * item_stride + item_gap
            item_rect = pygame.Rect(list_x + 2, item_y, list_w - 4, item_h)
            is_selected = actual_index == self.selected_file_index

            bg_color = (70, 90, 110) if is_selected else (45, 55, 65)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=4)
            pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, item_rect, 1, border_radius=4)

            filename_surf = self.font.render(save_file['filename'], True, display.COLOR_TEXT)
            screen.blit(filename_surf, (item_rect.x + 10, item_rect.y + 8))

            info_text = f"MY {save_file['mission_year']} - {save_file['timestamp'][:16]}"
            info_surf = self.small_font.render(info_text, True, (170, 170, 170))
            screen.blit(info_surf, (item_rect.x + 10, item_rect.y + 34))

            self.file_list_rects.append((item_rect, actual_index))

        screen.set_clip(old_clip)

        # ── scrollbar ─────────────────────────────────────────────────────
        sb_x     = list_x + list_w + 6
        sb_y     = list_y
        arrow_h  = 20

        # Track background
        track_rect = pygame.Rect(sb_x, sb_y, scrollbar_w, list_h)
        pygame.draw.rect(screen, (28, 36, 44), track_rect, border_radius=4)
        pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, track_rect, 1, border_radius=4)

        # Up arrow
        self.scroll_up_rect = pygame.Rect(sb_x, sb_y, scrollbar_w, arrow_h)
        up_hover = self.scroll_up_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, display.COLOR_BUTTON_HOVER if up_hover else display.COLOR_BUTTON,
                         self.scroll_up_rect, border_radius=3)
        up_surf = self.small_font.render("▲", True, display.COLOR_TEXT)
        screen.blit(up_surf, (self.scroll_up_rect.centerx - up_surf.get_width() // 2,
                               self.scroll_up_rect.centery - up_surf.get_height() // 2))

        # Down arrow
        self.scroll_down_rect = pygame.Rect(sb_x, sb_y + list_h - arrow_h, scrollbar_w, arrow_h)
        down_hover = self.scroll_down_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, display.COLOR_BUTTON_HOVER if down_hover else display.COLOR_BUTTON,
                         self.scroll_down_rect, border_radius=3)
        down_surf = self.small_font.render("▼", True, display.COLOR_TEXT)
        screen.blit(down_surf, (self.scroll_down_rect.centerx - down_surf.get_width() // 2,
                                 self.scroll_down_rect.centery - down_surf.get_height() // 2))

        # Thumb (only when there's something to scroll)
        if max_scroll > 0:
            usable_h  = list_h - 2 * arrow_h
            thumb_h   = max(20, int(usable_h * max_visible / len(self.save_files)))
            thumb_pos = int((usable_h - thumb_h) * self.scroll_offset / max_scroll)
            thumb_rect = pygame.Rect(sb_x + 2, sb_y + arrow_h + thumb_pos, scrollbar_w - 4, thumb_h)
            pygame.draw.rect(screen, (100, 130, 160), thumb_rect, border_radius=3)

        # ── counter label ─────────────────────────────────────────────────
        count_text = f"{self.scroll_offset + 1}–{min(self.scroll_offset + max_visible, len(self.save_files))} of {len(self.save_files)}"
        count_surf = self.small_font.render(count_text, True, (130, 130, 130))
        screen.blit(count_surf, (dialog_x + dialog_w // 2 - count_surf.get_width() // 2,
                                  list_y + list_h + 6))

        # ── action buttons ────────────────────────────────────────────────
        self._draw_dialog_buttons(screen, dialog_x, dialog_y, dialog_w, dialog_h, "Load")

    def _draw_dialog_buttons(self, screen, dialog_x, dialog_y, dialog_w, dialog_h, action_label):
        """Draw Save/Load and Cancel buttons."""

        button_y = dialog_y + dialog_h - 70
        button_w = 140
        button_h = 45

        # Action button (Save/Load)
        action_x = dialog_x + dialog_w // 2 - button_w - 10
        self.save_button_rect = pygame.Rect(action_x, button_y, button_w, button_h)

        action_hover = self.save_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, display.COLOR_BUTTON_HOVER if action_hover else display.COLOR_BUTTON,
                         self.save_button_rect, border_radius=6)
        pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, self.save_button_rect, 2, border_radius=6)

        action_surf = self.font.render(action_label, True, display.COLOR_TEXT)
        screen.blit(action_surf, (self.save_button_rect.centerx - action_surf.get_width() // 2,
                                 self.save_button_rect.centery - 10))

        # Cancel button
        cancel_x = dialog_x + dialog_w // 2 + 10
        self.cancel_button_rect = pygame.Rect(cancel_x, button_y, button_w, button_h)

        cancel_hover = self.cancel_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, display.COLOR_BUTTON_HOVER if cancel_hover else display.COLOR_BUTTON,
                         self.cancel_button_rect, border_radius=6)
        pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, self.cancel_button_rect, 2, border_radius=6)

        cancel_surf = self.font.render("Cancel", True, display.COLOR_TEXT)
        screen.blit(cancel_surf, (self.cancel_button_rect.centerx - cancel_surf.get_width() // 2,
                                 self.cancel_button_rect.centery - 10))

    def _draw_confirmation_popup(self, screen):
        """Draw overwrite confirmation popup."""
        # Semi-transparent overlay
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Confirmation dialog
        confirm_w, confirm_h = 500, 200
        confirm_x = display.SCREEN_WIDTH // 2 - confirm_w // 2
        confirm_y = display.SCREEN_HEIGHT // 2 - confirm_h // 2
        confirm_rect = pygame.Rect(confirm_x, confirm_y, confirm_w, confirm_h)

        pygame.draw.rect(screen, (40, 50, 60), confirm_rect, border_radius=8)
        pygame.draw.rect(screen, display.COLOR_BUTTON_HIGHLIGHT, confirm_rect, 3, border_radius=8)

        # Warning message
        message_lines = [
            "This will overwrite your save file.",
            "Are you sure?"
        ]

        for i, line in enumerate(message_lines):
            text_surf = self.font.render(line, True, display.COLOR_TEXT)
            text_x = confirm_x + confirm_w // 2 - text_surf.get_width() // 2
            text_y = confirm_y + 40 + i * 35
            screen.blit(text_surf, (text_x, text_y))

        # OK and Cancel buttons
        button_y = confirm_y + confirm_h - 60
        button_w = 120
        button_h = 40

        # OK button
        ok_x = confirm_x + confirm_w // 2 - button_w - 10
        self.confirm_ok_rect = pygame.Rect(ok_x, button_y, button_w, button_h)

        ok_hover = self.confirm_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, display.COLOR_BUTTON_HOVER if ok_hover else display.COLOR_BUTTON,
                         self.confirm_ok_rect, border_radius=6)
        pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, self.confirm_ok_rect, 2, border_radius=6)

        ok_surf = self.font.render("OK", True, display.COLOR_TEXT)
        screen.blit(ok_surf, (self.confirm_ok_rect.centerx - ok_surf.get_width() // 2,
                             self.confirm_ok_rect.centery - 10))

        # Cancel button
        cancel_x = confirm_x + confirm_w // 2 + 10
        self.confirm_cancel_rect = pygame.Rect(cancel_x, button_y, button_w, button_h)

        cancel_hover = self.confirm_cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, display.COLOR_BUTTON_HOVER if cancel_hover else display.COLOR_BUTTON,
                         self.confirm_cancel_rect, border_radius=6)
        pygame.draw.rect(screen, display.COLOR_BUTTON_BORDER, self.confirm_cancel_rect, 2, border_radius=6)

        cancel_surf = self.font.render("Cancel", True, display.COLOR_TEXT)
        screen.blit(cancel_surf, (self.confirm_cancel_rect.centerx - cancel_surf.get_width() // 2,
                                 self.confirm_cancel_rect.centery - 10))

    def handle_event(self, event, game):
        """Process events for the dialog.

        Args:
            event: Pygame event
            game: Current game instance

        Returns:
            str or tuple: 'save_complete', ('load_complete', new_game), 'close', or True/False
        """
        if self.mode is None:
            return False

        if event.type == pygame.KEYDOWN:
            return self.handle_keydown(event, game)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_click(event.pos, game)
        elif event.type == pygame.MOUSEWHEEL and self.mode == 'load':
            self.scroll_offset = max(0, min(
                self.scroll_offset - event.y,
                max(0, len(self.save_files) - 1)
            ))
            return True

        return True  # Consume all events when dialog is open

    def handle_keydown(self, event, game):
        """Handle keyboard input.

        Args:
            event: Pygame KEYDOWN event
            game: Current game instance

        Returns:
            str or bool: Result of action or True to consume event
        """
        # Block keyboard input when confirmation is showing
        if self.confirmation_mode == 'overwrite':
            if event.key == pygame.K_RETURN:
                # Enter confirms the overwrite
                return self._perform_save(game, self.pending_filepath)
            elif event.key == pygame.K_ESCAPE:
                # Escape cancels
                self.confirmation_mode = None
                self.pending_filepath = None
                return True
            return True

        if self.mode == 'save':
            # Text input for filename
            if event.key == pygame.K_BACKSPACE:
                self.save_name_input = self.save_name_input[:-1]
            elif event.key == pygame.K_RETURN:
                # Try to save
                return self._try_save(game)
            elif event.key == pygame.K_ESCAPE:
                self.mode = None
                return 'close'
            elif len(self.save_name_input) < 100:  # Limit filename length
                # Add character (filter out invalid filesystem characters)
                char = event.unicode
                if char.isprintable() and char not in r'<>:"/\|?*':
                    self.save_name_input += char
        elif self.mode == 'load':
            if event.key == pygame.K_RETURN:
                # Try to load
                return self._try_load(game)
            elif event.key == pygame.K_ESCAPE:
                self.mode = None
                return 'close'
            elif event.key == pygame.K_UP:
                if self.selected_file_index is not None and self.selected_file_index > 0:
                    self.selected_file_index -= 1
                    if self.selected_file_index < self.scroll_offset:
                        self.scroll_offset = self.selected_file_index
            elif event.key == pygame.K_DOWN:
                if self.selected_file_index is not None and self.selected_file_index < len(self.save_files) - 1:
                    self.selected_file_index += 1
                    # Scroll down if selection moves past the visible window
                    # (page size approximated; draw will clamp anyway)
                    if self.selected_file_index >= self.scroll_offset + 6:
                        self.scroll_offset = self.selected_file_index - 5

        return True

    def handle_click(self, pos, game):
        """Handle mouse clicks.

        Args:
            pos: Mouse position (x, y)
            game: Current game instance

        Returns:
            str or tuple or bool: Result of action or True to consume event
        """
        # Handle confirmation dialog clicks first
        if self.confirmation_mode == 'overwrite':
            if self.confirm_ok_rect and self.confirm_ok_rect.collidepoint(pos):
                # User confirmed overwrite - proceed with save
                return self._perform_save(game, self.pending_filepath)
            elif self.confirm_cancel_rect and self.confirm_cancel_rect.collidepoint(pos):
                # User cancelled - close confirmation and return to save dialog
                self.confirmation_mode = None
                self.pending_filepath = None
                return True
            return True  # Consume all clicks when confirmation is showing

        # Check Cancel button
        if self.cancel_button_rect and self.cancel_button_rect.collidepoint(pos):
            self.mode = None
            return 'close'

        # Check Save/Load button
        if self.save_button_rect and self.save_button_rect.collidepoint(pos):
            if self.mode == 'save':
                return self._try_save(game)
            else:
                return self._try_load(game)

        # Check scroll arrows and file list items (load mode only)
        if self.mode == 'load':
            if self.scroll_up_rect and self.scroll_up_rect.collidepoint(pos):
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            if self.scroll_down_rect and self.scroll_down_rect.collidepoint(pos):
                self.scroll_offset = min(self.scroll_offset + 1, max(0, len(self.save_files) - 1))
                return True
            for item_rect, file_index in self.file_list_rects:
                if item_rect.collidepoint(pos):
                    self.selected_file_index = file_index
                    return True

        # Check input field (save mode only)
        if self.mode == 'save' and self.input_rect and self.input_rect.collidepoint(pos):
            # Focus on input (already focused by default)
            return True

        return True

    def _try_save(self, game):
        """Attempt to save the game. Shows overwrite confirmation if file exists.

        Args:
            game: Current game instance

        Returns:
            str: 'save_complete' if successful, True otherwise
        """
        if not self.save_name_input.strip():
            self.error_message = "Please enter a filename"
            return True

        # Add .sav extension if not present
        filename = self.save_name_input.strip()
        if not filename.endswith('.sav'):
            filename += '.sav'

        filepath = os.path.join('game/saves', filename)

        # Check if file already exists
        if os.path.exists(filepath):
            # Show overwrite confirmation
            self.confirmation_mode = 'overwrite'
            self.pending_filepath = filepath
            return True

        # File doesn't exist - save directly
        return self._perform_save(game, filepath)

    def _perform_save(self, game, filepath):
        """Perform the actual save operation.

        Args:
            game: Current game instance
            filepath: Full path to save file

        Returns:
            str: 'save_complete' if successful, True otherwise
        """
        success, message = save_load.save_game(game, filepath)

        if success:
            self.mode = None
            self.confirmation_mode = None
            self.pending_filepath = None
            return 'save_complete'
        else:
            self.error_message = message
            self.confirmation_mode = None
            self.pending_filepath = None
            return True

    def _try_load(self, game):
        """Attempt to load a game.

        Args:
            game: Current game instance (will be replaced)

        Returns:
            tuple or str: ('load_complete', new_game) if successful, True otherwise
        """
        if self.selected_file_index is None:
            self.error_message = "Please select a save file"
            return True

        save_file = self.save_files[self.selected_file_index]
        filepath = save_file['filepath']

        try:
            new_game = save_load.load_game(filepath)
            self.mode = None
            return ('load_complete', new_game)
        except Exception as e:
            self.error_message = str(e)
            return True

    def update(self, dt):
        """Update dialog state (cursor blink).

        Args:
            dt: Delta time in milliseconds
        """
        if self.mode == 'save':
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # Blink every 500ms
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
