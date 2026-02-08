# tech.py
"""Technology tree system based on Alpha Centauri alpha.txt.

Technologies have prerequisites and unlock units, facilities, and abilities.
Players accumulate research points each turn to discover new technologies.
"""

from game.data.tech_tree_data import TECHS

class TechTree:
    """Manages the technology tree and research progress.

    Based on the authentic SMAC tech tree from alpha.txt (lines 255-344).
    Each tech has prerequisites that must be discovered first.

    Attributes:
        technologies (dict): All technologies with prereqs and costs
        discovered_techs (set): Set of discovered tech IDs
        current_research (str): Tech ID currently being researched
        research_accumulated (int): Research points toward current tech
        research_per_turn (int): Research points gained each turn
    """

    def __init__(self):
        """Initialize the tech tree with all SMAC technologies."""
        self.technologies = TECHS
        self.discovered_techs = set()
        self.current_research = None  # Player chooses what to research
        self.research_accumulated = 0
        self.research_per_turn = 2  # Base research rate (will scale with labs)

    def is_available(self, tech_id):
        """Check if a technology is available to be researched.

        Args:
            tech_id (str): Technology ID (e.g., 'Biogen')

        Returns:
            bool: True if prerequisites are met and not yet discovered
        """
        if tech_id not in self.technologies or tech_id in self.discovered_techs:
            return False

        tech = self.technologies[tech_id]

        # 'all()' returns True if the list is empty (Tier 1)
        # or if every prereq is in our discovered set.
        return all(prereq in self.discovered_techs for prereq in tech.get('prereqs', []))

    def get_available_techs(self):
        """Get all technologies that can currently be researched.

        Returns:
            list: List of (tech_id, tech_data) tuples for available techs
        """
        available = []
        for tech_id, tech_data in self.technologies.items():
            if self.is_available(tech_id):
                available.append((tech_id, tech_data))

        # Sort by cost (cheapest first)
        available.sort(key=lambda x: x[1]['cost'])
        return available

    def set_current_research(self, tech_id):
        """Set the technology to research.

        Args:
            tech_id (str): Technology ID to research
        """
        if self.is_available(tech_id):
            self.current_research = tech_id
            self.research_accumulated = 0

    def get_current_tech(self):
        """Get the name of the technology currently being researched.

        Returns:
            str: Name of current tech, or None if no research active
        """
        if self.current_research is None:
            return None
        return self.technologies[self.current_research]['name']

    def get_research_cost(self):
        """Get the research cost of the current technology.

        Returns:
            int: Research points needed
        """
        if self.current_research is None:
            return 0

        base_cost = self.technologies[self.current_research]['cost']

        # Cost scales with number of techs discovered
        # Formula: base * (1 + num_discovered * 0.05)
        multiplier = 1.0 + (len(self.discovered_techs) * 0.05)

        return int(base_cost * multiplier)

    def get_turns_remaining(self):
        """Calculate turns remaining until current tech is complete.

        Returns:
            int: Estimated turns to completion, or 0 if no research
        """
        if self.current_research is None:
            return 0

        remaining = self.get_research_cost() - self.research_accumulated
        if self.research_per_turn <= 0:
            return 999

        return max(1, (remaining + self.research_per_turn - 1) // self.research_per_turn)

    def auto_select_research(self):
        """Automatically select a technology to research.

        Chooses randomly from available techs weighted by cost (cheaper preferred).
        """
        import random

        available = self.get_available_techs()
        if not available:
            return

        # Randomly select from available techs
        tech_id = random.choice([t[0] for t in available])
        self.set_current_research(tech_id)

    def add_research(self, amount):
        """Add research points from base labs output.

        Args:
            amount (int): Research points to add this turn
        """
        # Update research_per_turn for accurate turn estimates
        self.research_per_turn = amount

        if self.current_research is not None:
            self.research_accumulated += amount

    def process_turn(self):
        """Process research for one turn.

        Checks for tech completion and auto-selects next research.
        Note: Research points should be added via add_research() before calling this.

        Returns:
            str or None: Tech ID of completed tech, or None if no completion
        """
        # Auto-select research if none active
        if self.current_research is None:
            self.auto_select_research()
            if self.current_research is None:
                return None

        # No longer add research_per_turn here - it comes from bases via add_research()

        # Check for tech completion
        if self.research_accumulated >= self.get_research_cost():
            completed_tech = self.current_research
            self.discovered_techs.add(completed_tech)
            tech_name = self.technologies[completed_tech]['name']
            print(f"Technology discovered: {tech_name}!")

            # Reset research and auto-select next
            self.current_research = None
            self.research_accumulated = 0
            self.auto_select_research()

            return completed_tech

        return None

    def get_progress_percentage(self):
        """Get research progress as a percentage.

        Returns:
            float: Progress from 0.0 to 1.0
        """
        if self.current_research is None:
            return 0.0

        cost = self.get_research_cost()
        if cost <= 0:
            return 1.0

        return min(1.0, self.research_accumulated / cost)

    def get_tech_status(self, tech_id):
        """Get the status of a specific technology.

        Args:
            tech_id (str): Technology ID

        Returns:
            str: "Completed", "Researching", "Available", or "Locked"
        """
        if tech_id in self.discovered_techs:
            return "Completed"
        elif tech_id == self.current_research:
            return "Researching"
        elif self.is_available(tech_id):
            return "Available"
        else:
            return "Locked"

    def get_current_category(self):
        """Get the category of the technology currently being researched.

        Returns:
            str: Category ('explore', 'discover', 'build', 'conquer') or None
        """
        if self.current_research is None:
            return None
        return self.technologies[self.current_research].get('category', None)

    def get_category_color(self, category):
        """Get the RGB color for a tech category.

        Args:
            category (str): 'explore', 'discover', 'build', or 'conquer'

        Returns:
            tuple: RGB color (R, G, B)
        """
        colors = {
            'explore': (50, 200, 50),    # Green
            'discover': (255, 255, 255),  # White
            'build': (220, 180, 50),      # Yellow
            'conquer': (220, 50, 50)      # Red
        }
        return colors.get(category, (255, 255, 255))  # Default white

    def has_tech(self, tech_id):
        """Check if a technology has been discovered.

        Args:
            tech_id (str): Technology ID

        Returns:
            bool: True if discovered
        """
        return tech_id in self.discovered_techs

    #TODO: I believe from_dict and to_dict were intended to save/load games. But I don't see this called anywhere,
    #and I think things load fine. I'll need to fix my tech view first before I can be sure.
    #Check these in other files too. There are a few that appear dead.
    def to_dict(self):
        """Serialize tech tree to dictionary.

        Returns:
            dict: Tech tree data as dictionary
        """
        return {
            'discovered_techs': list(self.discovered_techs),
            'current_research': self.current_research,
            'research_accumulated': self.research_accumulated
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct tech tree from dictionary.

        Args:
            data (dict): Tech tree data dictionary

        Returns:
            TechTree: Reconstructed tech tree instance
        """
        tree = cls.__new__(cls)

        # Initialize with full tech tree
        tree.__init__()

        # Restore research state
        tree.discovered_techs = set(data['discovered_techs'])
        tree.current_research = data['current_research']
        tree.research_accumulated = data['research_accumulated']

        return tree
