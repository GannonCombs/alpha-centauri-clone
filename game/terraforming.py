"""Terraforming system.

Handles all Former unit actions: starting, progressing, completing, and
cancelling terraforming work.  Also provides the tile improvement yield
calculator used by base.py's resource output.

Public API
----------
is_former(unit)                          → bool
get_available_actions(unit, tile, game)  → list[str]
start_terraforming(unit, action, game)   → None
cancel_terraforming(unit)                → None
process_terraforming(unit, game)         → None   (call once per former per turn)
get_tile_yields(tile)                    → (nutrients, minerals, energy)
"""

from game.data.terraforming_data import IMPROVEMENTS, EXCLUSIVE_SLOTS, SPEED_MODIFIERS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_former(unit):
    """Return True if this unit is a former (terraforming unit)."""
    return getattr(unit, 'is_former', False) or unit.weapon == 'terraforming'


def _get_tech_ids(game, faction_id):
    """Return the set of researched tech IDs for a faction."""
    try:
        tech_tree = game.factions[faction_id].tech_tree
        return set(tech_tree.researched_techs)
    except Exception:
        return set()


def _build_turns(unit, improvement_key):
    """Calculate actual turns needed accounting for ability speed modifiers."""
    imp = IMPROVEMENTS[improvement_key]
    base = imp['base_turns']

    multiplier = 1.0
    if unit.has_ability('super_former'):
        multiplier *= SPEED_MODIFIERS['super_former']
    if unit.has_ability('fungicide_tanks') and improvement_key in ('remove_fungus', 'sea_fungus'):
        multiplier *= SPEED_MODIFIERS['fungicide_tanks']

    return max(1, int(base * multiplier))


# ---------------------------------------------------------------------------
# Action availability
# ---------------------------------------------------------------------------

def get_available_actions(unit, tile, game):
    """Return list of improvement IDs available to this former on this tile.

    Filters by:
    - Unit must be a former
    - Tile terrain must match improvement terrain requirement
    - Tech prerequisite must be researched (or None)
    - 'requires' improvements must already be on tile
    - Special per-improvement feasibility checks
    """
    if not is_former(unit):
        return []

    researched = _get_tech_ids(game, unit.owner)
    available = []

    for key, imp in IMPROVEMENTS.items():
        # Terrain match
        terrain = imp['terrain']
        if terrain == 'land' and not tile.is_land():
            continue
        if terrain == 'ocean' and not tile.is_ocean():
            continue

        # Tech prerequisite
        if imp['prereq'] and imp['prereq'] not in researched:
            continue

        # 'requires' — prerequisite improvements must be present
        if imp.get('requires') and not imp['requires'].issubset(tile.improvements):
            continue

        # Action-specific feasibility
        action_type = imp.get('action_type', 'add')

        if action_type == 'remove':
            # Only show remove action if the target improvement is present
            target = imp.get('removes_improvement')
            if target and target not in tile.improvements:
                continue

        elif action_type == 'add':
            # Can't build something already present
            if key in tile.improvements:
                continue
            # Infrastructure stacks freely; exclusive slots block duplicates
            slot = imp.get('slot')
            if slot in EXCLUSIVE_SLOTS:
                occupied = any(
                    IMPROVEMENTS.get(k, {}).get('slot') == slot
                    for k in tile.improvements
                )
                if occupied and key not in _get_replaceable_by(key, tile):
                    # Slot is occupied and this improvement won't replace the occupant;
                    # it would still replace it via the 'replaces' field — allow it.
                    pass  # replaces logic handled in complete_improvement

        elif action_type == 'terraform':
            effect = imp.get('terraform_effect', {})
            if 'rockiness' in effect:
                # Level terrain only if rocky or rolling
                if tile.rockiness == 0:
                    continue
            if 'altitude' in effect:
                delta = effect['altitude']
                # Lower land: allowed on any land tile; flip to ocean handled in complete_improvement
                # Raise ocean: allow any ocean tile; flip to land handled in complete_improvement
                pass  # No altitude pre-check needed

        elif action_type == 'modify_tile':
            flag = imp.get('tile_flag')
            if flag and getattr(tile, flag, False):
                continue  # Already done

        # Borehole: requires no-monolith, and tile must not already have one
        if key == 'borehole' and getattr(tile, 'monolith', False):
            continue
        if key in tile.improvements:
            continue

        available.append(key)

    return available


