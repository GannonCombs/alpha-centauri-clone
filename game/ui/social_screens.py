"""Coordinator for Social Engineering, Tech Tree, and Design Workshop screens."""

from game.ui.social_engineering_screen import SocialEngineeringScreen
from game.ui.tech_tree_screen import TechTreeScreen
from game.ui.design_workshop_screen import DesignWorkshopScreen


class SocialScreensManager:
    """Coordinates Social Engineering, Tech Tree, and Design Workshop screens."""

    def __init__(self, font, small_font):
        """Initialize social screens manager with fonts.

        Args:
            font: Main pygame font object
            small_font: Small pygame font object
        """
        self.font = font
        self.small_font = small_font

        # Create screen instances
        self.social_engineering_screen = SocialEngineeringScreen(font, small_font)
        self.tech_tree_screen = TechTreeScreen(font, small_font)
        self.design_workshop_screen = DesignWorkshopScreen(font, small_font)

    # Properties for backward compatibility
    @property
    def social_engineering_open(self):
        """Get social engineering open state."""
        return self.social_engineering_screen.social_engineering_open

    @social_engineering_open.setter
    def social_engineering_open(self, value):
        """Set social engineering open state."""
        self.social_engineering_screen.social_engineering_open = value

    @property
    def tech_tree_open(self):
        """Get tech tree open state."""
        return self.tech_tree_screen.tech_tree_open

    @tech_tree_open.setter
    def tech_tree_open(self, value):
        """Set tech tree open state."""
        self.tech_tree_screen.tech_tree_open = value

    @property
    def design_workshop_open(self):
        """Get design workshop open state."""
        return self.design_workshop_screen.design_workshop_open

    @design_workshop_open.setter
    def design_workshop_open(self, value):
        """Set design workshop open state."""
        self.design_workshop_screen.design_workshop_open = value

    @property
    def unit_designs(self):
        """Get unit designs list."""
        return self.design_workshop_screen.unit_designs

    @property
    def tech_tree_focused_tech(self):
        """Get currently focused tech in tech tree."""
        return self.tech_tree_screen.tech_tree_focused_tech

    @tech_tree_focused_tech.setter
    def tech_tree_focused_tech(self, value):
        """Set currently focused tech in tech tree."""
        self.tech_tree_screen.tech_tree_focused_tech = value

    # Toggle methods
    def toggle_social_engineering(self):
        """Toggle social engineering screen."""
        self.social_engineering_screen.social_engineering_open = not self.social_engineering_screen.social_engineering_open

    def toggle_tech_tree(self):
        """Toggle tech tree screen."""
        self.tech_tree_screen.tech_tree_open = not self.tech_tree_screen.tech_tree_open

    def toggle_design_workshop(self):
        """Toggle design workshop screen."""
        self.design_workshop_screen.design_workshop_open = not self.design_workshop_screen.design_workshop_open

    # Draw methods - delegate to appropriate screen
    def draw_social_engineering(self, screen, game):
        """Draw the Social Engineering screen.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing game state
        """
        self.social_engineering_screen.draw_social_engineering(screen, game)

    def draw_tech_tree(self, screen, game):
        """Draw the Technology Tree screen.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing game state
        """
        self.tech_tree_screen.draw_tech_tree(screen, game)

    def draw_design_workshop(self, screen, game):
        """Draw the Design Workshop screen.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing game state
        """
        self.design_workshop_screen.draw_design_workshop(screen, game)

    # Click handling methods - delegate to appropriate screen
    def handle_social_engineering_click(self, pos, game):
        """Handle clicks in the Social Engineering screen.

        Args:
            pos: Mouse click position tuple (x, y)
            game: Game instance for accessing game state

        Returns:
            'close' if should exit the screen, None otherwise
        """
        return self.social_engineering_screen.handle_social_engineering_click(pos, game)

    def handle_tech_tree_click(self, pos, game):
        """Handle clicks in the Tech Tree screen.

        Args:
            pos: Mouse click position tuple (x, y)
            game: Game instance for accessing game state

        Returns:
            'close' if should exit the screen, None otherwise
        """
        return self.tech_tree_screen.handle_tech_tree_click(pos, game)

    def handle_design_workshop_click(self, pos):
        """Handle clicks in the Design Workshop screen.

        Args:
            pos: Mouse click position tuple (x, y)

        Returns:
            'close' if should exit the screen, None otherwise
        """
        return self.design_workshop_screen.handle_design_workshop_click(pos)

    # Design Workshop specific methods
    def rebuild_available_designs(self, tech_tree):
        """Rebuild unit designs based on available technology.

        Args:
            tech_tree: TechTree instance to check discovered techs
        """
        self.design_workshop_screen.rebuild_available_designs(tech_tree)
