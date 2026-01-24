# unit.py
"""Unit management system.

This module defines the Unit class representing all mobile units in the game
including military units, colony pods, and transports. Units can move across
the map, garrison in bases, and respect terrain restrictions.
"""
from constants import UNIT_LAND, UNIT_SEA, UNIT_AIR, UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA


class Unit:
    """Represents a game unit (military, colony pod, former, transport, etc.).

    Units are the primary mobile entities in the game. They can move across
    the map, garrison in friendly bases, and interact with terrain and other units.

    Attributes:
        x (int): X coordinate on the map
        y (int): Y coordinate on the map
        unit_type (str): Type constant (UNIT_LAND, UNIT_SEA, UNIT_AIR, etc.)
        owner (int): Player ID (0 = human, 1+ = AI)
        name (str): Display name of the unit
        moves_remaining (int): Movement points left this turn
        has_moved (bool): Whether unit has moved this turn
    """

    def __init__(self, x, y, unit_type, owner, name="Unit"):
        """Initialize a new unit.

        Args:
            x (int): Starting X coordinate
            y (int): Starting Y coordinate
            unit_type (str): Unit type constant
            owner (int): Player ID (0 = human, 1+ = AI)
            name (str, optional): Display name. Defaults to "Unit".
        """
        self.x = x
        self.y = y
        self.unit_type = unit_type  # UNIT_LAND, UNIT_SEA, or UNIT_AIR
        self.owner = owner  # Player ID (0 = human, 1+ = AI)
        self.name = name
        self.moves_remaining = self.max_moves()
        self.has_moved = False

        # Set unit stats based on type (weapon-armor-moves*reactor_level)
        if unit_type == UNIT_COLONY_POD_LAND:
            self.weapon = 0
            self.armor = 1
            self.reactor_level = 1  # Reactor value (d in a-b-c*d format)
        elif unit_type == UNIT_COLONY_POD_SEA:
            self.weapon = 0
            self.armor = 1
            self.reactor_level = 1
        elif unit_type == UNIT_LAND:
            self.weapon = 1
            self.armor = 1
            self.reactor_level = 1
        elif unit_type == UNIT_SEA:
            self.weapon = 1
            self.armor = 1
            self.reactor_level = 1
        elif unit_type == UNIT_AIR:
            self.weapon = 1
            self.armor = 1
            self.reactor_level = 1
        else:
            # Default for unknown types
            self.weapon = 1
            self.armor = 1
            self.reactor_level = 1

        # Health system: max HP = 10 * reactor_level
        self.max_health = 10 * self.reactor_level
        self.current_health = self.max_health

    def max_moves(self):
        """Return maximum movement points per turn.

        Returns:
            int: Movement points available each turn
        """
        # Air units have 10 moves, sea units have 4, land units have 1
        if self.unit_type == UNIT_AIR:
            return 10
        elif self.unit_type in [UNIT_SEA, UNIT_COLONY_POD_SEA]:
            return 4
        return 1

    def can_move_to(self, tile):
        """Check if this unit can legally move to a tile.

        Validates movement based on terrain type, movement points, and unit type.

        Args:
            tile (Tile): Target tile to move to

        Returns:
            bool: True if move is legal, False otherwise
        """
        if self.moves_remaining <= 0:
            return False

        # Land units and land colony pods can't enter ocean
        if self.unit_type in [UNIT_LAND, UNIT_COLONY_POD_LAND] and tile.is_ocean():
            return False

        # Sea units and sea colony pods can't enter land
        if self.unit_type in [UNIT_SEA, UNIT_COLONY_POD_SEA] and tile.is_land():
            return False

        # Air units can go anywhere (future: need bases/carriers to land)

        # Future: check for enemy units, zone of control, etc.
        return True

    def is_colony_pod(self):
        """Check if this unit is a colony pod.

        Returns:
            bool: True if unit is a land or sea colony pod
        """
        return self.unit_type in [UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA]

    def move_to(self, x, y):
        """Move unit to new position and consume movement points.

        Args:
            x (int): Target X coordinate
            y (int): Target Y coordinate
        """
        self.x = x
        self.y = y
        self.moves_remaining -= 1
        self.has_moved = True

    def end_turn(self):
        """Reset movement points and flags for a new turn."""
        self.moves_remaining = self.max_moves()
        self.has_moved = False

    def is_friendly(self, player_id):
        """Check if unit belongs to given player.

        Args:
            player_id (int): Player ID to check against

        Returns:
            bool: True if unit is owned by the specified player
        """
        return self.owner == player_id

    def get_stats_string(self):
        """Get stats string in format: weapon-armor-moves or weapon-armor-moves*reactor_level.

        Returns:
            str: Stats string (e.g., "1-1-1", "1-1-4*2", "0-1-1")
        """
        base = f"{self.weapon}-{self.armor}-{self.max_moves()}"
        if self.reactor_level > 1:
            return f"{base}*{self.reactor_level}"
        return base

    def take_damage(self, damage):
        """Reduce unit health by damage amount.

        Args:
            damage (int): Amount of damage to apply (1-3 points per hit)

        Returns:
            bool: True if unit is destroyed (health <= 0)
        """
        self.current_health -= damage
        return self.current_health <= 0

    def is_destroyed(self):
        """Check if unit is destroyed.

        Returns:
            bool: True if current_health <= 0
        """
        return self.current_health <= 0

    def get_health_percentage(self):
        """Get health as percentage for UI display.

        Returns:
            float: Health percentage (0.0 to 1.0)
        """
        if self.max_health <= 0:
            return 0.0
        return max(0.0, min(1.0, self.current_health / self.max_health))

    def get_health_color(self):
        """Get health bar color based on current health percentage.

        Returns:
            tuple: RGB color (green=80-100%, yellow=50-79%, red=0-49%)
        """
        pct = self.get_health_percentage()
        if pct >= 0.8:
            return (0, 255, 0)  # Green
        elif pct >= 0.5:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red