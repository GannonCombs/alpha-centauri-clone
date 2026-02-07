# territory.py
"""Territory control system.

Territory extends 7 tiles from each base and is visualized with dotted
borders in the owning player's color. Tiles are assigned to the closest
base, with ties resolved by various criteria.
"""


class TerritoryManager:
    """Manages territory control across the map.

    Territory is calculated based on proximity to bases. Each tile belongs
    to the owner of the nearest base within 7 tiles. Ties are resolved by:
    1. If same owner, assign to that owner
    2. If different owners, leave neutral
    3. Secondary tiebreaker: base with higher population wins

    Attributes:
        game_map (GameMap): Reference to the game map
        territory_map (dict): Maps (x, y) to owner_id or None
    """

    def __init__(self, game_map):
        """Initialize territory manager.

        Args:
            game_map (GameMap): The game map
        """
        self.game_map = game_map
        self.territory_map = {}  # (x, y) -> owner_id or None for neutral

    def update_territory(self, bases):
        """Recalculate all territory based on current bases.

        Args:
            bases (list): List of all bases in the game
        """
        # Reset territory map
        self.territory_map = {}

        # Calculate for each tile
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                owner = self._calculate_tile_owner(x, y, bases)
                if owner is not None:
                    self.territory_map[(x, y)] = owner

    def _calculate_tile_owner(self, x, y, bases):
        """Calculate which player owns a specific tile.

        Args:
            x (int): Tile X coordinate
            y (int): Tile Y coordinate
            bases (list): List of all bases

        Returns:
            int or None: Owner player_id, or None if neutral/unclaimed
        """
        if not bases:
            return None

        # Find all bases within 7 tiles
        candidates = []
        for base in bases:
            dist = self._manhattan_distance(x, y, base.x, base.y)
            if dist <= 7:
                candidates.append((dist, base))

        if not candidates:
            return None

        # Find minimum distance
        min_dist = min(c[0] for c in candidates)
        closest_bases = [c[1] for c in candidates if c[0] == min_dist]

        # Single closest base - clear ownership
        if len(closest_bases) == 1:
            return closest_bases[0].owner

        # Multiple bases at same distance - check if same owner
        owners = set(base.owner for base in closest_bases)
        if len(owners) == 1:
            # All same owner
            return list(owners)[0]

        # Different owners at same distance - use multiple tiebreakers
        # Tiebreaker 1: base with higher population wins
        closest_bases.sort(key=lambda b: (b.population, -b.x, -b.y), reverse=True)
        if closest_bases[0].population > closest_bases[1].population:
            return closest_bases[0].owner

        # Tiebreaker 2: Use coordinate-based hash for deterministic but fair distribution
        # This ensures ties are resolved consistently but distributes tiles fairly
        # Use a hash of tile coordinates to pick a base deterministically
        hash_val = (x * 73856093) ^ (y * 19349663)  # Prime number hash
        winner_idx = hash_val % len(closest_bases)
        return closest_bases[winner_idx].owner

    def _manhattan_distance(self, x1, y1, x2, y2):
        """Calculate Manhattan distance between two points with horizontal wrapping.

        Args:
            x1, y1 (int): First point coordinates
            x2, y2 (int): Second point coordinates

        Returns:
            int: Manhattan distance
        """
        dx = abs(x2 - x1)
        # Account for horizontal wrapping - take shortest path
        map_width = self.game_map.width
        if dx > map_width // 2:
            dx = map_width - dx
        dy = abs(y2 - y1)
        return dx + dy

    def get_tile_owner(self, x, y):
        """Get the owner of a specific tile.

        Args:
            x (int): Tile X coordinate
            y (int): Tile Y coordinate

        Returns:
            int or None: Owner player_id, or None if neutral
        """
        return self.territory_map.get((x, y), None)

    def is_border_tile(self, x, y):
        """Check if a tile is on a territory border.

        A tile is on a border if any adjacent tile has a different owner.

        Args:
            x (int): Tile X coordinate
            y (int): Tile Y coordinate

        Returns:
            bool: True if tile is on a border
        """
        owner = self.get_tile_owner(x, y)
        if owner is None:
            return False

        # Check all 4 cardinal directions
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            nx = (x + dx) % self.game_map.width  # Wrap X
            ny = y + dy
            # Y doesn't wrap - skip if out of bounds
            if ny < 0 or ny >= self.game_map.height:
                continue

            neighbor_owner = self.get_tile_owner(nx, ny)
            if neighbor_owner != owner:
                return True

        return False

    def get_border_edges(self, x, y):
        """Get which edges of a tile are borders.

        Returns a list of edges that border different territory.

        Args:
            x (int): Tile X coordinate
            y (int): Tile Y coordinate

        Returns:
            list: List of edge directions ('N', 'E', 'S', 'W')
        """
        owner = self.get_tile_owner(x, y)
        if owner is None:
            return []

        edges = []
        directions = [('N', 0, -1), ('E', 1, 0), ('S', 0, 1), ('W', -1, 0)]

        for edge, dx, dy in directions:
            nx = (x + dx) % self.game_map.width  # Wrap X
            ny = y + dy
            # Y doesn't wrap - check for map edge
            if ny < 0 or ny >= self.game_map.height:
                # Map edge (top or bottom)
                edges.append(edge)
                continue

            neighbor_owner = self.get_tile_owner(nx, ny)
            if neighbor_owner != owner:
                edges.append(edge)

        return edges
