# Alpha Centauri Clone - File Index

## Source Files

**main.py**
Entry point and main game loop. Initializes Pygame with dynamic screen sizing, manages the 60 FPS game loop, handles keyboard/mouse input, coordinates AI turn processing with 500ms delays, and renders all game layers (map, bases, units, UI, status messages) in correct order.

**game.py**
Core game state manager. Handles unit spawning and movement, base founding with adjacency validation, turn management (player → AI → new turn), garrison mechanics, status messages, click handling for units and bases, and AI turn sequencing with base growth processing.

**constants.py**
Centralized configuration defining all game-wide constants: map dimensions (dynamically sized to screen), tile size (70px), colors for units/bases/UI, unit type constants (land, sea, colony pods), and game parameters like land probability and FPS.

**map.py**
Map generation and tile management. Tile class stores terrain type, resources, improvements, units, and bases. GameMap class generates procedural land/ocean distribution and provides safe coordinate access with bounds checking.

**unit.py**
Unit class for all mobile game entities. Supports land units, sea units, air units, and colony pods (land/sea variants). Handles movement points, terrain restrictions, turn resets, garrison status, and ownership tracking.

**base.py**
Base (city) class with population growth mechanics. Tracks population (1-7 max), nutrients accumulation (1 per turn), progressive growth requirements (7, 10, 14, 19, 25, 32 nutrients), garrison units, production queue, facilities, and processes turn-based growth automatically.

**ai.py**
Classic rule-based AI using 1990s decision-making algorithms. Colony pods find good base locations with proper spacing (no adjacent bases), military units pursue player targets or explore randomly, movement uses greedy pathfinding with Manhattan distance calculations.

**tech.py**
Technology tree system with linear progression through 20 technologies. Tracks research progress (1 point per turn), calculates turns until completion, manages completed technologies, and processes research each turn for both player and AI.

**territory.py**
Territory control system calculating ownership based on proximity to bases. Extends 7 tiles from each base using Manhattan distance, resolves ties (same owner wins, different owners use population tiebreaker), tracks border edges, and updates when bases are founded.

**renderer.py**
Rendering system with horizontal centering for the map display. Draws tiles with terrain colors, bases with population indicators in top-left corner, units with type letters (L/S/C), status messages at bottom of map, and provides screen-to-tile coordinate conversion plus population square click detection.

**ui.py**
Comprehensive UI system with multiple screens: main game panel (turn counter, unit info, End Turn button), base management view (population growth, garrison display, production, facilities, unit support), Social Engineering screen (Politics/Economics/Values/Future Society choices), diplomacy interface with SMAC factions, and Planetary Council voting system.

## Documentation

**README.md**
Comprehensive project documentation including feature list (turn-based gameplay, base management, AI, Social Engineering), installation instructions, complete controls reference, and detailed gameplay guide covering base founding, unit management, population growth mechanics, and turn system.

**requirements.txt**
Python package dependencies file specifying pygame==2.6.1 as the sole required library.

**CLAUDE.md**
Context file for Claude Code containing project description and reference to general_index.md for file documentation.

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
