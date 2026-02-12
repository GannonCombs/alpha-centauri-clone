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


def tile_base_minerals(tile):
    """Unimproved base mineral yield for a tile.

    Ocean and flat land yield 0 unimproved minerals.
    Rolling and rocky land both yield 1 unimproved mineral
    (rocky can reach 4 with mine+road, rolling can reach 2 with mine).
    """
    if tile.is_ocean():
        return 0
    return 1 if getattr(tile, 'rockiness', 0) >= 1 else 0


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
        self.rockiness = 0  # 0=flat, 1=rolling, 2=rocky (land only; ocean is always 0)
        self.fungus = False  # Xenofungus present on this tile
        self.void = False  # True for edge rows — not part of the playable map
        self.river_edges = set()  # Directions {'N','S','E','W'} where a river crosses this tile's edge

    def is_land(self):
        """Check if this tile is land terrain."""
        return self.terrain_type == 'land'

    def is_ocean(self):
        """Check if this tile is ocean terrain."""
        return self.terrain_type == 'ocean'


class GameMap:
    """Handles map generation and tile management."""

    def __init__(self, width, height, ocean_percentage=None, cloud_cover=None, erosive_forces=None, native_life=None):
        """Initialize map with specified dimensions and ocean percentage.

        Args:
            width (int): Map width in tiles
            height (int): Map height in tiles
            ocean_percentage (int): Percentage of ocean tiles (30-90), None for default
            cloud_cover (str): 'arid', 'moderate', or 'rainy'; None picks randomly
            native_life (str): 'abundant', 'average', or 'rare'; None picks randomly
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

        # Erosive forces drives rockiness generation.
        # Positive bias → higher rocky threshold → fewer rocky tiles (strong erosion = smooth).
        # Negative bias → lower rocky threshold → more rocky tiles (weak erosion = rough).
        # None = pick randomly across the full range.
        if erosive_forces is None:
            erosive_forces = random.uniform(0.10, 0.30)
        self.erosive_forces = erosive_forces

        if native_life is None:
            native_life = random.choice(['abundant', 'average', 'rare'])
        self.native_life = native_life

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
        # Edge rows (y=0 and y=height-1) are marked void — they sit under the
        # black border overlay and are not part of the playable map.
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                terrain = 'ocean' if random_values[y][x] < threshold else 'land'
                tile = Tile(x, y, terrain)
                if y == 0 or y == self.height - 1:
                    tile.void = True
                row.append(tile)
            self.tiles.append(row)

        # Generate altitudes for all tiles
        self._generate_altitudes(random_values)

        # Scale land altitudes based on erosive forces (before rockiness so both benefit)
        self._apply_erosion(self.erosive_forces)

        # Generate rockiness using independent noise (must come before rainfall)
        rock_noise = [[random.random() for _ in range(self.width)] for _ in range(self.height)]
        self._generate_rockiness(rock_noise, self.erosive_forces)

        # Generate rainfall using altitude, cloud cover, and rockiness
        self._generate_rainfall(self.cloud_cover)

        # Place supply pods on 3% of tiles
        self._place_supply_pods()

        # Place monoliths on 1% of land tiles
        self._place_monoliths()

        # Generate xenofungus based on native life setting
        self._generate_fungus(self.native_life)

        # Generate 1-2 rivers on land
        self._generate_rivers()

    def _generate_rivers(self):
        """Place 1-2 rivers on the map.  Each river walks 3-10 land tiles,
        moving only cardinally (N/S/E/W), with occasional 90-degree turns.
        """
        import random
        num_rivers = random.randint(1, 2)
        land_tiles = [
            self.tiles[y][x]
            for y in range(1, self.height - 1)
            for x in range(self.width)
            if self.tiles[y][x].is_land()
        ]
        if not land_tiles:
            return
        for _ in range(num_rivers):
            start = random.choice(land_tiles)
            self.generate_river_from(start.x, start.y)

    def generate_river_from(self, start_x, start_y):
        """Walk a river starting at (start_x, start_y) for 3-10 land tiles.

        The path moves only cardinally.  At each step there is a 30% chance
        of a 90-degree turn (left or right with equal probability).
        River edges are written onto the tiles so the renderer can draw them.

        Args:
            start_x (int): Starting tile X coordinate
            start_y (int): Starting tile Y coordinate
        """
        import random
        OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
        PERP = {
            'N': ['E', 'W'], 'S': ['E', 'W'],
            'E': ['N', 'S'], 'W': ['N', 'S'],
        }
        STEP = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

        length = random.randint(3, 10)
        direction = random.choice(['N', 'S', 'E', 'W'])
        x, y = start_x, start_y

        for _ in range(length):
            tile = self.get_tile(x, y)
            if tile is None or not tile.is_land():
                break

            # Possibly turn 90 degrees
            if random.random() < 0.30:
                direction = random.choice(PERP[direction])

            dx, dy = STEP[direction]
            nx, ny = (x + dx) % self.width, y + dy
            if not (0 <= ny < self.height):
                break
            next_tile = self.get_tile(nx, ny)
            if next_tile is None or not next_tile.is_land():
                break

            # Mark the shared edge on both tiles
            tile.river_edges.add(direction)
            next_tile.river_edges.add(OPPOSITE[direction])

            x, y = nx, ny

        print(f"River generated from ({start_x},{start_y})")

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

    def _generate_fungus(self, native_life):
        """Generate xenofungus across the map.

        Uses independent noise with one smoothing pass to create clustered
        fungal regions. Land and ocean tiles are classified separately with
        different target densities per native_life setting.

        Land fungus appears as pink overlay; sea fungus as lighter blue.
        Both impose movement penalties (see game.py try_move_unit).

        Args:
            native_life (str): 'abundant', 'average', or 'rare'
        """
        print(f"\n=== GENERATING FUNGUS (native_life={native_life}) ===")

        # Target fraction of each terrain type that becomes fungus
        targets = {
            'abundant': (0.22, 0.15),  # (land_fraction, sea_fraction)
            'average':  (0.12, 0.08),
            'rare':     (0.04, 0.03),
        }
        land_frac, sea_frac = targets.get(native_life, targets['average'])

        # Step 1: Generate independent noise
        noise = [[random.random() for _ in range(self.width)] for _ in range(self.height)]

        # Step 2: One smoothing pass for geographic clustering
        smoothed = [row[:] for row in noise]
        for y in range(self.height):
            for x in range(self.width):
                neighbors = []
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx = (x + dx) % self.width
                        ny = y + dy
                        if 0 <= ny < self.height:
                            neighbors.append(noise[ny][nx])
                if neighbors:
                    smoothed[y][x] = noise[y][x] * 0.6 + (sum(neighbors) / len(neighbors)) * 0.4

        # Step 3: Separate percentile classification for land and sea
        land_scores = sorted(
            smoothed[y][x]
            for y in range(self.height)
            for x in range(self.width)
            if self.tiles[y][x].is_land()
        )
        sea_scores = sorted(
            smoothed[y][x]
            for y in range(self.height)
            for x in range(self.width)
            if self.tiles[y][x].is_ocean()
        )

        n_land = len(land_scores)
        n_sea = len(sea_scores)

        land_threshold = land_scores[max(0, int(n_land * (1.0 - land_frac)) - 1)] if n_land > 0 else 1.1
        sea_threshold = sea_scores[max(0, int(n_sea * (1.0 - sea_frac)) - 1)] if n_sea > 0 else 1.1

        land_fungus_count = sea_fungus_count = 0
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                s = smoothed[y][x]
                if tile.is_land() and s >= land_threshold:
                    tile.fungus = True
                    land_fungus_count += 1
                elif tile.is_ocean() and s >= sea_threshold:
                    tile.fungus = True
                    sea_fungus_count += 1

        print(f"  Land fungus: {land_fungus_count} tiles  Sea fungus: {sea_fungus_count} tiles")
        print("=== FUNGUS GENERATION COMPLETE ===\n")

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

                # Rocky terrain is drier: exposed rock sheds water quickly and
                # sits in high-altitude rain shadows.  Apply a moisture penalty
                # at classification time so the penalty doesn't propagate to
                # neighbouring tiles — rocky zones are dry but don't create
                # artificial aridity further inland.
                rock_penalty = (0.0, 0.07, 0.25)[tile.rockiness]
                effective_m = m - rock_penalty

                if effective_m < 0.25:
                    tile.rainfall = 0   # Arid
                elif effective_m < 0.62:
                    tile.rainfall = 1   # Moderate
                else:
                    tile.rainfall = 2   # Rainy

        print("=== RAINFALL GENERATION COMPLETE ===\n")

    def _apply_erosion(self, erosive_forces):
        """Scale land altitudes based on erosive forces.

        Weak erosion (negative bias) = terrain hasn't been worn down → peaks stay
        tall, average altitude rises.  Strong erosion (positive bias) = terrain
        has been smoothed → peaks lower, average altitude drops.

        Args:
            erosive_forces (float): Bias value; negative = weak/rough, positive = strong/smooth.
        """
        # erosive_forces is the target rocky fraction (0.10 = strong/smooth, 0.30 = weak/rough).
        # Centre at 0.20: below that → lower terrain, above → taller terrain.
        # Range 0.10–0.30 maps to scale 0.80–1.20 (±20% at extremes).
        scale = 1.0 + (erosive_forces - 0.20) * 2.0
        scale = max(0.7, min(1.3, scale))

        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.is_land():
                    tile.altitude = int(max(0, min(3500, tile.altitude * scale)))

    def _generate_rockiness(self, rock_noise, erosive_forces=0.0):
        """Generate rockiness levels for all land tiles.

        Uses independent noise blended with altitude to produce geographically
        clustered rocky terrain.  Higher altitude increases the chance of rocky
        tiles; the clustering comes from two smoothing passes so rocky zones
        spread naturally rather than appearing as isolated specks.

        Rockiness is generated BEFORE rainfall so the moisture classifier in
        _generate_rainfall can apply a dryness penalty to rocky tiles.

        Args:
            rock_noise: 2D array of random values (0.0–1.0), independent of
                        the altitude noise to provide genuine variety.
            erosive_forces (float): Bias added to the rocky threshold.
                Positive → fewer rocky tiles (strong erosion = smooth terrain).
                Negative → more rocky tiles (weak erosion = rough terrain).
        """
        print(f"\n=== GENERATING ROCKINESS (erosive_bias={erosive_forces:.3f}) ===")

        # Step 1: Compute raw score for each land tile.
        #   noise component   (65%) — provides variety independent of altitude
        #   altitude component (35%) — higher ground is more likely to be rocky
        score = [[0.0] * self.width for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.is_ocean():
                    continue
                alt_factor = tile.altitude / 3500.0  # 0 (sea level) → 1 (peak)
                score[y][x] = rock_noise[y][x] * 0.65 + alt_factor * 0.35

        # Step 2: Two passes of neighbor-averaging for geographic clustering.
        #   Tiles influence their neighbours so rocky zones clump together
        #   rather than scattering randomly across the map.
        for _ in range(2):
            new_score = [row[:] for row in score]
            for y in range(self.height):
                for x in range(self.width):
                    if self.tiles[y][x].is_ocean():
                        continue
                    neighbors = []
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue  # Exclude center tile from neighbor average
                            nx = (x + dx) % self.width
                            ny = y + dy
                            if 0 <= ny < self.height and self.tiles[ny][nx].is_land():
                                neighbors.append(score[ny][nx])
                    if neighbors:
                        # 70 % own score, 30 % neighbor average — enough smoothing to
                        # cluster rocky zones without collapsing the variance entirely.
                        new_score[y][x] = score[y][x] * 0.7 + (sum(neighbors) / len(neighbors)) * 0.3
            score = new_score

        # Step 3: Percentile-based classification.
        #   erosive_forces is the TARGET fraction of land tiles that should be rocky
        #   (e.g. 0.20 = exactly 20 %).  Using a percentile threshold guarantees the
        #   output matches the target regardless of how smoothing compressed the scores.
        #   Rolling fraction is fixed at 35 % of land tiles.
        rolling_fraction = 0.35
        rocky_fraction   = erosive_forces  # e.g. 0.20 for average

        land_scores = sorted(
            score[y][x]
            for y in range(self.height)
            for x in range(self.width)
            if self.tiles[y][x].is_land()
        )
        n = len(land_scores)
        if n > 0:
            rocky_threshold  = land_scores[max(0, int(n * (1.0 - rocky_fraction)) - 1)]
            rolling_threshold = land_scores[max(0, int(n * (1.0 - rocky_fraction - rolling_fraction)) - 1)]
        else:
            rocky_threshold  = 0.99
            rolling_threshold = 0.99

        flat_count = rolling_count = rocky_count = 0
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.is_ocean():
                    tile.rockiness = 0
                    continue
                s = score[y][x]
                if s >= rocky_threshold:
                    tile.rockiness = 2   # Rocky
                    rocky_count += 1
                elif s >= rolling_threshold:
                    tile.rockiness = 1   # Rolling
                    rolling_count += 1
                else:
                    tile.rockiness = 0   # Flat
                    flat_count += 1

        land_total = flat_count + rolling_count + rocky_count
        if land_total:
            print(f"  Flat: {flat_count} ({flat_count*100//land_total}%)  "
                  f"Rolling: {rolling_count} ({rolling_count*100//land_total}%)  "
                  f"Rocky: {rocky_count} ({rocky_count*100//land_total}%)")
        print("=== ROCKINESS GENERATION COMPLETE ===\n")

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
                    'rainfall': tile.rainfall,
                    'rockiness': tile.rockiness,
                    'fungus': tile.fungus,
                    'river_edges': list(tile.river_edges)
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
                tile.altitude = tile_data.get('altitude', 0)    # Default to 0 for old saves
                tile.rainfall = tile_data.get('rainfall', 1)    # Default to moderate for old saves
                tile.rockiness = tile_data.get('rockiness', 0)  # Default to flat for old saves
                tile.fungus = tile_data.get('fungus', False)    # Default to no fungus for old saves
                tile.river_edges = set(tile_data.get('river_edges', []))
                row.append(tile)
            game_map.tiles.append(row)

        return game_map