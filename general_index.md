# Alpha Centauri Clone - File Index

## Entry Point

**main.py**
Entry point and main game loop. Initializes Pygame with dynamic screen sizing, manages the 60 FPS game loop, handles keyboard/mouse input (SPACE ends unit movement, healing is automatic at turn end), coordinates AI turn processing, and renders all game layers (map, bases, units, UI, status messages) in correct order.

## Core Game Package (game/)

All game logic resides in the `game/` package, organized into modules by responsibility.

### Core Game Systems

**game/game.py**
Core game state manager. Handles unit spawning and movement, base founding with adjacency validation, turn management (player → AI → new turn), garrison mechanics, status messages, click handling for units and bases, and AI turn sequencing with base growth processing. Coordinates with the Combat system for battle resolution. Processes automatic end-of-turn healing for all factions using the repair module. Applies Command Center morale bonus (+2 additive, capped at Elite) to land units produced at bases with Command Centers.

**game/map.py**
Map generation and tile management. Tile class stores terrain type, resources, improvements, units, and bases. GameMap class generates procedural land/ocean distribution and provides safe coordinate access with bounds checking.

**game/unit.py**
Unit class for all mobile game entities. Supports land units, sea units, and air units. Handles movement points, terrain restrictions, turn resets, garrison status, ownership tracking, and combat calculations with weapon/armor/reactor components.

**game/base.py**
Base (city) class with population growth mechanics. Tracks population, nutrients accumulation, progressive growth requirements, garrison units, production queue, facilities, and processes turn-based growth automatically. Provides get_garrison_units() method for dynamic garrison calculation from tile units instead of cached garrison list.

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
Social Engineering system managing Politics, Economics, Values, and Future Society choices. Calculates stat modifiers and enforces faction restrictions.

**game/unit_components.py**
Unit component system for the Design Workshop. Provides utilities for chassis, weapons, armor, and reactors. Generates unit names based on component combinations and handles unit design validation.

**game/combat.py**
Combat resolution system handling all battle mechanics. Calculates combat modifiers using formula-based morale (+12.5% per level above Green), terrain, facilities, and special abilities. Implements combat bonuses: mobile units (speeder/hovertank) get +25% vs infantry in open terrain, infantry get +25% attacking bases, artillery gets +25% per 1000m altitude advantage vs land units or +50% vs ships. Computes combat odds for predictions, simulates round-by-round combat with 1-3 damage per hit, manages unit disengagement when damaged below 50% HP, handles retreat movement, and coordinates battle animations. Maintains pending_battle (player confirmation) and active_battle (ongoing animation) state.

**game/repair.py**
Unit repair and healing system implementing full SMAC repair formula. Base 10% healing per turn with additive +10% bonuses for: friendly territory, base location, airbase, bunker, fungus tiles. Full repair facilities: Command Center (land units), Naval Yard (sea units), Aerospace Complex (air units), Biology Lab (native units). Special cases: Nano Factory provides 100% repair anywhere, Monoliths provide instant 100% repair. Caps at 80% healing in field or 100% in bases. Provides calculate_healing() function returning heal amount, eligibility, reason, and full repair flag.

**game/commlink_text.py**
Dialog system for talking with other factions. Handles variable substitution in dialog text using faction-specific flavor text and context.

**game/debug.py**
Debug/cheat mode for testing game features. Press Ctrl+Shift+D to toggle debug mode. Provides shortcuts for spawning units, bases, completing technologies, and other testing utilities. All debug code isolated here for easy removal before release.

## Data Package (game/data/)

Centralized data definitions for all game content.

**game/data/constants.py**
Game-wide constants and configuration. Defines tile size, screen dimensions, FPS, color definitions for rendering (ocean, land, UI elements), unit type constants, and timing parameters for AI turns and scrolling.

**game/data/data.py**
Master data file containing SMAC faction definitions (Gaians, Hive, University, Morganites, Spartans, Believers, Peacekeepers) with leader names, colors, starting techs, bonuses, base names, and extensive flavor text for diplomacy. Also defines Council PROPOSALS (Governor, Unity Core, Trade Pact, etc.) and SE_EFFECTS for Social Engineering modifiers.

**game/data/facility_data.py**
Base facility and secret project definitions. FACILITIES array includes all buildable improvements (Headquarters, Recycling Tanks, Network Node, etc.) with costs, maintenance, tech prerequisites, and effects. SECRET_PROJECTS array defines unique wonders (Human Genome Project, Weather Paradigm, etc.) with global effects.

**game/data/unit_data.py**
Unit component definitions for the Design Workshop. Defines CHASSIS (infantry, speeder, hovertank, foil, cruiser, needlejet, copter, gravship, missile), WEAPONS (colony pod, terraforming, hand weapons through planet buster), ARMOR (no armor through stasis generator), and REACTORS (fission, fusion, quantum, singularity). Each includes tech prerequisites, costs, and combat stats.

**game/data/tech_tree_data.py**
Technology tree data. Defines all available technologies with names, categories, prerequisites, research costs, and unlock effects for new units, facilities, and abilities.

