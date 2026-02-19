"""Unit repair system.

This module implements the full SMAC repair formula including:
- Base 10% repair with additive bonuses
- Terrain and facility bonuses
- Full repair facilities (Command Center, Naval Yard, etc.)
- Special cases (Nano Factory, Monoliths)
- 80% repair cap in field, 100% in bases
"""


def calculate_repair(unit, game):
    """Calculate repair amount for a unit at end of turn.

    Args:
        unit (Unit): Unit to repair
        game (Game): Game instance (for checking map, bases, facilities)

    Returns:
        - repair_amount (int): Amount of HP to repair
    """
    # Can't repair if at full health
    if unit.current_health >= unit.max_health:
        return 0

    # Can't repair unless the unit skipped its entire previous turn
    if not getattr(unit, 'repair_eligible', True):
        return 0

    if _is_bombarded(unit, game):
        return 0

    # Get tile info
    tile = game.game_map.get_tile(unit.x, unit.y)
    if not tile:
        return 0

    # Check for instant full repair from Monolith
    if tile.monolith:
        repair_amount = unit.max_health - unit.current_health
        return repair_amount

    # Check if unit is in a friendly base
    at_base = tile.base and tile.base.owner == unit.owner
    base = tile.base if at_base else None

    # Check for Nano Factory (full repair anywhere)
    if _faction_has_nano_factory(unit.owner, game):
        repair_amount = unit.max_health - unit.current_health
        return repair_amount

    # Check for full repair facilities in base
    if at_base:
        full_repair_facility = _check_full_repair_facility(unit, base)
        if full_repair_facility:
            repair_amount = unit.max_health - unit.current_health
            return repair_amount

    # Calculate percentage-based repair
    repair_percent = _calculate_repair_percentage(unit, tile, base, game)

    # Calculate actual HP to repair
    damage = unit.max_health - unit.current_health
    repair_amount = max(1, int(damage * repair_percent))

    # Apply 80% cap if not in base
    if not at_base:
        max_allowed_health = int(unit.max_health * 0.80)
        if unit.current_health + repair_amount > max_allowed_health:
            repair_amount = max(0, max_allowed_health - unit.current_health)
            if repair_amount == 0:
                return 0

    return repair_amount


def _calculate_repair_percentage(unit, tile, base, game):
    """Calculate repair percentage based on conditions.

    Base rate: 10% of damage
    Each condition adds +10%:
    - In friendly territory
    - In a base
    - Air unit in Airbase
    - Land unit in Bunker
    - In fungus (natives only, or with Xenoempathy Dome)

    Args:
        unit (Unit): Unit being repaired
        tile (Tile): Tile unit is on
        base (Base): Base at tile (or None)
        game (Game): Game instance

    Returns:
        float: Repair percentage (0.10 to 0.60+)
    """
    repair_percent = 0.10  # Base 10% repair
    bonuses = ["Base 10%"]

    # +10% if in friendly territory
    if game.territory.get_tile_owner(tile.x, tile.y) == unit.owner:
        repair_percent += 0.10
        bonuses.append("Friendly territory +10%")

    # +10% if in a base
    if base and base.owner == unit.owner:
        repair_percent += 0.10
        bonuses.append("In base +10%")

    # +10% if air unit in Airbase
    if unit.type == 'air' and base and 'aerospace_complex' in base.facilities:
        # Note: Airbase improvement doesn't exist yet, using Aerospace Complex as proxy
        repair_percent += 0.10
        bonuses.append("Airbase +10%")

    # +10% if land unit in Bunker
    if unit.type == 'land' and 'bunker' in tile.improvements:
        repair_percent += 0.10
        bonuses.append("Bunker +10%")

    # +10% if in fungus (natives only, or with Xenoempathy Dome)
    if tile.fungus:
        is_native = unit.weapon == 'native'  # Placeholder for native units
        has_xenoempathy = _faction_has_xenoempathy_dome(unit.owner, game)

        if is_native or has_xenoempathy:
            repair_percent += 0.10
            bonuses.append("Fungus +10%")

    print(f"  Repair calculation: {', '.join(bonuses)}")
    return repair_percent


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


def _is_bombarded(unit, game):
    """Check if unit is subject to artillery bombardment.

    Args:
        unit (Unit): Unit to check
        game (Game): Game instance

    Returns:
        bool: True if unit is under bombardment
    """
    # TODO: Implement bombardment tracking
    # For now, return False
    return False
