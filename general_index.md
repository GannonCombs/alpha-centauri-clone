# Alpha Centauri Clone - File Index

## Entry Point

**main.py**
Entry point and main game loop. Initializes Pygame with dynamic screen sizing, manages the 60 FPS game loop, handles keyboard/mouse input, coordinates AI turn processing, and renders all game layers (map, bases, units, UI, status messages) in correct order.

## Core Game Package (game/)

All game logic resides in the `game/` package, organized into modules by responsibility.

### Core Game Systems

**game/game.py**
Core game state manager. Handles unit spawning and movement, base founding with adjacency validation, garrison mechanics, status messages, click handling for units and bases, and AI turn sequencing with base growth processing. Coordinates with the Combat system for battle resolution. Processes automatic end-of-turn healing for all factions using the repair module. Applies Command Center morale bonus (+2 additive, capped at Elite) to land units produced at bases with Command Centers.

**game/turn_manager.py**
Turn sequencing system extracted from game.py. Handles the full turn cycle: auto-cycle to next unit, auto-end-turn detection, end_turn (reset player units, increment year, start AI processing), process_ai_turns (AI base/tech/commerce/upkeep loop), upkeep event collection and advancement, and _start_new_turn (spawns production, increments turn counter). Accessed via game.turns.

**game/map.py**
Map generation and tile management. Tile class stores terrain type, resources, improvements, units, and bases. GameMap class generates procedural land/ocean distribution and provides safe coordinate access with bounds checking.

**game/base.py**
Base (city) class with population growth mechanics. Tracks population, nutrients accumulation, progressive growth requirements, garrison units, production queue, facilities, and processes turn-based growth automatically. Provides get_garrison_units() method for dynamic garrison calculation from tile units instead of cached garrison list.

**game/faction.py**
Faction state management. Defines the Faction class containing all per-faction game state: tech tree, unit designs (UnitDesign), energy credits, diplomatic relations, contacts, and AI personality/strategic state. Provides get_voting_power() with Empath Guild, Clinical Immortality, and Lal's double-vote bonuses. Planet Buster atrocity revokes voting rights.

**game/ai.py**
Classic rule-based AI using decision-making algorithms. Colony pods find good base locations, military units pursue player targets or explore randomly.

**game/tech.py**
Technology tree system with progressive discovery of technologies. Tracks research progress, calculates turns until completion, manages completed technologies, and processes research each turn for both player and AI.

**game/territory.py**
Territory control system calculating ownership based on proximity to bases. Extends 7 tiles from each base using Manhattan distance, resolves ties (same owner wins, different owners use population tiebreaker), tracks border edges, and updates when new bases are founded.

**game/renderer.py**
Rendering system with horizontal centering for the map display. Draws tiles with terrain colors, bases with population indicators in top-left corner, units with type letters (L/S/C), status messages at bottom of map, and provides screen-to-tile coordinate conversion plus population square click detection.

**game/save_load.py**
Save and load game system. Serializes game state to JSON files and restores complete game state including map, units, bases, technology, and faction data.

**game/facilities.py**
Facility management system. Handles base facilities and secret projects, including construction, maintenance costs, and special effects.

**game/social_engineering.py**
Social Engineering system managing Politics, Economics, Values, and Future Society choices. Calculates stat modifiers and enforces faction restrictions. Reads from SE_DATA in social_engineering_data.py.

**game/terraforming.py**
Terraforming system for Former units. Handles all former action types: add improvements, remove improvements (fungus), terraform (raise/lower land, level terrain), and modify_tile (aquifer/river). Calculates tile resource yields including improvement bonuses, fixed yields (borehole/forest), altitude-tier energy, and rocky mine bonuses.

**game/commerce.py**
Commerce income system. CommerceCalculator pairs faction bases by energy output and generates commerce pools divided by economic tech count. Handles Treaty (halved) vs Pact (full) income, Global Trade Pact doubling, Planetary Governor +1 bonus, Morgan faction +1 bonus, and atrocity sanctions. Called once per turn during upkeep.

**game/atrocity.py**
Atrocity system for war crimes committed by the player. Simple atrocities (nerve_staple, nerve_gas, genetic_warfare, obliterate_base): commerce sanctions for 10×count turns, target faction permanently hostile (Vendetta), integrity drops one level. Major atrocity (planet_buster): all of the above plus every faction immediately declares Vendetta and player vote count permanently becomes 0. Integrity levels: Noble → Faithful → Scrupulous → Dependable → Ruthless → Treacherous.

