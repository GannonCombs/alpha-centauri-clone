"""Unit repair and healing system.

This module implements the full SMAC repair formula including:
- Base 10% healing with additive bonuses
- Terrain and facility bonuses
- Full repair facilities (Command Center, Naval Yard, etc.)
- Special cases (Nano Factory, Monoliths)
- 80% healing cap in field, 100% in bases
"""


def calculate_healing(unit, game):
    """Calculate healing amount for a unit at end of turn.

    Args:
        unit (Unit): Unit to heal
        game (Game): Game instance (for checking map, bases, facilities)

    Returns:
        tuple: (can_heal, heal_amount, reason, is_full_repair)
            - can_heal (bool): Whether unit can heal
            - heal_amount (int): Amount of HP to heal
            - reason (str): Explanation of healing calculation
            - is_full_repair (bool): Whether this is a full instant repair
    """
    # Can't heal if at full health
    if unit.current_health >= unit.max_health:
        return (False, 0, "Already at full health", False)

    # Can't heal unless the unit skipped its entire previous turn
    if not getattr(unit, 'heal_eligible', True):
        return (False, 0, "Unit moved or acted this turn", False)

    # Get tile info
    tile = game.game_map.get_tile(unit.x, unit.y)
    if not tile:
        return (False, 0, "Invalid position", False)

    # Check for instant full repair from Monolith
    if tile.monolith:
        heal_amount = unit.max_health - unit.current_health
        return (True, heal_amount, "Monolith: Instant full repair", True)

    # Check if unit is in a friendly base
    at_base = tile.base and tile.base.owner == unit.owner
    base = tile.base if at_base else None

    # Check for Nano Factory (full repair anywhere)
    has_nano_factory = _faction_has_nano_factory(unit.owner, game)
    if has_nano_factory:
        heal_amount = unit.max_health - unit.current_health
        return (True, heal_amount, "Nano Factory: Full repair anywhere", True)

    # Check for full repair facilities in base
    if at_base and not _is_base_under_bombardment(base, game):
        full_repair_facility = _check_full_repair_facility(unit, base)
        if full_repair_facility:
            heal_amount = unit.max_health - unit.current_health
            return (True, heal_amount, f"{full_repair_facility}: Full repair in one turn", True)

    # Calculate percentage-based healing
    healing_percent = _calculate_healing_percentage(unit, tile, base, game)

    # Calculate actual HP to heal
    damage = unit.max_health - unit.current_health
    heal_amount = max(1, int(damage * healing_percent))

    # Apply 80% cap if not in base
    if not at_base:
        max_allowed_health = int(unit.max_health * 0.80)
        if unit.current_health + heal_amount > max_allowed_health:
            heal_amount = max(0, max_allowed_health - unit.current_health)
            if heal_amount == 0:
                return (False, 0, "Can only heal to 80% in field", False)

    # Build explanation
    reason = f"Healing {heal_amount} HP ({int(healing_percent * 100)}% rate)"

    return (True, heal_amount, reason, False)


def _calculate_healing_percentage(unit, tile, base, game):
    """Calculate healing percentage based on conditions.

    Base rate: 10% of damage
    Each condition adds +10%:
    - In friendly territory
    - In a base
    - Air unit in Airbase
    - Land unit in Bunker
    - In fungus (natives only, or with Xenoempathy Dome)

    Args:
        unit (Unit): Unit being healed
        tile (Tile): Tile unit is on
        base (Base): Base at tile (or None)
        game (Game): Game instance

    Returns:
        float: Healing percentage (0.10 to 0.60+)
    """
    healing_percent = 0.10  # Base 10% healing
    bonuses = ["Base 10%"]

    # +10% if in friendly territory
    if _is_in_friendly_territory(unit, tile, game):
        healing_percent += 0.10
        bonuses.append("Friendly territory +10%")

    # +10% if in a base
    if base and base.owner == unit.owner:
        healing_percent += 0.10
        bonuses.append("In base +10%")

    # +10% if air unit in Airbase
    if unit.type == 'air' and base and 'aerospace_complex' in base.facilities:
        # Note: Airbase improvement doesn't exist yet, using Aerospace Complex as proxy
        healing_percent += 0.10
        bonuses.append("Airbase +10%")

    # +10% if land unit in Bunker
    if unit.type == 'land' and _has_bunker(tile):
        healing_percent += 0.10
        bonuses.append("Bunker +10%")

    # +10% if in fungus (natives only, or with Xenoempathy Dome)
    if _is_in_fungus(tile):
        is_native = unit.weapon == 'native'  # Placeholder for native units
        has_xenoempathy = _faction_has_xenoempathy_dome(unit.owner, game)

        if is_native or has_xenoempathy:
            healing_percent += 0.10
            bonuses.append("Fungus +10%")

    print(f"  Healing calculation: {', '.join(bonuses)}")
    return healing_percent


