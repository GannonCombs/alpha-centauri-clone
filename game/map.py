"""Map generation and tile management.

This module handles the game map including:
- Tile creation and properties (terrain, elevation, resources)
- Map generation with configurable ocean percentage
- Special terrain features (monoliths, supply pods, fungus)
- Unit placement and stacking on tiles
- Tile state management (base, units, displayed unit index)

The Map class creates and manages the 2D grid of Tile objects that
represent the game world.
"""
import random


def tile_base_nutrients(tile):
    """Unimproved base nutrient yield for a tile.

    Land yield is determined by rainfall (0=arid, 1=moderate, 2=rainy).
    Ocean always yields 1 nutrient.
    """
    if tile.is_ocean():
        return 1
    return tile.rainfall  # 0 / 1 / 2


def tile_base_energy(tile):
    """Unimproved base energy yield for a tile.

    Land yield is determined by altitude band (per SMAC datalinks):
        < 1000m  → 1
        1000-1999m → 2
        2000-2999m → 3
        3000m+   → 4
    Ocean yields 0 without a Tidal Harness.
    """
    if tile.is_ocean():
        return 0
    alt = tile.altitude
    if alt >= 3000:
        return 4
    elif alt >= 2000:
        return 3
    elif alt >= 1000:
        return 2
    else:
        return 1


class Tile:
    """Represents a single map tile."""

    def __init__(self, x, y, terrain_type):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type  # 'land' or 'ocean' for now
        # Future expansion: resources, improvements, etc.
        self.resource = None
        self.improvement = None
        self.units = []  # Changed from single unit to list for stacking
        self.base = None
        self.supply_pod = False  # Unity supply pods
        self.monolith = False  # Alien monolith
        self.displayed_unit_index = 0  # Which unit in stack to display
        self.altitude = 0  # Exact altitude in meters: -3000 to 3500
        self.rainfall = 1  # 0=arid, 1=moderate, 2=rainy (land only; ocean is always 1)

    def is_land(self):
        """Check if this tile is land terrain."""
        return self.terrain_type == 'land'

    def is_ocean(self):
        """Check if this tile is ocean terrain."""
        return self.terrain_type == 'ocean'


