"""Terraforming improvement definitions.

Each improvement entry describes a tile enhancement a Former unit can build.

Fields
------
id          : str   — unique key, also stored in tile.improvements
name        : str   — display name
hotkey      : str   — single lowercase character (pygame key name)
base_turns  : int   — turns to complete at standard speed
terrain     : str   — 'land', 'ocean', or 'both'
prereq      : str|None — tech ID required; None means available from the start
slot        : str|None — exclusivity group (see SLOTS below); None = no conflict
replaces    : set   — improvement IDs removed from tile when this is placed
requires    : set   — improvement IDs that must already be on tile
action_type : str   — 'add' stores in tile.improvements; 'remove' deletes from it;
                       'terraform' modifies tile terrain properties; 'modify_tile'
                       sets a one-time tile flag (e.g. aquifer/river)
yields      : dict  — static resource deltas applied on top of base tile yield
    'nutrients', 'minerals', 'energy' — flat bonus each turn
    'fixed'     — tuple (N, M, E) that OVERRIDES all base + improvement yields
    'minerals_rocky_bonus' — extra minerals if tile is rocky (added on top of 'minerals')
    'energy_altitude'      — True: add altitude-tier energy (same table as base)
    'nutrients_multiplier' — float multiplier applied after all flat additions
description : str   — one-line summary for UI tooltip

Slot definitions
----------------
'cover'             Farm, Forest, Fungus (land) — only one at a time
'ocean_cover'       Kelp Farm, Sea Fungus — only one at a time
'extraction'        Mine, Solar Collector, Condenser, Echelon Mirror (land)
'ocean_extraction'  Mining Platform, Tidal Harness
'borehole'          Thermal Borehole — exclusive: clears cover + extraction on placement
'infrastructure'    Road, Mag Tube*, Sensor Array, Bunker, Air Base — all stackable
                    (* Mag Tube replaces Road via its 'replaces' field)

Soil Enricher is in the 'extraction' slot but requires {'farm'} in requires.
Forest placed over an occupied extraction slot clears that slot (see 'replaces').
"""

# ---------------------------------------------------------------------------
# Land improvements
# ---------------------------------------------------------------------------

