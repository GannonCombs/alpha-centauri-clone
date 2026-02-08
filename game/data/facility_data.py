
# Regular base facilities
# Format: {id, name, cost, maint, prereq, effect}
FACILITIES = [
    {
        'id': 'headquarters',
        'name': 'Headquarters',
        'cost': 5,
        'maint': 0,
        'prereq': None,
        'effect': 'Efficiency bonus',
        'description': '+1 Efficiency'
    },
    {
        'id': 'childrens_creche',
        'name': "Children's Creche",
        'cost': 5,
        'maint': 1,
        'prereq': 'EthCalc',
        'effect': 'Growth/Efficiency/Morale',
        'description': '+2 Growth, +1 Efficiency, +1 Morale for garrison'
    },
    {
        'id': 'recycling_tanks',
        'name': 'Recycling Tanks',
        'cost': 4,
        'maint': 0,
        'prereq': 'Biogen',
        'effect': 'Bonus Resources',
        'description': '+1 Nutrient/Mineral/Energy in base square'
    },
    {
        'id': 'perimeter_defense',
        'name': 'Perimeter Defense',
        'cost': 5,
        'maint': 0,
        'prereq': 'DocLoy',
        'effect': 'Defense +100%',
        'description': 'Doubles defense of units in base'
    },
    {
        'id': 'tachyon_field',
        'name': 'Tachyon Field',
        'cost': 12,
        'maint': 2,
        'prereq': 'ProbMec',
        'effect': 'All Defense +100%',
        'description': 'Doubles defense against all attack types'
    },
    {
        'id': 'recreation_commons',
        'name': 'Recreation Commons',
        'cost': 4,
        'maint': 1,
        'prereq': 'Psych',
        'effect': 'Fewer Drones',
        'description': '-2 Drones (psych bonus)'
    },
    {
        'id': 'energy_bank',
        'name': 'Energy Bank',
        'cost': 8,
        'maint': 1,
        'prereq': 'IndEcon',
        'effect': 'Economy Bonus',
        'description': '+50% energy production'
    },
    {
        'id': 'network_node',
        'name': 'Network Node',
        'cost': 8,
        'maint': 1,
        'prereq': 'InfNet',
        'effect': 'Labs Bonus',
        'description': '+50% research output'
    },
    {
        'id': 'biology_lab',
        'name': 'Biology Lab',
        'cost': 6,
        'maint': 1,
        'prereq': 'CentEmp',
        'effect': 'Research and PSI',
        'description': '+50% research, +50% PSI defense'
    },
    {
        'id': 'skunkworks',
        'name': 'Skunkworks',
        'cost': 6,
        'maint': 1,
        'prereq': 'Subat',
        'effect': 'Prototypes Free',
        'description': 'No prototype cost penalty'
    },
    {
        'id': 'hologram_theatre',
        'name': 'Hologram Theatre',
        'cost': 6,
        'maint': 3,
        'prereq': 'PlaNets',
        'effect': 'Psych and Fewer Drones',
        'description': '+50% psych, -2 drones'
    },
    {
        'id': 'tree_farm',
        'name': 'Tree Farm',
        'cost': 12,
        'maint': 3,
        'prereq': 'EnvEcon',
        'effect': 'Econ/Psych/Forest',
        'description': '+50% economy, +50% psych, +1 energy from forests'
    },
    {
        'id': 'fusion_lab',
        'name': 'Fusion Lab',
        'cost': 12,
        'maint': 3,
        'prereq': 'Fusion',
        'effect': 'Econ and Labs Bonus',
        'description': '+50% economy, +50% research'
    },
    {
        'id': 'research_hospital',
        'name': 'Research Hospital',
        'cost': 12,
        'maint': 3,
        'prereq': 'Gene',
        'effect': 'Labs and Psych Bonus',
        'description': '+25% research, +25% psych'
    },
    {
        'id': 'genejack_factory',
        'name': 'Genejack Factory',
        'cost': 10,
        'maint': 2,
        'prereq': 'Viral',
        'effect': 'Minerals; More Drones',
        'description': '+50% minerals, +1 drone'
    },
    {
        'id': 'hab_complex',
        'name': 'Hab Complex',
        'cost': 8,
        'maint': 2,
        'prereq': 'IndAuto',
        'effect': 'Increase Population Limit',
        'description': 'Increases population limit to 14'
    },
    {
        'id': 'habitation_dome',
        'name': 'Habitation Dome',
        'cost': 16,
        'maint': 4,
        'prereq': 'Solids',
        'effect': 'Increase Population Limit',
        'description': 'Removes population limit'
    },
    {
        'id': 'pressure_dome',
        'name': 'Pressure Dome',
        'cost': 8,
        'maint': 0,
        'prereq': 'DocFlex',
        'effect': 'Submersion/Resources',
        'description': 'Allows base on ocean floor, +1 minerals from ocean'
    },
    {
        'id': 'command_center',
        'name': 'Command Center',
        'cost': 4,
        'maint': 1,
        'prereq': 'Mobile',
        'effect': '+2 Morale:Land',
        'description': '+2 morale for land units'
    },
    {
        'id': 'naval_yard',
        'name': 'Naval Yard',
        'cost': 8,
        'maint': 2,
        'prereq': 'DocInit',
        'effect': '+2 Morale:Sea, Sea Def +100%',
        'description': '+2 morale for sea units, +100% sea defense'
    },
    {
        'id': 'aerospace_complex',
        'name': 'Aerospace Complex',
        'cost': 8,
        'maint': 2,
        'prereq': 'DocAir',
        'effect': '+2 Morale:Air, Air Def +100%',
        'description': '+2 morale for air units, +100% air defense'
    },
    {
        'id': 'bioenhancement_center',
        'name': 'Bioenhancement Center',
        'cost': 10,
        'maint': 2,
        'prereq': 'Neural',
        'effect': '+2 Morale:ALL',
        'description': '+2 morale for all units'
    },
    {
        'id': 'paradise_garden',
        'name': 'Paradise Garden',
        'cost': 12,
        'maint': 4,
        'prereq': 'SentEco',
        'effect': '+2 Talents',
        'description': '+2 talents at this base'
    },
    {
        'id': 'hybrid_forest',
        'name': 'Hybrid Forest',
        'cost': 24,
        'maint': 4,
        'prereq': 'PlaEcon',
        'effect': 'Econ/Psych/Forest',
        'description': '+50% economy, +50% psych, +1 energy from forests'
    },
    {
        'id': 'quantum_lab',
        'name': 'Quantum Lab',
        'cost': 24,
        'maint': 4,
        'prereq': 'Quantum',
        'effect': 'Econ and Labs Bonus',
        'description': '+50% economy, +50% research'
    },
    {
        'id': 'nanohospital',
        'name': 'Nanohospital',
        'cost': 24,
        'maint': 4,
        'prereq': 'HomoSup',
        'effect': 'Labs and Psych Bonus',
        'description': '+25% research, +25% psych'
    },
    {
        'id': 'robotic_assembly',
        'name': 'Robotic Assembly Plant',
        'cost': 20,
        'maint': 4,
        'prereq': 'IndRob',
        'effect': 'Minerals Bonus',
        'description': '+50% minerals'
    },
    {
        'id': 'nanoreplicator',
        'name': 'Nanoreplicator',
        'cost': 32,
        'maint': 6,
        'prereq': 'NanEdit',
        'effect': 'Minerals Bonus',
        'description': '+50% minerals'
    },
    {
        'id': 'quantum_converter',
        'name': 'Quantum Converter',
        'cost': 20,
        'maint': 5,
        'prereq': 'QuanMac',
        'effect': 'Minerals Bonus',
        'description': '+50% minerals'
    },
    {
        'id': 'punishment_sphere',
        'name': 'Punishment Sphere',
        'cost': 10,
        'maint': 2,
        'prereq': 'MilAlg',
        'effect': 'No Drones/-50% Tech',
        'description': 'Eliminates drones but -50% research'
    },
    {
        'id': 'centauri_preserve',
        'name': 'Centauri Preserve',
        'cost': 10,
        'maint': 2,
        'prereq': 'CentMed',
        'effect': 'Ecology Bonus',
        'description': '+1 lifecycle for fungus tiles'
    },
    {
        'id': 'temple_planet',
        'name': 'Temple of Planet',
        'cost': 20,
        'maint': 3,
        'prereq': 'AlphCen',
        'effect': 'Ecology Bonus',
        'description': '+2 lifecycle for fungus tiles'
    },
    {
        'id': 'psi_gate',
        'name': 'Psi Gate',
        'cost': 10,
        'maint': 2,
        'prereq': 'Matter',
        'effect': 'Teleport',
        'description': 'Units can teleport between bases with Psi Gates'
    },
    {
        'id': 'sky_hydro',
        'name': 'Sky Hydroponics Lab',
        'cost': 12,
        'maint': 0,
        'prereq': 'Orbital',
        'effect': '+1 Nutrient ALL BASES',
        'description': '+1 nutrient at all bases'
    },
    {
        'id': 'nessus_mining',
        'name': 'Nessus Mining Station',
        'cost': 12,
        'maint': 0,
        'prereq': 'HAL9000',
        'effect': '+1 Minerals ALL BASES',
        'description': '+1 minerals at all bases'
    },
    {
        'id': 'orbital_power',
        'name': 'Orbital Power Transmitter',
        'cost': 12,
        'maint': 0,
        'prereq': 'Space',
        'effect': '+1 Energy ALL BASES',
        'description': '+1 energy at all bases'
    },
    {
        'id': 'orbital_defense',
        'name': 'Orbital Defense Pod',
        'cost': 12,
        'maint': 0,
        'prereq': 'HAL9000',
        'effect': 'Missile Defense',
        'description': 'Protects against missile attacks'
    },
    {
        'id': 'stockpile_energy',
        'name': 'Stockpile Energy',
        'cost': 0,
        'maint': 0,
        'prereq': None,
        'effect': 'Minerals to Energy',
        'description': 'Converts minerals to energy credits'
    },
]