**game/data/social_engineering_data.py**
Social Engineering choices data. Defines available options for Politics, Economics, Values, and Future Society categories with associated stat modifiers and restrictions.

**game/data/commlink_text_data.py**
Commlink dialogue data. Contains the complete dialogue tree for faction communications including greetings, diplomatic proposals, threats, and context-specific responses. Supports variable substitution for personalized faction interactions.

## UI Package (game/ui/)

All user interface screens and components.

**game/ui/ui_manager.py**
Comprehensive UI system orchestrating all game screens. Manages main game panel (turn counter, unit info, End Turn button), screen transitions, and coordinates rendering of all UI elements. Central hub for UI state management.

**game/ui/base_screens.py**
Base management interface. Displays population growth, garrison units (with "H" indicator for held units), production queue, facility list, unit support costs, and nutrient/mineral/energy calculations. Provides production selection and facility management. Right-click garrison units to open context menu with Activate option for unheld and selecting held units.

**game/ui/social_engineering_screen.py**
Social Engineering interface with four categories: Politics (Frontier/Police State/Democratic/Fundamentalist), Economics (Simple/Free Market/Planned/Green), Values (Survival/Power/Knowledge/Wealth), and Future Society (None/Cybernetic/Eudaimonic/Thought Control). Shows stat effects and enforces faction restrictions.

**game/ui/diplomacy.py**
Diplomacy interface for interacting with AI factions. Handles commlink communications, treaty proposals, pact negotiations, and diplomatic status displays.

**game/ui/council.py**
Planetary Council voting system. Manages proposal submission, vote tallying, and election of Planetary Governor. Tracks voting power based on population and displays results.

**game/ui/tech_tree_screen.py**
Technology tree viewer. Displays all available technologies in a visual tree layout, shows prerequisites, research progress, and allows selecting research priorities.

**game/ui/design_workshop_screen.py**
Unit Design Workshop for creating custom units. Allows selection of chassis, weapon, armor, and reactor components. Shows unit stats, costs, and validates designs against available technologies.

**game/ui/intro_screen.py**
Game startup screen with faction selection. Displays faction leaders, bonuses, and starting technologies. Allows player to choose their faction before beginning the game.

**game/ui/battle_ui.py**
Combat interface for unit battles. Shows attacker and defender stats, calculates combat odds, displays terrain and facility bonuses, and presents battle results with damage calculations.

**game/ui/save_load_dialog.py**
Save and load game dialogs. Provides file browser for saved games, displays save metadata (turn, faction, date), and handles save/load operations with error handling.

**game/ui/exit_dialog.py**
Exit confirmation dialog. Prompts user before quitting, offers save option, and handles clean game exit.

**game/ui/dialogs.py**
Generic dialog components and utilities. Provides reusable dialog boxes for confirmations, alerts, and user input.

**game/ui/components.py**
Reusable UI components. Buttons, text boxes, lists, and other common UI elements used across multiple screens.

**game/ui/context_menu.py**
Right-click context menu system. Provides contextual actions for units, bases, and terrain tiles with keyboard shortcuts.

**game/ui/social_screens.py**
Additional social/political interfaces. Handles faction relationships, reputation tracking, and social dynamics displays.

## Notes (game/notes/)

Development notes and planning documents.

**game/notes/todo.txt**
Current development tasks and planned features.

**game/notes/diplomacyNotes.txt**
Diplomacy system design notes and SMAC reference material.

**game/notes/AI_GARRISON_PLAN.txt**
AI garrison mechanics planning document.

**game/notes/ARTILLERY.txt**
Artillery and bombardment system design notes.

**game/notes/DEBUG_MODE.txt**
Debug mode feature documentation and usage guide.

**game/notes/FEATURES_COMPLETE_SESSION_2.txt**
Log of completed features from development session 2.

**game/notes/FEATURES_IMPLEMENTED.txt**
Master list of all implemented features.

**game/notes/UNIT_STACKING_PLAN.txt**
Unit stacking system design and implementation plan.

**game/notes/holdNotes.txt**
Temporary notes and ideas on hold.

**game/notes/checklists/**
Subdirectory containing implementation checklists for tracking completion status of game content.

**game/notes/checklists/tech_implementation_checklist.txt**
Checklist of all 78 technologies from the tech tree. Used to track which techs have been fully implemented, which are waiting on features, and which remain to be implemented.

**game/notes/checklists/facility_implementation_checklist.txt**
Checklist of all 38 base facilities. Used to track which facilities have been fully implemented, which are waiting on features (e.g., drones, specialists), and which remain to be implemented.

**game/notes/checklists/secret_project_implementation_checklist.txt**
Checklist of all 33 secret projects (wonders). Used to track which projects have been fully implemented, which are waiting on features (e.g., fungus, social engineering effects), and which remain to be implemented.

**game/notes/smacNotes/**
Subdirectory containing original SMAC reference material (alpha.txt, concepts.txt, Script.txt).

**game/notes/factionNotes/**
Subdirectory for faction-specific design notes and flavor text research.

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
