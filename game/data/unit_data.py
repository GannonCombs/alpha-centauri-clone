
# 9 Chassis Types (SMAC values with tech prereqs from alpha.txt)
CHASSIS = [
    {
        'id': 'infantry',
        'name': 'Infantry',
        'offensive_names': ['Patrol', 'Sentinels'],  # Low armor / high weapon
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
    {'id': 'artifact', 'name': 'Alien Artifact', 'attack': 0, 'cost': 0, 'mode': 'noncombat', 'prereq': None},

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

# Citizen specialists: citizens who don't work tiles but provide fixed bonuses.
# prereq: tech ID required to unlock (None = always available).
# No nutrient cost — the cost is the foregone tile output.
SPECIALISTS = [
    {'id': 'doctor',     'name': 'Doctor',     'prereq': None,      'min_pop': 1, 'economy': 0, 'labs': 0, 'psych': 2},
    {'id': 'technician', 'name': 'Technician', 'prereq': None,      'min_pop': 5, 'economy': 3, 'labs': 0, 'psych': 0},
    {'id': 'librarian',  'name': 'Librarian',  'prereq': 'PlaNets', 'min_pop': 5, 'economy': 0, 'labs': 3, 'psych': 0},
    {'id': 'empath',     'name': 'Empath',     'prereq': 'CentMed', 'min_pop': 1, 'economy': 2, 'labs': 0, 'psych': 2},
    {'id': 'engineer',   'name': 'Engineer',   'prereq': 'Fusion',  'min_pop': 5, 'economy': 3, 'labs': 2, 'psych': 0},
    {'id': 'thinker',    'name': 'Thinker',    'prereq': 'MindMac', 'min_pop': 5, 'economy': 0, 'labs': 3, 'psych': 1},
    {'id': 'transcend',  'name': 'Transcend',  'prereq': 'AlphCen', 'min_pop': 1, 'economy': 2, 'labs': 4, 'psych': 2},
]