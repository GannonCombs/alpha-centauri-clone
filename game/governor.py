"""Governor system for automated base production.

The Governor automatically selects production for bases based on one of four modes:
- BUILD: Focus on base facilities, defensive units, and infrastructure
- CONQUER: Focus on offensive military units
- DISCOVER: Focus on science facilities and research
- EXPLORE: Focus on expansion (colony pods, scouts, formers)
"""

import random


def select_production(base, faction, game):
    """Select production for a base based on governor mode.

    Args:
        base: Base object needing production selection
        faction: Faction object that owns the base
        game: Game object for global state access

    Returns:
        str: Production item name, or None if no valid selection
    """
    if not base.governor_mode:
        # No mode set - use BUILD as default
        return select_build_production(base, faction, game)

    mode_functions = {
        'build': select_build_production,
        'conquer': select_conquer_production,
        'discover': select_discover_production,
        'explore': select_explore_production
    }

    func = mode_functions.get(base.governor_mode)
    if func:
        return func(base, faction, game)

    return None


def select_build_production(base, faction, game):
    """BUILD mode: Focus on infrastructure and defensive units.

    Priority:
    1. Defensive units if garrison is weak
    2. Happiness facilities if unrest
    3. Resource facilities if bottlenecks
    4. Secret projects if available
    5. General infrastructure
    """
    # 1. Check garrison strength
    garrison_size = len([u for u in base.garrison if u.owner == base.owner])
    if garrison_size < 2:
        unit = _select_defensive_unit(base, faction, game)
        if unit:
            return unit

    # 2. Check for unrest
    if base.drones > 0 or base.drone_riot:
        facility = _select_happiness_facility(base, faction, game)
        if facility:
            return facility

    # 3. Check for resource bottlenecks
    facility = _select_resource_facility(base, faction, game)
    if facility:
        return facility

    # 4. Secret projects if things are going well
    if faction.energy_credits > 200:
        project = _select_secret_project(base, faction, game)
        if project:
            return project

    # 5. General infrastructure
    facility = _select_general_facility(base, faction, game)
    if facility:
        return facility

    # 6. Fallback: defensive unit
    return _select_defensive_unit(base, faction, game) or "Scout Patrol"


def select_conquer_production(base, faction, game):
    """CONQUER mode: Focus on offensive military units.

    Priority:
    1. Offensive units (primary focus)
    2. Minimal garrison (1 unit)
    3. Military facilities (Command Center, etc.)
    4. More offensive units
    """
    # 1. Ensure minimal garrison
    garrison_size = len([u for u in base.garrison if u.owner == base.owner])
    if garrison_size < 1:
        unit = _select_defensive_unit(base, faction, game)
        if unit:
            return unit

    # 2. Military facilities
    if 'Command Center' not in base.facilities and _can_build(base, faction, 'Command Center'):
        return 'Command Center'

    # 3. Offensive units (main focus)
    unit = _select_offensive_unit(base, faction, game)
    if unit:
        return unit

    # 4. Fallback
    return "Scout Patrol"


def select_discover_production(base, faction, game):
    """DISCOVER mode: Focus on science and research.

    Priority:
    1. Science facilities
    2. Probe teams
    3. Science-focused secret projects
    4. Colony pods for new research sites
    """
    # 1. Science facilities first
    science_facilities = ['Network Node', 'Research Hospital', 'Fusion Lab', 'Quantum Lab']
    for facility in science_facilities:
        if facility not in base.facilities and _can_build(base, faction, facility):
            return facility

    # 2. Probe teams for intel
    if _should_build_probe(base, faction, game):
        if _can_build_unit(base, faction, 'probe'):
            return _get_probe_design_name(faction)

    # 3. Secret projects
    project = _select_secret_project(base, faction, game)
    if project:
        return project

    # 4. Expansion for more research sites
    if len(faction.bases) < 8:
        if _can_build_unit(base, faction, 'colony_pod'):
            return _get_colony_pod_design_name(faction)

    # 5. Fallback: general facility
    return _select_general_facility(base, faction, game) or "Scout Patrol"


