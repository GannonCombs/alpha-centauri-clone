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
        self.unit = None
        self.base = None
        self.supply_pod = False  # Unity supply pods

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
        """Get unit at a tile position, if any."""
        tile = self.get_tile(x, y)
        return tile.unit if tile else None

    def set_unit_at(self, x, y, unit):
        """Place a unit on a tile."""
        tile = self.get_tile(x, y)
        if tile:
            tile.unit = unit