**game/score.py**
Score computation system. Components: (1) 1pt per citizen in player bases, (2) diplomatic/economic victory bonus for allied/neutral faction citizens, (3) 1pt per citizen in surrendered bases, (4) 1pt per commerce income unit, (5) 1pt per tech discovered, (6) 10pts for Transcendent Thought, (7) 25pts per secret project, (8) victory type bonus minus 2pts/turn elapsed, (9) native life multiplier (rare −25%, abundant +25%). Iron Man modifier not yet implemented.

**game/governor.py**
Governor system for automated base production selection. Four modes: BUILD (defensive units, happiness/resource facilities, infrastructure), CONQUER (offensive military, Command Center), DISCOVER (science facilities, probe teams, research secret projects), EXPLORE (colony pods, scouts, formers). Used by both player-toggled base governors and AI faction production logic.

**game/commlink_text.py**
Dialog system for talking with other factions. Handles variable substitution in dialog text using faction-specific flavor text and context.

**game/debug.py**
Debug/cheat mode for testing game features. Press Ctrl+Shift+D to toggle debug mode. Provides shortcuts for spawning units, bases, completing technologies, and other testing utilities. All debug code isolated here for easy removal before release.

## Units Package (game/units/)

Unit logic, combat, movement, and design systems.

**game/units/unit.py**
Unit class for all mobile game entities. Supports land units, sea units, and air units. Handles movement points, terrain restrictions, turn resets, garrison status, ownership tracking, and combat calculations with weapon/armor/reactor components.

**game/units/unit_components.py**
Unit component system for the Design Workshop. Provides utilities for chassis, weapons, armor, and reactors. Generates unit names based on component combinations and handles unit design validation.

**game/units/unit_design.py**
Per-faction unit design storage. Defines the UnitDesign class with 64 design slots (SMAC-style). Initializes faction-specific starting designs (e.g. Former for Gaians, Rover for Spartans). Provides add/remove/get/set design methods.

**game/units/combat.py**
Combat resolution system handling all battle mechanics. Calculates combat modifiers using formula-based morale (+12.5% per level above Green), terrain, facilities, and special abilities. Implements combat bonuses: mobile units (speeder/hovertank) get +25% vs infantry in open terrain, infantry get +25% attacking bases, artillery gets +25% per 1000m altitude advantage vs land units or +50% vs ships. Computes combat odds for predictions, simulates round-by-round combat with 1-3 damage per hit, manages unit disengagement when damaged below 50% HP, handles retreat movement, and coordinates battle animations. Maintains pending_battle (player confirmation) and active_battle (ongoing animation) state.

**game/units/movement.py**
Unit movement manager (MovementManager). Handles try_move_unit, terrain movement costs, zone of control, fungus movement probability, sea/air unit restrictions, supply pod collection, and unit stacking rules. Accessed via game.movement.

**game/units/repair.py**
Unit repair and healing system implementing full SMAC repair formula. Base 10% healing per turn with additive +10% bonuses for: friendly territory, base location, airbase, bunker, fungus tiles. Full repair facilities: Command Center (land units), Naval Yard (sea units), Aerospace Complex (air units), Biology Lab (native units). Special cases: Nano Factory provides 100% repair anywhere, Monoliths provide instant 100% repair. Caps at 80% healing in field or 100% in bases.

## Data Package (game/data/)

Centralized data definitions for all game content.

**game/data/display_data.py**
Display and rendering configuration values. Defines TILE_SIZE (70px), FPS (60), UI_PANEL_HEIGHT, runtime-initialized screen dimensions (SCREEN_WIDTH/HEIGHT/MAP_AREA_HEIGHT/UI_PANEL_Y set by main.py), all color constants (ocean, land variants by rainfall, grid, UI elements, council), and timing constants (AI_TURN_DELAY, SCROLL_DELAY).

**game/data/faction_data.py**
Master data file containing SMAC faction definitions (Gaians, Hive, University, Morganites, Spartans, Believers, Peacekeepers) with leader names, colors, starting techs, bonuses, base names, and extensive flavor text for diplomacy.

**game/data/unit_data.py**
Unit component definitions for the Design Workshop. Defines CHASSIS (infantry, speeder, hovertank, foil, cruiser, needlejet, copter, gravship, missile), WEAPONS (colony pod, terraforming, hand weapons through planet buster), ARMOR (no armor through stasis generator), REACTORS (fission through singularity), and SPECIAL_ABILITIES. Each includes tech prerequisites, costs, and combat stats.

