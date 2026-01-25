# unit_components.py
"""Unit component definitions for the Design Workshop.

This module contains all available chassis, weapons, armor, and reactors
that can be combined to create custom units.
"""

# 9 Chassis Types (SMAC values)
CHASSIS = [
    {
        'id': 'infantry',
        'name': 'Infantry',
        'type': 'land',
        'speed': 1,
        'cost': 1,
        'description': 'Basic land unit'
    },
    {
        'id': 'speeder',
        'name': 'Speeder',
        'type': 'land',
        'speed': 2,
        'cost': 2,
        'description': 'Fast rover unit'
    },
    {
        'id': 'hovertank',
        'name': 'Hovertank',
        'type': 'land',
        'speed': 3,
        'cost': 3,
        'description': 'Hover tank'
    },
    {
        'id': 'foil',
        'name': 'Foil',
        'type': 'sea',
        'speed': 4,
        'cost': 4,
        'description': 'Basic sea unit'
    },
    {
        'id': 'cruiser',
        'name': 'Cruiser',
        'type': 'sea',
        'speed': 6,
        'cost': 6,
        'description': 'Advanced sea unit'
    },
    {
        'id': 'needlejet',
        'name': 'Needlejet',
        'type': 'air',
        'speed': 8,
        'cost': 8,
        'description': 'Air superiority'
    },
    {
        'id': 'copter',
        'name': 'Copter',
        'type': 'air',
        'speed': 8,
        'cost': 8,
        'description': 'Tactical helicopter'
    },
    {
        'id': 'gravship',
        'name': 'Gravship',
        'type': 'air',
        'speed': 8,
        'cost': 8,
        'description': 'Antigrav unit'
    },
    {
        'id': 'missile',
        'name': 'Missile',
        'type': 'air',
        'speed': 12,
        'cost': 12,
        'description': 'One-shot missile'
    }
]

# 20 Weapon Types (SMAC values)
WEAPONS = [
    # Non-combat
    {'id': 'colony_pod', 'name': 'Colony Module', 'attack': 0, 'cost': 10, 'mode': 'noncombat'},
    {'id': 'terraforming', 'name': 'Terraforming Unit', 'attack': 0, 'cost': 6, 'mode': 'noncombat'},
    {'id': 'transport', 'name': 'Troop Transport', 'attack': 0, 'cost': 4, 'mode': 'noncombat'},
    {'id': 'supply', 'name': 'Supply Transport', 'attack': 0, 'cost': 8, 'mode': 'noncombat'},
    {'id': 'probe', 'name': 'Probe Team', 'attack': 0, 'cost': 4, 'mode': 'noncombat'},

    # Combat - Projectile
    {'id': 'hand_weapons', 'name': 'Hand Weapons', 'attack': 1, 'cost': 1, 'mode': 'projectile'},
    {'id': 'particle_impactor', 'name': 'Particle Impactor', 'attack': 4, 'cost': 4, 'mode': 'projectile'},
    {'id': 'chaos_gun', 'name': 'Chaos Gun', 'attack': 8, 'cost': 8, 'mode': 'projectile'},
    {'id': 'graviton_gun', 'name': 'Graviton Gun', 'attack': 20, 'cost': 20, 'mode': 'projectile'},

    # Combat - Energy
    {'id': 'laser', 'name': 'Laser', 'attack': 2, 'cost': 2, 'mode': 'energy'},
    {'id': 'gatling_laser', 'name': 'Gatling Laser', 'attack': 5, 'cost': 5, 'mode': 'energy'},
    {'id': 'fusion_laser', 'name': 'Fusion Laser', 'attack': 10, 'cost': 10, 'mode': 'energy'},
    {'id': 'tachyon_bolt', 'name': 'Tachyon Bolt', 'attack': 12, 'cost': 12, 'mode': 'energy'},
    {'id': 'quantum_laser', 'name': 'Quantum Laser', 'attack': 16, 'cost': 16, 'mode': 'energy'},
    {'id': 'singularity_laser', 'name': 'Singularity Laser', 'attack': 24, 'cost': 24, 'mode': 'energy'},

    # Combat - Missile
    {'id': 'missile_launcher', 'name': 'Missile Launcher', 'attack': 6, 'cost': 6, 'mode': 'missile'},
    {'id': 'plasma_shard', 'name': 'Plasma Shard', 'attack': 13, 'cost': 13, 'mode': 'missile'},
    {'id': 'conventional', 'name': 'Conventional Payload', 'attack': 12, 'cost': 12, 'mode': 'missile'},

    # Special - Psi
    {'id': 'psi_attack', 'name': 'Psi Attack', 'attack': -1, 'cost': 10, 'mode': 'psi'},

    # Planet Buster (special)
    {'id': 'planet_buster', 'name': 'Planet Buster', 'attack': 99, 'cost': 32, 'mode': 'projectile'}
]