def _get_replaceable_by(new_key, tile):
    """Return the set of improvements on the tile that new_key would replace."""
    replaces = IMPROVEMENTS[new_key].get('replaces', set())
    return tile.improvements & replaces


# ---------------------------------------------------------------------------
# Starting and cancelling work
# ---------------------------------------------------------------------------

def start_terraforming(unit, action_key, game):
    """Begin terraforming.  Consumes all remaining movement points.

    Args:
        unit: Former unit
        action_key: Key from IMPROVEMENTS
        game: Game instance
    """
    unit.terraforming_action = action_key
    unit.terraforming_turns_left = _build_turns(unit, action_key)
    unit.moves_remaining = 0
    unit.has_moved = True
    unit.heal_eligible = False


def cancel_terraforming(unit):
    """Abort in-progress terraforming (e.g. unit moved or was attacked)."""
    unit.terraforming_action = None
    unit.terraforming_turns_left = 0


# ---------------------------------------------------------------------------
# Turn processing
# ---------------------------------------------------------------------------

def process_terraforming(unit, game):
    """Advance terraforming by one turn.  Call once per former during upkeep.

    If the work completes this turn, applies the improvement to the tile.
    """
    if not unit.terraforming_action:
        return

    unit.terraforming_turns_left -= 1
    if unit.terraforming_turns_left > 0:
        return

    # Work complete — apply improvement
    tile = game.game_map.get_tile(unit.x, unit.y)
    if tile:
        complete_improvement(tile, unit.terraforming_action, game, unit)

    unit.terraforming_action = None
    unit.terraforming_turns_left = 0


# ---------------------------------------------------------------------------
# Applying a completed improvement
# ---------------------------------------------------------------------------

def complete_improvement(tile, improvement_key, game, unit=None):
    """Apply a completed terraforming action to the tile.

    Handles all four action types: add, remove, terraform, modify_tile.
    """
    imp = IMPROVEMENTS.get(improvement_key)
    if not imp:
        return

    action_type = imp.get('action_type', 'add')

    if action_type == 'add':
        _apply_add(tile, improvement_key, imp, game, unit)

    elif action_type == 'remove':
        target = imp.get('removes_improvement')
        if target:
            tile.improvements.discard(target)
            if target in ('fungus', 'sea_fungus'):
                tile._fungus = False

    elif action_type == 'terraform':
        _apply_terraform(tile, imp, game)

    elif action_type == 'modify_tile':
        flag = imp.get('tile_flag')
        if flag:
            setattr(tile, flag, True)
        # Aquifer: raise rainfall of adjacent tiles
        if improvement_key == 'aquifer' and game:
            _raise_adjacent_rainfall(tile, game)


def _apply_add(tile, key, imp, game, unit):
    """Add an improvement to tile.improvements, respecting slot rules."""
    # Remove anything this improvement replaces
    for old_key in imp.get('replaces', set()):
        tile.improvements.discard(old_key)
        if old_key in ('fungus', 'sea_fungus'):
            tile._fungus = False

    # For exclusive slots, evict the current occupant first
    slot = imp.get('slot')
    if slot in EXCLUSIVE_SLOTS:
        to_remove = [k for k in tile.improvements
                     if IMPROVEMENTS.get(k, {}).get('slot') == slot]
        for k in to_remove:
            tile.improvements.discard(k)

    # Forest: give minerals to home base when harvesting existing improvements
    if key == 'forest' and unit and unit.home_base:
        harvested = tile.improvements & {'mine', 'solar', 'condenser',
                                         'echelon_mirror', 'soil_enricher', 'farm'}
        if harvested:
            unit.home_base.mineral_stockpile = (
                getattr(unit.home_base, 'mineral_stockpile', 0) + 5
            )

    tile.improvements.add(key)

    # Sync _fungus backing store
    if key in ('fungus', 'sea_fungus'):
        tile._fungus = True
    elif 'fungus' not in tile.improvements and 'sea_fungus' not in tile.improvements:
        tile._fungus = False