class GameMap:
    """Handles map generation and tile management."""

    def __init__(self, width, height, ocean_percentage=None, cloud_cover=None):
        """Initialize map with specified dimensions and ocean percentage.

        Args:
            width (int): Map width in tiles
            height (int): Map height in tiles
            ocean_percentage (int): Percentage of ocean tiles (30-90), None for default
            cloud_cover (str): 'arid', 'moderate', or 'rainy'; None picks randomly
        """
        self.width = width
        self.height = height
        self.tiles = []
        # Default to 60% ocean (equivalent to old default of 40% land)
        # TODO: This should not be here. Erase. (Edit: or do I randomize here, for Make Random Map?)
        self.ocean_percentage = ocean_percentage if ocean_percentage is not None else int(60)
        # Cloud cover drives rainfall generation.
        # Stored as a float bias in roughly [-0.50, 0.45].
        # None = pick randomly across the full range.
        if cloud_cover is None:
            cloud_cover = random.uniform(-0.15, 0.23)
        self.cloud_cover = cloud_cover
        self.generate_random_map()

    def generate_random_map(self):
        """Generate a map with specified ocean percentage using percentile-based approach."""
        # Generate random values for all tiles
        random_values = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                value = random.random()
                row.append(value)
            random_values.append(row)

        # Calculate threshold at desired percentile for exact ocean percentage
        # Flatten all values to sort them
        all_values = []
        for row in random_values:
            all_values.extend(row)
        all_values.sort()

        # Get threshold at the ocean percentage percentile
        # If we want X% ocean, then values < threshold become ocean
        threshold_index = int(len(all_values) * (self.ocean_percentage / 100.0))
        threshold = all_values[threshold_index] if threshold_index < len(all_values) else 0.0

        # Assign terrain based on threshold
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                terrain = 'ocean' if random_values[y][x] < threshold else 'land'
                tile = Tile(x, y, terrain)
                row.append(tile)
            self.tiles.append(row)

        # Generate altitudes for all tiles
        self._generate_altitudes(random_values)

        # Generate rainfall using altitude and cloud cover
        self._generate_rainfall(self.cloud_cover)

        # Place supply pods on 3% of tiles
        self._place_supply_pods()

        # Place monoliths on 1% of land tiles
        self._place_monoliths()

    def _place_supply_pods(self):
        """Place supply pods randomly on 3% of tiles (excluding edge rows)."""
        total_tiles = self.width * self.height
        num_pods = int(total_tiles * 0.03)

        placed = 0
        attempts = 0
        max_attempts = num_pods * 10  # Prevent infinite loop

        while placed < num_pods and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(1, self.height - 2)  # Avoid first and last rows
            tile = self.get_tile(x, y)

            if tile and not tile.supply_pod:
                tile.supply_pod = True
                placed += 1

            attempts += 1

        print(f"Placed {placed} supply pods on the map")

    def _place_monoliths(self):
        """Place monoliths randomly on 1% of land tiles (excluding edge rows)."""
        # Count land tiles (excluding edge rows)
        land_tiles = sum(1 for y, row in enumerate(self.tiles) for tile in row
                        if tile.is_land() and 0 < y < self.height - 1)
        num_monoliths = max(3, int(land_tiles * 0.01))  # At least 3 monoliths

        placed = 0
        attempts = 0
        max_attempts = num_monoliths * 20

        while placed < num_monoliths and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(1, self.height - 2)  # Avoid first and last rows
            tile = self.get_tile(x, y)

            # Only place on land, and not on supply pods or other monoliths
            if tile and tile.is_land() and not tile.supply_pod and not tile.monolith:
                tile.monolith = True
                placed += 1

            attempts += 1

        print(f"Placed {placed} monoliths on the map")

    def _generate_altitudes(self, noise_values):
        """Generate exact altitude values for all tiles using noise and constraint enforcement.

        Altitudes range from -3000m (deep ocean) to 3500m (mountain peaks).
        Adjacent tiles can differ by at most 1000m.

        Args:
            noise_values: 2D array of random values (0.0-1.0) from terrain generation
        """
        print("\n=== GENERATING ALTITUDES ===")

        # Step 1: Initial assignment based on noise values (exact meters)
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                noise = noise_values[y][x]

                if tile.is_ocean():
                    # Ocean: -3000 to -1 meters
                    # Map noise 0.0-1.0 to -3000 to -1
                    tile.altitude = int(-3000 + (noise * 2999))
                else:
                    # Land: 0 to 3500 meters
                    # Map noise 0.0-1.0 to 0 to 3500
                    tile.altitude = int(noise * 3500)

        # Step 2: Enforce ±1000m constraint using iterative relaxation
        # This gradually adjusts tiles instead of snapping them to boundaries
        max_iterations = 200
        relaxation_factor = 0.3  # Adjust 30% of violation per iteration

        for iteration in range(max_iterations):
            max_violation = 0
            adjustments_made = 0

            # Store proposed adjustments for this iteration
            adjustments = {}

            for y in range(self.height):
                for x in range(self.width):
                    tile = self.tiles[y][x]

                    # Calculate average desired adjustment from all neighbors
                    total_adjustment = 0
                    neighbor_count = 0

                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue

                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                neighbor = self.tiles[ny][nx]
                                diff = tile.altitude - neighbor.altitude

                                # If constraint violated, calculate adjustment needed
                                if abs(diff) > 1000:
                                    max_violation = max(max_violation, abs(diff) - 1000)

                                    # Calculate how much to move toward valid range
                                    if diff > 1000:
                                        # Too high, need to lower
                                        target = neighbor.altitude + 1000
                                        adjustment = target - tile.altitude
                                    else:  # diff < -1000
                                        # Too low, need to raise
                                        target = neighbor.altitude - 1000
                                        adjustment = target - tile.altitude

                                    total_adjustment += adjustment
                                    neighbor_count += 1

                    # If adjustments needed, apply gradual relaxation
                    if neighbor_count > 0:
                        avg_adjustment = total_adjustment / neighbor_count
                        proposed_altitude = tile.altitude + int(avg_adjustment * relaxation_factor)
                        adjustments[(x, y)] = proposed_altitude
                        adjustments_made += 1

            # Apply adjustments with clamping
            for (x, y), new_altitude in adjustments.items():
                tile = self.tiles[y][x]
                tile.altitude = new_altitude

                # Clamp to valid ranges
                if tile.is_ocean():
                    tile.altitude = max(-3000, min(-1, tile.altitude))
                else:
                    tile.altitude = max(0, min(3500, tile.altitude))

            # Stop if violations are minimal
            if max_violation < 5:
                print(f"  Converged after {iteration + 1} iterations")
                break

        print(f"  Initial altitude assignment complete")
        print(f"  Constraint enforcement: {iteration + 1} iterations, max violation: {max_violation}m")
        print("=== ALTITUDE GENERATION COMPLETE ===\n")

    def _generate_rainfall(self, cloud_cover):
        """Generate rainfall levels for all land tiles.

        Simulates orographic (wind-driven) rainfall on a west-to-east prevailing
        wind model.  Ocean tiles produce moisture; air carries moisture eastward,
        dropping it on the upwind (western) slopes of mountain ranges and leaving
        a rain shadow on the downwind (eastern) side.  The map wraps east-west.

        Args:
            cloud_cover (str): 'arid', 'moderate', or 'rainy' – overall wetness bias
        """
        print(f"\n=== GENERATING RAINFALL (cloud_bias={cloud_cover:.2f}) ===")

        # ------------------------------------------------------------------
        # Step 1: Initialise moisture grid
        #   Ocean = 1.0 (moisture source)
        #   Land  = 0.0 (dry starting point; propagation fills this)
        # ------------------------------------------------------------------
        moisture = [[0.0] * self.width for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].is_ocean():
                    moisture[y][x] = 1.0

        # ------------------------------------------------------------------
        # Step 2: Propagate moisture eastward in three Gauss-Seidel passes.
        #   Because the map wraps east-west, the western neighbour of x=0 is
        #   x=width-1.  Three passes converge well even with wrap-around.
        #
        #   decay=0.58  → moisture halves roughly every 2-3 tiles inland,
        #                 creating a clear wet-coast / dry-interior gradient.
        #   orographic  → altitude rise (upwind slope) adds moisture;
        #                 altitude drop (downwind/rain-shadow) removes it.
        #                 Only applied between two land tiles — the sea-to-land
        #                 altitude jump at the coast must not count, or it would
        #                 make nearly every coastal tile rainy regardless of bias.
        # ------------------------------------------------------------------
        decay = 0.58
        for _ in range(3):
            for y in range(self.height):
                for x in range(self.width):
                    tile = self.tiles[y][x]
                    if tile.is_ocean():
                        moisture[y][x] = 1.0
                        continue

                    west_x = (x - 1) % self.width
                    west_tile = self.tiles[y][west_x]
                    west_m = moisture[y][west_x]

                    # Orographic only between two land tiles (coast rise excluded)
                    if west_tile.is_land():
                        alt_diff = tile.altitude - west_tile.altitude
                        orographic = max(-0.4, min(0.4, alt_diff / 2500.0))
                    else:
                        orographic = 0.0

                    moisture[y][x] = max(0.0, min(1.0,
                        west_m * decay + orographic * 0.35))

        # ------------------------------------------------------------------
        # Step 3: Apply cloud-cover bias, equatorial bonus, noise, classify.
        #   The equatorial bonus is additive here (after propagation) so it
        #   is not overwritten.  It peaks at +0.10 on the map's centre row
        #   and falls to 0 at the top and bottom edges.
        # ------------------------------------------------------------------
        bias = cloud_cover  # float bias sampled from the chosen cloud cover range

        equator_y = (self.height - 1) / 2.0

        for y in range(self.height):
            dist = abs(y - equator_y) / equator_y if equator_y > 0 else 0.0
            tropical_bonus = 0.10 * (1.0 - dist)

            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.is_ocean():
                    tile.rainfall = 1  # Oceans always produce 1 base nutrient
                    continue

                m = moisture[y][x] + tropical_bonus + bias + random.gauss(0, 0.06)
                m = max(0.0, min(1.0, m))

                if m < 0.25:
                    tile.rainfall = 0   # Arid
                elif m < 0.62:
                    tile.rainfall = 1   # Moderate
                else:
                    tile.rainfall = 2   # Rainy

        print("=== RAINFALL GENERATION COMPLETE ===\n")

    def get_tile(self, x, y):
        """Safely get a tile at coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def is_valid_position(self, x, y):
        """Check if coordinates are within map bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_unit_at(self, x, y):
        """Get currently displayed unit at a tile position, if any."""
        tile = self.get_tile(x, y)
        if tile and tile.units:
            # Return the unit at the displayed index (cycling with W key)
            if 0 <= tile.displayed_unit_index < len(tile.units):
                return tile.units[tile.displayed_unit_index]
            # Fallback to first unit if index is invalid
            return tile.units[0]
        return None

    def add_unit_at(self, x, y, unit):
        """Add a unit to a tile (supports stacking)."""
        tile = self.get_tile(x, y)
        if tile and unit not in tile.units:
            tile.units.append(unit)

    def remove_unit_at(self, x, y, unit):
        """Remove a specific unit from a tile."""
        tile = self.get_tile(x, y)
        if tile and unit in tile.units:
            tile.units.remove(unit)
            # Adjust displayed index if needed
            if tile.displayed_unit_index >= len(tile.units):
                tile.displayed_unit_index = max(0, len(tile.units) - 1)

    def set_unit_at(self, x, y, unit):
        """Place a unit on a tile (legacy method - adds to stack)."""
        self.add_unit_at(x, y, unit)

    def clear_units_at(self, x, y):
        """Remove all units from a tile."""
        tile = self.get_tile(x, y)
        if tile:
            tile.units = []
            tile.displayed_unit_index = 0

    def cycle_displayed_unit(self, x, y):
        """Cycle to next unit in stack at this tile."""
        tile = self.get_tile(x, y)
        if tile and len(tile.units) > 1:
            tile.displayed_unit_index = (tile.displayed_unit_index + 1) % len(tile.units)
            return tile.units[tile.displayed_unit_index]
        return None

    def to_dict(self):
        """Serialize map (terrain only, not units/bases).

        Returns:
            dict: Map data as dictionary
        """
        tiles_data = []
        for row in self.tiles:
            row_data = []
            for tile in row:
                row_data.append({
                    'terrain': tile.terrain_type,
                    'supply_pod': tile.supply_pod,
                    'monolith': tile.monolith,
                    'altitude': tile.altitude,
                    'rainfall': tile.rainfall
                })
            tiles_data.append(row_data)

        return {
            'width': self.width,
            'height': self.height,
            'tiles': tiles_data
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct map from dictionary.

        Args:
            data (dict): Map data dictionary

        Returns:
            GameMap: Reconstructed map instance
        """
        game_map = cls.__new__(cls)
        game_map.width = data['width']
        game_map.height = data['height']

        # Rebuild tiles
        game_map.tiles = []
        for y, row_data in enumerate(data['tiles']):
            row = []
            for x, tile_data in enumerate(row_data):
                tile = Tile(x, y, tile_data['terrain'])
                tile.supply_pod = tile_data.get('supply_pod', False)
                tile.monolith = tile_data.get('monolith', False)
                tile.altitude = tile_data.get('altitude', 0)   # Default to 0 for old saves
                tile.rainfall = tile_data.get('rainfall', 1)   # Default to moderate for old saves
                row.append(tile)
            game_map.tiles.append(row)

        return game_map