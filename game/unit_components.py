# unit_components.py
"""Unit component definitions for the Design Workshop.

This module contains all available chassis, weapons, armor, and reactors
that can be combined to create custom units. Each component has a tech
prerequisite that must be researched before it can be used.
"""

from game.data.unit_data import CHASSIS, WEAPONS, ARMOR, REACTORS, SPECIAL_ABILITIES

def get_chassis_by_id(chassis_id):
    """Get chassis data by ID."""
    for chassis in CHASSIS:
        if chassis['id'] == chassis_id:
            return chassis
    return CHASSIS[0]  # Default to infantry


def get_weapon_by_id(weapon_id):
    """Get weapon data by ID."""
    for weapon in WEAPONS:
        if weapon['id'] == weapon_id:
            return weapon
    return WEAPONS[5]  # Default to hand weapons


def get_armor_by_id(armor_id):
    """Get armor data by ID."""
    for armor in ARMOR:
        if armor['id'] == armor_id:
            return armor
    return ARMOR[0]  # Default to no armor


def get_reactor_by_id(reactor_id):
    """Get reactor data by ID."""
    for reactor in REACTORS:
        if reactor['id'] == reactor_id:
            return reactor
    return REACTORS[0]  # Default to fission


def generate_unit_name(weapon_id, chassis_id, armor_id=None, reactor_id='fission', ability1='none', ability2='none'):
    """Generate a unit name using SMAC naming: [abilities] <component> <chassis variant>.

    Naming logic:
    - Abilities are prefixed (one word per ability)
    - Offensive units (weapon > armor): <weapon name> <offensive chassis name>
    - Defensive units (armor >= weapon): <armor name> <defensive chassis name>
    - Full format: "[ability] [ability] [component] [chassis]"

    Args:
        weapon_id (str): Weapon component ID
        chassis_id (str): Chassis component ID
        armor_id (str): Armor component ID (optional, used for offensive/defensive determination)
        reactor_id (str): Reactor component ID (optional, not used in current naming)
        ability1 (str): First special ability ID (default 'none')
        ability2 (str): Second special ability ID (default 'none')

    Returns:
        str: Generated unit name
    """
    weapon = get_weapon_by_id(weapon_id)
    chassis = get_chassis_by_id(chassis_id)

    # Special cases for non-combat units
    if weapon_id == 'colony_pod':
        if chassis_id == 'foil' or chassis_id == 'cruiser':
            return "Sea Colony Pod"
        else:
            return "Colony Pod"

    if weapon_id == 'terraforming':
        # Check for Super Former ability
        if ability1 == 'super_former' or ability2 == 'super_former':
            return "Super Former"
        return "Former"

    if weapon_id == 'probe':
        return "Probe Team"

    if weapon_id == 'transport':
        return "Transport"

    if weapon_id == 'supply':
        return "Supply Crawler"

    # Build name parts list
    name_parts = []

    # Add ability prefixes (from both ability slots)
    for ability_id in [ability1, ability2]:
        if ability_id and ability_id != 'none':
            ability = get_ability_by_id(ability_id)
            # Extract prefix from ability name (first word, or special cases)
            ability_prefix = _get_ability_prefix(ability)
            if ability_prefix:
                name_parts.append(ability_prefix)

    # SMAC naming convention for hand weapons:
    # - Land units with hand weapons: "Scout [chassis]"
    # - All other units: "[Weapon] [chassis]"
    if weapon_id == 'hand_weapons':
        chassis_type = chassis.get('type', 'land')
        if chassis_type == 'land':
            # Land units with hand weapons use "Scout" prefix
            name_parts.append("Scout")
            chassis_names = chassis.get('offensive_names', [chassis['name']])
            chassis_name = chassis_names[0]
            name_parts.append(chassis_name)
            return " ".join(name_parts)
        # Sea/air units with hand weapons fall through to standard naming

    # For combat units, determine offensive vs defensive
    armor = get_armor_by_id(armor_id) if armor_id else ARMOR[0]

    weapon_attack = weapon.get('attack', 0)
    armor_defense = armor.get('defense', 1)

    # Determine if offensive or defensive based on weapon vs armor
    # When equal, treat as offensive (use weapon name)
    is_offensive = weapon_attack >= armor_defense

    # Get clean component name (remove "Weapons" / "Armor" suffixes)
    weapon_name = weapon['name'].replace(' Weapons', '').replace(' Launcher', '')
    armor_name = armor['name'].replace(' Armor', '')

    if is_offensive:
        # Offensive unit: use weapon name + offensive chassis variant
        name_parts.append(weapon_name)
        chassis_names = chassis.get('offensive_names', [chassis['name']])
        chassis_name = chassis_names[0]
        name_parts.append(chassis_name)
    else:
        # Defensive unit: use armor name + defensive chassis variant
        name_parts.append(armor_name)
        chassis_names = chassis.get('defensive_names', [chassis['name']])
        chassis_name = chassis_names[0]
        name_parts.append(chassis_name)

    return " ".join(name_parts)


def _get_ability_prefix(ability):
    """Get the prefix word for an ability to use in unit names.

    Args:
        ability (dict): Ability data with 'name' field

    Returns:
        str: Prefix word for this ability, or None to skip
    """
    ability_name = ability.get('name', '')

    # Special cases for multi-word abilities
    special_prefixes = {
        'AAA Tracking': 'AAA',
        'Super Former': 'Super',
        'Deep Radar': 'Deep',
        'Cloaking Device': 'Cloaking',
        'Amphibious Pods': 'Amphibious',
        'Drop Pods': 'Drop',
        'Air Superiority': 'Air',
        'Deep Pressure Hull': 'Deep',
        'Carrier Deck': 'Carrier',
        'Comm Jammer': 'Comm',
        'Antigrav Struts': 'Antigrav',
        'Empath Song': 'Empath',
        'Polymorphic Encryption': 'Polymorphic',
        'Fungal Payload': 'Fungal',
        'Blink Displacer': 'Blink',
        'Heavy Artillery': 'Heavy',
        'Clean Reactor': 'Clean',
        'Repair Bay': 'Repair',
        'Police 2x': 'Police',
    }

    # Check for special case
    if ability_name in special_prefixes:
        return special_prefixes[ability_name]

    # Default: use first word of ability name
    first_word = ability_name.split()[0] if ability_name else None
    return first_word if first_word and first_word != 'None' else None


def is_component_available(component, tech_tree):
    """Check if a component is available based on tech prerequisites.

    Args:
        component (dict): Component with 'prereq' field
        tech_tree (TechTree): Player's tech tree

    Returns:
        bool: True if component is unlocked
    """
    if component['prereq'] is None:
        return True
    return tech_tree.has_tech(component['prereq'])


def get_ability_by_id(ability_id):
    """Get special ability data by ID."""
    for ability in SPECIAL_ABILITIES:
        if ability['id'] == ability_id:
            return ability
    return SPECIAL_ABILITIES[0]  # Default to none