IMPROVEMENTS = {

    # --- Infrastructure (stackable) ---

    'road': {
        'id': 'road',
        'name': 'Road',
        'hotkey': 'r',
        'base_turns': 1,
        'terrain': 'land',
        'prereq': None,
        'slot': 'infrastructure',
        'replaces': set(),
        'requires': set(),
        'action_type': 'add',
        'yields': {},
        'description': 'Movement costs 1/3 per tile; +1 mineral bonus on rocky with mine',
    },

    'mag_tube': {
        'id': 'mag_tube',
        'name': 'Mag Tube',
        'hotkey': 'r',
        'base_turns': 3,
        'terrain': 'land',
        'prereq': 'MagTube',   # Monopole Magnets
        'slot': 'infrastructure',
        'replaces': {'road'},
        'requires': {'road'},  # Road must be present first
        'action_type': 'add',
        'yields': {},
        'description': 'Units expend no movement points on this tile',
    },

    'sensor_array': {
        'id': 'sensor_array',
        'name': 'Sensor Array',
        'hotkey': 'o',
        'base_turns': 4,
        'terrain': 'land',
        'prereq': None,
        'slot': 'infrastructure',
        'replaces': set(),
        'requires': set(),
        'action_type': 'add',
        'yields': {},
        'description': '+25% defense; eliminates fog of war in 2-tile radius',
    },

    'bunker': {
        'id': 'bunker',
        'name': 'Bunker',
        'hotkey': 'k',
        'base_turns': 5,
        'terrain': 'land',
        'prereq': 'MilAlg',    # Advanced Military Algorithms
        'slot': 'infrastructure',
        'replaces': set(),
        'requires': set(),
        'action_type': 'add',
        'yields': {},
        'description': '+50% defense; no collateral damage to stacked units',
    },

    'airbase': {
        'id': 'airbase',
        'name': 'Air Base',
        'hotkey': '.',
        'base_turns': 10,
        'terrain': 'land',
        'prereq': 'DocAir',    # Doctrine: Air Power
        'slot': 'infrastructure',
        'replaces': set(),
        'requires': set(),
        'action_type': 'add',
        'yields': {},
        'description': 'Air units may refuel here',
    },

    # --- Cover slot (mutually exclusive) ---

    'farm': {
        'id': 'farm',
        'name': 'Farm',
        'hotkey': 'f',
        'base_turns': 4,
        'terrain': 'land',
        'prereq': None,
        'slot': 'cover',
        'replaces': {'forest', 'fungus'},
        'requires': set(),
        'action_type': 'add',
        'yields': {'nutrients': 1},
        'description': '+1 nutrient',
    },

    'forest': {
        'id': 'forest',
        'name': 'Forest',
        'hotkey': 'F',  # Shift+F
        'base_turns': 4,
        'terrain': 'land',
        'prereq': 'EcoEng',    # Ecological Engineering
        'slot': 'cover',
        'replaces': {'farm', 'fungus', 'mine', 'solar', 'condenser',
                     'echelon_mirror', 'soil_enricher'},
        'requires': set(),
        'action_type': 'add',
        'yields': {'fixed': (1, 2, 1)},
        'description': 'Fixed 1N/2M/1E; reduces eco-damage; spreads to adjacent tiles',
    },

    'fungus': {
        'id': 'fungus',
        'name': 'Xenofungus',
        'hotkey': 'Ctrl+f',
        'base_turns': 6,
        'terrain': 'land',
        'prereq': 'EcoEng',    # Ecological Engineering
        'slot': 'cover',
        'replaces': {'farm', 'forest', 'mine', 'solar', 'condenser',
                     'echelon_mirror', 'soil_enricher', 'road', 'mag_tube'},
        'requires': set(),
        'action_type': 'add',
        'yields': {},
        'description': 'Covers tile in fungus; movement hindrance',
    },

    # --- Extraction slot (mutually exclusive, but stackable with cover) ---

    'mine': {
        'id': 'mine',
        'name': 'Mine',
        'hotkey': 'm',
        'base_turns': 8,
        'terrain': 'land',
        'prereq': None,
        'slot': 'extraction',
        'replaces': {'condenser', 'echelon_mirror', 'soil_enricher'},
        'requires': set(),
        'action_type': 'add',
        # +1 mineral normally; +2 on rocky; +1 more with road on rocky
        'yields': {'minerals': 1, 'minerals_rocky_bonus': 1},
        'description': '+1 mineral; +2 on rocky; +3 on rocky with road',
    },

    'solar': {
        'id': 'solar',
        'name': 'Solar Collector',
        'hotkey': 's',
        'base_turns': 4,
        'terrain': 'land',
        'prereq': None,
        'slot': 'extraction',
        'replaces': {'condenser', 'echelon_mirror', 'soil_enricher'},
        'requires': set(),
        'action_type': 'add',
        # Produces altitude-tier energy (same table as base: <1000m=1, 1000m=2, etc.)
        'yields': {'energy_altitude': True},
        'description': '+1–4 energy depending on altitude',
    },

    'condenser': {
        'id': 'condenser',
        'name': 'Condenser',
        'hotkey': 'n',
        'base_turns': 12,
        'terrain': 'land',
        'prereq': 'EcoEng',    # Ecological Engineering
        'slot': 'extraction',
        'replaces': {'mine', 'solar', 'echelon_mirror', 'soil_enricher'},
        'requires': set(),
        'action_type': 'add',
        # +50% nutrient production on this tile; also raises rainfall of adjacent tiles
        'yields': {'nutrients_multiplier': 1.5},
        'description': '+50% nutrients; raises rainfall of adjacent tiles; eco-damage',
    },

    'echelon_mirror': {
        'id': 'echelon_mirror',
        'name': 'Echelon Mirror',
        'hotkey': 'E',
        'base_turns': 12,
        'terrain': 'land',
        'prereq': 'EcoEng',    # Ecological Engineering
        'slot': 'extraction',
        'replaces': {'mine', 'solar', 'condenser', 'soil_enricher'},
        'requires': set(),
        'action_type': 'add',
        # Same base energy as a Solar Collector; +1 to adjacent Solar Collectors
        'yields': {'energy_altitude': True, 'energy_adjacent_solar': 1},
        'description': 'Energy = Solar Collector value; +1 to adjacent solar; eco-damage',
    },

    'soil_enricher': {
        'id': 'soil_enricher',
        'name': 'Soil Enricher',
        'hotkey': 'f',
        'base_turns': 8,
        'terrain': 'land',
        'prereq': 'EcoEng2',   # Advanced Ecological Engineering
        'slot': 'extraction',
        'replaces': {'mine', 'solar', 'condenser', 'echelon_mirror'},
        'requires': {'farm'},
        'action_type': 'add',
        # +50% food production (stacks with farm's flat +1)
        'yields': {'nutrients_multiplier': 1.5},
        'description': '+50% nutrients; requires Farm',
    },

    # Borehole — exclusive: clears cover and extraction on placement

    'borehole': {
        'id': 'borehole',
        'name': 'Thermal Borehole',
        'hotkey': 'B',
        'base_turns': 24,
        'terrain': 'land',
        'prereq': 'EcoEng',    # Ecological Engineering
        'slot': 'borehole',
        'replaces': {'farm', 'forest', 'fungus', 'mine', 'solar',
                     'condenser', 'echelon_mirror', 'soil_enricher'},
        'requires': set(),
        'action_type': 'add',
        'yields': {'fixed': (0, 6, 6)},
        'description': 'Fixed 0N/6M/6E; massive eco-damage',
    },

    # --- Removal actions (action_type='remove') ---

    'remove_fungus': {
        'id': 'remove_fungus',
        'name': 'Remove Fungus',
        'hotkey': 'f',
        'base_turns': 6,
        'terrain': 'land',
        'prereq': None,
        'slot': None,
        'replaces': set(),
        'requires': {'fungus'},
        'action_type': 'remove',
        'yields': {},
        'removes_improvement': 'fungus',
        'description': 'Removes fungus from tile',
    },

    # --- Terrain modification actions (action_type='terraform') ---

    'level_terrain': {
        'id': 'level_terrain',
        'name': 'Level Terrain',
        'hotkey': 'l',
        'base_turns': 8,
        'terrain': 'land',
        'prereq': None,
        'slot': None,
        'replaces': set(),
        'requires': set(),
        'action_type': 'terraform',
        # Reduces rockiness by one step: rocky → rolling → flat
        'terraform_effect': {'rockiness': -1},
        'yields': {},
        'description': 'Rocky → Rolling, or Rolling → Flat',
    },

    'raise_land': {
        'id': 'raise_land',
        'name': 'Raise Land',
        'hotkey': ']',
        'base_turns': 12,
        'terrain': 'land',
        'prereq': 'EnvEcon',   # Environmental Economics
        'slot': None,
        'replaces': set(),
        'requires': set(),
        'action_type': 'terraform',
        'terraform_effect': {'altitude': +1000},
        'yields': {},
        'description': 'Raises elevation ~1000m; costs energy credits',
    },

    'lower_land': {
        'id': 'lower_land',
        'name': 'Lower Land',
        'hotkey': '[',
        'base_turns': 12,
        'terrain': 'land',
        'prereq': 'EnvEcon',   # Environmental Economics
        'slot': None,
        'replaces': set(),
        'requires': set(),
        'action_type': 'terraform',
        'terraform_effect': {'altitude': -1000},
        'yields': {},
        'description': 'Lowers elevation ~1000m; costs energy credits',
    },

    # --- One-time tile modification (action_type='modify_tile') ---

    'aquifer': {
        'id': 'aquifer',
        'name': 'Drill Aquifer',
        'hotkey': 'q',
        'base_turns': 18,
        'terrain': 'land',
        'prereq': 'EcoEng',    # Ecological Engineering
        'slot': None,
        'replaces': set(),
        'requires': set(),
        'action_type': 'modify_tile',
        'tile_flag': 'has_river',
        'yields': {'energy': 1},
        'description': 'Creates a river; +1 energy to this and adjacent tiles',
    },

    # ---------------------------------------------------------------------------
    # Ocean improvements
    # ---------------------------------------------------------------------------

    'kelp_farm': {
        'id': 'kelp_farm',
        'name': 'Kelp Farm',
        'hotkey': 'f',   # same as land farm — context-gated by terrain
        'base_turns': 4,
        'terrain': 'ocean',
        'prereq': 'CentEco',   # Centauri Ecology
        'slot': 'ocean_cover',
        'replaces': {'sea_fungus'},
        'requires': set(),
        'action_type': 'add',
        'yields': {'nutrients': 2},
        'description': '+2 nutrients; spreads to adjacent ocean tiles',
    },

    'sea_fungus': {
        'id': 'sea_fungus',
        'name': 'Sea Fungus',
        'hotkey': 'Ctrl+f',   # same as land fungus — context-gated by terrain
        'base_turns': 6,
        'terrain': 'ocean',
        'prereq': 'EcoEng',
        'slot': 'ocean_cover',
        'replaces': {'kelp_farm'},
        'requires': set(),
        'action_type': 'add',
        'yields': {},
        'description': 'Sea fungus; movement hindrance',
    },

    'remove_sea_fungus': {
        'id': 'remove_sea_fungus',
        'name': 'Remove Sea Fungus',
        'hotkey': 'f',   # same as remove_fungus — context-gated
        'base_turns': 6,
        'terrain': 'ocean',
        'prereq': None,
        'slot': None,
        'replaces': set(),
        'requires': {'sea_fungus'},
        'action_type': 'remove',
        'yields': {},
        'removes_improvement': 'sea_fungus',
        'description': 'Removes sea fungus from tile',
    },

    'mining_platform': {
        'id': 'mining_platform',
        'name': 'Mining Platform',
        'hotkey': 'm',   # same as mine — context-gated by terrain
        'base_turns': 8,
        'terrain': 'ocean',
        'prereq': 'IndEcon',   # Industrial Economics
        'slot': 'ocean_extraction',
        'replaces': {'tidal_harness'},
        'requires': set(),
        'action_type': 'add',
        'yields': {'nutrients': -1, 'minerals': 1},
        'description': '-1 nutrient, +1 mineral',
    },

    'tidal_harness': {
        'id': 'tidal_harness',
        'name': 'Tidal Harness',
        'hotkey': 's',
        'base_turns': 4,
        'terrain': 'ocean',
        'prereq': 'DocInit',   # Doctrine: Initiative
        'slot': 'ocean_extraction',
        'replaces': {'mining_platform'},
        'requires': set(),
        'action_type': 'add',
        'yields': {'energy': 3},
        'description': '+3 energy',
    },
}

