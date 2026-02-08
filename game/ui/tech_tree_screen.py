"""Tech Tree screen for viewing and selecting research."""

import pygame
from game.data import display
from game.data.display import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)
from game.data.data import FACTION_DATA


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
        self.viewed_faction_id = None  # Which faction's tech tree to view (None = player's faction)
        self.is_dragging_scrollbar = False  # Track if user is dragging scrollbar
        self.drag_start_y = 0  # Y position where drag started
        self.drag_start_offset = 0  # Scroll offset when drag started

        # UI elements
        self.tech_tree_selection_rects = []
        self.tech_tree_up_arrow = None
        self.tech_tree_down_arrow = None
        self.tech_tree_ok_rect = None
        self.tech_tree_prereq_rects = []  # List of (rect, tech_id) tuples for clickable prerequisites
        self.tech_tree_unlock_rects = []  # List of (rect, tech_id) tuples for clickable unlocks
        self.faction_icon_rects = []  # List of (rect, faction_id) tuples for faction selector
        self.scrollbar_rect = None  # Scrollbar background rect
        self.scrollbar_thumb_rect = None  # Scrollbar thumb rect

    def draw_tech_tree(self, screen, game):
        """Draw the Technology Tree screen with visualization.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing tech tree and other game state
        """
        # Default to viewing player's faction
        if self.viewed_faction_id is None:
            self.viewed_faction_id = game.player_faction_id

        # Get the tech tree for the faction being viewed
        tech_tree = game.factions[self.viewed_faction_id].tech_tree

        # Initialize focused tech to viewed faction's starting tech on first draw
        if self.tech_tree_focused_tech is None:
            viewed_faction = FACTION_DATA[self.viewed_faction_id]
            self.tech_tree_focused_tech = viewed_faction.get('starting_tech', 'Ecology')

        # Fill background
        screen.fill((15, 20, 25))

        screen_w = display.SCREEN_WIDTH
        screen_h = display.SCREEN_HEIGHT

        # TOP PROGRESS BAR (~80% screen width)
        progress_bar_w = int(screen_w * 0.8)
        progress_bar_h = 50
        progress_bar_x = (screen_w - progress_bar_w) // 2
        progress_bar_y = 10

        # Progress bar background
        prog_bg_rect = pygame.Rect(progress_bar_x, progress_bar_y, progress_bar_w, progress_bar_h)
        pygame.draw.rect(screen, (30, 35, 40), prog_bg_rect, border_radius=8)

        current_tech_name = tech_tree.get_current_tech()
        if current_tech_name and tech_tree.current_research:
            # Get category color for progress bar
            category = tech_tree.get_current_category()
            fill_color = tech_tree.get_category_color(category) if category else (80, 150, 200)

            # Fill progress
            progress_pct = tech_tree.get_progress_percentage()
            fill_w = int(progress_bar_w * progress_pct)
            fill_rect = pygame.Rect(progress_bar_x, progress_bar_y, fill_w, progress_bar_h)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=8)

            # Progress text (hide tech name - keep it mysterious!)
            turns_left = tech_tree.get_turns_remaining()
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
        all_techs = [(tech_id, tech_data) for tech_id, tech_data in tech_tree.technologies.items()]
        all_techs.sort(key=lambda x: x[1]['name'])

        # Scrollable list
        tech_list_y = left_panel_y + 45
        tech_line_h = 22
        visible_lines = (left_panel_h - 60) // tech_line_h
        self.tech_tree_selection_rects = []

        # Draw scroll bar and arrows if needed
        if len(all_techs) > visible_lines:
            # Scroll bar background
            scrollbar_x = left_panel_x + left_panel_w - 25
            scrollbar_y = left_panel_y + 40
            scrollbar_h = left_panel_h - 80
            self.scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, 15, scrollbar_h)
            pygame.draw.rect(screen, (30, 35, 40), self.scrollbar_rect, border_radius=4)

            # Scroll bar thumb
            scroll_ratio = self.tech_tree_scroll_offset / max(1, len(all_techs) - visible_lines)
            thumb_h = max(20, int(scrollbar_h * (visible_lines / len(all_techs))))
            thumb_y = scrollbar_y + int((scrollbar_h - thumb_h) * scroll_ratio)
            self.scrollbar_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 15, thumb_h)

            # Highlight thumb on hover or drag
            thumb_color = (100, 120, 140)
            if self.is_dragging_scrollbar or (self.scrollbar_thumb_rect and self.scrollbar_thumb_rect.collidepoint(pygame.mouse.get_pos())):
                thumb_color = (140, 160, 180)

            pygame.draw.rect(screen, thumb_color, self.scrollbar_thumb_rect, border_radius=4)

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

            # Clickable rect
            tech_rect = pygame.Rect(left_panel_x + 10, tech_y, left_panel_w - 50, tech_line_h)

            # Check if focused or hovered
            is_focused = (tech_id == self.tech_tree_focused_tech)
            is_hovered = tech_rect.collidepoint(pygame.mouse.get_pos())

            # Simple color scheme: white if selected, gray otherwise
            if is_focused:
                tech_color = (255, 255, 255)  # White for selected
                pygame.draw.rect(screen, (50, 70, 90), tech_rect, border_radius=4)
            else:
                tech_color = (140, 150, 160)  # Gray for not selected

            if is_hovered and not is_focused:
                pygame.draw.rect(screen, (40, 50, 60), tech_rect, border_radius=4)

            # Store for click detection
            self.tech_tree_selection_rects.append((tech_rect, tech_id))

            # Tech name
            tech_text = self.small_font.render(tech_data['name'], True, tech_color)
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
        if self.tech_tree_focused_tech and self.tech_tree_focused_tech in tech_tree.technologies:
            self._draw_tech_visualization(screen, game, main_panel_rect, tech_tree)

        # Faction selector icons - draw at bottom above OK button
        self._draw_faction_selector(screen, game, main_panel_rect)

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

    def _draw_tech_visualization(self, screen, game, main_rect, tech_tree):
        """Draw the main tech visualization showing focused tech and connections.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing tech tree
            main_rect: Rectangle defining the main visualization area
            tech_tree: The tech tree to visualize
        """
        focused_id = self.tech_tree_focused_tech
        focused_data = tech_tree.technologies[focused_id]

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

        # Get category color (always use full color, never gray out)
        category = focused_data.get('category', 'unknown')
        category_color = tech_tree.get_category_color(category)

        # Determine ownership status for text colors
        status = tech_tree.get_tech_status(focused_id)
        is_discovered = (status == "Completed")

        # Text colors: White if discovered, gray if not
        text_color = (255, 255, 255) if is_discovered else (120, 120, 120)

        # Background color based on status
        if status == "Completed":
            bg_color = (40, 60, 40)
        elif status == "Researching":
            bg_color = (60, 60, 40)
        elif status == "Available":
            bg_color = (40, 50, 60)
        else:  # Locked
            bg_color = (30, 30, 30)

        # Draw tech box with category color border (always full color)
        pygame.draw.rect(screen, bg_color, center_rect, border_radius=10)
        pygame.draw.rect(screen, category_color, center_rect, 3, border_radius=10)

        # Tech icon circle (always category color)
        icon_size = 80
        icon_rect = pygame.Rect(center_rect.centerx - icon_size // 2, center_rect.top + 20, icon_size, icon_size)
        pygame.draw.circle(screen, category_color, icon_rect.center, icon_size // 2)
        pygame.draw.circle(screen, bg_color, icon_rect.center, icon_size // 2 - 3)

        # Tech ID abbreviation in icon (white if discovered, gray if not)
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
        prereqs = focused_data.get('prereqs', [])

        arrow_spacing = 100
        prereq_x = center_x - tech_box_w // 2 - 200
        prereq_start_y = center_y - (len(prereqs) - 1) * arrow_spacing // 2

        for i, prereq_id in enumerate(prereqs):
            if prereq_id in tech_tree.technologies:
                prereq_data = tech_tree.technologies[prereq_id]
                prereq_y = prereq_start_y + i * arrow_spacing

                # Small prereq box
                prereq_w, prereq_h = 140, 60
                prereq_rect = pygame.Rect(prereq_x - prereq_w // 2, prereq_y - prereq_h // 2, prereq_w, prereq_h)

                # Store for click detection
                self.tech_tree_prereq_rects.append((prereq_rect, prereq_id))

                # Color based on status: white if discovered, gray if not
                prereq_status = tech_tree.get_tech_status(prereq_id)
                prereq_bg = (25, 25, 25)  # Dark background for all
                if prereq_status == "Completed":
                    prereq_border = (255, 255, 255)  # White border for discovered
                    prereq_text_color = (255, 255, 255)  # White text for discovered
                else:
                    prereq_border = (80, 80, 80)  # Gray border for not discovered
                    prereq_text_color = (120, 120, 120)  # Gray text for not discovered

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
        for tech_id, tech_data in tech_tree.technologies.items():
            if focused_id in tech_data.get('prereqs', []):
                unlocks.append((tech_id, tech_data))

        unlock_x = center_x + tech_box_w // 2 + 200
        # Center based on number of unlocks we'll actually display (max 4)
        displayed_count = min(len(unlocks), 4)
        unlock_start_y = center_y - (displayed_count - 1) * arrow_spacing // 2

        for i, (unlock_id, unlock_data) in enumerate(unlocks[:4]):  # Max 4 (tech unlock limit)
            unlock_y = unlock_start_y + i * arrow_spacing

            # Small unlock box
            unlock_w, unlock_h = 140, 60
            unlock_rect = pygame.Rect(unlock_x - unlock_w // 2, unlock_y - unlock_h // 2, unlock_w, unlock_h)

            # Store for click detection
            self.tech_tree_unlock_rects.append((unlock_rect, unlock_id))

            # Color based on status: white if discovered, gray if not
            unlock_status = tech_tree.get_tech_status(unlock_id)
            unlock_bg = (25, 25, 25)  # Dark background for all
            if unlock_status == "Completed":
                unlock_border = (255, 255, 255)  # White border for discovered
                unlock_text_color = (255, 255, 255)  # White text for discovered
            else:
                unlock_border = (80, 80, 80)  # Gray border for not discovered
                unlock_text_color = (120, 120, 120)  # Gray text for not discovered

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

        # Show count if more than 4 unlocks exist (shouldn't happen, but just in case)
        if len(unlocks) > 4:
            more_text = self.small_font.render(f"+{len(unlocks) - 4} more", True, (150, 150, 150))
            screen.blit(more_text, (unlock_x - more_text.get_width() // 2, unlock_start_y + 4 * arrow_spacing - 20))

    def _draw_faction_selector(self, screen, game, main_rect):
        """Draw faction selector icons at bottom of screen.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing faction data
            main_rect: Main panel rectangle for positioning
        """
        self.faction_icon_rects = []

        # Position icons at bottom of main panel, above OK button (moved up 15%)
        icon_size = 40
        icon_spacing = 10
        total_width = 7 * icon_size + 6 * icon_spacing
        start_x = main_rect.centerx - total_width // 2
        # Move up by 15% of main panel height plus original offset
        extra_offset = int(main_rect.height * 0.15)
        y = main_rect.bottom - 80 - extra_offset  # Above OK button

        # Draw each faction icon
        for faction_id in range(7):
            faction_data = FACTION_DATA[faction_id]
            color = faction_data['color']

            icon_x = start_x + faction_id * (icon_size + icon_spacing)
            icon_rect = pygame.Rect(icon_x, y, icon_size, icon_size)
            self.faction_icon_rects.append((icon_rect, faction_id))

            # Determine if this faction is currently viewed
            is_selected = (faction_id == self.viewed_faction_id)
            is_hovered = icon_rect.collidepoint(pygame.mouse.get_pos())

            # Draw icon background
            if is_selected:
                # Bright silver outer border for selected faction
                pygame.draw.rect(screen, (230, 230, 240), icon_rect, border_radius=6)
                inner_rect = icon_rect.inflate(-6, -6)
                pygame.draw.rect(screen, color, inner_rect, border_radius=4)
                # Add a darker inner border for depth
                highlight_rect = icon_rect.inflate(-4, -4)
                pygame.draw.rect(screen, (180, 180, 190), highlight_rect, 2, border_radius=5)
            else:
                # Normal faction color
                pygame.draw.rect(screen, color, icon_rect, border_radius=6)
                if is_hovered:
                    # Light gray overlay on hover
                    overlay_rect = icon_rect.inflate(-2, -2)
                    pygame.draw.rect(screen, (200, 200, 210), overlay_rect, 2, border_radius=5)

            # Draw faction initial in icon
            # Use cool gray with slight blue tint for selected, darker gray for unselected
            # Override for "The Hive" to show "H" instead of "T"
            faction_initial_overrides = {1: 'H'}  # Faction 1 = "The Hive"
            faction_initial = faction_initial_overrides.get(faction_id, faction_data['name'][0])
            letter_color = (200, 205, 210) if is_selected else (85, 85, 85)
            initial_text = self.font.render(faction_initial, True, letter_color)
            text_x = icon_rect.centerx - initial_text.get_width() // 2
            text_y = icon_rect.centery - initial_text.get_height() // 2
            screen.blit(initial_text, (text_x, text_y))

        # Draw faction name label for currently viewed faction
        viewed_faction_data = FACTION_DATA[self.viewed_faction_id]
        faction_name = viewed_faction_data['name']
        is_player = (self.viewed_faction_id == game.player_faction_id)
        label_text = f"{faction_name}" + (" (You)" if is_player else " (AI)")

        label_surf = self.small_font.render(label_text, True, COLOR_TEXT)
        label_x = main_rect.centerx - label_surf.get_width() // 2
        label_y = y - 25
        screen.blit(label_surf, (label_x, label_y))

    def handle_tech_tree_scroll(self, y_delta, game):
        """Handle mouse wheel scrolling in the Tech Tree screen.

        Args:
            y_delta: Mouse wheel scroll amount (positive = scroll up, negative = scroll down)
            game: Game instance for accessing tech tree

        Returns:
            True if scroll was handled
        """
        # Get the tech tree for the faction being viewed
        if self.viewed_faction_id is None:
            self.viewed_faction_id = game.player_faction_id
        tech_tree = game.factions[self.viewed_faction_id].tech_tree

        all_techs_count = len(tech_tree.technologies)
        visible_lines = 25  # Approximate

        if y_delta > 0:
            # Scroll up
            if self.tech_tree_scroll_offset > 0:
                self.tech_tree_scroll_offset = max(0, self.tech_tree_scroll_offset - 3)
                return True
        elif y_delta < 0:
            # Scroll down
            if self.tech_tree_scroll_offset < all_techs_count - visible_lines:
                self.tech_tree_scroll_offset = min(all_techs_count - visible_lines, self.tech_tree_scroll_offset + 3)
                return True
        return False

    def handle_scrollbar_drag_start(self, pos, game):
        """Handle start of scrollbar thumb drag.

        Args:
            pos: Mouse position tuple (x, y)
            game: Game instance for accessing tech tree

        Returns:
            True if drag started
        """
        if self.scrollbar_thumb_rect and self.scrollbar_thumb_rect.collidepoint(pos):
            self.is_dragging_scrollbar = True
            self.drag_start_y = pos[1]
            self.drag_start_offset = self.tech_tree_scroll_offset
            return True
        return False

    def handle_scrollbar_drag_motion(self, pos, game):
        """Handle scrollbar thumb drag motion.

        Args:
            pos: Mouse position tuple (x, y)
            game: Game instance for accessing tech tree

        Returns:
            True if drag was handled
        """
        # Safety check: if mouse button isn't pressed, end drag immediately
        import pygame
        if self.is_dragging_scrollbar and not pygame.mouse.get_pressed()[0]:
            self.is_dragging_scrollbar = False
            return False

        if not self.is_dragging_scrollbar or not self.scrollbar_rect:
            return False

        # Get the tech tree for the faction being viewed
        if self.viewed_faction_id is None:
            self.viewed_faction_id = game.player_faction_id
        tech_tree = game.factions[self.viewed_faction_id].tech_tree

        all_techs_count = len(tech_tree.technologies)
        visible_lines = 25  # Approximate
        max_scroll = max(0, all_techs_count - visible_lines)

        # Calculate scroll delta from mouse movement
        delta_y = pos[1] - self.drag_start_y
        scrollbar_h = self.scrollbar_rect.height
        thumb_h = self.scrollbar_thumb_rect.height if self.scrollbar_thumb_rect else 20

        # Convert pixel delta to scroll offset delta
        usable_height = scrollbar_h - thumb_h
        if usable_height > 0:
            scroll_delta = int((delta_y / usable_height) * max_scroll)
            self.tech_tree_scroll_offset = max(0, min(max_scroll, self.drag_start_offset + scroll_delta))

        return True

    def handle_scrollbar_drag_end(self):
        """Handle end of scrollbar thumb drag.

        Returns:
            True if drag was active
        """
        was_dragging = self.is_dragging_scrollbar
        self.is_dragging_scrollbar = False
        return was_dragging

    def handle_tech_tree_click(self, pos, game):
        """Handle clicks in the Tech Tree screen.

        Args:
            pos: Mouse click position tuple (x, y)
            game: Game instance for accessing tech tree and status messages

        Returns:
            'close' if should exit the screen, None otherwise
        """
        # Get the tech tree for the faction being viewed
        if self.viewed_faction_id is None:
            self.viewed_faction_id = game.player_faction_id
        tech_tree = game.factions[self.viewed_faction_id].tech_tree

        # Check scrollbar thumb for drag start
        if self.handle_scrollbar_drag_start(pos, game):
            return None

        # Check faction selector icons
        if hasattr(self, 'faction_icon_rects'):
            for rect, faction_id in self.faction_icon_rects:
                if rect.collidepoint(pos):
                    # Switch to viewing this faction's tech tree
                    self.viewed_faction_id = faction_id
                    # Reset focused tech to this faction's starting tech
                    viewed_faction = FACTION_DATA[faction_id]
                    self.tech_tree_focused_tech = viewed_faction.get('starting_tech', 'Ecology')
                    return None

        # Check scroll arrows (scroll 3 lines at a time)
        if hasattr(self, 'tech_tree_up_arrow') and self.tech_tree_up_arrow and self.tech_tree_up_arrow.collidepoint(pos):
            if self.tech_tree_scroll_offset > 0:
                self.tech_tree_scroll_offset = max(0, self.tech_tree_scroll_offset - 3)
            return None

        if hasattr(self, 'tech_tree_down_arrow') and self.tech_tree_down_arrow and self.tech_tree_down_arrow.collidepoint(pos):
            all_techs_count = len(tech_tree.technologies)
            visible_lines = 25  # Approximate
            if self.tech_tree_scroll_offset < all_techs_count - visible_lines:
                self.tech_tree_scroll_offset = min(all_techs_count - visible_lines, self.tech_tree_scroll_offset + 3)
            return None

        # Check prerequisite boxes (left side of visualization)
        if hasattr(self, 'tech_tree_prereq_rects'):
            for rect, tech_id in self.tech_tree_prereq_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id
                    game.set_status_message(f"Viewing: {tech_tree.technologies[tech_id]['name']}")
                    return None

        # Check unlock boxes (right side of visualization)
        if hasattr(self, 'tech_tree_unlock_rects'):
            for rect, tech_id in self.tech_tree_unlock_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id
                    # If it's available and viewing player's faction, set it as current research
                    status = tech_tree.get_tech_status(tech_id)
                    if status == "Available" and self.viewed_faction_id == game.player_faction_id:
                        tech_tree.set_current_research(tech_id)
                        category = tech_tree.technologies[tech_id].get('category', 'unknown')
                        category_name = {'explore': 'Explore', 'discover': 'Discover', 'build': 'Build', 'conquer': 'Conquer'}.get(category, 'Unknown')
                        game.set_status_message(f"Now researching a {category_name} technology")
                    else:
                        game.set_status_message(f"Viewing: {tech_tree.technologies[tech_id]['name']}")
                    return None

        # Check tech selection (clicking focuses the tech)
        if hasattr(self, 'tech_tree_selection_rects'):
            for rect, tech_id in self.tech_tree_selection_rects:
                if rect.collidepoint(pos):
                    # Focus this tech in the main view
                    self.tech_tree_focused_tech = tech_id

                    # If it's available and viewing player's faction, set it as current research
                    status = tech_tree.get_tech_status(tech_id)
                    if status == "Available" and self.viewed_faction_id == game.player_faction_id:
                        tech_tree.set_current_research(tech_id)
                        category = tech_tree.technologies[tech_id].get('category', 'unknown')
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
