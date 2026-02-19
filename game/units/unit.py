# unit.py
"""Unit management system.

This module defines the Unit class representing all mobile units in the game
including military units, colony pods, and transports. Units can move across
the map, garrison in bases, and respect terrain restrictions.
"""


class Unit:
    """Represents a game unit (military, colony pod, former, transport, etc.).

    Units are the primary mobile entities in the game. They can move across
    the map, garrison in friendly bases, and interact with terrain and other units.

    Attributes:
        x (int): X coordinate on the map
        y (int): Y coordinate on the map
        chassis (str): Chassis ID ('infantry', 'foil', 'needlejet', etc.)
        weapon (str): Weapon ID ('hand_weapons', 'laser', 'probe', etc.)
        armor (str): Armor ID ('no_armor', 'synthmetal', etc.)
        reactor (str): Reactor ID ('fission', 'fusion', 'quantum', 'singularity')
        ability1 (str): First special ability ID
        ability2 (str): Second special ability ID
        owner (int): Player ID (0 = human, 1+ = AI)
        name (str): Display name of the unit
        type (str): Derived from chassis ('land', 'sea', or 'air')
        moves_remaining (int): Movement points left this turn
        has_moved (bool): Whether unit has moved this turn
    """

    def __init__(self, x, y, chassis, owner, name, weapon, armor, reactor,
                 ability1='none', ability2='none'):
        """Initialize unit with mandatory components.

        Args:
            x, y: Map coordinates
            chassis: Chassis ID ('infantry', 'foil', 'needlejet', etc.) - REQUIRED
            owner: Player ID - REQUIRED
            name: Display name - REQUIRED
            weapon: Weapon ID ('hand_weapons', 'probe', 'laser', etc.) - REQUIRED
            armor: Armor ID ('no_armor', 'synthmetal', etc.) - REQUIRED
            reactor: Reactor ID ('fission', 'fusion', 'quantum', 'singularity') - REQUIRED
            ability1: First ability ID (default 'none')
            ability2: Second ability ID (default 'none')
        """
        # Validate required components
        if chassis is None:
            raise ValueError("chassis is required")
        if weapon is None:
            raise ValueError("weapon is required")
        if armor is None:
            raise ValueError("armor is required")
        if reactor is None:
            raise ValueError("reactor is required")

        # Store core attributes
        self.x = x
        self.y = y
        self.chassis = chassis
        self.owner = owner
        self.name = name
        self.weapon = weapon
        self.armor = armor
        self.reactor = reactor
        self.ability1 = ability1
        self.ability2 = ability2
        self.has_moved = False
        self.repair_eligible = True  # True if unit skipped its turn entirely (eligible for natural repair)
        self.held = False  # If True, unit won't be auto-cycled for actions

        # Derive reactor level from component data
        reactor_data = self.reactor_data
        self.reactor_level = reactor_data['power']  # 1-4

        # Movement (stored as float to support road/river 1/3-cost fractions)
        self.moves_remaining = float(self.max_moves())
        self.moves_this_turn = 0  # Count of moves made this turn (overflow protection)

        # Health system: max HP = 10 * reactor power
        self.max_health = 10 * self.reactor_level
        self.current_health = self.max_health

        # Morale/Experience
        self.experience = 0
        self.morale_level = 2  # Start at Green
        self.kills = 0
        self.monolith_upgrade = False

        # Artillery capability
        self.has_artillery = False
        self.artillery_mode = False

        # Type-specific systems
        if self.type == 'air':
            self.fuel = 10
            self.max_fuel = 10
            self.operational_range = 2
            self.last_refuel_x = x
            self.last_refuel_y = y
        else:
            self.fuel = None
            self.max_fuel = None
            self.operational_range = None
            self.last_refuel_x = None
            self.last_refuel_y = None

        # Unit support
        self.home_base = None
        self.support_cost = 1

        # Transport system (for sea units)
        if self.type == 'sea':
            self.transport_capacity = 4
            self.loaded_units = []
        else:
            self.transport_capacity = 0
            self.loaded_units = []

        # Special weapon checks
        self.is_probe = (weapon == 'probe')
        self.is_former = (weapon == 'terraforming')
        self.is_cloaked = False  # Runtime cloak status

        # Terraforming state (formers only)
        self.terraforming_action = None   # str key from IMPROVEMENTS, or None
        self.terraforming_turns_left = 0

    @property
    def chassis_data(self):
        """Get full chassis data dictionary."""
        from game.units.unit_components import get_chassis_by_id
        return get_chassis_by_id(self.chassis)

    @property
    def weapon_data(self):
        """Get full weapon data dictionary."""
        from game.units.unit_components import get_weapon_by_id
        return get_weapon_by_id(self.weapon)

    @property
    def armor_data(self):
        """Get full armor data dictionary."""
        from game.units.unit_components import get_armor_by_id
        return get_armor_by_id(self.armor)

    @property
    def reactor_data(self):
        """Get full reactor data dictionary."""
        from game.units.unit_components import get_reactor_by_id
        return get_reactor_by_id(self.reactor)

    @property
    def type(self):
        """Get unit type from chassis ('land', 'sea', or 'air')."""
        return self.chassis_data['type']

    def has_ability(self, ability_id):
        """Check if unit has a specific ability.

        Args:
            ability_id: Ability ID to check for

        Returns:
            bool: True if unit has this ability in either slot
        """
        return self.ability1 == ability_id or self.ability2 == ability_id

    # Legacy property accessors for abilities (for backwards compatibility with existing code)
    def __getattr__(self, name):
        """Dynamic attribute lookup for has_* ability checks."""
        if name.startswith('has_'):
            # Map common ability check patterns to ability IDs
            ability_map = {
                'has_cloaking': 'cloaking',
                'has_drop_pods': 'drop_pods',
                'has_amphibious_pods': 'amphibious',
                'has_clean_reactor': 'clean_reactor',
                'has_aaa_tracking': 'AAA',
                'has_comm_jammer': 'comm_jammer',
                'has_blink_displacer': 'blink',
                'has_empath_song': 'empath',
                'has_fungal_payload': 'fungal_payload'
            }
            if name in ability_map:
                return self.has_ability(ability_map[name])
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def max_moves(self):
        """Return maximum movement points per turn."""
        base_moves = self.chassis_data['speed']

        # Elite units get +1 move
        if hasattr(self, 'morale_level') and self.morale_level >= 7:
            base_moves += 1

        # Antigrav struts modifier
        if self.has_ability('antigrav'):
            if self.type == 'air':
                base_moves += (2*self.reactor_level)
            else:
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

        # Void tiles are not part of the playable map
        if getattr(tile, 'void', False):
            return False

        # Land units can't enter ocean
        if self.type == 'land' and tile.is_ocean():
            return False

        # Sea units can't enter land
        if self.type == 'sea' and tile.is_land():
            return False

        # Air units can go anywhere (future: need bases/carriers to land)

        # Future: check for enemy units, zone of control, etc.
        return True

    def is_colony_pod(self):
        """Check if this unit is a colony pod.

        Returns:
            bool: True if unit is a land or sea colony pod
        """
        return self.weapon == 'colony_pod'

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
        return self.type == 'air'

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

        # Prevent double-loading the same unit
        if unit in self.loaded_units:
            return False

        # Only land units can be loaded onto transports
        if unit.type != 'land':
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
        unit.held = False  # Debarking clears held status set when boarding
        unit.moves_remaining = 0  # Unloading consumes all moves
        return True

    def repair(self, amount):
        """Repair unit by specified amount (capped at max_health).

        Args:
            amount (int): Amount to repair

        Returns:
            int: Actual amount repaired
        """
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - old_health

    def end_turn(self):
        """Reset movement points and flags for a new turn."""
        # Capture heal eligibility before clearing has_moved: unit must not have
        # moved or acted at all this turn to qualify for natural healing next upkeep.
        self.repair_eligible = not self.has_moved
        self.moves_remaining = float(self.max_moves())
        self.moves_this_turn = 0
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
        # Get numeric values from component data
        attack = self.weapon_data.get('attack', 0)
        defense = self.armor_data.get('defense', 0)

        base = f"{attack}-{defense}-{self.max_moves()}"
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
            'chassis': self.chassis,
            'weapon': self.weapon,
            'armor': self.armor,
            'reactor': self.reactor,
            'ability1': self.ability1,
            'ability2': self.ability2,
            'owner': self.owner,
            'name': self.name,
            'moves_remaining': self.moves_remaining,
            'current_health': self.current_health,
            'max_health': self.max_health,
            'morale_level': self.morale_level,
            'experience': self.experience,
            'kills': self.kills,
            'monolith_upgrade': self.monolith_upgrade,
            'has_artillery': self.has_artillery,
            'artillery_mode': self.artillery_mode,
            'fuel': self.fuel,
            'max_fuel': self.max_fuel,
            'operational_range': self.operational_range,
            'last_refuel_x': self.last_refuel_x,
            'last_refuel_y': self.last_refuel_y,
            'home_base_coords': (self.home_base.x, self.home_base.y) if self.home_base else None,
            'support_cost': self.support_cost,
            'transport_capacity': self.transport_capacity,
            'loaded_unit_indices': [id(u) for u in self.loaded_units],
            'is_probe': self.is_probe,
            'is_cloaked': self.is_cloaked,
            'terraforming_action': self.terraforming_action,
            'terraforming_turns_left': self.terraforming_turns_left,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct unit from dictionary.

        Args:
            data (dict): Unit data dictionary

        Returns:
            Unit: Reconstructed unit instance
        """
        # Create unit using new signature
        unit = Unit(
            x=data['x'],
            y=data['y'],
            chassis=data['chassis'],
            owner=data['owner'],
            name=data['name'],
            weapon=data['weapon'],
            armor=data['armor'],
            reactor=data['reactor'],
            ability1=data.get('ability1', 'none'),
            ability2=data.get('ability2', 'none')
        )

        # Restore runtime state
        unit.moves_remaining = float(data['moves_remaining'])
        unit.moves_this_turn = 0  # Reset each session; not persisted
        unit.current_health = data['current_health']
        unit.max_health = data['max_health']
        unit.morale_level = data['morale_level']
        unit.experience = data['experience']
        unit.kills = data['kills']
        unit.monolith_upgrade = data.get('monolith_upgrade', False)
        unit.has_artillery = data.get('has_artillery', False)
        unit.artillery_mode = data.get('artillery_mode', False)
        unit.fuel = data.get('fuel')
        unit.max_fuel = data.get('max_fuel')
        unit.operational_range = data.get('operational_range')
        unit.last_refuel_x = data.get('last_refuel_x')
        unit.last_refuel_y = data.get('last_refuel_y')
        unit.home_base = None  # Reconstructed from base.supported_units
        unit.support_cost = data.get('support_cost', 1)
        unit.transport_capacity = data.get('transport_capacity', 0)
        unit.loaded_units = []  # Reconstructed in game.py
        unit.is_probe = data.get('is_probe', unit.weapon == 'probe')
        unit.is_former = data.get('is_former', unit.weapon == 'terraforming')
        unit.is_cloaked = data.get('is_cloaked', False)
        unit.terraforming_action = data.get('terraforming_action', None)
        unit.terraforming_turns_left = data.get('terraforming_turns_left', 0)
        unit.has_moved = False  # Reset per-turn state

        return unit