def _check_full_repair_facility(unit, base):
    """Check if base has a full repair facility for this unit type.

    Full repair facilities:
    - Command Center: Land units
    - Naval Yard: Naval units
    - Aerospace Complex: Air units
    - Biology Lab: Native units

    Args:
        unit (Unit): Unit to check
        base (Base): Base to check

    Returns:
        str: Name of facility that provides full repair, or None
    """
    if unit.type == 'land' and 'command_center' in base.facilities:
        return 'Command Center'

    if unit.type == 'sea' and 'naval_yard' in base.facilities:
        return 'Naval Yard'

    if unit.type == 'air' and 'aerospace_complex' in base.facilities:
        return 'Aerospace Complex'

    # Check for native units (placeholder)
    is_native = unit.weapon == 'native'
    if is_native and 'biology_lab' in base.facilities:
        return 'Biology Lab'

    return None


def _is_in_friendly_territory(unit, tile, game):
    """Check if tile is in friendly territory.

    Args:
        unit (Unit): Unit to check
        tile (Tile): Tile to check
        game (Game): Game instance

    Returns:
        bool: True if in friendly territory
    """
    # TODO: Implement proper territory system
    # For now, check if there's a friendly base within 2 tiles
    for base in game.bases:
        if base.owner == unit.owner:
            distance = abs(tile.x - base.x) + abs(tile.y - base.y)
            if distance <= 2:
                return True
    return False


def _has_bunker(tile):
    """Check if tile has a bunker improvement.

    Args:
        tile (Tile): Tile to check

    Returns:
        bool: True if tile has bunker
    """
    # TODO: Implement bunker improvements
    # For now, return False
    return False


def _is_in_fungus(tile):
    """Check if tile has fungus.

    Args:
        tile (Tile): Tile to check

    Returns:
        bool: True if tile has fungus
    """
    # TODO: Implement fungus terrain
    # For now, return False
    return False


def _faction_has_nano_factory(faction_id, game):
    """Check if faction owns the Nano Factory secret project.

    Args:
        faction_id (int): Faction to check
        game (Game): Game instance

    Returns:
        bool: True if faction has Nano Factory
    """
    # TODO: Implement secret projects tracking
    # For now, check all bases for Nano Factory
    for base in game.bases:
        if base.owner == faction_id and 'nano_factory' in base.facilities:
            return True
    return False


def _faction_has_xenoempathy_dome(faction_id, game):
    """Check if faction owns the Xenoempathy Dome secret project.

    Args:
        faction_id (int): Faction to check
        game (Game): Game instance

    Returns:
        bool: True if faction has Xenoempathy Dome
    """
    # TODO: Implement secret projects tracking
    # For now, check all bases for Xenoempathy Dome
    for base in game.bases:
        if base.owner == faction_id and 'xenoempathy_dome' in base.facilities:
            return True
    return False


def _is_base_under_bombardment(base, game):
    """Check if base is under artillery bombardment.

    Args:
        base (Base): Base to check
        game (Game): Game instance

    Returns:
        bool: True if base is under bombardment
    """
    # TODO: Implement bombardment tracking
    # For now, return False
    return False
