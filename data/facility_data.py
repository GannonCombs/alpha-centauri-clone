
# Regular base facilities
# Format: {id, name, cost, maint, prereq, effect}
# TODO: Double check that all facilities are in this list
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
]

# Secret Projects (unique wonders, one per game)
# TODO: there are many secret projects missing from this list
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
]