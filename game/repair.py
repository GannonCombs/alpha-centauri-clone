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
    # TODO: This, and xenoempathy dome, need to be checked against a proper global secret project data structure. Fix
    # these once one is built.
    has_nano_factory = any('nano_factory' in b.facilities for b in game.bases if b.owner == unit.owner)
    if has_nano_factory:
        repair_amount = unit.max_health - unit.current_health
        return repair_amount

    # Check for full repair facilities in base
    if at_base:
        has_full_repair = (
            (unit.type == 'land' and 'command_center' in base.facilities) or
            (unit.type == 'sea' and 'naval_yard' in base.facilities) or
            (unit.type == 'air' and 'aerospace_complex' in base.facilities) or
            (unit.weapon == 'native' and 'biology_lab' in base.facilities)
        )
        if has_full_repair:
            return unit.max_health - unit.current_health

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

# TODO: The division of tasks between this function and calculate_repair is illogical. Fix.
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

        has_xenoempathy = any('xenoempathy_dome' in b.facilities for b in game.bases if b.owner == unit.owner)

        if is_native or has_xenoempathy:
            repair_percent += 0.10
            bonuses.append("Fungus +10%")

    print(f"  Repair calculation: {', '.join(bonuses)}")
    return repair_percent


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
