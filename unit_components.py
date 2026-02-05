# unit_components.py
"""Unit component definitions for the Design Workshop.

This module contains all available chassis, weapons, armor, and reactors
that can be combined to create custom units. Each component has a tech
prerequisite that must be researched before it can be used.
"""

# 9 Chassis Types (SMAC values with tech prereqs from alpha.txt)
CHASSIS = [
    {
        'id': 'infantry',
        'name': 'Infantry',
        'offensive_names': ['Squad', 'Sentinels'],  # Low armor / high weapon
        'defensive_names': ['Garrison', 'Shock Troops'],  # High armor / low weapon
        'elite_names': ['Elite Guard'],  # High reactor
        'type': 'land',
        'speed': 1,
        'cost': 1,
        'prereq': None,  # Available from start
        'description': 'Basic land unit'
    },
    {
        'id': 'speeder',
        'name': 'Speeder',
        'offensive_names': ['Speeder', 'Rover'],
        'defensive_names': ['Defensive', 'Skirmisher'],
        'elite_names': ['Dragon', 'Enforcer'],
        'type': 'land',
        'speed': 2,
        'cost': 2,
        'prereq': 'Mobile',  # Doctrine: Mobility
        'description': 'Fast rover unit'
    },
    {
        'id': 'hovertank',
        'name': 'Hovertank',
        'offensive_names': ['Hovertank', 'Tank'],
        'defensive_names': ['Skimmer', 'Evasive'],
        'elite_names': ['Behemoth', 'Guardian'],
        'type': 'land',
        'speed': 3,
        'cost': 3,
        'prereq': 'NanoMin',  # Nanominiaturization
        'description': 'Hover tank'
    },
    {
        'id': 'foil',
        'name': 'Foil',
        'offensive_names': ['Foil', 'Skimship'],
        'defensive_names': ['Hoverboat', 'Coastal'],
        'elite_names': ['Megafoil', 'Superfoil'],
        'type': 'sea',
        'speed': 4,
        'cost': 4,
        'prereq': 'DocFlex',  # Doctrine: Flexibility
        'description': 'Basic sea unit'
    },
    {
        'id': 'cruiser',
        'name': 'Cruiser',
        'offensive_names': ['Cruiser', 'Destroyer'],
        'defensive_names': ['Cutter', 'Gunboat'],
        'elite_names': ['Battleship', 'Monitor'],
        'type': 'sea',
        'speed': 6,
        'cost': 6,
        'prereq': 'DocInit',  # Doctrine: Initiative
        'description': 'Advanced sea unit'
    },
    {
        'id': 'needlejet',
        'name': 'Needlejet',
        'offensive_names': ['Needlejet', 'Penetrator'],
        'defensive_names': ['Interceptor', 'Tactical'],
        'elite_names': ['Thunderbolt', 'Sovereign'],
        'type': 'air',
        'speed': 8,
        'cost': 8,
        'prereq': 'DocAir',  # Doctrine: Air Power
        'description': 'Air superiority'
    },
    {
        'id': 'copter',
        'name': 'Copter',
        'offensive_names': ['Copter', 'Chopper'],
        'defensive_names': ['Rotor', 'Lifter'],
        'elite_names': ['Gunship', 'Warbird'],
        'type': 'air',
        'speed': 8,
        'cost': 8,
        'prereq': 'MindMac',  # Mind/Machine Interface
        'description': 'Tactical helicopter'
    },
    {
        'id': 'gravship',
        'name': 'Gravship',
        'offensive_names': ['Gravship', 'Skybase'],
        'defensive_names': ['Antigrav', 'Skyfort'],
        'elite_names': ['Deathsphere', 'Doomwall'],
        'type': 'air',
        'speed': 8,
        'cost': 8,
        'prereq': 'Gravity',  # Graviton Theory
        'description': 'Antigrav unit'
    },
    {
        'id': 'missile',
        'name': 'Missile',
        'offensive_names': ['Missile'],
        'defensive_names': ['Missile'],
        'elite_names': ['Missile'],
        'type': 'air',
        'speed': 12,
        'cost': 12,
        'prereq': 'Orbital',  # Orbital Spaceflight
        'description': 'One-shot missile'
    }
]

