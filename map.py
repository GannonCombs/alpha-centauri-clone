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
from constants import LAND_PROBABILITY


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

    def is_land(self):
        """Check if this tile is land terrain."""
        return self.terrain_type == 'land'

    def is_ocean(self):
        """Check if this tile is ocean terrain."""
        return self.terrain_type == 'ocean'


class GameMap:
    """Handles map generation and tile management."""

    def __init__(self, width, height, ocean_percentage=None):
        """Initialize map with specified dimensions and ocean percentage.

        Args:
            width (int): Map width in tiles
            height (int): Map height in tiles
            ocean_percentage (int): Percentage of ocean tiles (30-90), None for default
        """
        self.width = width
        self.height = height
        self.tiles = []
        # Default to 70% ocean (equivalent to old default of 30% land)
        self.ocean_percentage = ocean_percentage if ocean_percentage is not None else int((1.0 - LAND_PROBABILITY) * 100)
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
                    'monolith': tile.monolith
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
                row.append(tile)
            game_map.tiles.append(row)

        return game_map