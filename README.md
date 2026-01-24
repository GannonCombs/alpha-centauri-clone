# Alpha Centauri Clone

A turn-based 4X strategy game inspired by Sid Meier's Alpha Centauri, built with Python and Pygame.

## Features

### Core Gameplay
- **Turn-based strategy** with player and AI turns
- **Square tile-based map** with procedural generation (land/ocean)
- **Unit management** - Land units, sea units, and colony pods
- **Base founding and growth** - Establish cities that grow in population over time
- **Unit garrison system** - Station units in bases for defense

### UI Systems
- **Base management screen** - View population, growth, garrison, production
- **Social Engineering** - Configure society with Politics, Economics, Values, and Future Society choices
- **Diplomacy interface** - Communicate with AI factions (Gaians, Hive, University, etc.)
- **Planetary Council** - Vote on proposals affecting the entire planet

### AI
- **Computer opponents** with classic rule-based AI
- AI founds bases, moves units strategically, and grows cities
- Sequential turn processing with visible AI actions

## Requirements

- Python 3.x
- Pygame 2.6.1

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the game with:
```bash
python main.py
```

## Controls

- **N** - Start a new game
- **W** - Cycle through units
- **B** - Found a base (when colony pod is selected)
- **E** - Open/close Social Engineering screen
- **F2** - Open/close Technology Tree screen
- **ESC** - Exit game / Close dialogs
- **Mouse Click** - Select units, cycle through garrisoned units, or open base view
- **Arrow Keys / Numpad** - Move selected unit (8 directions)
- **Enter** - Confirm dialog inputs

## Gameplay Guide

### Base Management
- **Founding bases**: Colony pods can found new bases by pressing **B**
- **Spacing rules**: Bases cannot be adjacent to any other base (including diagonals)
- **Population growth**: Bases gain 1 nutrient per turn and grow when reaching threshold
  - Pop 1→2: 7 turns, Pop 2→3: 10 turns, scaling up to max population of 7
- **Accessing base view**: Click the population square (top-left of base icon) to open

### Territory Control
- Each base projects territory up to 7 tiles away (Manhattan distance)
- Territory is shown with dotted borders in the player's color
- Tiles belong to the closest base within range
- **Tie resolution**:
  - Multiple bases of same owner at equal distance → that owner controls the tile
  - Multiple bases of different owners at equal distance → higher population wins
  - If still tied → tile remains neutral (no owner)
- Territory automatically updates when new bases are founded

### Unit Management
- **Movement**: Arrow keys or numpad for 8-directional movement
- **Garrison**: Move units into friendly bases to garrison them for defense
- **Cycling units**: Click on a base tile to cycle through garrisoned units
- **Unit types**:
  - Land units (scouts) - move on land only
  - Sea units (foils) - move on ocean only
  - Colony pods - land or sea variants for founding bases

### Social Engineering
- Press **E** to configure your society across four categories:
  - Politics (Frontier, Police State, Democratic, Fundamentalist)
  - Economics (Simple, Free Market, Planned, Green)
  - Values (Survival, Power, Knowledge, Wealth)
  - Future Society (None, Cybernetic, Eudaimonic, Thought Control)
- Each choice affects 10 social factors: Economy, Efficiency, Support, Morale, Police, Growth, Planet, Probe, Industry, Research

### Technology Research
- Press **F2** to view the Technology Tree
- Research progresses automatically (1 point per turn)
- Each technology costs 10 research points (10 turns to complete)
- Linear progression through 20 technologies: Tech 1 → Tech 2 → ... → Tech 20
- Both player and AI research technologies at the same rate
- Progress bar shows turns remaining until next discovery

### Turn System
- Player phase → AI phase → New turn
- Bases process growth at the end of each player's own turn
- Technology research advances at the end of each player's turn
- AI moves are visible with 500ms delay between actions

## Project Structure

- `main.py` - Entry point and main game loop
- `game.py` - Core game logic and state management
- `map.py` - Map generation and management
- `unit.py` - Unit classes and behaviors
- `renderer.py` - Rendering system for map and units
- `ui.py` - User interface panel
- `constants.py` - Game configuration and constants

## License

This project is for educational purposes.