# 20 Weapon Types (SMAC values with tech prereqs from alpha.txt)
WEAPONS = [
    # Non-combat
    {'id': 'colony_pod', 'name': 'Colony Module', 'attack': 0, 'cost': 10, 'mode': 'noncombat', 'prereq': None},
    {'id': 'terraforming', 'name': 'Terraforming Unit', 'attack': 0, 'cost': 6, 'mode': 'noncombat', 'prereq': 'Ecology'},
    {'id': 'transport', 'name': 'Troop Transport', 'attack': 0, 'cost': 4, 'mode': 'noncombat', 'prereq': 'DocFlex'},
    {'id': 'supply', 'name': 'Supply Transport', 'attack': 0, 'cost': 8, 'mode': 'noncombat', 'prereq': 'IndAuto'},
    {'id': 'probe', 'name': 'Probe Team', 'attack': 0, 'cost': 4, 'mode': 'noncombat', 'prereq': 'PlaNets'},

    # Combat - Projectile
    {'id': 'hand_weapons', 'name': 'Hand Weapons', 'attack': 1, 'cost': 1, 'mode': 'projectile', 'prereq': None},
    {'id': 'particle_impactor', 'name': 'Particle Impactor', 'attack': 4, 'cost': 4, 'mode': 'projectile', 'prereq': 'Chaos'},
    {'id': 'chaos_gun', 'name': 'Chaos Gun', 'attack': 8, 'cost': 8, 'mode': 'projectile', 'prereq': 'String'},
    {'id': 'graviton_gun', 'name': 'Graviton Gun', 'attack': 20, 'cost': 20, 'mode': 'projectile', 'prereq': 'AGrav'},

    # Combat - Energy
    {'id': 'laser', 'name': 'Laser', 'attack': 2, 'cost': 2, 'mode': 'energy', 'prereq': 'Physic'},
    {'id': 'gatling_laser', 'name': 'Gatling Laser', 'attack': 5, 'cost': 5, 'mode': 'energy', 'prereq': 'Super'},
    {'id': 'fusion_laser', 'name': 'Fusion Laser', 'attack': 10, 'cost': 10, 'mode': 'energy', 'prereq': 'SupLube'},
    {'id': 'tachyon_bolt', 'name': 'Tachyon Bolt', 'attack': 12, 'cost': 12, 'mode': 'energy', 'prereq': 'Unified'},
    {'id': 'quantum_laser', 'name': 'Quantum Laser', 'attack': 16, 'cost': 16, 'mode': 'energy', 'prereq': 'QuanMac'},
    {'id': 'singularity_laser', 'name': 'Singularity Laser', 'attack': 24, 'cost': 24, 'mode': 'energy', 'prereq': 'ConSing'},

    # Combat - Missile
    {'id': 'missile_launcher', 'name': 'Missile Launcher', 'attack': 6, 'cost': 6, 'mode': 'missile', 'prereq': 'Fossil'},
    {'id': 'plasma_shard', 'name': 'Plasma Shard', 'attack': 13, 'cost': 13, 'mode': 'missile', 'prereq': 'Space'},
    {'id': 'conventional', 'name': 'Conventional Payload', 'attack': 12, 'cost': 12, 'mode': 'missile', 'prereq': 'Orbital'},

    # Special - Psi
    {'id': 'psi_attack', 'name': 'Psi Attack', 'attack': -1, 'cost': 10, 'mode': 'psi', 'prereq': 'CentPsi'},

    # Planet Buster (special)
    {'id': 'planet_buster', 'name': 'Planet Buster', 'attack': 99, 'cost': 32, 'mode': 'projectile', 'prereq': 'Orbital'}
]

# 10 Armor Types (SMAC values with tech prereqs from alpha.txt)
ARMOR = [
    {'id': 'no_armor', 'name': 'No Armor', 'defense': 1, 'cost': 1, 'mode': 'projectile', 'prereq': None},
    {'id': 'synthmetal', 'name': 'Synthmetal Armor', 'defense': 2, 'cost': 2, 'mode': 'projectile', 'prereq': 'Indust'},
    {'id': 'plasma_steel', 'name': 'Plasma Steel Armor', 'defense': 3, 'cost': 3, 'mode': 'binary', 'prereq': 'Chemist'},
    {'id': 'silksteel', 'name': 'Silksteel Armor', 'defense': 4, 'cost': 4, 'mode': 'energy', 'prereq': 'Alloys'},
    {'id': 'photon_wall', 'name': 'Photon Wall', 'defense': 5, 'cost': 5, 'mode': 'energy', 'prereq': 'DocSec'},
    {'id': 'probability', 'name': 'Probability Sheath', 'defense': 6, 'cost': 6, 'mode': 'binary', 'prereq': 'ProbMec'},
    {'id': 'neutronium', 'name': 'Neutronium Armor', 'defense': 8, 'cost': 8, 'mode': 'energy', 'prereq': 'MatComp'},
    {'id': 'antimatter', 'name': 'Antimatter Plate', 'defense': 10, 'cost': 10, 'mode': 'binary', 'prereq': 'NanEdit'},
    {'id': 'stasis', 'name': 'Stasis Generator', 'defense': 12, 'cost': 12, 'mode': 'binary', 'prereq': 'TempMec'},
    {'id': 'psi_defense', 'name': 'Psi Defense', 'defense': -1, 'cost': 6, 'mode': 'psi', 'prereq': 'Eudaim'}
]

