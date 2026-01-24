# tech.py
"""Technology tree system.

Simple linear tech progression where each technology unlocks the next.
Technologies are researched by accumulating research points each turn.
"""


class TechTree:
    """Manages the technology tree and research progress.

    The tech tree is a simple linked list where each tech leads to the next.
    Players accumulate research points each turn to unlock technologies.

    Attributes:
        techs (list): Ordered list of technology names
        current_tech_index (int): Index of currently researching tech
        research_accumulated (int): Research points toward current tech
        research_per_turn (int): Research points gained each turn
        completed_techs (set): Set of completed technology names
    """

    def __init__(self):
        """Initialize the tech tree."""
        # Simple linear tech tree (20 technologies total)
        self.techs = [
            "Tech 1", "Tech 2", "Tech 3", "Tech 4", "Tech 5",
            "Tech 6", "Tech 7", "Tech 8", "Tech 9", "Tech 10",
            "Tech 11", "Tech 12", "Tech 13", "Tech 14", "Tech 15",
            "Tech 16", "Tech 17", "Tech 18", "Tech 19", "Tech 20"
        ]

        self.current_tech_index = 0
        self.research_accumulated = 0
        self.research_per_turn = 1  # Base research rate
        self.completed_techs = set()

    def get_current_tech(self):
        """Get the name of the technology currently being researched.

        Returns:
            str: Name of current tech, or "Complete" if all techs researched
        """
        if self.current_tech_index >= len(self.techs):
            return "Complete"
        return self.techs[self.current_tech_index]

    def get_research_cost(self):
        """Get the research cost of the current technology.

        Returns:
            int: Research points needed (10 for all techs currently)
        """
        return 10  # All techs cost 10 research points for now

    def get_turns_remaining(self):
        """Calculate turns remaining until current tech is complete.

        Returns:
            int: Estimated turns to completion
        """
        if self.current_tech_index >= len(self.techs):
            return 0

        remaining = self.get_research_cost() - self.research_accumulated
        return max(1, remaining // self.research_per_turn)

    def process_turn(self):
        """Process research for one turn.

        Adds research points and checks for tech completion.

        Returns:
            str or None: Name of completed tech, or None if no completion
        """
        if self.current_tech_index >= len(self.techs):
            return None

        self.research_accumulated += self.research_per_turn

        # Check for tech completion
        if self.research_accumulated >= self.get_research_cost():
            completed_tech = self.techs[self.current_tech_index]
            self.completed_techs.add(completed_tech)
            self.current_tech_index += 1
            self.research_accumulated = 0
            print(f"Technology discovered: {completed_tech}!")
            return completed_tech

        return None

    def get_progress_percentage(self):
        """Get research progress as a percentage.

        Returns:
            float: Progress from 0.0 to 1.0
        """
        if self.current_tech_index >= len(self.techs):
            return 1.0

        return self.research_accumulated / self.get_research_cost()

    def get_tech_status(self, tech_name):
        """Get the status of a specific technology.

        Args:
            tech_name (str): Name of the technology

        Returns:
            str: "Completed", "Researching", or "Locked"
        """
        if tech_name in self.completed_techs:
            return "Completed"
        elif tech_name == self.get_current_tech():
            return "Researching"
        else:
            return "Locked"