**game/data/citizen_data.py**
Citizen specialist data. SPECIALISTS list defines specialists who don't work tiles but provide fixed bonuses (Doctor, Technician, Librarian, Empath, Engineer, Thinker, Transcend) with economy/labs/psych output values, population minimums, and tech prerequisites.

**game/data/facility_data.py**
Base facility and secret project definitions. FACILITIES array includes all buildable improvements (Headquarters, Recycling Tanks, Network Node, etc.) with costs, maintenance, tech prerequisites, and effects. SECRET_PROJECTS array defines unique wonders (Human Genome Project, Weather Paradigm, etc.) with global effects.

**game/data/tech_tree_data.py**
Technology tree data. Defines all available technologies with names, categories, prerequisites, research costs, and unlock effects for new units, facilities, and abilities.

**game/data/social_engineering_data.py**
Social Engineering choice data. SE_DATA dict maps each category (Politics, Economics, Values, Future Society) to a list of choices, each with name, tech prerequisite, and effects dict (STAT → value). Single unified structure used by both the social_engineering logic module and the SocialEngineeringScreen UI.

**game/data/council_proposal_data.py**
Planetary Council proposal definitions. PROPOSALS list defines all votable proposals (Governor, Unity Core, Trade Pact, etc.) with effects and requirements.

**game/data/terraforming_data.py**
Terraforming improvement definitions. IMPROVEMENTS dict defines all land and ocean improvements (farm, mine, solar, road, mag tube, borehole, forest, fungus, condenser, echelon mirror, soil enricher, sensor array, bunker, airbase, kelp farm, mining platform, tidal harness, etc.) with hotkeys, build times, terrain requirements, tech prerequisites, slot assignments, resource yields, and action types. Also defines EXCLUSIVE_SLOTS, SPEED_MODIFIERS, land/ocean hotkey maps, and TERRAFORM_MAP_LETTERS for in-game display.

**game/data/commlink_text_data.py**
Commlink dialogue data. Contains the complete dialogue tree for faction communications including greetings, diplomatic proposals, threats, and context-specific responses. Supports variable substitution for personalized faction interactions.

## UI Package (game/ui/)

All user interface screens and components, organized into screens/ and dialogs/ subdirectories.

**game/ui/ui_manager.py**
Comprehensive UI system orchestrating all game screens. Manages main game panel (turn counter, unit info, End Turn button), screen transitions, and coordinates rendering of all UI elements. Central hub for UI state management. Directly instantiates all screen and dialog classes.

**game/ui/components.py**
Reusable UI components. Buttons, text boxes, lists, and other common UI elements used across multiple screens.

**game/ui/context_menu.py**
Right-click context menu system. Provides contextual actions for units, bases, and terrain tiles with keyboard shortcuts.

### Screens (game/ui/screens/)

Full-screen interfaces that replace the main game view.

**game/ui/screens/base_screen.py**
Base management interface (BaseScreen). Displays population growth, garrison units (with "H" indicator for held units), production queue, facility list, unit support costs, and nutrient/mineral/energy calculations. Provides production selection and facility management. Right-click garrison units to open context menu with Activate option for unheld and selecting held units.

**game/ui/screens/social_engineering_screen.py**
Social Engineering interface (SocialEngineeringScreen) with four categories: Politics, Economics, Values, and Future Society. Shows stat effects, enforces tech prerequisites, displays energy allocation meters, and calculates the credit cost of changing policies.

**game/ui/screens/tech_tree_screen.py**
Technology tree viewer (TechTreeScreen). Displays all available technologies in a visual tree layout, shows prerequisites, research progress, and allows selecting research priorities.

**game/ui/screens/design_workshop_screen.py**
Unit Design Workshop (DesignWorkshopScreen). Allows selection of chassis, weapon, armor, and reactor components. Shows unit stats, costs, and validates designs against available technologies.

**game/ui/screens/diplomacy_screen.py**
Diplomacy interface (DiplomacyScreen). Handles commlink communications, treaty proposals, pact negotiations, and diplomatic status displays.

**game/ui/screens/council_screen.py**
Planetary Council voting system (CouncilScreen). Manages proposal submission, vote tallying, and election of Planetary Governor. Tracks voting power based on population and displays results.

**game/ui/screens/intro_screen.py**
Game startup screen (IntroScreen). Displays faction leaders, bonuses, and starting technologies. Allows player to choose their faction before beginning the game.

