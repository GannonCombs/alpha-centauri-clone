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


def generate_unit_name(weapon_id, chassis_id, armor_id=None, reactor_id='fission'):
    """Generate a unit name using simplified SMAC naming: <component> <chassis variant>.

    Naming logic:
    - Offensive units (weapon > armor): <weapon name> <offensive chassis name>
    - Defensive units (armor >= weapon): <armor name> <defensive chassis name>
    - This ensures every unit has a unique name based on its components

    Args:
        weapon_id (str): Weapon component ID
        chassis_id (str): Chassis component ID
        armor_id (str): Armor component ID (optional, used for offensive/defensive determination)
        reactor_id (str): Reactor component ID (optional, not used in current naming)

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
        return "Former"

    if weapon_id == 'probe':
        return "Probe Team"

    if weapon_id == 'transport':
        return "Transport"

    if weapon_id == 'supply':
        return "Supply Crawler"

    # Standard military units with hand weapons use "Scout" prefix
    # if weapon_id == 'hand_weapons' and (armor_id is None or armor_id == 'no_armor'):
    #     if chassis_id == 'infantry':
    #         return "Scout Patrol"
    #     elif chassis_id == 'speeder' or chassis_id == 'rover':
    #         return "Scout Speeder"
        # For other chassis, fall through to standard naming

    # For combat units, use <component> <chassis name> format
    armor = get_armor_by_id(armor_id) if armor_id else ARMOR[0]

    weapon_attack = weapon.get('attack', 0)
    armor_defense = armor.get('defense', 1)

    # Determine if offensive or defensive based on weapon vs armor
    # When equal, treat as offensive (use weapon name)
    is_offensive = weapon_attack >= armor_defense

    # Get clean component name (remove "Armor" suffix from armor names)
    weapon_name = weapon['name'].replace(' Weapons', '').replace(' Launcher', '')
    armor_name = armor['name'].replace(' Armor', '')

    if is_offensive:
        # Offensive unit: use weapon name + offensive chassis variant
        chassis_names = chassis.get('offensive_names', [chassis['name']])
        chassis_name = chassis_names[0]
        return f"{weapon_name} {chassis_name}"
    else:
        # Defensive unit: use armor name + defensive chassis variant
        chassis_names = chassis.get('defensive_names', [chassis['name']])
        chassis_name = chassis_names[0]
        return f"{armor_name} {chassis_name}"
        for ability in special_abilities:
            name_parts.insert(0, ability)

    # Add chassis name
    name_parts.append(chassis['name'])

    return " ".join(name_parts)


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
