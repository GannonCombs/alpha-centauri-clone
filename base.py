# base.py
"""Base (city) management system.

This module handles the Base class which represents player and AI cities
on the game map. Bases grow in population over time, produce units,
and can garrison military units for defense.
"""

class Base:
    """Represents a base (city) on the map.

    Bases are the primary settlements in the game, founded by colony pods.
    They grow in population over time by accumulating nutrients, produce
    units and facilities, and serve as defensive strongpoints.

    Attributes:
        x (int): X coordinate on the map
        y (int): Y coordinate on the map
        owner (int): Player ID who owns this base (0 = human, 1+ = AI)
        name (str): Display name of the base
        population (int): Current population (1-7)
        facilities (list): Buildings constructed in this base
        garrison (list): Units stationed at this base for defense
        supported_units (list): Units being supplied by this base
        current_production (str): Item currently being produced
        production_progress (int): Progress toward completing production
        production_turns_remaining (int): Turns until production completes
        nutrients_accumulated (int): Nutrients collected toward next pop growth
        nutrients_needed (int): Total nutrients required for next growth
        growth_turns_remaining (int): Estimated turns until population grows
    """

    def __init__(self, x, y, owner, name):
        """Initialize a new base.

        Args:
            x (int): X coordinate on the map
            y (int): Y coordinate on the map
            owner (int): Player ID (0 = human, 1+ = AI)
            name (str): Name for this base
        """
        self.x = x
        self.y = y
        self.owner = owner  # Player ID (0 = human, 1+ = AI)
        self.name = name

        # Base attributes
        self.population = 1
        self.facilities = []  # Buildings in the base
        self.garrison = []  # Units stationed at this base
        self.supported_units = []  # Units this base supports

        # Production
        self.current_production = None
        self.production_progress = 0
        self.production_turns_remaining = 5  # Placeholder

        # Growth
        self.nutrients_accumulated = 0
        self.nutrients_needed = self._calculate_nutrients_needed()
        self.growth_turns_remaining = self._calculate_growth_turns()

    def _calculate_nutrients_needed(self):
        """Calculate nutrients needed for next population growth.

        Uses progressive scaling: each population level requires more nutrients.
        Formula: base_cost (7) + (population - 1) * 3

        Returns:
            int: Nutrients required for next growth, or 999 if at max population
        """
        # Scaling: 7, 10, 14, 19, 25, 32 for pops 1->2, 2->3, 3->4, etc.
        if self.population >= 7:
            return 999  # Max pop reached, won't grow

        base_cost = 7
        scaling_factor = (self.population - 1) * 3
        return base_cost + scaling_factor

    def _calculate_growth_turns(self):
        """Calculate turns remaining until growth.

        Assumes 1 nutrient per turn accumulation rate.

        Returns:
            int: Number of turns until next population growth
        """
        remaining = self.nutrients_needed - self.nutrients_accumulated
        # Assuming 1 nutrient per turn for now
        return remaining

    def process_turn(self):
        """Process end of turn for this base.

        Adds nutrients, checks for population growth, and updates growth timers.
        Called at the end of each player's turn phase.
        """
        # Add nutrients (1 per turn for now)
        if self.population < 7:
            self.nutrients_accumulated += 1

            # Check for growth
            if self.nutrients_accumulated >= self.nutrients_needed:
                self.population += 1
                self.nutrients_accumulated = 0
                self.nutrients_needed = self._calculate_nutrients_needed()
                print(f"{self.name} grew to population {self.population}")

        # Update growth turns remaining
        self.growth_turns_remaining = self._calculate_growth_turns()

    def is_friendly(self, player_id):
        """Check if base belongs to given player."""
        return self.owner == player_id