def _apply_terraform(tile, imp, game=None):
    """Apply a terrain modification (level, raise, lower).

    If the altitude change causes land to sink below sea level or ocean to rise
    above sea level, the terrain type is flipped and all units on the tile are
    destroyed (they cannot survive the transition).
    """
    effect = imp.get('terraform_effect', {})
    if 'rockiness' in effect:
        tile.rockiness = max(0, tile.rockiness + effect['rockiness'])
    if 'altitude' in effect:
        was_land = tile.is_land()
        tile.altitude = tile.altitude + effect['altitude']

        if game:
            new_is_land = tile.altitude >= 0
            if was_land and not new_is_land:
                # Land sank below sea level — flip to ocean
                tile.terrain_type = 'ocean'
                tile.improvements.clear()
                tile._fungus = False
                units_here = [u for u in game.units if u.x == tile.x and u.y == tile.y]
                for u in units_here:
                    game._remove_unit(u)
            elif not was_land and new_is_land:
                # Ocean rose above sea level — flip to land
                tile.terrain_type = 'land'
                tile.improvements.clear()
                tile._fungus = False
                units_here = [u for u in game.units if u.x == tile.x and u.y == tile.y]
                for u in units_here:
                    game._remove_unit(u)


def _raise_adjacent_rainfall(tile, game):
    """Raise rainfall of tiles adjacent to an aquifer by 1 (max 2)."""
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        adj = game.game_map.get_tile(
            (tile.x + dx) % game.game_map.width,
            tile.y + dy
        )
        if adj and adj.is_land():
            adj.rainfall = min(2, adj.rainfall + 1)


# ---------------------------------------------------------------------------
# Tile yield calculation
# ---------------------------------------------------------------------------

def get_tile_yields(tile):
    """Return (nutrients, minerals, energy) bonus from all improvements on tile.

    Called by base.py's calculate_resource_output to add improvement bonuses
    on top of the unimproved base yields.  For 'fixed' yield improvements
    (Forest, Borehole) the caller should replace — not add — base yields.

    Returns:
        dict with keys:
            'nutrients'  (int)   — flat bonus to add
            'minerals'   (int)   — flat bonus to add
            'energy'     (int)   — flat bonus to add
            'fixed'      (tuple) — (N, M, E) override, or None
            'nutrients_multiplier' (float) — applied after flat additions (default 1.0)
    """
    result = {
        'nutrients': 0,
        'minerals': 0,
        'energy': 0,
        'fixed': None,
        'nutrients_multiplier': 1.0,
    }

    # Fixed-yield improvements take full precedence (borehole, forest)
    for key in ('borehole', 'forest'):
        if key in tile.improvements:
            fixed = IMPROVEMENTS[key]['yields'].get('fixed')
            if fixed:
                result['fixed'] = fixed
                return result  # Nothing else matters

    for key in tile.improvements:
        imp = IMPROVEMENTS.get(key)
        if not imp:
            continue
        yields = imp.get('yields', {})

        # Flat bonuses
        result['nutrients'] += yields.get('nutrients', 0)
        result['minerals'] += yields.get('minerals', 0)
        result['energy'] += yields.get('energy', 0)

        # Mine rocky bonus: +1 extra if rocky, +1 more if road also present
        if key == 'mine' and yields.get('minerals_rocky_bonus'):
            if getattr(tile, 'rockiness', 0) == 2:
                result['minerals'] += 1          # rocky: +2 total
                if 'road' in tile.improvements or 'mag_tube' in tile.improvements:
                    result['minerals'] += 1      # rocky+road: +3 total

        # Solar / Echelon Mirror altitude bonus
        if yields.get('energy_altitude'):
            alt = getattr(tile, 'altitude', 0)
            if alt >= 3000:
                bonus = 4
            elif alt >= 2000:
                bonus = 3
            elif alt >= 1000:
                bonus = 2
            else:
                bonus = 1
            result['energy'] += bonus

        # Multiplier (Condenser, Soil Enricher — last one wins; both can't coexist)
        mult = yields.get('nutrients_multiplier', 1.0)
        if mult != 1.0:
            result['nutrients_multiplier'] = mult

    # River: +1 energy
    if getattr(tile, 'has_river', False) or tile.river_edges:
        result['energy'] += 1

    return result
