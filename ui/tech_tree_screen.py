"""Tech Tree screen for viewing and selecting research."""

import pygame
from data import constants
from data.constants import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                            COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)
from ui.data import FACTIONS


class TechTreeScreen:
    """Manages the Technology Tree screen with visualization."""

    def __init__(self, font, small_font):
        """Initialize tech tree screen with fonts.

        Args:
            font: Main pygame font object
            small_font: Small pygame font object
        """
        self.font = font
        self.small_font = small_font

        # State
        self.tech_tree_open = False
        self.tech_tree_scroll_offset = 0
        self.tech_tree_focused_tech = None  # Will be set to player's faction starting tech on first draw

        # UI elements
        self.tech_tree_selection_rects = []
        self.tech_tree_up_arrow = None
        self.tech_tree_down_arrow = None
        self.tech_tree_ok_rect = None
        self.tech_tree_prereq_rects = []  # List of (rect, tech_id) tuples for clickable prerequisites
        self.tech_tree_unlock_rects = []  # List of (rect, tech_id) tuples for clickable unlocks

    def draw_tech_tree(self, screen, game):
        """Draw the Technology Tree screen with visualization.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing tech tree and other game state
        """
        # Initialize focused tech to player's faction starting tech on first draw
        if self.tech_tree_focused_tech is None:
            player_faction = FACTIONS[game.player_faction_id]
            self.tech_tree_focused_tech = player_faction.get('starting_tech', 'Ecology')

        # Fill background
        screen.fill((15, 20, 25))

        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # TOP PROGRESS BAR (~80% screen width)
        progress_bar_w = int(screen_w * 0.8)
        progress_bar_h = 50
        progress_bar_x = (screen_w - progress_bar_w) // 2
        progress_bar_y = 10

        # Progress bar background
        prog_bg_rect = pygame.Rect(progress_bar_x, progress_bar_y, progress_bar_w, progress_bar_h)
        pygame.draw.rect(screen, (30, 35, 40), prog_bg_rect, border_radius=8)

        current_tech_name = game.tech_tree.get_current_tech()
        if current_tech_name and game.tech_tree.current_research:
            # Get category color for progress bar
            category = game.tech_tree.get_current_category()
            fill_color = game.tech_tree.get_category_color(category) if category else (80, 150, 200)

            # Fill progress
            progress_pct = game.tech_tree.get_progress_percentage()
            fill_w = int(progress_bar_w * progress_pct)
            fill_rect = pygame.Rect(progress_bar_x, progress_bar_y, fill_w, progress_bar_h)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=8)

            # Progress text (hide tech name - keep it mysterious!)
            turns_left = game.tech_tree.get_turns_remaining()
            prog_text = self.font.render(f"Research: {turns_left} turns remaining", True, COLOR_TEXT)
            screen.blit(prog_text, (prog_bg_rect.centerx - prog_text.get_width() // 2, prog_bg_rect.centery - 10))
        else:
            # No research active (should not happen with auto-research)
            prog_text = self.font.render("Selecting research...", True, (180, 150, 100))
            screen.blit(prog_text, (prog_bg_rect.centerx - prog_text.get_width() // 2, prog_bg_rect.centery - 10))

        pygame.draw.rect(screen, (100, 140, 180), prog_bg_rect, 3, border_radius=8)

        # LEFT PANEL: Scrollable alphabetized list
        left_panel_x = 20
        left_panel_y = progress_bar_y + progress_bar_h + 20
        left_panel_w = 320
        left_panel_h = screen_h - left_panel_y - 20

        # Panel background
        left_panel_rect = pygame.Rect(left_panel_x, left_panel_y, left_panel_w, left_panel_h)
        pygame.draw.rect(screen, (25, 30, 35), left_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 100, 120), left_panel_rect, 2, border_radius=8)

        # Panel title
        list_title = self.font.render("Technologies", True, (150, 180, 200))
        screen.blit(list_title, (left_panel_x + 10, left_panel_y + 10))

        # Get all techs alphabetically
        all_techs = [(tech_id, tech_data) for tech_id, tech_data in game.tech_tree.technologies.items()]
        all_techs.sort(key=lambda x: x[1]['name'])

        # Scrollable list
        tech_list_y = left_panel_y + 45
        tech_line_h = 22
        visible_lines = (left_panel_h - 60) // tech_line_h
        self.tech_tree_selection_rects = []

        # Draw scroll arrows if needed
        if len(all_techs) > visible_lines:
            # Up arrow
            up_arrow_rect = pygame.Rect(left_panel_x + left_panel_w - 30, left_panel_y + 10, 20, 20)
            pygame.draw.polygon(screen, (150, 180, 200), [
                (up_arrow_rect.centerx, up_arrow_rect.top + 5),
                (up_arrow_rect.left + 3, up_arrow_rect.bottom - 5),
                (up_arrow_rect.right - 3, up_arrow_rect.bottom - 5)
            ])
            self.tech_tree_up_arrow = up_arrow_rect

            # Down arrow
            down_arrow_rect = pygame.Rect(left_panel_x + left_panel_w - 30, left_panel_y + left_panel_h - 30, 20, 20)
            pygame.draw.polygon(screen, (150, 180, 200), [
                (down_arrow_rect.centerx, down_arrow_rect.bottom - 5),
                (down_arrow_rect.left + 3, down_arrow_rect.top + 5),
                (down_arrow_rect.right - 3, down_arrow_rect.top + 5)
            ])
            self.tech_tree_down_arrow = down_arrow_rect
        else:
            self.tech_tree_up_arrow = None
            self.tech_tree_down_arrow = None

        # Display visible techs
        for i in range(self.tech_tree_scroll_offset, min(self.tech_tree_scroll_offset + visible_lines, len(all_techs))):
            tech_id, tech_data = all_techs[i]
            display_index = i - self.tech_tree_scroll_offset
            tech_y = tech_list_y + display_index * tech_line_h

            # Tech status
            status = game.tech_tree.get_tech_status(tech_id)

            # Color based on status
            if status == "Completed":
                tech_color = (100, 220, 100)
                prefix = "✓ "
            elif status == "Researching":
                tech_color = (200, 220, 100)
                prefix = "→ "
            elif status == "Available":
                tech_color = (180, 200, 220)
                prefix = "  "
            else:  # Locked
                tech_color = (100, 110, 120)
                prefix = "  "

            # Clickable rect
            tech_rect = pygame.Rect(left_panel_x + 10, tech_y, left_panel_w - 50, tech_line_h)

            # Highlight if focused or hovered
            is_focused = (tech_id == self.tech_tree_focused_tech)
            is_hovered = tech_rect.collidepoint(pygame.mouse.get_pos())

            if is_focused:
                pygame.draw.rect(screen, (50, 70, 90), tech_rect, border_radius=4)
            elif is_hovered:
                pygame.draw.rect(screen, (40, 50, 60), tech_rect, border_radius=4)

            # Store for click detection
            self.tech_tree_selection_rects.append((tech_rect, tech_id))

            # Tech name
            tech_text = self.small_font.render(f"{prefix}{tech_data['name']}", True, tech_color)
            screen.blit(tech_text, (left_panel_x + 15, tech_y + 3))

        # MAIN VIEW: Tech visualization
        main_panel_x = left_panel_x + left_panel_w + 20
        main_panel_y = left_panel_y
        main_panel_w = screen_w - main_panel_x - 20
        main_panel_h = left_panel_h

        # Main panel background
        main_panel_rect = pygame.Rect(main_panel_x, main_panel_y, main_panel_w, main_panel_h)
        pygame.draw.rect(screen, (20, 25, 30), main_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 100, 120), main_panel_rect, 2, border_radius=8)

        # Draw focused tech
        if self.tech_tree_focused_tech and self.tech_tree_focused_tech in game.tech_tree.technologies:
            self._draw_tech_visualization(screen, game, main_panel_rect)

        # OK button - centered at bottom of main panel
        ok_button_w = 150
        ok_button_h = 50
        ok_button_x = main_panel_rect.centerx - ok_button_w // 2
        ok_button_y = main_panel_rect.bottom - ok_button_h - 10
        self.tech_tree_ok_rect = pygame.Rect(ok_button_x, ok_button_y, ok_button_w, ok_button_h)

        ok_hover = self.tech_tree_ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, self.tech_tree_ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if ok_hover else COLOR_BUTTON_BORDER, self.tech_tree_ok_rect, 2, border_radius=6)

        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (self.tech_tree_ok_rect.centerx - ok_text.get_width() // 2, self.tech_tree_ok_rect.centery - 10))

    def _draw_tech_visualization(self, screen, game, main_rect):
        """Draw the main tech visualization showing focused tech and connections.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing tech tree
            main_rect: Rectangle defining the main visualization area
        """
        focused_id = self.tech_tree_focused_tech
        focused_data = game.tech_tree.technologies[focused_id]

        # Storage for clickable prerequisite/unlock rectangles
        self.tech_tree_prereq_rects = []  # List of (rect, tech_id) tuples
        self.tech_tree_unlock_rects = []  # List of (rect, tech_id) tuples

        # Center tech box
        center_x = main_rect.centerx
        center_y = main_rect.centery
        tech_box_w = 240
        tech_box_h = 180

        # Draw center tech (focused)
        center_rect = pygame.Rect(center_x - tech_box_w // 2, center_y - tech_box_h // 2, tech_box_w, tech_box_h)

        # Get category color for border
        category = focused_data.get('category', 'unknown')
        category_color = game.tech_tree.get_category_color(category)

        # Color based on status
        status = game.tech_tree.get_tech_status(focused_id)
        if status == "Completed":
            bg_color = (40, 60, 40)
            text_color = (255, 255, 255)  # White for completed
        elif status == "Researching":
            bg_color = (60, 60, 40)
            text_color = (255, 255, 100)  # Yellow for researching
        elif status == "Available":
            bg_color = (40, 50, 60)
            text_color = (180, 180, 180)  # Light gray for available
        else:  # Locked
            bg_color = (30, 30, 30)
            category_color = (80, 80, 80)  # Gray out locked techs
            text_color = (100, 100, 100)  # Dark gray for locked

        pygame.draw.rect(screen, bg_color, center_rect, border_radius=10)
        pygame.draw.rect(screen, category_color, center_rect, 3, border_radius=10)  # Use category color for border

        # Tech icon (simple placeholder)
        icon_size = 80
        icon_rect = pygame.Rect(center_rect.centerx - icon_size // 2, center_rect.top + 20, icon_size, icon_size)
        pygame.draw.circle(screen, category_color, icon_rect.center, icon_size // 2)
        pygame.draw.circle(screen, bg_color, icon_rect.center, icon_size // 2 - 3)

        # Tech ID abbreviation in icon
        abbrev_font = pygame.font.Font(None, 32)
        abbrev_text = abbrev_font.render(focused_id[:4], True, text_color)
        screen.blit(abbrev_text, (icon_rect.centerx - abbrev_text.get_width() // 2, icon_rect.centery - 12))

        # Tech name (wrapped)
        name_y = center_rect.top + 110
        name_lines = self._wrap_text(focused_data['name'], tech_box_w - 20, self.font)
        for i, line in enumerate(name_lines[:2]):
            line_surf = self.font.render(line, True, text_color)
            screen.blit(line_surf, (center_rect.centerx - line_surf.get_width() // 2, name_y + i * 24))

        # Category badge (centered at bottom of tech box)
        category_names = {'explore': 'EXPLORE', 'discover': 'DISCOVER', 'build': 'BUILD', 'conquer': 'CONQUER'}
        category_name = category_names.get(category, 'UNKNOWN')
        category_text = self.small_font.render(category_name, True, category_color)
        badge_width = category_text.get_width() + 10
        badge_x = center_rect.centerx - badge_width // 2  # Center the badge horizontally
        category_badge_rect = pygame.Rect(badge_x, center_rect.bottom - 30, badge_width, 20)
        pygame.draw.rect(screen, (20, 25, 30), category_badge_rect, border_radius=4)
        pygame.draw.rect(screen, category_color, category_badge_rect, 2, border_radius=4)
        screen.blit(category_text, (category_badge_rect.x + 5, category_badge_rect.y + 2))

        # PREREQUISITES (arrows from left)
        prereq1 = focused_data.get('prereq1')
        prereq2 = focused_data.get('prereq2')
        prereqs = [p for p in [prereq1, prereq2] if p is not None]

        arrow_spacing = 100
        prereq_x = center_x - tech_box_w // 2 - 200
        prereq_start_y = center_y - (len(prereqs) - 1) * arrow_spacing // 2

        for i, prereq_id in enumerate(prereqs):
            if prereq_id in game.tech_tree.technologies:
                prereq_data = game.tech_tree.technologies[prereq_id]
                prereq_y = prereq_start_y + i * arrow_spacing

                # Small prereq box
                prereq_w, prereq_h = 140, 60
                prereq_rect = pygame.Rect(prereq_x - prereq_w // 2, prereq_y - prereq_h // 2, prereq_w, prereq_h)

                # Store for click detection
                self.tech_tree_prereq_rects.append((prereq_rect, prereq_id))

                # Color based on status
                prereq_status = game.tech_tree.get_tech_status(prereq_id)
                if prereq_status == "Completed":
                    prereq_bg = (30, 50, 30)
                    prereq_border = (80, 180, 80)
                    prereq_text_color = (200, 220, 200)
                else:
                    prereq_bg = (25, 25, 25)
                    prereq_border = (60, 60, 60)
                    prereq_text_color = (100, 100, 100)

                # Highlight on hover
                is_hovered = prereq_rect.collidepoint(pygame.mouse.get_pos())
                if is_hovered:
                    prereq_border = tuple(min(255, c + 50) for c in prereq_border)

                pygame.draw.rect(screen, prereq_bg, prereq_rect, border_radius=6)
                pygame.draw.rect(screen, prereq_border, prereq_rect, 2, border_radius=6)

                # Prereq name (wrapped)
                prereq_lines = self._wrap_text(prereq_data['name'], prereq_w - 10, self.small_font)
                for j, line in enumerate(prereq_lines[:2]):
                    line_surf = self.small_font.render(line, True, prereq_text_color)
                    screen.blit(line_surf, (prereq_rect.centerx - line_surf.get_width() // 2, prereq_rect.top + 10 + j * 16))

                # Arrow from prereq to center
                arrow_start = (prereq_rect.right, prereq_y)
                arrow_end = (center_rect.left, center_y)
                pygame.draw.line(screen, prereq_border, arrow_start, arrow_end, 2)
                # Arrowhead
                pygame.draw.polygon(screen, prereq_border, [
                    arrow_end,
                    (arrow_end[0] - 10, arrow_end[1] - 5),
                    (arrow_end[0] - 10, arrow_end[1] + 5)
                ])

        # UNLOCKS (arrows to right - techs that require this one)
        unlocks = []
        for tech_id, tech_data in game.tech_tree.technologies.items():
            if tech_data.get('prereq1') == focused_id or tech_data.get('prereq2') == focused_id:
                unlocks.append((tech_id, tech_data))

        unlock_x = center_x + tech_box_w // 2 + 200
        unlock_start_y = center_y - (len(unlocks) - 1) * arrow_spacing // 2

        for i, (unlock_id, unlock_data) in enumerate(unlocks[:3]):  # Max 3 to avoid clutter
            unlock_y = unlock_start_y + i * arrow_spacing

            # Small unlock box
            unlock_w, unlock_h = 140, 60
            unlock_rect = pygame.Rect(unlock_x - unlock_w // 2, unlock_y - unlock_h // 2, unlock_w, unlock_h)

            # Store for click detection
            self.tech_tree_unlock_rects.append((unlock_rect, unlock_id))

            # Color based on status
            unlock_status = game.tech_tree.get_tech_status(unlock_id)
            if unlock_status == "Completed":
                unlock_bg = (30, 50, 30)
                unlock_border = (80, 180, 80)
                unlock_text_color = (200, 220, 200)
            elif unlock_status == "Available":
                unlock_bg = (30, 40, 50)
                unlock_border = (100, 150, 180)
                unlock_text_color = (180, 200, 220)
            else:
                unlock_bg = (25, 25, 25)
                unlock_border = (60, 60, 60)
                unlock_text_color = (100, 100, 100)

            # Highlight on hover
            is_hovered = unlock_rect.collidepoint(pygame.mouse.get_pos())
            if is_hovered:
                unlock_border = tuple(min(255, c + 50) for c in unlock_border)

            pygame.draw.rect(screen, unlock_bg, unlock_rect, border_radius=6)
            pygame.draw.rect(screen, unlock_border, unlock_rect, 2, border_radius=6)

            # Unlock name (wrapped)
            unlock_lines = self._wrap_text(unlock_data['name'], unlock_w - 10, self.small_font)
            for j, line in enumerate(unlock_lines[:2]):
                line_surf = self.small_font.render(line, True, unlock_text_color)
                screen.blit(line_surf, (unlock_rect.centerx - line_surf.get_width() // 2, unlock_rect.top + 10 + j * 16))

            # Arrow from center to unlock
            arrow_start = (center_rect.right, center_y)
            arrow_end = (unlock_rect.left, unlock_y)
            pygame.draw.line(screen, unlock_border, arrow_start, arrow_end, 2)
            # Arrowhead
            pygame.draw.polygon(screen, unlock_border, [
                arrow_end,
                (arrow_end[0] - 10, arrow_end[1] - 5),
                (arrow_end[0] - 10, arrow_end[1] + 5)
            ])

        # Show count if more unlocks exist
        if len(unlocks) > 3:
            more_text = self.small_font.render(f"+{len(unlocks) - 3} more", True, (150, 150, 150))
            screen.blit(more_text, (unlock_x - more_text.get_width() // 2, unlock_start_y + 3 * arrow_spacing - 20))

    def handle_tech_tree_click(self, pos, game):
        """Handle clicks in the Tech Tree screen.

        Args:
            pos: Mouse click position tuple (x, y)
            game: Game instance for accessing tech tree and status messages

        Returns:
            'close' if should exit the screen, None otherwise
        """
        # Check scroll arrows
        if hasattr(self, 'tech_tree_up_arrow') and self.tech_tree_up_arrow and self.tech_tree_up_arrow.collidepoint(pos):
            if self.tech_tree_scroll_offset > 0:
                self.tech_tree_scroll_offset -= 1
            return None

        if hasattr(self, 'tech_tree_down_arrow') and self.tech_tree_down_arrow and self.tech_tree_down_arrow.collidepoint(pos):
            all_techs_count = len(game.tech_tree.technologies)
            visible_lines = 25  # Approximate
            if self.tech_tree_scroll_offset < all_techs_count - visible_lines:
                self.tech_tree_scroll_offset += 1
            return None

        # Check prerequisite boxes (left side of visualization)
        if hasattr(self, 'tech_tree_prereq_rects'):
            for rect, tech_id in self.tech_tree_prereq_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id
                    game.set_status_message(f"Viewing: {game.tech_tree.technologies[tech_id]['name']}")
                    return None

        # Check unlock boxes (right side of visualization)
        if hasattr(self, 'tech_tree_unlock_rects'):
            for rect, tech_id in self.tech_tree_unlock_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id
                    # If it's available, also set it as current research
                    status = game.tech_tree.get_tech_status(tech_id)
                    if status == "Available":
                        game.tech_tree.set_current_research(tech_id)
                        category = game.tech_tree.technologies[tech_id].get('category', 'unknown')
                        category_name = {'explore': 'Explore', 'discover': 'Discover', 'build': 'Build', 'conquer': 'Conquer'}.get(category, 'Unknown')
                        game.set_status_message(f"Now researching a {category_name} technology")
                    else:
                        game.set_status_message(f"Viewing: {game.tech_tree.technologies[tech_id]['name']}")
                    return None

        # Check tech selection (clicking focuses the tech)
        if hasattr(self, 'tech_tree_selection_rects'):
            for rect, tech_id in self.tech_tree_selection_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id

                    # If it's available, also set it as current research
                    status = game.tech_tree.get_tech_status(tech_id)
                    if status == "Available":
                        game.tech_tree.set_current_research(tech_id)
                        category = game.tech_tree.technologies[tech_id].get('category', 'unknown')
                        category_name = {'explore': 'Explore', 'discover': 'Discover', 'build': 'Build', 'conquer': 'Conquer'}.get(category, 'Unknown')
                        game.set_status_message(f"Now researching a {category_name} technology")
                    return None

        # Check OK button
        if hasattr(self, 'tech_tree_ok_rect') and self.tech_tree_ok_rect.collidepoint(pos):
            self.tech_tree_open = False
            return 'close'
        return None

    def _wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width.

        Args:
            text: String to wrap
            max_width: Maximum width in pixels
            font: Pygame font to use for measuring text

        Returns:
            List of wrapped text lines
        """
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines
