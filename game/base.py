# base.py
"""Base (city) management system.

This module handles the Base class which represents player and AI cities
on the game map. Bases grow in population over time, produce units,
and can garrison military units for defense.
"""

from game import facilities


def _default_unit_name(faction):
    """Return the generated name of the faction's default (slot 0) unit design."""
    if faction is None:
        return "Scout Patrol"
    try:
        from game.governor import get_default_unit_name
        return get_default_unit_name(faction)
    except Exception:
        return "Scout Patrol"

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
        self.original_owner = owner  # Never changes on capture — for atrocity tracking
        self.name = name
        self.nerve_stapled = False  # True after nerve stapling; suppresses all drones

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
        self.specialists = []       # List of specialist IDs assigned by the player

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

        # Initialise happiness so the citizens bar is correct before the first upkeep
        self.calculate_population_happiness()

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
        # Specialists don't work tiles — reduce available slots accordingly
        num_specialists = len(getattr(self, 'specialists', []))
        slots = max(0, self.population - num_specialists)
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

        # 2. Auto-fill remaining slots, skipping excluded and already-placed.
        # Each manual_exclude reduces available auto-fill by 1 so that deselecting
        # a tile leaves a real empty slot rather than immediately replacing it.
        remaining = slots - (len(worked) - 1) - len(self.manual_exclude_coords)
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
        from game.data.data import FACTION_DATA
        from game.terraforming import get_tile_yields
        bonuses = FACTION_DATA[self.owner].get('bonuses', {}) if self.owner < len(FACTION_DATA) else {}
        fungus_nut_bonus = bonuses.get('fungus_nutrients', 0)

        worked = self.get_worked_tiles(game_map)
        n = 0
        m = 0
        e = 0
        for t in worked:
            imp_yields = get_tile_yields(t)
            if imp_yields['fixed']:
                fn, fm, fe = imp_yields['fixed']
                n += fn
                m += fm
                e += fe
            else:
                tn = tile_base_nutrients(t) + imp_yields['nutrients']
                tm = tile_base_minerals(t) + imp_yields['minerals']
                te = tile_base_energy(t) + imp_yields['energy']
                mult = imp_yields['nutrients_multiplier']
                n += int(tn * mult)
                m += tm
                e += te

        # Deirdre: +1 nutrient per fungus tile worked (including base tile)
        if fungus_nut_bonus:
            n += sum(fungus_nut_bonus for t in worked if getattr(t, 'fungus', False))

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

    def _get_max_pop(self):
        """Return the population cap for this base based on facilities and faction bonuses."""
        from game.data.data import FACTION_DATA
        bonuses = FACTION_DATA[self.owner].get('bonuses', {}) if self.owner < len(FACTION_DATA) else {}

        # Base hard cap from facilities
        if 'habitation_dome' in self.facilities:
            return 999

        # Base limit without hab complex (faction-specific)
        base_limit = bonuses.get('hab_complex_limit', 7)

        if 'hab_complex' in self.facilities:
            # Hab complex raises cap to 14; faction bonus raises that further
            return 14 + bonuses.get('hab_complex_bonus', 0)

        # No hab complex: use faction base limit
        return base_limit + bonuses.get('hab_complex_bonus', 0)

    def _get_growth_rating(self, faction, game):
        """Return the effective GROWTH SE rating for this base's faction.

        Combines faction innate bonus with player SE selection.
        Clamped to [-3, 6].  AI factions use SE=0 until wired.
        Children's Crèche bonus is stubbed (not yet applied here).
        """
        from game.social_engineering import calculate_se_effects
        rating = 0
        if faction is not None:
            rating += faction.bonuses.get('GROWTH', 0)
            if (game is not None and hasattr(game, 'se_selections')
                    and faction.id == game.player_faction_id):
                rating += calculate_se_effects(game.se_selections).get('GROWTH', 0)
        return max(-3, min(6, rating))

    def _calculate_nutrients_needed(self, growth_rating=0):
        """Return the nutrient tank capacity (columns × rows).

        Tank formula (SMAC rules):
          columns = 10 − growth_rating  (boom → 5, ≤−3 → 12)
          rows    = 1 + population
          capacity = columns × rows

        Returns 999 when the base is at max population.
        """
        if self.population >= self._get_max_pop():
            return 999
        if growth_rating >= 6:
            columns = 5
        elif growth_rating <= -3:
            columns = 12  # Near-zero: treats as −2 for capacity
        else:
            columns = 10 - growth_rating
        return columns * (1 + self.population)

    def _calculate_growth_turns(self):
        """Estimate turns until next population growth.

        Returns 999 when nutrients are not accumulating.
        """
        surplus = getattr(self, 'nutrients_per_turn', 0) - self.population * 2
        if surplus <= 0:
            return 999
        remaining = self.nutrients_needed - self.nutrients_accumulated
        return max(1, (remaining + surplus - 1) // surplus)

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

        Uses actual minerals from worked tiles minus support costs, matching
        what process_turn actually applies each turn.

        Returns:
            int: Number of turns until production completes
        """
        if not self.current_production:
            return 0

        remaining = self.production_cost - self.production_progress
        # Mirror the exact formula used in process_turn
        minerals_per_turn = max(1, getattr(self, 'minerals_per_turn', 0) - getattr(self, 'support_cost_paid', 0))

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

    def process_turn(self, energy_allocation=None, faction=None, game=None, inefficiency_loss=0, bureaucracy_drones=0):
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
        self.apply_specialist_bonuses()

        # Increment turns since capture (for disloyal citizens)
        if self.turns_since_capture is not None:
            self.turns_since_capture += 1

        # Calculate resources from all worked tiles (base tile + workers' tiles).
        if game is not None:
            nutrients_per_turn, minerals_from_tiles, _ = self.calculate_resource_output(game.game_map)
        else:
            nutrients_per_turn = 1
            minerals_from_tiles = 1
        # --- Population growth / starvation (SMAC tank mechanics) ---
        growth_rating = self._get_growth_rating(faction, game)
        is_boom = growth_rating >= 6  # TODO: also trigger on Cloning Vats
        nut_surplus = nutrients_per_turn - self.population * 2
        max_pop = self._get_max_pop()

        if is_boom:
            columns = 5
        elif growth_rating <= -3:
            columns = 12  # Near-zero growth: acts as −2 for column count
        else:
            columns = 10 - growth_rating
        tank_capacity = columns * (1 + self.population)

        self.nutrients_accumulated += nut_surplus

        if self.nutrients_accumulated < 0:
            # Starvation: lose a citizen, reset tanks
            if self.population > 1:
                self.population -= 1
                print(f"{self.name} lost population due to starvation, now {self.population}")
            self.nutrients_accumulated = 0
        elif is_boom:
            # Boom: grow immediately if surplus ≥ 2 this turn
            if nut_surplus >= 2 and self.population < max_pop:
                self.population += 1
                self.nutrients_accumulated = 0
                print(f"{self.name} boom-grew to population {self.population}")
            else:
                # Cap tanks (storage only in boom mode)
                self.nutrients_accumulated = min(self.nutrients_accumulated, tank_capacity)
        elif self.nutrients_accumulated >= tank_capacity:
            # Normal growth trigger: tanks full
            if self.population >= max_pop:
                self.nutrients_accumulated = tank_capacity  # Stay capped, no growth
            elif growth_rating <= -3:
                # Near-zero: tanks reset but population does not change
                self.nutrients_accumulated = 0
            else:
                # Check if new population can be fed; if not, tanks empty but no growth
                if nutrients_per_turn - (self.population + 1) * 2 >= 0:
                    self.population += 1
                    print(f"{self.name} grew to population {self.population}")
                self.nutrients_accumulated = 0

        # Recompute tank capacity after any population change, store for display
        self.nutrients_needed = columns * (1 + self.population)

        # Update growth turns remaining
        self.growth_turns_remaining = self._calculate_growth_turns()

        # Calculate population happiness after growth so icon counts match population
        riot_before = self.drone_riot
        self.calculate_population_happiness(bureaucracy_drones=bureaucracy_drones)
        riot_transition = None
        if self.drone_riot and not riot_before:
            riot_transition = 'started'
        elif not self.drone_riot and riot_before:
            riot_transition = 'ended'

        # Notify the player when riot status changes
        if game is not None and riot_transition == 'started':
            if hasattr(game, 'upkeep_events'):
                game.upkeep_events.append({
                    'type': 'drone_riot',
                    'base_name': self.name,
                })
        if game is not None and riot_transition == 'ended':
            if hasattr(game, 'set_status_message'):
                game.set_status_message(f"Drone riot ended at {self.name}.")

        # Calculate unit support cost
        self.calculate_support_cost()

        # Drone riot: suppress surplus energy (economy and labs outputs go to zero)
        # Nutrients still feed the population (handled above), psych still applies.
        if self.drone_riot:
            self.economy_output = 0
            self.labs_output = 0

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
                        self.current_production = governor_choice if governor_choice else _default_unit_name(faction)
                    else:
                        self.current_production = _default_unit_name(faction)
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

    def calculate_population_happiness(self, bureaucracy_drones=0):
        """Calculate workers, drones, and talents based on psych and facilities.

        Specialists are a separate citizen category and are not subject to the
        drone/talent/worker classification.  All happiness math operates on the
        non-specialist pool (population − num_specialists) so specialist psych
        bonuses cannot circularly consume the specialist's own citizen slot.

        Formula:
        - Base drones: 1 drone per 4 citizens beyond size 3 (difficulty scaled)
        - Bureaucracy drones: extra drones when faction exceeds BaseLimit bases
        - Disloyal drones: Extra drones from recently conquered bases
        - Facilities: Recreation Commons (-2 drones), Hologram Theatre (-2 drones)
        - Psych: 2 psych points = 1 talent (capped to non-specialist pool)
        - Workers: non-specialist citizens − drones − talents
        """
        # Specialists: can have at most one per citizen; trim only hard overflow
        num_specialists = len(self.specialists)
        if num_specialists > self.population:
            self.specialists = self.specialists[:self.population]
            num_specialists = self.population

        # Non-specialist citizens: these are the only ones classified as W/D/T
        non_spec = self.population - num_specialists

        # Base drones (threshold still based on total population, not just non-spec)
        base_drones = 0
        if self.population > 3:
            base_drones = (self.population - 3) // 4

        # Zakharov (University, id 2): +1 extra drone per 4 citizens
        from game.data.data import FACTION_DATA
        bonuses = FACTION_DATA[self.owner].get('bonuses', {}) if self.owner < len(FACTION_DATA) else {}
        if bonuses.get('extra_drone_per_4'):
            base_drones += self.population // 4

        # Add disloyal citizens (for conquered bases)
        if self.turns_since_capture is not None and self.turns_since_capture < 50:
            # Formula: 5 - turns/10, capped by (base_size + 2) / 4
            disloyal_raw = 5 - (self.turns_since_capture // 10)
            disloyal_cap = (self.population + 2) // 4
            self.disloyal_drones = max(0, min(disloyal_raw, disloyal_cap))
            base_drones += self.disloyal_drones
        else:
            self.disloyal_drones = 0

        # Bureaucracy drones (from exceeding BaseLimit bases)
        base_drones += bureaucracy_drones

        # Apply facility effects
        if 'recreation_commons' in self.facilities:
            base_drones = max(0, base_drones - 2)
        if 'hologram_theatre' in self.facilities:
            base_drones = max(0, base_drones - 2)

        # Cap drones to the non-specialist pool
        base_drones = min(base_drones, non_spec)

        # Convert psych to talents (2 psych = 1 talent)
        base_talents = self.psych_output // 2

        # Faction bonus: Lal (Peacekeepers, ID 6) gets 1 free talent per 4 citizens
        # Citizens 1, 5, 9, 13, ... are always talents — formula: (pop + 3) // 4
        if self.owner == 6:
            base_talents += (self.population + 3) // 4

        # Cap talents to what remains in the non-specialist pool after drones
        base_talents = min(base_talents, max(0, non_spec - base_drones))

        # Nerve staple suppresses all drones permanently
        if getattr(self, 'nerve_stapled', False):
            base_drones = 0
            base_talents = min(base_talents, non_spec)

        # Final population breakdown
        self.drones = base_drones
        self.talents = base_talents
        self.workers = max(0, non_spec - base_drones - base_talents)

        # Check for drone riot
        self.check_drone_riot()

    def apply_specialist_bonuses(self):
        """Add fixed specialist output on top of tile-based energy allocation.

        Called after allocate_energy() so specialist bonuses are included in
        the totals shown to the player and used by calculate_population_happiness.
        """
        from game.data.unit_data import SPECIALISTS
        spec_map = {s['id']: s for s in SPECIALISTS}
        for spec_id in self.specialists:
            spec = spec_map.get(spec_id, {})
            self.economy_output += spec.get('economy', 0)
            self.labs_output    += spec.get('labs', 0)
            self.psych_output   += spec.get('psych', 0)

    def check_drone_riot(self):
        """Check if drones outnumber talents, causing a riot.

        Returns:
            str: 'started' if riot just began, 'ended' if it just ended, else None
        """
        if self.drones > self.talents:
            if not self.drone_riot:
                self.drone_riot = True
                return 'started'
        else:
            if self.drone_riot:
                self.drone_riot = False
                return 'ended'
        return None

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
            'specialists': list(self.specialists),
            'drone_riot': self.drone_riot,
            'free_support': self.free_support,
            'support_cost_paid': self.support_cost_paid,
            'turns_since_capture': self.turns_since_capture,
            'disloyal_drones': self.disloyal_drones,
            'original_owner': self.original_owner,
            'nerve_stapled': self.nerve_stapled,
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
        base.specialists = data.get('specialists', [])
        base.drone_riot = data.get('drone_riot', False)
        base.free_support = data.get('free_support', 2)
        base.support_cost_paid = data.get('support_cost_paid', 0)
        base.turns_since_capture = data.get('turns_since_capture', None)
        base.disloyal_drones = data.get('disloyal_drones', 0)
        base.original_owner = data.get('original_owner', base.owner)
        base.nerve_stapled = data.get('nerve_stapled', False)
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
