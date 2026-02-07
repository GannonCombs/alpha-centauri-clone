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
        self.previous_production = None  # Track for retooling penalties
        self.production_progress = 0  # Minerals accumulated
        self.production_cost = self._get_production_cost("Scout Patrol")
        self.production_turns_remaining = self._calculate_production_turns()
        self.production_queue = []  # Queue of items to build after current

        # Growth
        self.nutrients_accumulated = 0
        self.nutrients_needed = self._calculate_nutrients_needed()
        self.growth_turns_remaining = self._calculate_growth_turns()

        # Energy production and allocation
        self.energy_production = 0  # Total energy before allocation
        self.economy_output = 0     # Energy to credits
        self.labs_output = 0        # Energy to research
        self.psych_output = 0       # Energy to happiness

        # Population happiness (for psych system)
        self.workers = 1            # Working citizens
        self.drones = 0             # Unhappy citizens
        self.talents = 0            # Happy citizens
        self.drone_riot = False     # Riot status

        # Unit support
        self.free_support = 2       # Free units supported
        self.support_cost_paid = 0  # Minerals spent on support

        # Disloyal citizenry (for conquered bases)
        self.turns_since_capture = None  # None = never captured, else turns since capture
        self.disloyal_drones = 0    # Extra drones from disloyal citizens

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

        Dynamically calculates cost from unit components when possible.

        Args:
            item_name (str): Name of the unit or facility to produce

        Returns:
            int: Total cost in minerals/credits
        """
        # Check if it's a facility or secret project
        facility_data = facilities.get_facility_by_name(item_name)
        if facility_data:
            return facility_data['cost']

        # Special case: Stockpile Energy
        if item_name == "Stockpile Energy":
            return 0  # Instant, converts production to energy

        # Try to calculate from unit components dynamically
        try:
            import unit_components

            # Try to find unit design in current designs (for custom units)
            # For now, use hardcoded base unit costs
            # TODO: Integrate with design workshop designs

            # Calculate base unit costs from components
            unit_costs = {
                "Scout Patrol": 1 + 1 + 1,  # hand_weapons(1) + no_armor(1) + infantry(1) = 3
                "Colony Pod": 10 + 1 + 1,   # colony_pod(10) + no_armor(1) + infantry(1) = 12
                "Sea Colony Pod": 10 + 1 + 4,  # colony_pod(10) + no_armor(1) + foil(4) = 15
                "Former": 6 + 1 + 1,  # terraforming(6) + no_armor(1) + infantry(1) = 8
                "Probe Team": 4 + 1 + 1,  # probe(4) + no_armor(1) + infantry(1) = 6
                "Transport": 4 + 1 + 4,  # transport(4) + no_armor(1) + foil(4) = 9
            }

            if item_name in unit_costs:
                return unit_costs[item_name]

            # For units not in the table, try to estimate from name
            # This is a fallback for dynamically created units
            # Parse unit name to get components (simplified)
            return 10  # Default reasonable cost

        except ImportError:
            # Fallback to hardcoded values if unit_components not available
            production_costs = {
                "Scout Patrol": 3,
                "Colony Pod": 12,
                "Sea Colony Pod": 15,
            }
            return production_costs.get(item_name, 10)  # Default to 10 if not found

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
            return 0, False

        remaining_cost = self.production_cost - self.production_progress

        # Calculate how much production this buys (2 credits = 1 mineral, SMAC standard)
        production_added = credits_spent // 2
        production_added = min(production_added, remaining_cost)

        # Add to progress
        self.production_progress += production_added

        # Check if completed
        completed = self.production_progress >= self.production_cost

        # Update turns remaining
        self.production_turns_remaining = self._calculate_production_turns()

        return production_added, completed

    def change_production(self, new_item):
        """Change what this base is producing, applying retooling penalties.

        From alpha.txt: 50% penalty on minerals, first 10 minerals exempt.

        Args:
            new_item (str): Name of the new item to produce

        Returns:
            int: Minerals lost to retooling penalty
        """
        if new_item == self.current_production:
            return 0  # No change, no penalty

        # Calculate retooling penalty: 50% of minerals beyond first 10
        penalty = 0
        if self.production_progress > 10:
            penalty = (self.production_progress - 10) // 2  # 50% of excess
            self.production_progress -= penalty

        # Track previous production and change to new item
        self.previous_production = self.current_production
        self.current_production = new_item
        self.production_cost = self._get_production_cost(new_item)

        # Reset progress if changing to a different item category
        # (In SMAC, you keep minerals when changing within category, but we'll simplify)
        if self.production_progress > 0:
            # Keep the minerals (already reduced by penalty above)
            pass

        # Update turns remaining
        self.production_turns_remaining = self._calculate_production_turns()

        return penalty

    def process_turn(self, energy_allocation=None):
        """Process end of turn for this base.

        Adds nutrients, checks for population growth, handles production,
        calculates energy, and updates all timers. Called at the end of each player's turn phase.

        Args:
            energy_allocation (dict): Dict with 'economy', 'labs', 'psych' percentages
                                     If None, defaults to 50% economy, 50% labs

        Returns:
            str: Name of completed production item, or None if nothing completed
        """
        completed_item = None

        # Default energy allocation
        if energy_allocation is None:
            energy_allocation = {'economy': 50, 'labs': 50, 'psych': 0}

        # Calculate energy production and allocate it
        self.calculate_energy_output()
        self.allocate_energy(
            energy_allocation['economy'],
            energy_allocation['labs'],
            energy_allocation['psych']
        )

        # Increment turns since capture (for disloyal citizens)
        if self.turns_since_capture is not None:
            self.turns_since_capture += 1

        # Calculate population happiness
        self.calculate_population_happiness()

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

        # Calculate unit support cost
        self.calculate_support_cost()

        # Handle production (halt if drone riot)
        if self.current_production and not self.drone_riot:
            # Minerals per turn = population - support cost
            minerals_per_turn = max(1, self.population - self.support_cost_paid)
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

                # Reset production - check queue first
                if completed_item == "Stockpile Energy":
                    # Stockpile Energy continues each turn
                    self.current_production = "Stockpile Energy"
                    self.production_progress = 0
                    self.production_cost = self._get_production_cost("Stockpile Energy")
                elif self.production_queue:
                    # Start next item in queue
                    next_item = self.production_queue.pop(0)
                    self.current_production = next_item
                    self.production_progress = 0
                    self.production_cost = self._get_production_cost(next_item)
                    print(f"{self.name} starting queued item: {next_item}")
                else:
                    # No queue - reset to default
                    self.current_production = "Scout Patrol"
                    self.production_progress = 0
                    self.production_cost = self._get_production_cost(self.current_production)

            # Update turns remaining
            self.production_turns_remaining = self._calculate_production_turns()

        return completed_item

    def calculate_energy_output(self):
        """Calculate total energy production before allocation.

        For now, uses a simple formula: population * 2
        In the future, this will sum energy from worked tiles.

        Returns:
            int: Total energy production
        """
        # Simple formula for now: 2 energy per citizen
        self.energy_production = self.population * 2
        return self.energy_production

    def allocate_energy(self, economy_percent, labs_percent, psych_percent):
        """Split energy production based on allocation percentages.

        Args:
            economy_percent (int): Percentage to economy (0-100)
            labs_percent (int): Percentage to labs (0-100)
            psych_percent (int): Percentage to psych (0-100)

        Note: Percentages should sum to 100, but will be normalized if not
        """
        # Normalize percentages if they don't sum to 100
        total = economy_percent + labs_percent + psych_percent
        if total == 0:
            total = 1  # Avoid division by zero

        # Calculate actual allocation
        self.economy_output = int(self.energy_production * economy_percent / total)
        self.labs_output = int(self.energy_production * labs_percent / total)
        self.psych_output = int(self.energy_production * psych_percent / total)

    def calculate_population_happiness(self):
        """Calculate workers, drones, and talents based on psych and facilities.

        Formula:
        - Base drones: 1 drone per 4 citizens beyond size 3 (difficulty scaled)
        - Disloyal drones: Extra drones from recently conquered bases
        - Facilities: Recreation Commons (-2 drones), Hologram Theatre (-2 drones)
        - Psych: 2 psych points = 1 talent
        - Workers: remaining population
        """
        # Start with all population as workers
        base_drones = 0
        base_talents = 0

        # Calculate base drones (simplified: 1 drone per 4 citizens beyond size 3)
        if self.population > 3:
            base_drones = (self.population - 3) // 4

        # Add disloyal citizens (for conquered bases)
        if self.turns_since_capture is not None and self.turns_since_capture < 50:
            # Formula: 5 - turns/10, capped by (base_size + 2) / 4
            disloyal_raw = 5 - (self.turns_since_capture // 10)
            disloyal_cap = (self.population + 2) // 4
            self.disloyal_drones = max(0, min(disloyal_raw, disloyal_cap))
            base_drones += self.disloyal_drones
        else:
            self.disloyal_drones = 0

        # Apply facility effects
        if 'Recreation Commons' in self.facilities:
            base_drones = max(0, base_drones - 2)
        if 'Hologram Theatre' in self.facilities:
            base_drones = max(0, base_drones - 2)

        # Convert psych to talents (2 psych = 1 talent)
        base_talents = self.psych_output // 2

        # Final population breakdown
        self.drones = base_drones
        self.talents = base_talents
        self.workers = max(0, self.population - self.drones - self.talents)

        # Check for drone riot
        self.check_drone_riot()

    def check_drone_riot(self):
        """Check if drones outnumber talents, causing a riot."""
        if self.drones > self.talents:
            if not self.drone_riot:
                self.drone_riot = True
                print(f"DRONE RIOT at {self.name}! Drones: {self.drones}, Talents: {self.talents}")
        else:
            if self.drone_riot:
                self.drone_riot = False
                print(f"Drone riot ended at {self.name}")

    def calculate_free_support(self):
        """Calculate number of units this base can support for free.

        Base: 2 units free
        Children's Creche: +1
        SE Support modifiers will be added later

        Returns:
            int: Number of free support slots
        """
        free = 2  # Base support
        if "Children's Creche" in self.facilities:
            free += 1
        self.free_support = free
        return free

    def calculate_support_cost(self):
        """Calculate mineral cost for supporting units.

        Units beyond free support level cost 1 mineral each.
        Units with Clean Reactor ability don't require support.

        Returns:
            int: Total mineral cost for unit support
        """
        # Count units that actually need support (exclude Clean Reactor units)
        num_supported = 0
        for unit in self.supported_units:
            if not getattr(unit, 'has_clean_reactor', False):
                num_supported += 1

        free_support = self.calculate_free_support()

        if num_supported <= free_support:
            self.support_cost_paid = 0
        else:
            self.support_cost_paid = num_supported - free_support

        return self.support_cost_paid

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
            'previous_production': self.previous_production,
            'production_progress': self.production_progress,
            'nutrients_accumulated': self.nutrients_accumulated,
            'energy_production': self.energy_production,
            'economy_output': self.economy_output,
            'labs_output': self.labs_output,
            'psych_output': self.psych_output,
            'workers': self.workers,
            'drones': self.drones,
            'talents': self.talents,
            'drone_riot': self.drone_riot,
            'free_support': self.free_support,
            'support_cost_paid': self.support_cost_paid,
            'turns_since_capture': self.turns_since_capture,
            'disloyal_drones': self.disloyal_drones,
            'production_queue': list(self.production_queue)
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
        base.previous_production = data.get('previous_production', None)
        base.production_progress = data['production_progress']
        base.nutrients_accumulated = data['nutrients_accumulated']

        # Rebuild garrison from indices
        base.garrison = [units_list[idx] for idx in data['garrison_unit_indices']]

        # Load energy and happiness data (with defaults for backward compatibility)
        base.energy_production = data.get('energy_production', 0)
        base.economy_output = data.get('economy_output', 0)
        base.labs_output = data.get('labs_output', 0)
        base.psych_output = data.get('psych_output', 0)
        base.workers = data.get('workers', base.population)
        base.drones = data.get('drones', 0)
        base.talents = data.get('talents', 0)
        base.drone_riot = data.get('drone_riot', False)
        base.free_support = data.get('free_support', 2)
        base.support_cost_paid = data.get('support_cost_paid', 0)
        base.turns_since_capture = data.get('turns_since_capture', None)
        base.disloyal_drones = data.get('disloyal_drones', 0)
        base.production_queue = data.get('production_queue', [])

        # Initialize derived/calculated values
        base.supported_units = []
        base.production_cost = base._get_production_cost(base.current_production)
        base.production_turns_remaining = base._calculate_production_turns()
        base.nutrients_needed = base._calculate_nutrients_needed()
        base.growth_turns_remaining = base._calculate_growth_turns()

        return base
