# map.py
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
        self.displayed_unit_index = 0  # Which unit in stack to display

    def is_land(self):
        """Check if this tile is land terrain."""
        return self.terrain_type == 'land'

    def is_ocean(self):
        """Check if this tile is ocean terrain."""
        return self.terrain_type == 'ocean'


class GameMap:
    """Handles map generation and tile management."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []
        self.generate_random_map()

    def generate_random_map(self):
        """Generate a simple random map with land and ocean."""
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Random land/ocean assignment
                terrain = 'land' if random.random() < LAND_PROBABILITY else 'ocean'
                tile = Tile(x, y, terrain)
                row.append(tile)
            self.tiles.append(row)

        # Place supply pods on 3% of tiles
        self._place_supply_pods()

    def _place_supply_pods(self):
        """Place supply pods randomly on 3% of tiles."""
        total_tiles = self.width * self.height
        num_pods = int(total_tiles * 0.03)

        placed = 0
        attempts = 0
        max_attempts = num_pods * 10  # Prevent infinite loop

        while placed < num_pods and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            tile = self.get_tile(x, y)

            if tile and not tile.supply_pod:
                tile.supply_pod = True
                placed += 1

            attempts += 1

        print(f"Placed {placed} supply pods on the map")

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
                    'supply_pod': tile.supply_pod
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
                tile.supply_pod = tile_data['supply_pod']
                row.append(tile)
            game_map.tiles.append(row)

        return game_map