# Secret Projects (unique wonders, one per game)
SECRET_PROJECTS = [
    {
        'id': 'human_genome',
        'name': 'The Human Genome Project',
        'cost': 20,
        'maint': 0,
        'prereq': 'Biogen',
        'effect': '+1 Talent Each Base',
        'description': '+1 Talent at every base'
    },
    {
        'id': 'command_nexus',
        'name': 'The Command Nexus',
        'cost': 20,
        'maint': 0,
        'prereq': 'DocLoy',
        'effect': 'Command Center Each Base',
        'description': 'Free Command Center at every base'
    },
    {
        'id': 'weather_paradigm',
        'name': 'The Weather Paradigm',
        'cost': 20,
        'maint': 0,
        'prereq': 'Ecology',
        'effect': 'Terraform Rate +50%',
        'description': 'Formers terraform 50% faster'
    },
    {
        'id': 'merchant_exchange',
        'name': 'The Merchant Exchange',
        'cost': 20,
        'maint': 0,
        'prereq': 'Indust',
        'effect': '+1 Energy Each Square Here',
        'description': '+1 energy in every square at this base'
    },
    {
        'id': 'empath_guild',
        'name': 'The Empath Guild',
        'cost': 20,
        'maint': 0,
        'prereq': 'CentEmp',
        'effect': 'Commlink For Every Faction',
        'description': 'Establish contact with all factions'
    },
    {
        'id': 'citizens_defense',
        'name': "The Citizens' Defense Force",
        'cost': 30,
        'maint': 0,
        'prereq': 'Integ',
        'effect': 'Perimeter Defense Each Base',
        'description': 'Free Perimeter Defense at every base'
    },
    {
        'id': 'virtual_world',
        'name': 'The Virtual World',
        'cost': 30,
        'maint': 0,
        'prereq': 'PlaNets',
        'effect': 'Network Nodes Help Drones',
        'description': 'Network Nodes count as Hologram Theatres'
    },
    {
        'id': 'planetary_transit',
        'name': 'The Planetary Transit System',
        'cost': 30,
        'maint': 0,
        'prereq': 'IndAuto',
        'effect': 'New Bases Begin At Size 3',
        'description': 'New bases start at population 3'
    },
    {
        'id': 'xenoempathy_dome',
        'name': 'The Xenoempathy Dome',
        'cost': 30,
        'maint': 0,
        'prereq': 'CentMed',
        'effect': 'Fungus Movement Bonus',
        'description': 'Fungus does not impede movement'
    },
    {
        'id': 'neural_amplifier',
        'name': 'The Neural Amplifier',
        'cost': 30,
        'maint': 0,
        'prereq': 'Neural',
        'effect': 'Psi Defense +50%',
        'description': '+50% PSI defense for all units'
    },
    {
        'id': 'maritime_control',
        'name': 'The Maritime Control Center',
        'cost': 30,
        'maint': 0,
        'prereq': 'DocInit',
        'effect': 'Naval Movement +2; Naval Bases',
        'description': '+2 movement for sea units, naval bases'
    },
    {
        'id': 'planetary_datalinks',
        'name': 'The Planetary Datalinks',
        'cost': 30,
        'maint': 0,
        'prereq': 'Cyber',
        'effect': 'Any Tech Known To 3 Others',
        'description': 'Receive any tech known to 3+ other factions'
    },
    {
        'id': 'supercollider',
        'name': 'The Supercollider',
        'cost': 30,
        'maint': 0,
        'prereq': 'E=Mc2',
        'effect': 'Labs +100% At This Base',
        'description': 'Doubles research at this base'
    },
    {
        'id': 'ascetic_virtues',
        'name': 'The Ascetic Virtues',
        'cost': 30,
        'maint': 0,
        'prereq': 'PlaEcon',
        'effect': 'Pop. Limit Relaxed; +1 POLICE',
        'description': 'Population limit increased, +1 POLICE rating'
    },
    {
        'id': 'longevity_vaccine',
        'name': 'The Longevity Vaccine',
        'cost': 30,
        'maint': 0,
        'prereq': 'BioEng',
        'effect': 'Fewer Drones or More Profits',
        'description': 'Choose -1 drone each base or +2 economy'
    },
    {
        'id': 'hunter_seeker',
        'name': 'The Hunter-Seeker Algorithm',
        'cost': 30,
        'maint': 0,
        'prereq': 'Algor',
        'effect': 'Immunity to Probe Teams',
        'description': 'Immune to probe team infiltration'
    },
    {
        'id': 'pholus_mutagen',
        'name': 'The Pholus Mutagen',
        'cost': 40,
        'maint': 0,
        'prereq': 'CentGen',
        'effect': 'Ecology Bonus; Lifecycle Bonus',
        'description': '+1 lifecycle, faster terraforming'
    },
    {
        'id': 'cyborg_factory',
        'name': 'The Cyborg Factory',
        'cost': 40,
        'maint': 0,
        'prereq': 'MindMac',
        'effect': 'Bioenh. Center Every Base',
        'description': 'Free Bioenhancement Center at every base'
    },
    {
        'id': 'theory_everything',
        'name': 'The Theory of Everything',
        'cost': 40,
        'maint': 0,
        'prereq': 'Unified',
        'effect': 'Labs +100% At This Base',
        'description': 'Doubles research at this base'
    },
    {
        'id': 'dream_twister',
        'name': 'The Dream Twister',
        'cost': 40,
        'maint': 0,
        'prereq': 'WillPow',
        'effect': 'Psi Attack +50%',
        'description': '+50% PSI attack for all units'
    },
    {
        'id': 'universal_translator',
        'name': 'The Universal Translator',
        'cost': 40,
        'maint': 0,
        'prereq': 'HomoSup',
        'effect': 'Two Free Techs',
        'description': 'Receive two free technologies'
    },
    {
        'id': 'network_backbone',
        'name': 'The Network Backbone',
        'cost': 40,
        'maint': 0,
        'prereq': 'DigSent',
        'effect': '+1 Lab Per Commerce/Net Node',
        'description': '+1 research per Network Node'
    },
    {
        'id': 'nano_factory',
        'name': 'The Nano Factory',
        'cost': 40,
        'maint': 0,
        'prereq': 'IndRob',
        'effect': 'Repair Units; Low Upgrade Costs',
        'description': 'Units repair fully each turn, reduced upgrade costs'
    },
    {
        'id': 'living_refinery',
        'name': 'The Living Refinery',
        'cost': 40,
        'maint': 0,
        'prereq': 'Space',
        'effect': '+2 SUPPORT (social)',
        'description': '+2 SUPPORT rating'
    },
    {
        'id': 'cloning_vats',
        'name': 'The Cloning Vats',
        'cost': 50,
        'maint': 0,
        'prereq': 'BioMac',
        'effect': 'Population Boom At All Bases',
        'description': 'All bases grow every turn'
    },
    {
        'id': 'self_aware_colony',
        'name': 'The Self-Aware Colony',
        'cost': 50,
        'maint': 0,
        'prereq': 'HAL9000',
        'effect': 'Maintenance Halved; Extra Police',
        'description': 'Facility maintenance halved, +2 police'
    },
    {
        'id': 'clinical_immortality',
        'name': 'Clinical Immortality',
        'cost': 50,
        'maint': 0,
        'prereq': 'NanEdit',
        'effect': 'Extra Talent Every Base',
        'description': '+1 talent at every base'
    },
    {
        'id': 'space_elevator',
        'name': 'The Space Elevator',
        'cost': 50,
        'maint': 0,
        'prereq': 'Solids',
        'effect': 'Energy +100%/Orbital Cost Halved',
        'description': 'Doubles energy, halves orbital facility costs'
    },
    {
        'id': 'singularity_inductor',
        'name': 'The Singularity Inductor',
        'cost': 60,
        'maint': 0,
        'prereq': 'ConSing',
        'effect': 'Quantum Converter Every Base',
        'description': 'Free Quantum Converter at every base'
    },
    {
        'id': 'bulk_matter',
        'name': 'The Bulk Matter Transmitter',
        'cost': 60,
        'maint': 0,
        'prereq': 'Matter',
        'effect': '+2 Minerals Every Base',
        'description': '+2 minerals at every base'
    },
    {
        'id': 'telepathic_matrix',
        'name': 'The Telepathic Matrix',
        'cost': 60,
        'maint': 0,
        'prereq': 'Eudaim',
        'effect': 'No More Drone Riots; +2 PROBE',
        'description': 'Eliminates drone riots, +2 PROBE rating'
    },
    {
        'id': 'voice_planet',
        'name': 'The Voice of Planet',
        'cost': 60,
        'maint': 0,
        'prereq': 'Thresh',
        'effect': 'Begins Ascent To Transcendence',
        'description': 'Starts the Ascent to Transcendence victory'
    },
    {
        'id': 'ascent_transcendence',
        'name': 'The Ascent to Transcendence',
        'cost': 200,
        'maint': 0,
        'prereq': 'Thresh',
        'effect': 'End of Human Era',
        'description': 'Completes Transcendence victory'
    },
]