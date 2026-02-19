"""Display and rendering configuration values.

This module contains all display-related settings including:
- Display dimensions (set at runtime by main.py)
- Color definitions for rendering
- UI layout constants
- Rendering timing constants
"""

# Display settings (actual constants)
TILE_SIZE = 70  # pixels per tile
FPS = 60  # frames per second

# UI Layout constants
UI_PANEL_HEIGHT = 280  # Fixed height for UI panel (increased for unit stack panel)

# Runtime-initialized screen dimensions (set in main.py during pygame initialization)
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
MAP_AREA_HEIGHT = 0
UI_PANEL_Y = 0

# Colors (RGB)
COLOR_OCEAN = (20, 50, 120)
COLOR_LAND_RAINY = (34, 139, 34)     # Luscious green
COLOR_LAND_MODERATE = (95, 125, 50)  # Green-brown savanna
COLOR_LAND_ARID = (148, 116, 80)     # Dusty desert brown
COLOR_LAND = COLOR_LAND_RAINY        # Fallback (unused by renderer after rainfall)
COLOR_GRID = (60, 60, 60)
COLOR_BLACK = (0, 0, 0)
COLOR_UI_BACKGROUND = (25, 25, 30)
COLOR_UI_BORDER = (80, 120, 140)
COLOR_BUTTON = (45, 55, 65)
COLOR_BUTTON_HOVER = (65, 85, 100)
COLOR_BUTTON_BORDER = (100, 140, 160)
COLOR_BUTTON_HIGHLIGHT = (120, 180, 200)
COLOR_TEXT = (220, 230, 240)
COLOR_UNIT_SELECTED = (255, 255, 0)  # Yellow
COLOR_BASE_BORDER = (255, 255, 255)    # White border
COLOR_TILE_CURSOR = (255, 255, 255)    # White pulsing tile cursor

# Council colors
COLOR_COUNCIL_BG = (15, 25, 20)
COLOR_COUNCIL_ACCENT = (60, 180, 120)
COLOR_COUNCIL_BORDER = (80, 200, 140)
COLOR_COUNCIL_BOX = (25, 35, 30)

# Timing constants (milliseconds)
AI_TURN_DELAY = 300  # Delay between AI unit moves
SCROLL_DELAY = 300  # Delay between scroll ticks