def select_explore_production(base, faction, game):
    """EXPLORE mode: Focus on expansion and exploration.

    Priority:
    1. Colony pods (aggressive expansion)
    2. Scouts/fast units
    3. Formers (terraform new territory)
    4. Transport ships (if coastal)
    5. Minimal infrastructure
    """
    # 1. Colony pods - primary focus
    if len(faction.bases) < 12 and base.population >= 3:
        if _can_build_unit(base, faction, 'colony_pod'):
            return _get_colony_pod_design_name(faction)

    # 2. Scouts for exploration
    scout_count = len([u for u in game.units if u.owner == base.owner and u.weapon == 'hand_weapons'])
    if scout_count < len(faction.bases) * 2:
        unit = _select_scout_unit(base, faction, game)
        if unit:
            return unit

    # 3. Formers for terraforming
    former_count = len([u for u in game.units if u.owner == base.owner and u.weapon == 'terraform'])
    if former_count < len(faction.bases):
        if _can_build_unit(base, faction, 'terraform'):
            return _get_former_design_name(faction)

    # 4. Basic infrastructure
    if base.population < 3:
        facility = _select_growth_facility(base, faction, game)
        if facility:
            return facility

    # 5. Fallback: colony pod or scout
    if _can_build_unit(base, faction, 'colony_pod'):
        return _get_colony_pod_design_name(faction)

    return "Scout Patrol"


# Helper functions

def _can_build(base, faction, item_name):
    """Check if base can build a specific item."""
    from game.data.facility_data import FACILITIES, SECRET_PROJECTS

    # Check facilities
    for facility in FACILITIES:
        if facility['name'] == item_name:
            # Check if already built
            if item_name in base.facilities:
                return False
            # Check tech prereq
            if facility['prereq'] and not faction.tech_tree.has_tech(facility['prereq']):
                return False
            return True

    # Check secret projects
    for project in SECRET_PROJECTS:
        if project['name'] == item_name:
            # Check if already built anywhere
            for other_base in faction.bases:
                if item_name in other_base.facilities:
                    return False
            # Check tech prereq
            if project['prereq'] and not faction.tech_tree.has_tech(project['prereq']):
                return False
            return True

    return False


def _can_build_unit(base, faction, weapon_type):
    """Check if faction has a design for a unit with the given weapon."""
    designs = faction.designs.get_designs()
    for design in designs:
        if design and design.get('weapon') == weapon_type:
            return True
    return False


def _get_design_name(faction, weapon_type):
    """Get the name of a design with the given weapon type."""
    from game.unit_components import generate_unit_name

    designs = faction.designs.get_designs()
    for design in designs:
        if design and design.get('weapon') == weapon_type:
            return generate_unit_name(
                design['weapon'],
                design['chassis'],
                design['armor'],
                design['reactor'],
                design.get('ability1', 'none'),
                design.get('ability2', 'none')
            )
    return None


def _get_colony_pod_design_name(faction):
    """Get colony pod design name."""
    return _get_design_name(faction, 'colony_pod')


def _get_former_design_name(faction):
    """Get former design name."""
    return _get_design_name(faction, 'terraform')


def _get_probe_design_name(faction):
    """Get probe team design name."""
    return _get_design_name(faction, 'probe')


def _select_defensive_unit(base, faction, game):
    """Select a defensive military unit."""
    # Prefer units with good armor
    designs = faction.designs.get_designs()

    # Filter to combat units (not colony pods, formers, probes)
    combat_designs = []
    for design in designs:
        if design:
            weapon = design.get('weapon')
            if weapon not in ['colony_pod', 'terraform', 'probe', 'artifact']:
                combat_designs.append(design)

    if not combat_designs:
        return "Scout Patrol"

    # Pick one with decent armor
    from game.unit_components import generate_unit_name
    design = random.choice(combat_designs)
    return generate_unit_name(
        design['weapon'],
        design['chassis'],
        design['armor'],
        design['reactor'],
        design.get('ability1', 'none'),
        design.get('ability2', 'none')
    )