# 10 Armor Types (SMAC values)
ARMOR = [
    {'id': 'no_armor', 'name': 'No Armor', 'defense': 1, 'cost': 1, 'mode': 'projectile'},
    {'id': 'synthmetal', 'name': 'Synthmetal Armor', 'defense': 2, 'cost': 2, 'mode': 'projectile'},
    {'id': 'plasma_steel', 'name': 'Plasma Steel Armor', 'defense': 3, 'cost': 3, 'mode': 'binary'},
    {'id': 'silksteel', 'name': 'Silksteel Armor', 'defense': 4, 'cost': 4, 'mode': 'energy'},
    {'id': 'photon_wall', 'name': 'Photon Wall', 'defense': 5, 'cost': 5, 'mode': 'energy'},
    {'id': 'probability', 'name': 'Probability Sheath', 'defense': 6, 'cost': 6, 'mode': 'binary'},
    {'id': 'neutronium', 'name': 'Neutronium Armor', 'defense': 8, 'cost': 8, 'mode': 'energy'},
    {'id': 'antimatter', 'name': 'Antimatter Plate', 'defense': 10, 'cost': 10, 'mode': 'binary'},
    {'id': 'stasis', 'name': 'Stasis Generator', 'defense': 12, 'cost': 12, 'mode': 'binary'},
    {'id': 'psi_defense', 'name': 'Psi Defense', 'defense': -1, 'cost': 6, 'mode': 'psi'}
]

# 4 Reactor Types (SMAC values)
REACTORS = [
    {'id': 'fission', 'name': 'Fission Plant', 'power': 1, 'cost': 0},
    {'id': 'fusion', 'name': 'Fusion Reactor', 'power': 2, 'cost': 0},
    {'id': 'quantum', 'name': 'Quantum Chamber', 'power': 3, 'cost': 0},
    {'id': 'singularity', 'name': 'Singularity Engine', 'power': 4, 'cost': 0}
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


def get_reactor_by_id(reactor_id):
    """Get reactor data by ID."""
    for reactor in REACTORS:
        if reactor['id'] == reactor_id:
            return reactor
    return REACTORS[0]  # Default to fission


# 22 Special Abilities
SPECIAL_ABILITIES = [
    {'id': 'none', 'name': 'None', 'cost': 0, 'description': 'No special ability'},
    {'id': 'super_former', 'name': 'Super Former', 'cost': 10, 'description': 'Terraform twice as fast'},
    {'id': 'deep_radar', 'name': 'Deep Radar', 'cost': 20, 'description': 'See 2 squares farther'},
    {'id': 'cloaking', 'name': 'Cloaking Device', 'cost': 25, 'description': 'Invisible to enemy units'},
    {'id': 'amphibious', 'name': 'Amphibious Pods', 'cost': 15, 'description': 'Move on land and sea'},
    {'id': 'drop_pods', 'name': 'Drop Pods', 'cost': 30, 'description': 'Make airdrops anywhere'},
    {'id': 'air_superiority', 'name': 'Air Superiority', 'cost': 20, 'description': '+100% vs air units'},
    {'id': 'deep_pressure', 'name': 'Deep Pressure Hull', 'cost': 15, 'description': 'Operate in ocean trenches'},
    {'id': 'carrier_deck', 'name': 'Carrier Deck', 'cost': 40, 'description': 'Carry up to 4 air units'},
    {'id': 'AAA', 'name': 'AAA Tracking', 'cost': 25, 'description': '+100% vs air attacks'},
    {'id': 'comm_jammer', 'name': 'Comm Jammer', 'cost': 20, 'description': 'Enemy -50% when attacking this'},
    {'id': 'antigrav', 'name': 'Antigrav Struts', 'cost': 20, 'description': '+1 movement, ignore terrain'},
    {'id': 'empath', 'name': 'Empath Song', 'cost': 25, 'description': '+50% vs psi'},
    {'id': 'polymorphic', 'name': 'Polymorphic Encryption', 'cost': 30, 'description': 'Immune to probe teams'},
    {'id': 'fungal_payload', 'name': 'Fungal Payload', 'cost': 25, 'description': 'Creates fungus on impact'},
    {'id': 'blink', 'name': 'Blink Displacer', 'cost': 50, 'description': 'Teleport short distances'},
    {'id': 'trance', 'name': 'Trance', 'cost': 10, 'description': '+50% vs psi attacks'},
    {'id': 'heavy_artillery', 'name': 'Heavy Artillery', 'cost': 30, 'description': 'Bombard from 2 squares'},
    {'id': 'clean_reactor', 'name': 'Clean Reactor', 'cost': 20, 'description': 'No support costs'},
    {'id': 'repair_bay', 'name': 'Repair Bay', 'cost': 35, 'description': 'Repair nearby units'},
    {'id': 'slow', 'name': 'Slow', 'cost': -10, 'description': '-1 movement (prototype)'},
    {'id': 'police', 'name': 'Police 2x', 'cost': 15, 'description': 'Counts as 2 police units'}
]


def get_ability_by_id(ability_id):
    """Get special ability data by ID."""
    for ability in SPECIAL_ABILITIES:
        if ability['id'] == ability_id:
            return ability
    return SPECIAL_ABILITIES[0]  # Default to none
