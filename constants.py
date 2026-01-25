# constants.py
# All game-wide constants in one place for easy tweaking

# Map settings
MAP_WIDTH = 1  # tiles (fixed size)
MAP_HEIGHT = 1  # tiles (fixed size)
TILE_SIZE = 70  # pixels

# Display settings - will be set dynamically for fullscreen
SCREEN_WIDTH = 0  # Set at runtime
SCREEN_HEIGHT = 0  # Set at runtime
FPS = 60

# UI Layout - will be calculated at runtime
MAP_AREA_HEIGHT = 0
UI_PANEL_HEIGHT = 280  # Fixed height for UI panel (increased for unit stack panel)
UI_PANEL_Y = 0

# Colors (RGB)
COLOR_OCEAN = (20, 50, 120)
COLOR_LAND = (34, 139, 34)
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
COLOR_UNIT_FRIENDLY = (50, 205, 50)   # Gaian green
COLOR_UNIT_ENEMY = (255, 80, 80)       # Bright red

# Council colors
COLOR_COUNCIL_BG = (15, 25, 20)
COLOR_COUNCIL_ACCENT = (60, 180, 120)
COLOR_COUNCIL_BORDER = (80, 200, 140)
COLOR_COUNCIL_BOX = (25, 35, 30)

# Map generation
LAND_PROBABILITY = 0.4  # 40% of tiles will be land

# Unit types
UNIT_LAND = "land"
UNIT_SEA = "sea"
UNIT_AIR = "air"
UNIT_COLONY_POD_LAND = "colony_pod_land"
UNIT_COLONY_POD_SEA = "colony_pod_sea"

# Base colors
COLOR_BASE_FRIENDLY = (150, 220, 150)  # Light green
COLOR_BASE_ENEMY = (220, 100, 100)     # Light red
COLOR_BASE_BORDER = (255, 255, 255)    # White border