# 4 Reactor Types (SMAC values with tech prereqs from alpha.txt)
REACTORS = [
    {'id': 'fission', 'name': 'Fission Plant', 'power': 1, 'cost': 0, 'prereq': None},
    {'id': 'fusion', 'name': 'Fusion Reactor', 'power': 2, 'cost': 0, 'prereq': 'Fusion'},
    {'id': 'quantum', 'name': 'Quantum Chamber', 'power': 3, 'cost': 0, 'prereq': 'Quantum'},
    {'id': 'singularity', 'name': 'Singularity Engine', 'power': 4, 'cost': 0, 'prereq': 'SingMec'}
]


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

    # Standard military units: Hand Weapons Infantry = Scout Patrol
    if weapon_id == 'hand_weapons' and chassis_id == 'infantry' and (armor_id is None or armor_id == 'no_armor'):
        return "Scout Patrol"

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


def get_reactor_by_id(reactor_id):
    """Get reactor data by ID."""
    for reactor in REACTORS:
        if reactor['id'] == reactor_id:
            return reactor
    return REACTORS[0]  # Default to fission


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


# 22 Special Abilities (tech prereqs from alpha.txt)
SPECIAL_ABILITIES = [
    {'id': 'none', 'name': 'None', 'cost': 0, 'prereq': None, 'description': 'No special ability'},
    {'id': 'super_former', 'name': 'Super Former', 'cost': 10, 'prereq': 'EcoEng2', 'description': 'Terraform twice as fast'},
    {'id': 'deep_radar', 'name': 'Deep Radar', 'cost': 20, 'prereq': 'MilAlg', 'description': 'See 2 squares farther'},
    {'id': 'cloaking', 'name': 'Cloaking Device', 'cost': 25, 'prereq': 'Surface', 'description': 'Invisible to enemy units'},
    {'id': 'amphibious', 'name': 'Amphibious Pods', 'cost': 15, 'prereq': 'DocInit', 'description': 'Move on land and sea'},
    {'id': 'drop_pods', 'name': 'Drop Pods', 'cost': 30, 'prereq': 'MindMac', 'description': 'Make airdrops anywhere'},
    {'id': 'air_superiority', 'name': 'Air Superiority', 'cost': 20, 'prereq': 'DocAir', 'description': '+100% vs air units'},
    {'id': 'deep_pressure', 'name': 'Deep Pressure Hull', 'cost': 15, 'prereq': 'Metal', 'description': 'Operate in ocean trenches'},
    {'id': 'carrier_deck', 'name': 'Carrier Deck', 'cost': 40, 'prereq': 'Metal', 'description': 'Carry up to 4 air units'},
    {'id': 'AAA', 'name': 'AAA Tracking', 'cost': 25, 'prereq': 'MilAlg', 'description': '+100% vs air attacks'},
    {'id': 'comm_jammer', 'name': 'Comm Jammer', 'cost': 20, 'prereq': 'Subat', 'description': 'Enemy -50% when attacking this'},
    {'id': 'antigrav', 'name': 'Antigrav Struts', 'cost': 20, 'prereq': 'Gravity', 'description': '+1 movement, ignore terrain'},
    {'id': 'empath', 'name': 'Empath Song', 'cost': 25, 'prereq': 'CentEmp', 'description': '+50% vs psi'},
    {'id': 'polymorphic', 'name': 'Polymorphic Encryption', 'cost': 30, 'prereq': 'Algor', 'description': 'Immune to probe teams'},
    {'id': 'fungal_payload', 'name': 'Fungal Payload', 'cost': 25, 'prereq': 'Fossil', 'description': 'Creates fungus on impact'},
    {'id': 'blink', 'name': 'Blink Displacer', 'cost': 50, 'prereq': 'Matter', 'description': 'Teleport short distances'},
    {'id': 'trance', 'name': 'Trance', 'cost': 10, 'prereq': 'Brain', 'description': '+50% vs psi attacks'},
    {'id': 'heavy_artillery', 'name': 'Heavy Artillery', 'cost': 30, 'prereq': 'Poly', 'description': 'Bombard from 2 squares'},
    {'id': 'clean_reactor', 'name': 'Clean Reactor', 'cost': 20, 'prereq': 'BioEng', 'description': 'No support costs'},
    {'id': 'repair_bay', 'name': 'Repair Bay', 'cost': 35, 'prereq': 'Metal', 'description': 'Repair nearby units'},
    {'id': 'slow', 'name': 'Slow', 'cost': -10, 'prereq': None, 'description': '-1 movement (prototype)'},
    {'id': 'police', 'name': 'Police 2x', 'cost': 15, 'prereq': 'Integ', 'description': 'Counts as 2 police units'}
]


def get_ability_by_id(ability_id):
    """Get special ability data by ID."""
    for ability in SPECIAL_ABILITIES:
        if ability['id'] == ability_id:
            return ability
    return SPECIAL_ABILITIES[0]  # Default to none