def _select_offensive_unit(base, faction, game):
    """Select an offensive military unit."""
    # Prefer units with good weapons
    designs = faction.designs.get_designs()

    # Filter to combat units
    combat_designs = []
    for design in designs:
        if design:
            weapon = design.get('weapon')
            if weapon not in ['colony_pod', 'terraform', 'probe', 'artifact']:
                combat_designs.append(design)

    if not combat_designs:
        return "Scout Patrol"

    from game.unit_components import generate_unit_name
    design = random.choice(combat_designs)
    return generate_unit_name(
        design['weapon'],
        design['chassis'],
        design['armor'],
        design['reactor'],
        design.get('ability1', 'none'),
        design.get('ability2', 'none')
    )


def _select_scout_unit(base, faction, game):
    """Select a scout/fast unit."""
    from game.unit_components import generate_unit_name

    # Look for a basic scout design (hand weapons on fast chassis)
    designs = faction.designs.get_designs()
    for design in designs:
        if design and design.get('weapon') == 'hand_weapons':
            return generate_unit_name(
                design['weapon'],
                design['chassis'],
                design['armor'],
                design['reactor'],
                design.get('ability1', 'none'),
                design.get('ability2', 'none')
            )

    return "Scout Patrol"


def _select_happiness_facility(base, faction, game):
    """Select a facility that improves happiness."""
    happiness_facilities = [
        'Recreation Commons',
        'Hologram Theatre',
        'Paradise Garden',
        'Temple of Planet'
    ]

    for facility in happiness_facilities:
        if _can_build(base, faction, facility):
            return facility

    return None


def _select_resource_facility(base, faction, game):
    """Select a facility that boosts resources."""
    # Simple heuristic: build facilities that help production
    resource_facilities = [
        'Recycling Tanks',
        'Genejack Factory',
        'Quantum Converter',
        'Robotic Assembly Plant'
    ]

    for facility in resource_facilities:
        if _can_build(base, faction, facility):
            return facility

    return None


def _select_growth_facility(base, faction, game):
    """Select a facility that helps growth."""
    growth_facilities = [
        'Kelp Farm',
        'Tree Farm',
        'Hybrid Forest'
    ]

    for facility in growth_facilities:
        if _can_build(base, faction, facility):
            return facility

    return None


def _select_general_facility(base, faction, game):
    """Select any useful facility."""
    # Try various categories
    all_facilities = [
        'Recycling Tanks',
        'Perimeter Defense',
        'Network Node',
        'Tree Farm',
        'Recreation Commons'
    ]

    for facility in all_facilities:
        if _can_build(base, faction, facility):
            return facility

    return None


def _select_secret_project(base, faction, game):
    """Select a secret project if available."""
    from game.data.facility_data import SECRET_PROJECTS

    # Get affordable projects
    affordable = []
    for project in SECRET_PROJECTS:
        if _can_build(base, faction, project['name']):
            if project['cost'] <= faction.energy_credits // 2:
                affordable.append(project['name'])

    if affordable:
        return random.choice(affordable)

    return None


def _should_build_probe(base, faction, game):
    """Check if we should build a probe team."""
    # Simple check: do we have fewer than 2 probes?
    probe_count = len([u for u in game.units if u.owner == base.owner and u.weapon == 'probe'])
    return probe_count < 2


def get_ai_governor_mode(faction_id):
    """Get the default governor mode for an AI faction.

    Args:
        faction_id: Faction index (0-6)

    Returns:
        str: Governor mode ('build', 'conquer', 'discover', 'explore')
    """
    # AI faction governor modes based on personality
    modes = {
        0: 'build',      # Gaians (actually Explore, but 0 is player)
        1: 'explore',    # Gaians
        2: 'conquer',    # Spartans
        3: 'conquer',    # Hive (has Build and Conquer - choose Conquer)
        4: 'discover',   # University
        5: 'build',      # Morgan
        6: 'conquer',    # Believers
        7: 'discover'    # Peacekeepers (has Explore and Discover - choose Discover)
    }

    return modes.get(faction_id, 'build')
