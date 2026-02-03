# base.py
"""Base (city) management system.

This module handles the Base class which represents player and AI cities
on the game map. Bases grow in population over time, produce units,
and can garrison military units for defense.
"""

import facilities

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
        self.current_production = "Scout Patrol"  # Default production
        self.production_progress = 0  # Minerals accumulated
        self.production_cost = self._get_production_cost("Scout Patrol")
        self.production_turns_remaining = self._calculate_production_turns()

        # Growth
        self.nutrients_accumulated = 0
        self.nutrients_needed = self._calculate_nutrients_needed()
        self.growth_turns_remaining = self._calculate_growth_turns()

    def _calculate_nutrients_needed(self):
        """Calculate nutrients needed for next population growth.

        Uses progressive scaling: each population level requires more nutrients.
        Formula: base_cost (7) + (population - 1) * 3

        Population limits:
        - 7 without Habitation Complex
        - 14 with Habitation Complex
        - Unlimited with Habitation Dome

        Returns:
            int: Nutrients required for next growth, or 999 if at max population
        """
        # Determine population limit based on facilities
        max_pop = 7  # Default limit
        if 'Habitation Dome' in self.facilities:
            max_pop = 999  # Effectively unlimited
        elif 'Habitation Complex' in self.facilities:
            max_pop = 14

        # Scaling: 7, 10, 14, 19, 25, 32 for pops 1->2, 2->3, 3->4, etc.
        if self.population >= max_pop:
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

    def _get_production_cost(self, item_name):
        """Get the mineral/credit cost for producing an item.

        Args:
            item_name (str): Name of the unit or facility to produce

        Returns:
            int: Total cost in minerals/credits
        """
        # Check if it's a facility or secret project
        facility_data = facilities.get_facility_by_name(item_name)
        if facility_data:
            return facility_data['cost']

        # Otherwise check unit costs
        production_costs = {
            "Scout Patrol": 3,
            "Gunship Foil": 8,
            "Gunship Needlejet": 15,
            "Colony Pod": 10,
            "Sea Colony Pod": 12,
            "Stockpile Energy": 0  # Instant, used for converting production to energy
        }
        return production_costs.get(item_name, 30)  # Default to 30 if not found

    def _calculate_production_turns(self):
        """Calculate turns remaining until production completes.

        Assumes base produces minerals based on population (for now, 1 mineral per turn).

        Returns:
            int: Number of turns until production completes
        """
        if not self.current_production:
            return 0

        remaining = self.production_cost - self.production_progress
        minerals_per_turn = self.population  # Simple: 1 mineral per citizen
        if minerals_per_turn == 0:
            return 999

        return (remaining + minerals_per_turn - 1) // minerals_per_turn  # Ceiling division

    def hurry_production(self, credits_spent):
        """Rush production by spending energy credits.

        The cost is 10 credits per 1 production point. Partial payments
        reduce the number of turns remaining.

        Args:
            credits_spent (int): Amount of energy credits to spend

        Returns:
            tuple: (production_added, completed) where completed is True if production finished
        """
        if not self.current_production:
            return (0, False)

        remaining_cost = self.production_cost - self.production_progress

        # Calculate how much production this buys (10 credits = 1 production)
        production_added = credits_spent // 10
        production_added = min(production_added, remaining_cost)

        # Add to progress
        self.production_progress += production_added

        # Check if completed
        completed = self.production_progress >= self.production_cost

        # Update turns remaining
        self.production_turns_remaining = self._calculate_production_turns()

        return (production_added, completed)

    def process_turn(self):
        """Process end of turn for this base.

        Adds nutrients, checks for population growth, handles production,
        and updates all timers. Called at the end of each player's turn phase.

        Returns:
            str: Name of completed production item, or None if nothing completed
        """
        completed_item = None

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

        # Handle production
        if self.current_production:
            minerals_per_turn = self.population  # Simple: 1 mineral per citizen
            self.production_progress += minerals_per_turn

            # Check if production completed
            if self.production_progress >= self.production_cost:
                completed_item = self.current_production
                print(f"{self.name} completed production of {completed_item}")

                # Check if it's a facility or project - add to base
                facility_data = facilities.get_facility_by_name(completed_item)
                if facility_data:
                    self.facilities.append(completed_item)
                    print(f"{self.name} now has facility: {completed_item}")

                # Reset production
                if completed_item == "Stockpile Energy":
                    # Stockpile Energy continues each turn
                    self.current_production = "Stockpile Energy"
                    self.production_progress = 0
                    self.production_cost = self._get_production_cost("Stockpile Energy")
                else:
                    # Other items reset to default
                    self.current_production = "Scout Patrol"
                    self.production_progress = 0
                    self.production_cost = self._get_production_cost(self.current_production)

            # Update turns remaining
            self.production_turns_remaining = self._calculate_production_turns()

        return completed_item

    def is_friendly(self, player_id):
        """Check if base belongs to given player."""
        return self.owner == player_id

    def to_dict(self, unit_index_map):
        """Serialize base to dictionary.

        Args:
            unit_index_map (dict): Map from unit objects to indices

        Returns:
            dict: Base data as dictionary
        """
        # Convert garrison units to indices
        garrison_indices = [unit_index_map[u] for u in self.garrison if u in unit_index_map]

        return {
            'x': self.x,
            'y': self.y,
            'owner': self.owner,
            'name': self.name,
            'population': self.population,
            'facilities': list(self.facilities),
            'garrison_unit_indices': garrison_indices,
            'current_production': self.current_production,
            'production_progress': self.production_progress,
            'nutrients_accumulated': self.nutrients_accumulated
        }

    @classmethod
    def from_dict(cls, data, units_list):
        """Reconstruct base from dictionary.

        Args:
            data (dict): Base data dictionary
            units_list (list): List of all units (for resolving garrison indices)

        Returns:
            Base: Reconstructed base instance
        """
        base = cls.__new__(cls)

        # Copy basic attributes
        base.x = data['x']
        base.y = data['y']
        base.owner = data['owner']
        base.name = data['name']
        base.population = data['population']
        base.facilities = data['facilities']
        base.current_production = data['current_production']
        base.production_progress = data['production_progress']
        base.nutrients_accumulated = data['nutrients_accumulated']

        # Rebuild garrison from indices
        base.garrison = [units_list[idx] for idx in data['garrison_unit_indices']]

        # Initialize derived/calculated values
        base.supported_units = []
        base.production_cost = base._get_production_cost(base.current_production)
        base.production_turns_remaining = base._calculate_production_turns()
        base.nutrients_needed = base._calculate_nutrients_needed()
        base.growth_turns_remaining = base._calculate_growth_turns()

        return base