### Dialogs (game/ui/dialogs/)

Modal popups that overlay the current screen.

**game/ui/dialogs/combat_dialog.py**
Combat interface (CombatDialog). Shows attacker and defender stats, calculates combat odds, displays terrain and facility bonuses as a pre-battle prediction modal. Also draws the in-progress battle animation panel.

**game/ui/dialogs/supply_pod_dialog.py**
Unity Supply Pod discovery popup (SupplyPodDialog). Displays the reward message when a unit opens a supply pod.

**game/ui/dialogs/save_load_dialog.py**
Save and load game dialogs (SaveLoadDialog). Provides file browser for saved games, displays save metadata (turn, faction, date), and handles save/load operations with error handling.

**game/ui/dialogs/exit_dialog.py**
Exit/menu confirmation dialog (ExitDialog). Prompts user before quitting or returning to main menu.

## Notes (game/notes/)

Development notes and planning documents.

**game/notes/datalinks.md**
Authoritative SMAC rules reference. Comprehensive documentation of game mechanics including combat formulas, resource calculations, facility effects, social engineering, and other gameplay systems. Should be read before implementing any game mechanic.

**game/notes/diplomacyNotes.txt**
Diplomacy system design notes and SMAC reference material.

**game/notes/terraforming.txt**
Terraforming reference notes from the original SMAC. Documents all terraforming improvements with SMAC prerequisites, build times, and effects. Used as reference when implementing and validating the terraforming system.

**game/notes/unitState.txt**
Unit state behavior documentation. Describes hold, board/transport, disembark, and busy-unit mechanics with expected behavior for each state transition.

**game/notes/ARTILLERY.txt**
Artillery and bombardment system design notes.

**game/notes/DEBUG_MODE.txt**
Debug mode feature documentation and usage guide.

**game/notes/FEATURES_IMPLEMENTED.txt**
Master list of all implemented features and known stubs.

**game/notes/checklists/**
Subdirectory containing implementation checklists for tracking completion status of game content.

**game/notes/checklists/todo.txt**
Current development tasks, planned features, and known bugs. Primary bug tracking list — only add checkmarks here, do not remove entries.

**game/notes/checklists/concept_implementation_checklist.txt**
Checklist of basic game concepts (rainfall, terrain, etc.) to track which have been implemented to SMAC accuracy.

**game/notes/checklists/tech_implementation_checklist.txt**
Checklist of all 78 technologies from the tech tree. Used to track which techs have been fully implemented, which are waiting on features, and which remain to be implemented.

**game/notes/checklists/facility_implementation_checklist.txt**
Checklist of all 38 base facilities. Used to track which facilities have been fully implemented, which are waiting on features (e.g., drones, specialists), and which remain to be implemented.

**game/notes/checklists/secret_project_implementation_checklist.txt**
Checklist of all 33 secret projects (wonders). Used to track which projects have been fully implemented, which are waiting on features (e.g., fungus, social engineering effects), and which remain to be implemented.

**game/notes/smacNotes/**
Subdirectory containing original SMAC reference material (alpha.txt, concepts.txt, Script.txt).

**game/notes/factionNotes/**
Subdirectory for faction-specific design notes and flavor text research. Contains original SMAC faction files: BELIEVE.TXT, GAIANS.TXT, HIVE.TXT, MORGAN.TXT, PEACE.TXT, SPARTANS.TXT, UNIV.TXT.

## Documentation

**README.md**
Comprehensive project documentation including feature list (turn-based gameplay, base management, AI, Social Engineering), installation instructions, complete controls reference, and detailed gameplay guide covering base founding, unit management, population growth mechanics, and turn system.

**requirements.txt**
Python package dependencies file specifying pygame==2.6.1 as the sole required library.

**CLAUDE.md**
Context file for Claude Code containing project description, technical stack, development approach, and reference to general_index.md for file documentation.

**general_index.md**
This file - comprehensive index of all project files with detailed descriptions of functionality.

## Configuration

**.claude/settings.local.json**
Claude Code settings file that permits Python compilation (py_compile) for development environment configuration.

## Auto-Generated

**__pycache__/**
Python bytecode cache directory with compiled .pyc files for faster module loading across Python versions.

**venv/**
Python virtual environment containing pygame library, pip package manager, and all project dependencies.

**.idea/**
IntelliJ IDEA/PyCharm IDE configuration directory with workspace settings, module configuration, and inspection profiles.

**game/saves/**
Directory for saved game files in JSON format.