# ---------------------------------------------------------------------------
# Slot exclusivity groups
# Tiles may have at most one improvement per slot (except 'infrastructure').
# ---------------------------------------------------------------------------

EXCLUSIVE_SLOTS = {'cover', 'extraction', 'borehole', 'ocean_cover', 'ocean_extraction'}

# ---------------------------------------------------------------------------
# Build-time speed modifiers
# Applied multiplicatively to base_turns.
# ---------------------------------------------------------------------------

SPEED_MODIFIERS = {
    'super_former': 0.5,      # Super Former ability halves build time
    'fungicide_tanks': 0.5,   # Fungicide Tanks halves remove_fungus/sea_fungus time
}

# ---------------------------------------------------------------------------
# Hotkey → improvement ID lookup (for quick dispatch in main.py)
# Land and ocean share some keys; callers must filter by tile.is_ocean().
# ---------------------------------------------------------------------------

LAND_HOTKEYS = {imp['hotkey']: key
                for key, imp in IMPROVEMENTS.items()
                if imp['terrain'] in ('land', 'both')}

OCEAN_HOTKEYS = {imp['hotkey']: key
                 for key, imp in IMPROVEMENTS.items()
                 if imp['terrain'] in ('ocean', 'both')}

# Single-character map indicators shown on units that are actively terraforming.
# These are display letters, not hotkeys — some differ to avoid collisions
# (e.g. forest uses 'o' so 'f' stays unambiguous for farm).
TERRAFORM_MAP_LETTERS = {
    'farm': 'f', 'forest': 'o', 'mine': 'm', 'solar': 's',
    'road': 'r', 'mag_tube': 't', 'sensor_array': 'n',
    'borehole': 'b', 'condenser': 'c', 'echelon_mirror': 'e',
    'soil_enricher': 'l', 'remove_fungus': 'x',
    'raise_land': '+', 'lower_land': '-', 'level_terrain': 'v',
    'aquifer': 'q', 'bunker': 'k', 'airbase': 'a',
    'kelp_farm': 'f', 'mining_platform': 'm', 'tidal_harness': 's',
    'remove_sea_fungus': 'x',
}
