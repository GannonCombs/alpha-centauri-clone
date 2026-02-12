# base.py
"""Base (city) management system.

This module handles the Base class which represents player and AI cities
on the game map. Bases grow in population over time, produce units,
and can garrison military units for defense.
"""

from game import facilities

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
        self.facilities = []  # Facility IDs in the base (e.g., 'perimeter_defense', 'network_node')
        self.free_facilities = []  # IDs of facilities that are free (for UI display with *)
        self.garrison = []  # Units stationed at this base (legacy - use get_garrison_units instead)
        self.supported_units = []  # Units this base supports

        # Production
        self.current_production = "Scout Patrol"  # Default production
        self.previous_production = None  # Track for retooling penalties
        self.production_progress = 0  # Minerals accumulated
        self.production_cost = self._get_production_cost("Scout Patrol")
        self.production_turns_remaining = self._calculate_production_turns()
        self.production_queue = []  # Queue of items to build after current

        # Governor (automated production)
        self.governor_enabled = False  # Whether governor is active for this base
        self.governor_mode = None  # 'build', 'conquer', 'discover', 'explore', or None

        # Growth
        self.nutrients_accumulated = 0
        self.nutrients_needed = self._calculate_nutrients_needed()
        self.growth_turns_remaining = self._calculate_growth_turns()

        # Energy production and allocation
        self.energy_production = 0  # Total energy before allocation
        self.economy_output = 0     # Energy to credits
        self.labs_output = 0        # Energy to research
        self.psych_output = 0       # Energy to happiness
        self.commerce_income = 0    # Bonus energy from commerce (set by commerce system)
        self.inefficiency_loss = 0  # Energy lost to inefficiency this turn (for display)

        # Population happiness (for psych system)
        self.workers = 1            # Working citizens
        self.drones = 0             # Unhappy citizens
        self.talents = 0            # Happy citizens
        self.drone_riot = False     # Riot status

        # Production management
        self.hurried_this_turn = False  # Track if base has used hurry this turn

        # Unit support
        self.free_support = 2       # Free units supported
        self.support_cost_paid = 0  # Minerals spent on support

        # Disloyal citizenry (for conquered bases)
        self.turns_since_capture = None  # None = never captured, else turns since capture
        self.disloyal_drones = 0    # Extra drones from disloyal citizens

        # Cached resource output from worked tiles (updated each turn)
        self.nutrients_per_turn = 0
        self.minerals_per_turn = 0
        self.energy_per_turn = 0

        # Manual tile assignment overrides
        self.manual_include_coords = set()  # player explicitly wants these worked
        self.manual_exclude_coords = set()  # player explicitly doesn't want these worked

    def _get_fat_cross_domain(self, game_map):
        """Return list of (tile, (nx, ny)) for all domain tiles in the fat cross.

        Fat cross = 5×5 grid minus the 4 corner tiles where |dx|=2 AND |dy|=2.
        Does not include the base tile itself.  East-west wraps; top/bottom clamps.
        """
        domain = []
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue
                if abs(dx) == 2 and abs(dy) == 2:
                    continue  # corner — outside domain
                nx = (self.x + dx) % game_map.width
                ny = self.y + dy
                if not (0 <= ny < game_map.height):
                    continue
                tile = game_map.get_tile(nx, ny)
                if tile is not None:
                    domain.append((tile, (nx, ny)))
        return domain

    def get_worked_tiles(self, game_map):
        """Return the list of tiles this base is currently working.

        Domain is the SMAC fat cross (5×5 minus corners = 21 tiles).
        The base tile is always worked.  Remaining slots (population - 1) are
        filled first from manually-included tiles, then auto-filled by weighted
        score (nutrients×4 + minerals×2 + energy×1), skipping manually-excluded
        tiles.  Ties broken deterministically by map position.

        Args:
            game_map: GameMap instance

        Returns:
            list[Tile]: Tiles being worked (base tile first)
        """
        from game.map import tile_base_nutrients, tile_base_minerals, tile_base_energy

        base_tile = game_map.get_tile(self.x, self.y)
        if base_tile is None:
            return []

        worked = [base_tile]
        slots = self.population  # base tile is free; each citizen works one additional tile
        if slots <= 0:
            return worked

        domain = self._get_fat_cross_domain(game_map)
        domain_coord_set = {coord for _, coord in domain}

        # 1. Fill manually-included tiles first (in sorted coord order for determinism)
        for coord in sorted(self.manual_include_coords):
            if len(worked) - 1 >= slots:
                break
            if coord not in domain_coord_set:
                continue
            tile = game_map.get_tile(coord[0], coord[1])
            if tile is not None:
                worked.append(tile)

        placed_coords = {(t.x, t.y) for t in worked}

        # 2. Auto-fill remaining slots, skipping excluded and already-placed
        remaining = slots - (len(worked) - 1)
        if remaining > 0:
            candidates = []
            for tile, coord in domain:
                if coord in self.manual_exclude_coords:
                    continue
                if coord in placed_coords:
                    continue
                score = (tile_base_nutrients(tile) * 4
                         + tile_base_minerals(tile) * 2
                         + tile_base_energy(tile))
                nx, ny = coord
                # Adjust dx for east-west wrapping to get true ring distance
                adx = nx - self.x
                if adx > game_map.width // 2:
                    adx -= game_map.width
                elif adx < -(game_map.width // 2):
                    adx += game_map.width
                ady = ny - self.y
                ring = max(abs(adx), abs(ady))  # 1 = adjacent, 2 = outer ring
                candidates.append((-score, ring, ady, adx, tile))
            candidates.sort()
            for _, _, _, _, tile in candidates[:remaining]:
                worked.append(tile)

        return worked

    def toggle_worked_tile(self, tx, ty, game_map):
        """Toggle manual work assignment for a domain tile.

        If currently worked:  exclude it (or un-include if manually included).
        If currently unworked: include it (or un-exclude if manually excluded).
        The base tile cannot be toggled.

        Args:
            tx, ty: Tile coordinates to toggle
            game_map: GameMap instance
        """
        coord = (tx, ty)
        if coord == (self.x, self.y):
            return  # base tile is permanent

        # Verify the tile is in the fat cross domain
        raw_dx = tx - self.x
        # Adjust for east-west wrapping
        if raw_dx > game_map.width // 2:
            raw_dx -= game_map.width
        elif raw_dx < -(game_map.width // 2):
            raw_dx += game_map.width
        dy = ty - self.y
        if abs(raw_dx) > 2 or abs(dy) > 2 or (abs(raw_dx) == 2 and abs(dy) == 2):
            return  # outside domain

        current_worked_coords = {(t.x, t.y) for t in self.get_worked_tiles(game_map)}

        if coord in current_worked_coords:
            # Deselect: remove from manual_include or add to manual_exclude
            if coord in self.manual_include_coords:
                self.manual_include_coords.discard(coord)
            else:
                self.manual_exclude_coords.add(coord)
        else:
            # Select: remove from manual_exclude or add to manual_include
            if coord in self.manual_exclude_coords:
                self.manual_exclude_coords.discard(coord)
            else:
                self.manual_include_coords.add(coord)

    def calculate_resource_output(self, game_map):
        """Sum nutrients, minerals, and energy from all worked tiles.

        Updates self.nutrients_per_turn, self.minerals_per_turn, and
        self.energy_per_turn as a side effect.

        Args:
            game_map: GameMap instance

        Returns:
            tuple: (nutrients_per_turn, minerals_per_turn, energy_per_turn)
        """
        from game.map import tile_base_nutrients, tile_base_minerals, tile_base_energy

        worked = self.get_worked_tiles(game_map)
        n = sum(tile_base_nutrients(t) for t in worked)
        m = sum(tile_base_minerals(t) for t in worked)
        e = sum(tile_base_energy(t) for t in worked)

        self.nutrients_per_turn = n
        self.minerals_per_turn = m
        self.energy_per_turn = e
        return n, m, e

    def get_garrison_units(self, game):
        """Get all units actually garrisoned at this base.

        This dynamically reads from the tile instead of relying on the garrison list,
        which can get out of sync.

        Args:
            game: Game instance (to access map)

        Returns:
            list: Units at this base belonging to the base owner
        """
        tile = game.game_map.get_tile(self.x, self.y)
        if not tile:
            return []
        return [u for u in tile.units if u.owner == self.owner]

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
        if 'habitation_dome' in self.facilities:
            max_pop = 999  # Effectively unlimited
        elif 'hab_complex' in self.facilities:
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
        # Surplus = intake - (population * 2 consumption)
        surplus = getattr(self, 'nutrients_per_turn', 0) - self.population * 2
        if surplus <= 0:
            return 999  # No growth (starvation or break-even)
        return max(1, (remaining + surplus - 1) // surplus)  # ceiling division

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
            import game.unit_components

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

    def process_turn(self, energy_allocation=None, faction=None, game=None, inefficiency_loss=0):
        """Process end of turn for this base.

        Adds nutrients, checks for population growth, handles production,
        calculates energy, and updates all timers. Called at the end of each player's turn phase.

        Args:
            energy_allocation (dict): Dict with 'economy', 'labs', 'psych' percentages
                                     If None, defaults to 50% economy, 50% labs
            faction: Faction object that owns this base (for governor)
            game: Game object (for governor)

        Returns:
            str: Name of completed production item, or None if nothing completed
        """
        completed_item = None

        # Default energy allocation
        if energy_allocation is None:
            energy_allocation = {'economy': 50, 'labs': 50, 'psych': 0}

        # Calculate energy production and allocate it
        self.calculate_energy_output(game)
        self.inefficiency_loss = min(self.energy_production, max(0, inefficiency_loss))
        self.energy_production = max(0, self.energy_production - self.inefficiency_loss)
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

        # Calculate resources from all worked tiles (base tile + workers' tiles).
        if game is not None:
            nutrients_per_turn, minerals_from_tiles, _ = self.calculate_resource_output(game.game_map)
        else:
            nutrients_per_turn = 1
            minerals_from_tiles = 1
        if self.population < 7:
            self.nutrients_accumulated += nutrients_per_turn

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
            minerals_per_turn = max(1, minerals_from_tiles - self.support_cost_paid)
            self.production_progress += minerals_per_turn

            # Check if production completed
            if self.production_progress >= self.production_cost:
                completed_item = self.current_production
                print(f"{self.name} completed production of {completed_item}")

                # Check if it's a facility or project - add to base
                facility_data = facilities.get_facility_by_name(completed_item)
                if facility_data:
                    self.facilities.append(facility_data['id'])
                    print(f"{self.name} now has facility: {completed_item} ({facility_data['id']})")

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
                    # No queue - use governor if enabled, otherwise reset to default
                    if self.governor_enabled and faction and game:
                        from game.governor import select_production
                        governor_choice = select_production(self, faction, game)
                        self.current_production = governor_choice if governor_choice else "Scout Patrol"
                    else:
                        self.current_production = "Scout Patrol"
                    self.production_progress = 0
                    self.production_cost = self._get_production_cost(self.current_production)

            # Update turns remaining
            self.production_turns_remaining = self._calculate_production_turns()

        return completed_item

    def calculate_energy_output(self, game=None):
        """Calculate total energy production before allocation.

        Sums energy from all worked tiles (base tile + workers' adjacent tiles).
        Falls back to 2 if no game reference is available.

        Returns:
            int: Total energy production
        """
        if game is not None:
            from game.map import tile_base_energy
            worked = self.get_worked_tiles(game.game_map)
            self.energy_production = sum(tile_base_energy(t) for t in worked)
            self.energy_per_turn = self.energy_production
        else:
            self.energy_production = 2
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
        if 'recreation_commons' in self.facilities:
            base_drones = max(0, base_drones - 2)
        if 'hologram_theatre' in self.facilities:
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
        if 'childrens_creche' in self.facilities:
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
            'free_facilities': list(self.free_facilities),
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
            'production_queue': list(self.production_queue),
            'hurried_this_turn': self.hurried_this_turn,
            'governor_enabled': self.governor_enabled,
            'governor_mode': self.governor_mode,
            'manual_include_coords': [list(c) for c in self.manual_include_coords],
            'manual_exclude_coords': [list(c) for c in self.manual_exclude_coords],
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
        # Call __init__ first so all attributes have defaults, then overwrite with saved data.
        # This ensures any attribute added after a save was created is still present.
        base = cls(data['x'], data['y'], data['owner'], data['name'])

        # Copy basic attributes
        base.population = data['population']
        base.facilities = data['facilities']
        base.free_facilities = data.get('free_facilities', [])  # Default to empty for old saves
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
        base.hurried_this_turn = data.get('hurried_this_turn', False)
        base.production_queue = data.get('production_queue', [])
        base.governor_enabled = data.get('governor_enabled', False)
        base.governor_mode = data.get('governor_mode', None)
        base.commerce_income = data.get('commerce_income', 0)
        base.manual_include_coords = set(tuple(c) for c in data.get('manual_include_coords', []))
        base.manual_exclude_coords = set(tuple(c) for c in data.get('manual_exclude_coords', []))

        # Initialize derived/calculated values
        base.supported_units = []
        base.production_cost = base._get_production_cost(base.current_production)
        base.production_turns_remaining = base._calculate_production_turns()
        base.nutrients_needed = base._calculate_nutrients_needed()
        base.growth_turns_remaining = base._calculate_growth_turns()

        return base
