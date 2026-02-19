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

    Repair rules (SMAC):
    - Unit must have skipped its entire turn and not be bombarded
    - Monolith / Nano Factory / matching base facility → full heal in one turn
    - Otherwise: 10% of damage + additive bonuses for territory, base, airbase,
      bunker, fungus; field repair capped at 80% max health

    Args:
        unit (Unit): Unit to repair
        game (Game): Game instance (for checking map, bases, facilities)

    Returns:
        int: Amount of HP to repair (0 if no repair occurs)
    """
    # --- Step 1: Eligibility checks ---
    if unit.current_health >= unit.max_health:
        return 0
    if not getattr(unit, 'repair_eligible', True):
        return 0
    if _is_bombarded(unit, game):
        return 0

    tile = game.game_map.get_tile(unit.x, unit.y)
    if not tile:
        return 0

    at_base = tile.base and tile.base.owner == unit.owner
    base = tile.base if at_base else None
    full_damage = unit.max_health - unit.current_health

    # --- Step 2: Full-heal sources ---
    if tile.monolith:
        return full_damage

    # TODO: Nano Factory and Xenoempathy Dome need a proper global secret project
    # data structure. Fix once one is built.
    if any('nano_factory' in b.facilities for b in game.bases if b.owner == unit.owner):
        return full_damage

    if at_base:
        has_full_repair = (
            (unit.type == 'land' and 'command_center' in base.facilities) or
            (unit.type == 'sea' and 'naval_yard' in base.facilities) or
            (unit.type == 'air' and 'aerospace_complex' in base.facilities) or
            (unit.weapon == 'native' and 'biology_lab' in base.facilities)
        )
        if has_full_repair:
            return full_damage

    # --- Step 3: Percentage-based repair ---
    repair_percent = 0.10  # Base 10%
    bonuses = ["Base 10%"]

    if game.territory.get_tile_owner(tile.x, tile.y) == unit.owner:
        repair_percent += 0.10
        bonuses.append("Friendly territory +10%")

    if at_base:
        repair_percent += 0.10
        bonuses.append("In base +10%")

    if unit.type == 'air' and base and 'aerospace_complex' in base.facilities:
        # Note: Airbase improvement doesn't exist yet; Aerospace Complex is proxy
        repair_percent += 0.10
        bonuses.append("Airbase +10%")

    if unit.type == 'land' and 'bunker' in tile.improvements:
        repair_percent += 0.10
        bonuses.append("Bunker +10%")

    if tile.fungus:
        is_native = unit.weapon == 'native'
        has_xenoempathy = any('xenoempathy_dome' in b.facilities for b in game.bases if b.owner == unit.owner)
        if is_native or has_xenoempathy:
            repair_percent += 0.10
            bonuses.append("Fungus +10%")

    print(f"  Repair calculation: {', '.join(bonuses)}")

    repair_amount = max(1, int(full_damage * repair_percent))

    # Field cap: units outside a base can only heal to 80% max health
    if not at_base:
        max_allowed = int(unit.max_health * 0.80)
        repair_amount = max(0, min(repair_amount, max_allowed - unit.current_health))

    return repair_amount


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
