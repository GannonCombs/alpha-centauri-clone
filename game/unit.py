# unit.py
"""Unit management system.

This module defines the Unit class representing all mobile units in the game
including military units, colony pods, and transports. Units can move across
the map, garrison in bases, and respect terrain restrictions.
"""
from game.data.constants import UNIT_LAND, UNIT_SEA, UNIT_AIR, UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA, UNIT_ARTIFACT, UNIT_PROBE_TEAM


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

    def __init__(self, x, y, unit_type, owner, name="Unit", chassis_speed=None, weapon=None, armor=None, reactor_level=None):
        """Initialize a new unit.

        Args:
            x (int): Starting X coordinate
            y (int): Starting Y coordinate
            unit_type (str): Unit type constant
            owner (int): Player ID (0 = human, 1+ = AI)
            name (str, optional): Display name. Defaults to "Unit".
            chassis_speed (int, optional): Movement points from chassis. If None, uses default.
            weapon (int, optional): Weapon strength. If None, uses default.
            armor (int, optional): Armor strength. If None, uses default.
            reactor_level (int, optional): Reactor level. If None, uses default.
        """
        self.x = x
        self.y = y
        self.unit_type = unit_type  # UNIT_LAND, UNIT_SEA, or UNIT_AIR
        self.owner = owner  # Player ID (0 = human, 1+ = AI)
        self.name = name
        self.chassis_speed = chassis_speed  # Store chassis speed separately
        self.has_moved = False
        self.held = False  # If True, unit won't be auto-cycled for actions

        # Set unit stats based on type (weapon-armor-moves*reactor_level)
        if unit_type == UNIT_COLONY_POD_LAND:
            self.weapon = weapon if weapon is not None else 0
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'noncombat'
            self.armor_mode = 'projectile'
        elif unit_type == UNIT_COLONY_POD_SEA:
            self.weapon = weapon if weapon is not None else 0
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'noncombat'
            self.armor_mode = 'projectile'
        elif unit_type == UNIT_LAND:
            self.weapon = weapon if weapon is not None else 1
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'projectile'  # Hand weapons (projectile)
            self.armor_mode = 'projectile'   # No armor (projectile)
        elif unit_type == UNIT_SEA:
            self.weapon = weapon if weapon is not None else 1
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'projectile'
            self.armor_mode = 'projectile'
        elif unit_type == UNIT_AIR:
            self.weapon = weapon if weapon is not None else 1
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'missile'     # Air units default to missile
            self.armor_mode = 'projectile'
        elif unit_type == UNIT_ARTIFACT:
            self.weapon = weapon if weapon is not None else 0
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'noncombat'
            self.armor_mode = 'projectile'
        elif unit_type == UNIT_PROBE_TEAM:
            self.weapon = weapon if weapon is not None else 0
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'noncombat'
            self.armor_mode = 'projectile'
        else:
            # Default for unknown types
            self.weapon = weapon if weapon is not None else 1
            self.armor = armor if armor is not None else 1
            self.reactor_level = reactor_level if reactor_level is not None else 1
            self.weapon_mode = 'projectile'
            self.armor_mode = 'projectile'

        self.moves_remaining = self.max_moves()

        # Health system: max HP = 10 * reactor_level
        self.max_health = 10 * self.reactor_level
        self.current_health = self.max_health

        # Morale/Experience system
        self.experience = 0
        self.morale_level = 2  # Start at Green (0=Very Very Green, 1=Very Green, 2=Green, 3=Disciplined, 4=Hardened, 5=Veteran, 6=Commando, 7=Elite)
        self.kills = 0  # Track total kills for promotion logic
        self.monolith_upgrade = False  # Has this unit received a monolith morale upgrade?

        # Artillery capability
        self.has_artillery = False  # Set to True for artillery units
        self.artillery_mode = False  # Toggle for artillery firing mode

        # Air unit fuel system (for UNIT_AIR only)
        if self.unit_type == UNIT_AIR:
            self.fuel = 10             # Remaining fuel
            self.max_fuel = 10         # Maximum fuel capacity
            self.operational_range = 2  # Turns from base/airbase
            self.last_refuel_x = x     # Last refuel location
            self.last_refuel_y = y
        else:
            self.fuel = None
            self.max_fuel = None
            self.operational_range = None
            self.last_refuel_x = None
            self.last_refuel_y = None

        # Unit support system
        self.home_base = None       # Base that supports this unit
        self.support_cost = 1       # Minerals per turn (default 1)

        # Probe team system
        self.is_probe = (unit_type == UNIT_PROBE_TEAM)

        # Transport system (for sea units carrying land units)
        if self.unit_type == UNIT_SEA:
            self.transport_capacity = 4  # Can carry 4 land units
            self.loaded_units = []       # Units currently loaded
        else:
            self.transport_capacity = 0
            self.loaded_units = []

        # Special abilities
        self.has_cloaking = False           # Invisible to enemies until attacking
        self.is_cloaked = False             # Current cloak status
        self.has_drop_pods = False          # Can drop from orbit/air to any tile
        self.has_amphibious_pods = False    # Can attack from sea
        self.has_clean_reactor = False      # No support cost
        self.has_aaa_tracking = False       # +100% vs air units
        self.has_comm_jammer = False        # -50% enemy defense
        self.has_blink_displacer = False    # Ignores base defenses
        self.has_empath_song = False        # +50% vs psi
        self.has_fungal_payload = False     # Creates fungus on impact

    def max_moves(self):
        """Return maximum movement points per turn.

        Returns:
            int: Movement points available each turn
        """
        # Use chassis_speed if set, otherwise use default based on unit_type
        if hasattr(self, 'chassis_speed') and self.chassis_speed is not None:
            base_moves = self.chassis_speed
        else:
            # Fallback for units created without chassis_speed
            base_moves = 1
            if self.unit_type == UNIT_AIR:
                base_moves = 10
            elif self.unit_type in [UNIT_SEA, UNIT_COLONY_POD_SEA]:
                base_moves = 4

        # Elite units get +1 move (backward compatibility check)
        if hasattr(self, 'morale_level') and self.morale_level >= 7:  # Elite
            base_moves += 1

        return base_moves

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

        # Land units, land colony pods, and artifacts can't enter ocean
        if self.unit_type in [UNIT_LAND, UNIT_COLONY_POD_LAND, UNIT_ARTIFACT] and tile.is_ocean():
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

    def can_artillery_fire_at(self, target_x, target_y):
        """Check if this unit can fire artillery at target coordinates.

        Args:
            target_x (int): Target X coordinate
            target_y (int): Target Y coordinate

        Returns:
            bool: True if target is within artillery range (2 squares)
        """
        if not hasattr(self, 'has_artillery') or not self.has_artillery:
            return False

        # Calculate distance (max of dx and dy for square grid)
        dx = abs(target_x - self.x)
        dy = abs(target_y - self.y)
        distance = max(dx, dy)

        # Artillery range is 2 squares, can't fire at self
        return 1 <= distance <= 2

    def is_air_unit(self):
        """Check if this is an air unit.

        Returns:
            bool: True if unit is an air unit
        """
        return self.unit_type == UNIT_AIR

    def consume_fuel(self, amount=1):
        """Consume fuel for movement (air units only).

        Args:
            amount (int): Amount of fuel to consume (default 1)

        Returns:
            bool: True if fuel was consumed, False if no fuel system
        """
        if not self.is_air_unit() or self.fuel is None:
            return False

        self.fuel = max(0, self.fuel - amount)
        return True

    def refuel(self, x=None, y=None):
        """Refuel at a base or airbase (air units only).

        Args:
            x (int): X coordinate of refuel location (optional)
            y (int): Y coordinate of refuel location (optional)
        """
        if not self.is_air_unit():
            return

        self.fuel = self.max_fuel
        if x is not None and y is not None:
            self.last_refuel_x = x
            self.last_refuel_y = y

    def is_out_of_fuel(self):
        """Check if air unit is out of fuel.

        Returns:
            bool: True if fuel is depleted
        """
        if not self.is_air_unit():
            return False

        return self.fuel is not None and self.fuel <= 0

    def can_reach_refuel_point(self, game_map, bases):
        """Check if unit can reach a refuel point (base or airbase).

        Args:
            game_map: GameMap instance
            bases: List of all bases

        Returns:
            bool: True if a refuel point is reachable
        """
        if not self.is_air_unit() or self.fuel is None:
            return True  # Non-air units always return True

        # Check distance to nearest friendly base
        min_distance = float('inf')
        for base in bases:
            if base.owner == self.owner:
                dx = abs(base.x - self.x)
                dy = abs(base.y - self.y)
                distance = max(dx, dy)  # Chebyshev distance
                min_distance = min(min_distance, distance)

        # TODO: Also check for airbases when terrain improvements are implemented

        # Can we reach it with current fuel?
        return self.fuel >= min_distance

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

        # Air units consume fuel when moving
        if self.is_air_unit():
            self.consume_fuel(1)

        # Move loaded units with transport
        if hasattr(self, 'loaded_units'):
            for unit in self.loaded_units:
                unit.x = x
                unit.y = y

    def can_load_unit(self, unit):
        """Check if this transport can load another unit.

        Args:
            unit (Unit): Unit to check if it can be loaded

        Returns:
            bool: True if unit can be loaded
        """
        if self.transport_capacity == 0:
            return False

        if len(self.loaded_units) >= self.transport_capacity:
            return False

        # Only land units can be loaded onto transports
        if unit.unit_type not in [UNIT_LAND, UNIT_COLONY_POD_LAND]:
            return False

        return True

    def load_unit(self, unit):
        """Load a unit onto this transport.

        Args:
            unit (Unit): Unit to load

        Returns:
            bool: True if unit was successfully loaded
        """
        if not self.can_load_unit(unit):
            return False

        self.loaded_units.append(unit)
        # Unit's position will be updated to match transport in game logic
        return True

    def unload_unit(self, unit, x, y):
        """Unload a unit from this transport.

        Args:
            unit (Unit): Unit to unload
            x (int): X coordinate to unload to
            y (int): Y coordinate to unload to

        Returns:
            bool: True if unit was successfully unloaded
        """
        if unit not in self.loaded_units:
            return False

        self.loaded_units.remove(unit)
        unit.x = x
        unit.y = y
        unit.moves_remaining = 0  # Unloading consumes all moves
        return True

    def can_heal(self, in_friendly_base=False):
        """Check if unit can heal.

        Args:
            in_friendly_base (bool): Whether unit is in a friendly base

        Returns:
            tuple: (can_heal, heal_amount, reason) - reason is string explaining why/why not
        """
        # Can't heal if at full health
        if self.current_health >= self.max_health:
            return (False, 0, "Already at full health")

        # Can't heal if unit moved this turn
        if self.has_moved:
            return (False, 0, "Unit has moved this turn")

        # In base: can heal 20% per turn, can reach full health
        if in_friendly_base:
            heal_amount = max(1, int(self.max_health * 0.20))
            return (True, heal_amount, f"Healing {heal_amount} HP in base")

        # In field: can heal 10% per turn, but only up to 80% health
        current_pct = self.current_health / self.max_health
        if current_pct >= 0.80:
            return (False, 0, "Can only heal to 80% in field")

        heal_amount = max(1, int(self.max_health * 0.10))
        return (True, heal_amount, f"Healing {heal_amount} HP")

    def heal(self, amount):
        """Heal unit by specified amount (capped at max_health).

        Args:
            amount (int): Amount to heal

        Returns:
            int: Actual amount healed
        """
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - old_health

    def end_turn(self):
        """Reset movement points and flags for a new turn."""
        self.moves_remaining = self.max_moves()
        self.has_moved = False

        # Note: Refueling happens in game logic, not here
        # (game checks if unit is at base/airbase and calls refuel())

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

    def get_morale_name(self):
        """Get morale level as string.

        Returns:
            str: Morale level name
        """
        # Backward compatibility - initialize if missing
        if not hasattr(self, 'morale_level'):
            self.morale_level = 2  # Green
            self.experience = 0
            self.kills = 0

        morale_names = [
            "Very Very Green",  # 0
            "Very Green",       # 1
            "Green",            # 2
            "Disciplined",      # 3
            "Hardened",         # 4
            "Veteran",          # 5
            "Commando",         # 6
            "Elite"             # 7
        ]
        if 0 <= self.morale_level < len(morale_names):
            return morale_names[self.morale_level]
        return "Unknown"

    def gain_experience(self, amount):
        """Gain experience and check for promotion.

        Args:
            amount (int): Amount of XP to gain
        """
        # Backward compatibility
        if not hasattr(self, 'experience'):
            self.morale_level = 2
            self.experience = 0
            self.kills = 0

        self.experience += amount
        self._check_promotion()

    def record_kill(self):
        """Record a kill and gain experience.

        Special rule: Units below Disciplined (morale < 3) automatically
        promote on their first kill.
        """
        # Backward compatibility
        if not hasattr(self, 'kills'):
            self.morale_level = 2
            self.experience = 0
            self.kills = 0

        self.kills += 1

        # Special rule: below Disciplined, first kill = auto-promote
        if self.morale_level < 3:  # Very Very Green, Very Green, or Green
            self.morale_level += 1
            print(f"{self.name} promoted to {self.get_morale_name()} (first kill)")
        else:
            # Normal XP gain
            self.gain_experience(10)  # Arbitrary XP amount for kill

    def _check_promotion(self):
        """Check if unit has enough XP to promote."""
        # XP thresholds for each level (after Disciplined)
        # These are somewhat arbitrary - adjust as needed
        thresholds = {
            3: 0,    # Disciplined (starting point after auto-promotions)
            4: 20,   # Hardened
            5: 50,   # Veteran
            6: 100,  # Commando
            7: 200   # Elite
        }

        # Check if we've reached next threshold
        if self.morale_level < 7:  # Not yet Elite
            next_level = self.morale_level + 1
            if next_level in thresholds and self.experience >= thresholds[next_level]:
                old_morale = self.get_morale_name()
                self.morale_level = next_level
                print(f"{self.name} promoted from {old_morale} to {self.get_morale_name()}!")

    def to_dict(self):
        """Serialize unit to dictionary.

        Returns:
            dict: Unit data as dictionary
        """
        return {
            'x': self.x,
            'y': self.y,
            'unit_type': self.unit_type,
            'owner': self.owner,
            'name': self.name,
            'moves_remaining': self.moves_remaining,
            'chassis_speed': getattr(self, 'chassis_speed', None),
            'weapon': self.weapon,
            'armor': self.armor,
            'reactor_level': self.reactor_level,
            'current_health': self.current_health,
            'max_health': self.max_health,
            'morale_level': self.morale_level,
            'experience': self.experience,
            'kills': self.kills,
            'weapon_mode': self.weapon_mode,
            'armor_mode': self.armor_mode,
            'monolith_upgrade': self.monolith_upgrade,
            'has_artillery': getattr(self, 'has_artillery', False),
            'artillery_mode': getattr(self, 'artillery_mode', False),
            'fuel': getattr(self, 'fuel', None),
            'max_fuel': getattr(self, 'max_fuel', None),
            'operational_range': getattr(self, 'operational_range', None),
            'last_refuel_x': getattr(self, 'last_refuel_x', None),
            'last_refuel_y': getattr(self, 'last_refuel_y', None),
            'home_base_coords': (self.home_base.x, self.home_base.y) if self.home_base else None,
            'support_cost': getattr(self, 'support_cost', 1),
            'transport_capacity': getattr(self, 'transport_capacity', 0),
            'loaded_unit_indices': [id(u) for u in getattr(self, 'loaded_units', [])],  # Will be resolved in game.py
            'has_cloaking': getattr(self, 'has_cloaking', False),
            'is_cloaked': getattr(self, 'is_cloaked', False),
            'has_drop_pods': getattr(self, 'has_drop_pods', False),
            'has_amphibious_pods': getattr(self, 'has_amphibious_pods', False),
            'has_clean_reactor': getattr(self, 'has_clean_reactor', False),
            'has_aaa_tracking': getattr(self, 'has_aaa_tracking', False),
            'has_comm_jammer': getattr(self, 'has_comm_jammer', False),
            'has_blink_displacer': getattr(self, 'has_blink_displacer', False),
            'has_empath_song': getattr(self, 'has_empath_song', False),
            'has_fungal_payload': getattr(self, 'has_fungal_payload', False)
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct unit from dictionary.

        Args:
            data (dict): Unit data dictionary

        Returns:
            Unit: Reconstructed unit instance
        """
        unit = cls.__new__(cls)

        # Copy all attributes from data dict
        unit.x = data['x']
        unit.y = data['y']
        unit.unit_type = data['unit_type']
        unit.owner = data['owner']
        unit.name = data['name']
        unit.moves_remaining = data['moves_remaining']
        unit.chassis_speed = data.get('chassis_speed', None)
        unit.weapon = data['weapon']
        unit.armor = data['armor']
        unit.reactor_level = data['reactor_level']
        unit.current_health = data['current_health']
        unit.max_health = data['max_health']
        unit.morale_level = data['morale_level']
        unit.experience = data['experience']
        unit.kills = data['kills']
        unit.weapon_mode = data['weapon_mode']
        unit.armor_mode = data['armor_mode']
        unit.monolith_upgrade = data.get('monolith_upgrade', False)
        unit.has_artillery = data.get('has_artillery', False)
        unit.artillery_mode = data.get('artillery_mode', False)
        unit.fuel = data.get('fuel', None)
        unit.max_fuel = data.get('max_fuel', None)
        unit.operational_range = data.get('operational_range', None)
        unit.last_refuel_x = data.get('last_refuel_x', None)
        unit.last_refuel_y = data.get('last_refuel_y', None)
        unit.home_base = None  # Will be reconstructed from base.supported_units
        unit.support_cost = data.get('support_cost', 1)
        unit.transport_capacity = data.get('transport_capacity', 0)
        unit.loaded_units = []  # Will be reconstructed in game.py from loaded_unit_indices
        unit.is_probe = data.get('is_probe', unit.unit_type == UNIT_PROBE_TEAM)

        # Special abilities
        unit.has_cloaking = data.get('has_cloaking', False)
        unit.is_cloaked = data.get('is_cloaked', False)
        unit.has_drop_pods = data.get('has_drop_pods', False)
        unit.has_amphibious_pods = data.get('has_amphibious_pods', False)
        unit.has_clean_reactor = data.get('has_clean_reactor', False)
        unit.has_aaa_tracking = data.get('has_aaa_tracking', False)
        unit.has_comm_jammer = data.get('has_comm_jammer', False)
        unit.has_blink_displacer = data.get('has_blink_displacer', False)
        unit.has_empath_song = data.get('has_empath_song', False)
        unit.has_fungal_payload = data.get('has_fungal_payload', False)

        # Reset per-turn state
        unit.has_moved = False

        return unit