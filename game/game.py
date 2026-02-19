"""Core game logic and state management.

This module contains the main Game class that manages all game state including:
- Map and terrain
- Units and bases
- AI players and turns
- Combat resolution
- Technology research
- Diplomacy and faction contacts
- Victory/defeat conditions

The Game class coordinates all major game systems and handles turn processing,
unit movement, combat, and AI behavior.
"""
import random
import pygame
from game import facilities
from game.map import GameMap
from game.units.unit import Unit
from game.base import Base
from game.ai import AIPlayer
from game.tech import TechTree
from game.territory import TerritoryManager
from game.units.combat import Combat
from game.commerce import CommerceCalculator
from game.units.movement import MovementManager
from game.turn_manager import TurnManager
from game.debug import DebugManager  # DEBUG: Remove for release


class Game:
    """Main game state manager."""

    def __init__(self, player_faction_id=0, player_name=None, ocean_percentage=None, map_width=None, map_height=None, cloud_cover=None, erosive_forces=None, native_life=None, difficulty=1):
        """Initialize a new game.

        Args:
            player_faction_id (int): Faction ID for the player (0-6)
            player_name (str): Player's custom name (optional)
            ocean_percentage (int): Percentage of ocean tiles (30-90)
            map_width (int): Map width in tiles
            map_height (int): Map height in tiles
            cloud_cover (str): 'arid', 'moderate', or 'rainy'; None picks randomly
        """
        # Store map dimensions for new_game() resets
        self.map_width = map_width
        self.map_height = map_height

        self.game_map = GameMap(map_width, map_height, ocean_percentage, cloud_cover, erosive_forces, native_life)
        self.turn = 1
        self.running = True
        self.difficulty = difficulty  # 1=Citizen, 2=Specialist, 3=Talent, 4=Librarian, 5=Thinker, 6=Transcend
        self.player_faction_id = player_faction_id  # Which faction the player chose
        self.player_name = player_name  # Player's custom name
        self.mission_year = 2100  # Starting year

        # Initialize all factions (player + AIs)
        from game.faction import Faction
        self.factions = {}  # Dict[faction_id -> Faction]

        # Create faction objects for all 7 factions
        for faction_id in range(7):
            is_player = (faction_id == player_faction_id)
            self.factions[faction_id] = Faction(faction_id, is_player=is_player)

        # Legacy: Keep energy_credits as direct attribute for now
        # TODO: Migrate to self.factions[player_faction_id].energy_credits
        # Apply starting_credits bonus from faction data
        from game.data.faction_data import FACTION_DATA
        player_faction_data = FACTION_DATA[player_faction_id]
        self.energy_credits = player_faction_data.get('bonuses', {}).get('starting_credits', 0)

        # Global energy allocation (applies to all bases)
        self.global_energy_allocation = {
            'economy': 50,  # % to energy credits
            'labs': 50,     # % to research
            'psych': 0      # % to happiness
        }

        # Unit management
        self.units = []
        self.selected_unit = None

        # Base management
        self.bases = []

        # Status message
        self.status_message = ""
        self.status_message_timer = 0

        # Supply pod message
        self.supply_pod_message = None
        self.supply_pod_tech_event = None  # Tech event to show immediately after pod message
        self.mid_turn_upkeep = False  # True when upkeep phase triggered mid-turn (skip _start_new_turn)

        # Atrocity tracking
        self.atrocity_count = 0                  # Total atrocities committed by player
        self.sanctions_turns_remaining = 0       # Turns of commerce sanctions remaining
        self.permanent_vendetta_factions = set() # Faction IDs that will never make peace
        self.major_atrocity_committed = False    # Planet buster used — votes permanently 0
        self.pending_major_atrocity_popup = False  # Show major atrocity declaration popup

        # Integrity (0=Noble … 5=Treacherous, only decreases)
        self.integrity_level = 0

        # Blood Truce expiry: faction_id -> turn number when Truce expires
        self.truce_expiry_turns = {}

        # Battle system
        self.combat = Combat(self)
        self.movement = MovementManager(self)
        self.turns = TurnManager(self)
        self.pending_treaty_break = None  # Dict for player attacks that might break treaties
        self.pending_ai_attack = None  # Dict for AI surprise attacks

        # Get list of AI faction IDs (all factions except player's)
        self.ai_faction_ids = [fid for fid in range(7) if fid != player_faction_id]

        # Initialize tech trees for all factions
        for faction_id in range(7):
            self.factions[faction_id].tech_tree = TechTree()
            self._grant_starting_tech(faction_id)
            self.factions[faction_id].tech_tree.auto_select_research()

        # Initialize unit designs for all factions
        from game.units.unit_design import UnitDesign
        for faction_id in range(7):
            self.factions[faction_id].designs = UnitDesign(faction_id)

        # Facilities and Projects
        self.built_projects = set()  # Global set of secret projects built (one per game)
        self.secret_project_notifications = []  # Queue of {type, project_name, faction_id, ...} popups
        self.known_ai_secret_projects = set()  # (faction_id, project_name) already notified
        self.known_ai_secret_project_warnings = set()  # (faction_id, project_name) 1-turn warnings fired

        # Social Engineering (player selections)
        self.se_selections = {
            'Politics': 0,  # 0=Frontier, 1=Police State, 2=Democratic, 3=Fundamentalist
            'Economics': 0,  # 0=Simple, 1=Free Market, 2=Planned, 3=Green
            'Values': 0,  # 0=Survival, 1=Power, 2=Knowledge, 3=Wealth
            'Future Society': 0  # 0=None, 1=Cybernetic, 2=Eudaimonic, 3=Thought Control
        }

        # Territory
        self.territory = TerritoryManager(self.game_map)

        # AI players (one for each AI faction)
        self.ai_players = [AIPlayer(fid) for fid in self.ai_faction_ids]

        # Turn state
        self.processing_ai = False
        self.current_ai_index = 0
        self.ai_unit_queue = []  # Queue of units for AI to process
        self.ai_current_unit_index = 0

        # Victory state
        self.game_over = False
        self.winner = None  # 0 = human, 1+ = AI player
        self.victory_type = None  # conquest, diplomatic, economic, transcendence, scenario
        self.resigned = False  # True when player chose to retire via main menu
        self.player_ever_had_base = False  # Track if player has founded at least one base
        self.enemy_ever_had_base = False  # Track if enemy has founded at least one base

        # Victory condition tracking
        self.transcendence_victory_complete = False  # Has Ascent to Transcendence been completed?
        self.diplomatic_victory_complete = False  # Turn when player became supreme leader (None if not leader)
        self.economic_victory_complete = False  # Has Economic Victory project been completed?
        self.conquer_victory_complete = False # Have we conquered all non-Pact factions?

        # Upkeep phase
        self.upkeep_phase_active = False  # Is upkeep phase currently showing?
        self.upkeep_events = []  # List of events to show during upkeep
        self.current_upkeep_event_index = 0  # Current event being displayed

        # Auto-cycle timer
        self.auto_cycle_timer = 0  # Time in ms since last unit action
        self.auto_cycle_delay = 500  # Wait 500ms (0.5 seconds) before auto-cycling

        # Auto-end turn tracking
        self.last_unit_action = None  # 'action', 'hold', or None

        # Commerce system
        self.commerce = CommerceCalculator(self)
        self.global_trade_pact_active = False  # Planetary council proposal (placeholder)

        # Production queue (for spawning at start of next turn)
        self.pending_production = []  # List of (base, item_name) tuples to spawn

        # Flag to rebuild unit designs when tech is completed
        self.designs_need_rebuild = False
        self.new_designs_available = False  # Flag for popup to view new units
        self.pending_new_designs_flag = False  # Delayed flag (shows after upkeep)

        # Commlink tracking (contacts with other factions)
        self.faction_contacts = set()  # Set of faction IDs we've contacted
        self.all_contacts_obtained = False  # Flag: have we contacted all living factions?
        self.shown_all_contacts_popup = False  # Flag: have we shown the popup?
        self.pending_commlink_requests = []  # List of {faction_id, player_id} dicts for AI contact popups
        self.pending_artifact_link = None   # {artifact, base} set when artifact enters base with network node
        self.pending_busy_former = None     # Unit set when player clicks a terraforming former
        self.pending_terraform_cost = None  # {'unit', 'action', 'cost'} for raise/lower confirmation
        self.pending_movement_overflow_unit = None  # Unit that exceeded 100 moves in one turn
        self.eliminated_factions = set()  # Set of faction IDs that have been eliminated
        self.factions_that_had_bases = set()  # Set of faction IDs that have founded at least one base
        self.pending_faction_eliminations = []  # List of faction_ids for elimination popups
        self.infiltrated_datalinks = set()  # Set of faction IDs whose datalinks player has infiltrated

        # Camera control
        self.center_camera_on_selected = False  # Flag to center camera on selected unit
        self.center_camera_on_tile = None  # Tuple (x, y) to center camera on specific tile

        # Tile cursor mode (V key)
        self.tile_cursor_mode = False   # Whether tile inspection cursor is active
        self.cursor_x = 0               # Cursor tile X
        self.cursor_y = 0               # Cursor tile Y

        # DEBUG: Debug/cheat mode manager (remove for release)
        self.debug = DebugManager()

        # Spawn some initial units for testing
        self._spawn_test_units()

    def _grant_starting_tech(self, faction_id):
        """Grant a faction's starting technology (without prerequisites).

        Args:
            faction_id (int): The faction ID (0-6)
        """
        from game.data.faction_data import FACTION_DATA

        if faction_id < len(FACTION_DATA):
            tech_tree = self.factions[faction_id].tech_tree
            starting_tech = FACTION_DATA[faction_id].get('starting_tech')
            if starting_tech and starting_tech in tech_tree.technologies:
                tech_tree.discovered_techs.add(starting_tech)
                tech_name = tech_tree.technologies[starting_tech]['name']
                is_player = (faction_id == self.player_faction_id)
                prefix = "Player" if is_player else f"AI Faction {faction_id}"
                print(f"{prefix} starts with {tech_name}")

    def _spawn_test_units(self):
        """Create starting units for all 7 factions."""
        # Find some land tiles for land units (excluding map edges that might have black borders)
        # Also exclude tiles with supply pods
        land_tiles = []
        ocean_tiles = []

        # Avoid first and last rows to prevent spawning on black border tiles
        for y in range(1, self.game_map.height - 1):
            for x in range(self.game_map.width):
                tile = self.game_map.get_tile(x, y)
                if tile.is_land() and not tile.supply_pod and getattr(tile, 'rockiness', 0) != 2 and not getattr(tile, 'fungus', False):
                    land_tiles.append((x, y))
                elif not tile.is_land():
                    ocean_tiles.append((x, y))

        print(f"Found {len(land_tiles)} land tiles (no supply pods), {len(ocean_tiles)} ocean tiles")

        # Distribute starting positions across the map
        # Each faction gets a Scout Patrol and a Colony Pod on the same tile
        import random
        random.shuffle(land_tiles)  # Randomize spawn positions

        tile_idx = 0
        # Spawn player faction first, then AI factions
        all_faction_ids = [self.player_faction_id] + self.ai_faction_ids

        for faction_id in all_faction_ids:
            # Get faction data for naming
            from game.data.faction_data import FACTION_DATA
            faction_name = FACTION_DATA[faction_id]['name'] if faction_id < len(FACTION_DATA) else f"Faction{faction_id}"
            faction_prefix = "Player" if faction_id == self.player_faction_id else faction_name

            # Both units spawn on the same tile
            if tile_idx < len(land_tiles):
                x, y = land_tiles[tile_idx]
                tile_idx += 1  # Move to next tile for next faction

                # Starting military unit - only Santiago actually starts with special unit
                from game.units.unit_components import generate_unit_name
                # Santiago starts with Scout Rover, all others get Scout Patrol
                if faction_id == 4:  # Santiago only
                    military_design = self.factions[faction_id].designs.get_design(2)
                else:
                    # Everyone else starts with Scout Patrol (slot 0)
                    military_design = self.factions[faction_id].designs.get_design(0)

                military_name = generate_unit_name(
                    military_design['weapon'],
                    military_design['chassis'],
                    military_design['armor'],
                    military_design['reactor'],
                    military_design.get('ability1', 'none'),
                    military_design.get('ability2', 'none')
                )

                scout = Unit(
                    x=x, y=y,
                    chassis=military_design['chassis'],
                    owner=faction_id,
                    name=f"{faction_prefix} {military_name}",
                    weapon=military_design['weapon'],
                    armor=military_design['armor'],
                    reactor=military_design['reactor'],
                    ability1=military_design.get('ability1', 'none'),
                    ability2=military_design.get('ability2', 'none')
                )
                self.units.append(scout)
                self.game_map.set_unit_at(x, y, scout)
                print(f"Spawned {faction_prefix} {military_name} at ({x}, {y})")

                # Colony Pod - use design from slot 1
                colony_design = self.factions[faction_id].designs.get_design(1)
                colony_name = generate_unit_name(
                    colony_design['weapon'],
                    colony_design['chassis'],
                    colony_design['armor'],
                    colony_design['reactor'],
                    colony_design.get('ability1', 'none'),
                    colony_design.get('ability2', 'none')
                )
                colony = Unit(
                    x=x, y=y,
                    chassis=colony_design['chassis'],
                    owner=faction_id,
                    name=f"{faction_prefix} {colony_name}",
                    weapon=colony_design['weapon'],
                    armor=colony_design['armor'],
                    reactor=colony_design['reactor'],
                    ability1=colony_design.get('ability1', 'none'),
                    ability2=colony_design.get('ability2', 'none')
                )
                self.units.append(colony)
                self.game_map.set_unit_at(x, y, colony)
                print(f"Spawned {faction_prefix} {colony_name} at ({x}, {y})")

        print(f"Total units spawned: {len(self.units)}")

        # Auto-select starting colony pod; fall back to first friendly unit
        friendly_units = [u for u in self.units if u.owner == self.player_faction_id]
        colony_pods = [u for u in friendly_units if u.weapon == 'colony_pod']
        if friendly_units:
            self._select_unit(colony_pods[0] if colony_pods else friendly_units[0])
            self.center_camera_on_selected = True  # Flag to center camera on game start
            print(f"Selected {self.selected_unit.name}")

    def _select_unit(self, unit):
        """Select a unit and sync the tile's displayed_unit_index to it."""
        self.selected_unit = unit
        if unit is not None:
            tile = self.game_map.get_tile(unit.x, unit.y)
            if tile and unit in tile.units:
                tile.displayed_unit_index = tile.units.index(unit)
            # If an artifact is selected while sitting on a base with a Network Node,
            # prompt the player to link it (handles the case where the artifact was
            # already on the tile from a previous turn).
            if (unit.weapon == 'artifact'
                    and unit.owner == self.player_faction_id
                    and tile is not None
                    and getattr(tile, 'base', None) is not None
                    and 'network_node' in tile.base.facilities
                    and not getattr(tile.base, 'network_node_linked', False)
                    and self.pending_artifact_link is None):
                self.pending_artifact_link = {'artifact': unit, 'base': tile.base}

    def handle_input(self, renderer):
        """Process keyboard input for unit movement."""
        # Movement is handled in main.py event loop, not continuous input
        pass

    def handle_click(self, screen_x, screen_y, renderer):
        """Handle mouse clicks on the map."""
        tile_x, tile_y = renderer.screen_to_tile(screen_x, screen_y, self.game_map)

        # Check if clicked on a tile
        tile = self.game_map.get_tile(tile_x, tile_y)
        if not tile:
            return None

        # If there's a base, check if clicked on population square
        if tile.base and renderer.is_click_on_pop_square(screen_x, screen_y, tile.base, self.game_map):
            return 'base_click', tile.base

        # If there's a base with garrisoned units, clicking elsewhere cycles through units
        if tile.base:
            friendly_garrison = [u for u in tile.base.get_garrison_units(self) if u.is_friendly(self.player_faction_id)]
            if friendly_garrison:
                # If currently selected unit is in this garrison, select next one
                if self.selected_unit in friendly_garrison:
                    current_idx = friendly_garrison.index(self.selected_unit)
                    next_idx = (current_idx + 1) % len(friendly_garrison)
                    self._select_unit(friendly_garrison[next_idx])
                    # Center camera on this tile when cycling units
                    self.center_camera_on_tile = (tile_x, tile_y)
                    return 'unit_selected', self.selected_unit
                else:
                    # Select first garrison unit
                    self._select_unit(friendly_garrison[0])
                    # Center camera on this tile when selecting garrison
                    self.center_camera_on_tile = (tile_x, tile_y)
                    return 'unit_selected', self.selected_unit

            # If there's a base but no garrison units, clicking opens base view
            return 'base_click', tile.base

        # Check if clicked on a unit on the tile
        clicked_unit = self.game_map.get_unit_at(tile_x, tile_y)
        if clicked_unit:
            if clicked_unit.is_friendly(self.player_faction_id):
                # If a former is actively terraforming, ask player before interrupting
                if (getattr(clicked_unit, 'is_former', False)
                        and clicked_unit.terraforming_action
                        and not getattr(self, '_always_select_busy_formers', False)):
                    self.pending_busy_former = clicked_unit
                    return None
                # Select friendly unit and center camera
                self._select_unit(clicked_unit)
                self.center_camera_on_tile = (tile_x, tile_y)
            else:
                # Clicked on enemy unit - try to attack with selected unit
                if self.selected_unit and self.selected_unit.is_friendly(self.player_faction_id):
                    # Try to move to enemy unit (will initiate combat)
                    self.movement.try_move_unit(self.selected_unit, tile_x, tile_y)
                # Also center camera on enemy unit
                self.center_camera_on_tile = (tile_x, tile_y)
        else:
            # Clicked on empty tile - center camera
            self.center_camera_on_tile = (tile_x, tile_y)

        return None

    def _collect_supply_pod(self, tile, unit):
        """Handle unit collecting a supply pod.

        Outcomes (40 / 15 / 15 / 15 / 15):
          40% — free tech (random researchable tech the faction could have studied)
          15% — Alien Artifact spawned on the tile
          15% — Commlink to a faction not yet contacted
          15% — 500 energy credits
          15% — River spawns from this tile

        Args:
            tile: The tile with the supply pod
            unit: The unit collecting the pod
        """
        import random

        # Remove the pod from the tile
        tile.supply_pod = False

        roll = random.random()

        if roll < 0.40:
            # --- Free technology ---
            tech_tree = self.factions[unit.owner].tech_tree
            available = tech_tree.get_available_techs()  # [(tech_id, tech_data), ...]
            if available:
                tech_id, tech_data = random.choice(available)
                tech_name = tech_data.get('name', tech_id)
                tech_tree.discovered_techs.add(tech_id)
                # If they were researching this tech, clear it (it's done)
                if tech_tree.current_research == tech_id:
                    tech_tree.current_research = None
                    tech_tree.research_points = 0
                if unit.owner == self.player_faction_id:
                    self.supply_pod_message = "Supply Pod discovered! Ancient datalinks contain a technological blueprint!"
                    self._auto_generate_unit_designs(tech_id)
                    # Store a tech_complete event to show immediately after the pod message
                    self.supply_pod_tech_event = {
                        'type': 'tech_complete',
                        'tech_id': tech_id,
                        'tech_name': tech_name,
                    }
                    print(f"Supply pod tech at ({tile.x}, {tile.y}): {tech_name}")
                else:
                    print(f"AI faction {unit.owner} gained tech '{tech_name}' from supply pod")
            else:
                # No researchable techs — fall back to credits
                if unit.owner == self.player_faction_id:
                    self.energy_credits += 500
                    self.supply_pod_message = "Supply Pod discovered! You gain 500 energy credits."
                else:
                    print(f"AI collected supply pod at ({tile.x}, {tile.y}): fallback credits")

        elif roll < 0.55:
            # --- Alien Artifact ---
            from game.units.unit import Unit
            artifact = Unit(
                x=tile.x, y=tile.y,
                chassis='infantry',
                owner=unit.owner,
                name="Alien Artifact",
                weapon='artifact',
                armor='no_armor',
                reactor='fission'
            )
            artifact.moves_remaining = 0  # Can't move on turn discovered
            artifact.has_moved = True
            self.units.append(artifact)
            self.game_map.add_unit_at(tile.x, tile.y, artifact)

            if unit.owner == self.player_faction_id:
                self.supply_pod_message = "Supply Pod discovered! You found an Alien Artifact!"
                print(f"Artifact found at ({tile.x}, {tile.y})")
            else:
                print(f"AI found artifact at ({tile.x}, {tile.y})")

        elif roll < 0.70:
            # --- Commlink to an uncontacted faction ---
            if unit.owner == self.player_faction_id:
                from game.data.faction_data import FACTION_DATA
                uncontacted = [
                    fid for fid in range(7)
                    if fid != self.player_faction_id
                    and fid not in self.faction_contacts
                    and fid not in self.eliminated_factions
                    and fid in self.factions
                ]
                if uncontacted:
                    new_faction_id = random.choice(uncontacted)
                    faction_name = FACTION_DATA[new_faction_id]['name'] if new_faction_id < len(FACTION_DATA) else f"Faction {new_faction_id}"
                    self.supply_pod_message = f"Supply Pod discovered! Commlink frequencies for {faction_name} recovered from ancient datalinks!"
                    self.add_faction_contact(new_faction_id)
                    # NOTE: intentionally NOT adding to pending_commlink_requests — supply pod
                    # commlinks just unlock the contact in the commlink panel; they don't start a call.
                    print(f"Supply pod commlink: player gained contact with faction {new_faction_id}")
                else:
                    # Already know everyone — fall back to credits
                    self.energy_credits += 500
                    self.supply_pod_message = "Supply Pod discovered! You gain 500 energy credits."
                    print(f"Supply pod commlink fallback (all known) at ({tile.x}, {tile.y}): +500 credits")
            else:
                print(f"AI collected supply pod (commlink) at ({tile.x}, {tile.y})")

        elif roll < 0.85:
            # --- 500 energy credits ---
            if unit.owner == self.player_faction_id:
                self.energy_credits += 500
                self.supply_pod_message = "Supply Pod discovered! You gain 500 energy credits."
                print(f"Supply pod collected at ({tile.x}, {tile.y}): +500 credits")
            else:
                print(f"AI collected supply pod at ({tile.x}, {tile.y})")

        else:
            # --- River spawns from this tile (land only; ocean falls back to credits) ---
            if tile.is_land():
                self.game_map.generate_river_from(tile.x, tile.y)
                if unit.owner == self.player_faction_id:
                    self.supply_pod_message = "Supply Pod discovered! A river springs from the ground!"
                    print(f"Supply pod river at ({tile.x}, {tile.y})")
            else:
                if unit.owner == self.player_faction_id:
                    self.energy_credits += 500
                    self.supply_pod_message = "Supply Pod discovered! You gain 500 energy credits."
                print(f"Supply pod river fallback (ocean tile) at ({tile.x}, {tile.y}): +500 credits")

    def _check_artifact_stolen_by_proximity(self, artifact):
        """If an artifact moves adjacent to an enemy unit, the enemy steals it.

        The artifact teleports to the tile of the enemy unit that triggered the steal.
        Shows a popup if the player owns the artifact.
        """
        directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        for dx, dy in directions:
            nx, ny = artifact.x + dx, artifact.y + dy
            adj_tile = self.game_map.get_tile(nx, ny)
            if not adj_tile or not adj_tile.units:
                continue
            for adj_unit in adj_tile.units:
                if adj_unit.owner != artifact.owner and adj_unit.weapon != 'artifact':
                    # Enemy unit found — steal the artifact
                    old_owner = artifact.owner
                    self.game_map.remove_unit_at(artifact.x, artifact.y, artifact)
                    artifact.move_to(nx, ny)
                    artifact.owner = adj_unit.owner
                    self.game_map.add_unit_at(nx, ny, artifact)
                    if old_owner == self.player_faction_id:
                        thief_faction = self.factions.get(adj_unit.owner, {})
                        thief_name = thief_faction.get('name', 'an enemy') if isinstance(thief_faction, dict) else getattr(thief_faction, 'name', 'an enemy')
                        self.supply_pod_message = f"Your Alien Artifact was stolen by {thief_name}!"
                    return  # Only one steal per move

    def _apply_monolith_effects(self, unit):
        """Apply monolith effects to a unit.

        Monoliths always repair units and upgrade morale once per unit.

        Args:
            unit: The unit entering the monolith
        """
        # Always repair the unit
        if unit.current_health < unit.max_health:
            unit.current_health = unit.max_health
            if unit.owner == self.player_faction_id:
                self.set_status_message(f"{unit.name} repaired at Monolith!")
                print(f"Unit repaired at monolith: ({unit.x}, {unit.y})")

        # Upgrade morale once per unit (if not already upgraded)
        if not unit.monolith_upgrade and unit.morale_level < 7:  # Max morale is Elite (7)
            unit.morale_level += 1
            unit.monolith_upgrade = True

            morale_name = unit.get_morale_name()

            # Upgrading at monolith ends the unit's turn
            unit.moves_remaining = 0

            if unit.owner == self.player_faction_id:
                self.set_status_message(f"{unit.name} upgraded to {morale_name} at Monolith!")
                print(f"Unit upgraded at monolith: ({unit.x}, {unit.y}) -> {morale_name}")

            # 1/32 chance the monolith disappears permanently after granting an upgrade
            import random
            if random.randint(1, 32) == 1:
                tile = self.game_map.get_tile(unit.x, unit.y)
                if tile:
                    tile.monolith = False
                    if unit.owner == self.player_faction_id:
                        self.set_status_message(f"{unit.name} upgraded at Monolith! The Monolith crumbles to dust.")
                    print(f"Monolith at ({unit.x}, {unit.y}) disappeared after use")

        elif not unit.monolith_upgrade:
            # Already at max morale, mark as upgraded so they don't try again
            unit.monolith_upgrade = True
            if unit.owner == self.player_faction_id:
                self.set_status_message(f"{unit.name} visited Monolith (already Elite)")

    def _remove_unit(self, unit, killer=None):
        """Remove a unit from the game completely.

        Args:
            unit (Unit): Unit to remove
            killer (Unit): Optional — the unit that killed this one (for artifact transfer)
        """
        # If this is a transport with loaded units, destroy them too
        if hasattr(unit, 'loaded_units') and unit.loaded_units:
            for loaded_unit in unit.loaded_units[:]:  # Copy list to avoid modification during iteration
                if loaded_unit in self.units:
                    self.units.remove(loaded_unit)
                # Remove from home base's supported units list
                if hasattr(loaded_unit, 'home_base') and loaded_unit.home_base:
                    if loaded_unit in loaded_unit.home_base.supported_units:
                        loaded_unit.home_base.supported_units.remove(loaded_unit)

        # Remove from units list
        if unit in self.units:
            self.units.remove(unit)

        # Remove from map
        tile = self.game_map.get_tile(unit.x, unit.y)
        if tile:
            self.game_map.remove_unit_at(unit.x, unit.y, unit)

        # Remove from base garrison if present
        if tile and tile.base and unit in tile.base.garrison:
            tile.base.garrison.remove(unit)

        # Remove from home base's supported units list
        if hasattr(unit, 'home_base') and unit.home_base:
            if unit in unit.home_base.supported_units:
                unit.home_base.supported_units.remove(unit)

        # If all military unit(s) on a tile die and leave an artifact alone on the tile,
        # it automatically becomes the enemy's.
        if killer and tile and unit.weapon != 'artifact':
            remaining = [u for u in tile.units if u.weapon != 'artifact']
            artifacts_here = [u for u in tile.units if u.weapon == 'artifact']
            if not remaining and artifacts_here:
                for artifact in artifacts_here:
                    old_owner = artifact.owner
                    self.game_map.remove_unit_at(artifact.x, artifact.y, artifact)
                    artifact.move_to(killer.x, killer.y)
                    artifact.owner = killer.owner
                    self.game_map.add_unit_at(killer.x, killer.y, artifact)
                    if old_owner == self.player_faction_id:
                        killer_faction = self.factions.get(killer.owner, {})
                        killer_name = killer_faction.get('name', 'an enemy') if isinstance(killer_faction, dict) else getattr(killer_faction, 'name', 'an enemy')
                        self.supply_pod_message = f"Your Alien Artifact was captured by {killer_name}!"
                    elif killer.owner == self.player_faction_id:
                        self.supply_pod_message = "You captured an Alien Artifact!"

        # Deselect if this was the selected unit
        if self.selected_unit == unit:
            # Try to select next friendly unit
            friendly_units = [u for u in self.units if u.is_friendly(self.player_faction_id)]
            self._select_unit(friendly_units[0] if friendly_units else None)

    def toggle_artillery_mode(self, unit):
        """Toggle artillery firing mode for a unit.

        Args:
            unit (Unit): Unit to toggle artillery mode for

        Returns:
            bool: True if artillery mode was toggled, False if unit doesn't have artillery
        """
        if not hasattr(unit, 'has_artillery') or not unit.has_artillery:
            return False

        unit.artillery_mode = not unit.artillery_mode
        status = "enabled" if unit.artillery_mode else "disabled"
        self.set_status_message(f"Artillery mode {status} for {unit.name}")
        return True

    def can_artillery_fire_at(self, unit, target_x, target_y):
        """Check if unit can fire artillery at target location.

        Args:
            unit (Unit): Firing unit
            target_x (int): Target X coordinate
            target_y (int): Target Y coordinate

        Returns:
            tuple: (bool, str) - (can_fire, error_message)
        """
        if not hasattr(unit, 'has_artillery') or not unit.has_artillery:
            return False, "Unit does not have artillery capability"

        if not unit.can_artillery_fire_at(target_x, target_y):
            return False, "Target out of artillery range (max 2 squares)"

        # Check if there's a valid target at location
        tile = self.game_map.get_tile(target_x, target_y)
        if not tile:
            return False, "Invalid target location"

        target_unit = self.game_map.get_unit_at(target_x, target_y)
        if not target_unit:
            return False, "No unit at target location"

        if target_unit.is_friendly(unit.owner):
            return False, "Cannot fire on friendly units"

        return True, ""

    def execute_artillery_fire(self, unit, target_x, target_y):
        """Execute artillery fire at target location.

        Artillery does reduced damage compared to direct combat and doesn't
        risk the firing unit. Damage is based on weapon strength.

        Args:
            unit (Unit): Firing unit
            target_x (int): Target X coordinate
            target_y (int): Target Y coordinate

        Returns:
            bool: True if fire was executed, False otherwise
        """
        import random

        can_fire, error = self.can_artillery_fire_at(unit, target_x, target_y)
        if not can_fire:
            if unit.owner == self.player_faction_id:
                self.set_status_message(f"Cannot fire: {error}")
            return False

        target_unit = self.game_map.get_unit_at(target_x, target_y)
        if not target_unit:
            return False

        # Artillery damage: weapon strength * random(1-3) * 0.5 (artillery penalty)
        weapon_attack = unit.weapon_data['attack']
        base_damage = weapon_attack * random.randint(1, 3)
        artillery_damage = max(1, int(base_damage * 0.5))  # At least 1 damage

        target_unit.take_damage(artillery_damage)

        # Status message
        if unit.owner == self.player_faction_id or target_unit.owner == self.player_faction_id:
            self.set_status_message(
                f"{unit.name} fires artillery at {target_unit.name} for {artillery_damage} damage!"
            )

        # Check if target destroyed
        if target_unit.is_destroyed():
            self.set_status_message(f"{target_unit.name} destroyed by artillery!")
            unit.record_kill()
            self._remove_unit(target_unit)

        # Consume unit's turn
        unit.moves_remaining = 0
        unit.has_moved = True

        # Track that last action was an action (not hold)
        if unit.owner == self.player_faction_id:
            self.last_unit_action = 'action'

        # Disable artillery mode after firing
        unit.artillery_mode = False

        return True

    def _process_air_unit_fuel(self, player_id):
        """Process air unit fuel: refuel at bases, check for crashes.

        Args:
            player_id (int): Player ID whose air units to process
        """
        units_to_remove = []

        for unit in self.units:
            if unit.owner != player_id or not unit.is_air_unit():
                continue

            # Check if unit is at a friendly base
            tile = self.game_map.get_tile(unit.x, unit.y)
            at_base = tile and tile.base and tile.base.owner == player_id

            if at_base:
                # Refuel at base
                unit.refuel(unit.x, unit.y)
            else:
                # Not at base - check if out of fuel
                if unit.is_out_of_fuel():
                    self.set_status_message(f"{unit.name} crashed! Out of fuel!")
                    print(f"{unit.name} crashed at ({unit.x}, {unit.y}) - out of fuel")
                    units_to_remove.append(unit)
                elif not unit.can_reach_refuel_point(self.game_map, self.bases):
                    # Warning: can't reach refuel point
                    self.set_status_message(f"WARNING: {unit.name} cannot reach base!")

        # Remove crashed units
        for unit in units_to_remove:
            self._remove_unit(unit)

    def _process_unit_repair(self, player_id):
        """Process unit repair at end of turn using the repair module.

        Args:
            player_id (int): Player ID whose units to repair
        """
        from game.units.repair import calculate_repair

        for unit in self.units:
            if unit.owner != player_id:
                continue

            # Calculate repair using the repair module
            repair_amount = calculate_repair(unit, self)

            if repair_amount > 0:
                # Apply repair
                actual_repaired = unit.repair(repair_amount)

                # Show message for player units
                if actual_repaired > 0 and player_id == self.player_faction_id:
                    print(f"{unit.name}: Repaired {actual_repaired} HP")

    def calculate_probe_success(self, probe_unit, target_base):
        """Calculate probability of probe action success.

        Args:
            probe_unit (Unit): The probe team
            target_base (Base): Target base

        Returns:
            float: Success probability (0.0 to 1.0)
        """
        # Probe rating = morale level (simplified, SE bonuses would go here)
        probe_rating = probe_unit.morale_level

        # Target defense = base size (simplified)
        target_defense = target_base.population

        # Success formula: (probe_rating - target_defense + 5) / 10
        # Clamped between 0.1 and 0.9
        success_chance = (probe_rating - target_defense + 5) / 10.0
        return max(0.1, min(0.9, success_chance))

    def execute_probe_action(self, probe_unit, target_base, action):
        """Execute a probe team action.

        Args:
            probe_unit (Unit): The probe team
            target_base (Base): Target base
            action (str): Action type ('steal_tech', 'sabotage', 'mind_control')

        Returns:
            tuple: (success, message)
        """
        import random

        # Calculate success chance
        success_chance = self.calculate_probe_success(probe_unit, target_base)

        # Determine success
        success = random.random() < success_chance

        if action == 'steal_tech':
            cost = 50
            if self.energy_credits < cost:
                return False, f"Insufficient energy ({cost} required)"

            self.energy_credits -= cost

            if success:
                # Steal a random tech they have that we don't
                player_tech_tree = self.factions[self.player_faction_id].tech_tree
                target_techs = self.factions[target_base.owner].tech_tree.discovered_techs
                stealable = target_techs - player_tech_tree.discovered_techs

                if stealable:
                    stolen_tech = random.choice(list(stealable))
                    tech_name = player_tech_tree.technologies[stolen_tech]['name']
                    player_tech_tree.discovered_techs.add(stolen_tech)
                    return True, f"Stole technology: {tech_name}!"
                else:
                    return True, "No new technologies to steal"
            else:
                # Failed - lose probe team
                self._remove_unit(probe_unit)
                return False, f"Probe team detected and eliminated!"

        elif action == 'sabotage':
            cost = 100
            if self.energy_credits < cost:
                return False, f"Insufficient energy ({cost} required)"

            self.energy_credits -= cost

            if success:
                # Destroy a random facility
                if target_base.facilities:
                    destroyed = random.choice(target_base.facilities)
                    target_base.facilities.remove(destroyed)
                    return True, f"Sabotaged {destroyed}!"
                else:
                    # Reset production instead
                    target_base.production_progress = 0
                    return True, "Sabotaged production!"
            else:
                self._remove_unit(probe_unit)
                return False, "Probe team detected and eliminated!"

        elif action == 'mind_control_base':
            cost = 500
            if self.energy_credits < cost:
                return False, f"Insufficient energy ({cost} required)"

            self.energy_credits -= cost

            if success:
                # Capture the base
                old_owner = target_base.owner
                target_base.owner = probe_unit.owner
                target_base.turns_since_capture = 0  # Mark as newly captured for disloyal citizens

                # Transfer all units in the base
                for unit in self.units:
                    if unit.x == target_base.x and unit.y == target_base.y and unit.owner == old_owner:
                        unit.owner = probe_unit.owner

                return True, f"Mind controlled {target_base.name}!"
            else:
                self._remove_unit(probe_unit)
                return False, "Probe team detected and eliminated!"

        return False, "Unknown action"

    def _check_first_contact(self, unit, x, y):
        """Check for first contact with adjacent enemy units or bases and establish commlink.

        Args:
            unit: The unit that just moved
            x: Current x position
            y: Current y position
        """

        # Check all adjacent tiles (8 directions including diagonals)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                adj_x = x + dx
                adj_y = y + dy

                # Check bounds
                if adj_x < 0 or adj_x >= self.game_map.width or adj_y < 0 or adj_y >= self.game_map.height:
                    continue

                adj_tile = self.game_map.get_tile(adj_x, adj_y)
                if not adj_tile:
                    continue

                # Check for bases on adjacent tile
                if adj_tile.base:
                    other_base = adj_tile.base
                    # Skip if same owner
                    if other_base.owner == unit.owner:
                        continue

                    # Establish commlink between the two factions
                    if unit.owner == self.player_faction_id:
                        # Player met the AI faction's base
                        other_faction_id = other_base.owner
                        if other_faction_id not in self.faction_contacts:
                            print(f"Player established contact with faction {other_faction_id} (via base)")

                            # Show commlink request popup
                            if not hasattr(self, 'pending_commlink_requests'):
                                self.pending_commlink_requests = []
                            self.pending_commlink_requests.append({
                                'other_faction_id': other_faction_id,
                                'player_faction_id': self.player_faction_id
                            })

                            self.add_faction_contact(other_faction_id)

                    elif other_base.owner == self.player_faction_id:
                        # AI unit met the player's base
                        other_faction_id = unit.owner
                        if other_faction_id not in self.faction_contacts:
                            print(f"Player established contact with faction {other_faction_id} (via base)")

                            # Show commlink request popup
                            if not hasattr(self, 'pending_commlink_requests'):
                                self.pending_commlink_requests = []
                            self.pending_commlink_requests.append({
                                'other_faction_id': other_faction_id,
                                'player_faction_id': self.player_faction_id
                            })

                            self.add_faction_contact(other_faction_id)

                # Check for units on adjacent tile
                for other_unit in adj_tile.units:
                    # Skip if same owner
                    if other_unit.owner == unit.owner:
                        continue

                    # Skip if not a player faction (0-6)
                    if other_unit.owner < 0 or other_unit.owner > 6:
                        continue

                    # Establish commlink between the two factions
                    # If player is involved, add to faction_contacts
                    print(f" Unit.owner: {unit.owner}")
                    print(f" player_id: {self.player_faction_id}")
                    #TODO: Ensure we are using good ID values below.
                    if unit.owner == self.player_faction_id:
                        # Player met the AI faction (owner IS faction_id)
                        other_faction_id = other_unit.owner
                        if other_faction_id not in self.faction_contacts:
                            print(f"Player established contact with faction {other_faction_id}")

                            # Show commlink request popup (player initiated contact)
                            if not hasattr(self, 'pending_commlink_requests'):
                                self.pending_commlink_requests = []
                            self.pending_commlink_requests.append({
                                'other_faction_id': other_faction_id,
                                'player_faction_id': self.player_faction_id
                            })

                            self.add_faction_contact(other_faction_id)

                    elif other_unit.owner == self.player_faction_id:
                        # AI met the player (owner IS faction_id)
                        other_faction_id = unit.owner
                        if other_faction_id not in self.faction_contacts:
                            print(f"Player established contact with faction {other_faction_id}")

                            # Show commlink request popup (AI initiated contact)
                            if not hasattr(self, 'pending_commlink_requests'):
                                self.pending_commlink_requests = []
                            self.pending_commlink_requests.append({
                                'other_faction_id': other_faction_id,
                                'player_faction_id': self.player_faction_id
                            })

                            self.add_faction_contact(other_faction_id)

    def can_found_base(self, unit):
        """Check if a unit can found a base at its current location.

        Args:
            unit: The unit attempting to found a base

        Returns:
            tuple: (bool, str) - (can_found, error_message)
        """
        if not unit.is_colony_pod():
            return False, "Unit is not a colony pod"

        # Check if unit has movement remaining
        if unit.moves_remaining <= 0:
            return False, "No movement remaining"

        # Check if there's already a base at this location
        tile = self.game_map.get_tile(unit.x, unit.y)
        if tile and tile.base:
            return False, "Base already exists here"

        # Cannot found on rocky terrain
        if tile and getattr(tile, 'rockiness', 0) == 2:
            return False, "Cannot found base on rocky terrain"

        # Cannot found on xenofungus
        if tile and getattr(tile, 'fungus', False):
            return False, "Cannot found base on xenofungus"

        # Cannot found on a monolith
        if tile and getattr(tile, 'monolith', False):
            return False, "Cannot found base on a Monolith"

        # Check for adjacent bases (including diagonals, with wrapping)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x = (unit.x + dx) % self.game_map.width
                check_y = unit.y + dy
                # Skip if Y is out of bounds (no vertical wrapping)
                if check_y < 0 or check_y >= self.game_map.height:
                    continue
                check_tile = self.game_map.get_tile(check_x, check_y)
                if check_tile and check_tile.base:
                    return False, "Too close to another base"

        return True, ""

    def generate_base_name(self, player_id):
        """Generate a base name for a player based on their faction.

        Uses faction-specific base names from SMAC. First base uses the HQ name,
        subsequent bases use random names from the faction list, then fallback to
        "Sector N" when all names are exhausted.

        Args:
            player_id: The player ID to generate a name for

        Returns:
            str: The generated base name
        """
        from game.data.faction_data import FACTION_DATA
        import random

        # Get faction ID for this player
        # player_id IS faction_id
        faction_id = player_id
        if faction_id >= len(FACTION_DATA):
            # Fallback if faction not found
            player_bases = [b for b in self.bases if b.owner == player_id]
            return f"Base {len(player_bases) + 1}"

        faction = FACTION_DATA[faction_id]
        base_names = faction.get('base_names', [])

        if not base_names:
            # Fallback if no base names defined
            player_bases = [b for b in self.bases if b.owner == player_id]
            return f"Base {len(player_bases) + 1}"

        # Get existing base names for this player
        player_bases = [b for b in self.bases if b.owner == player_id]
        used_names = {b.name for b in player_bases}

        # First base always gets the HQ name (first in list)
        if len(player_bases) == 0:
            return base_names[0]

        # For subsequent bases, pick random from remaining faction names
        available_names = [name for name in base_names[1:] if name not in used_names]
        if available_names:
            return random.choice(available_names)

        # All faction names used - fallback to "Sector N"
        # Find next available sector number (1-99)
        for sector_num in range(1, 100):
            sector_name = f"Sector {sector_num}"
            if sector_name not in used_names:
                return sector_name

        # Ultimate fallback if somehow we have 99+ sectors
        return f"Base {len(player_bases) + 1}"

    def found_base(self, unit, base_name):
        """Convert a colony pod into a base."""
        # Re-check validity
        can_found, error_msg = self.can_found_base(unit)
        if not can_found:
            self.set_status_message(f"Cannot found base: {error_msg}")
            print(f"Cannot found base: {error_msg}")
            return False

        tile = self.game_map.get_tile(unit.x, unit.y)

        # Create the base
        base = Base(unit.x, unit.y, unit.owner, base_name)

        # Check if this is the player's first base - if so, add Headquarters
        player_bases = [b for b in self.bases if b.owner == unit.owner]
        if len(player_bases) == 0:
            base.facilities.append('headquarters')
            print(f"First base founded - Headquarters added automatically")
            # First base starts with governor OFF
            base.governor_enabled = False
            base.governor_mode = None

        # Add faction's free facility (always gets it)
        from game.data.faction_data import FACTION_DATA
        from game.facilities import get_facility_by_name
        if unit.owner < len(FACTION_DATA):
            faction = FACTION_DATA[unit.owner]
            free_facility_name = faction.get('bonuses', {}).get('free_facility')
            if free_facility_name:
                # Convert name to ID
                facility_data = get_facility_by_name(free_facility_name)
                if facility_data:
                    facility_id = facility_data['id']
                    base.facilities.append(facility_id)
                    base.free_facilities.append(facility_id)
                    print(f"Added free facility: {free_facility_name} ({facility_id})")

        if len(player_bases) > 0:
            # Not first base - check governor settings
            if unit.owner == self.player_faction_id:
                # Player faction: enable governor if any other base has it enabled
                any_governor_enabled = any(b.governor_enabled for b in player_bases)
                if any_governor_enabled:
                    # Copy mode from first enabled governor base
                    for other_base in player_bases:
                        if other_base.governor_enabled:
                            base.governor_enabled = True
                            base.governor_mode = other_base.governor_mode
                            break
            else:
                # AI faction: always enable governor with faction's default mode
                from game.governor import get_ai_governor_mode
                base.governor_enabled = True
                base.governor_mode = get_ai_governor_mode(unit.owner)

        self.bases.append(base)

        # Set initial production to the faction's actual slot 0 design name
        from game.governor import get_default_unit_name
        faction_obj = self.factions.get(unit.owner)
        if faction_obj and faction_obj.designs:
            base.current_production = get_default_unit_name(faction_obj)
            base.production_cost = base._get_production_cost(base.current_production)
            base.production_turns_remaining = base._calculate_production_turns()

        # Update the tile
        if tile:
            tile.base = base
            self.game_map.remove_unit_at(unit.x, unit.y, unit)

        # Track that this faction has now founded at least one base (guards against false elimination)
        self.factions_that_had_bases.add(unit.owner)

        # Add any other friendly units at this location to the garrison
        other_units = [u for u in self.units if u != unit and u.x == unit.x and u.y == unit.y and u.owner == unit.owner]
        for other_unit in other_units:
            if other_unit not in base.garrison:
                base.garrison.append(other_unit)
                print(f"{other_unit.name} garrisoned at newly founded {base.name}")

        # Remove the unit (if still in list - may have been removed during faction elimination)
        if unit in self.units:
            self.units.remove(unit)

        # Deselect if this was the selected unit
        if self.selected_unit == unit:
            self.selected_unit = None
            # Trigger auto-cycle after delay if player unit
            if unit.owner == self.player_faction_id:
                self.auto_cycle_timer = pygame.time.get_ticks()
                # Track that last action was an action (not hold)
                self.last_unit_action = 'action'

        # Update territory
        self.territory.update_territory(self.bases)

        # Center camera on newly founded base
        if unit.owner != self.player_faction_id:
            # AI founded a base - center on it
            self.center_camera_on_tile = (base.x, base.y)

        print(f"Founded base '{base_name}' at ({base.x}, {base.y})")
        return True

    def is_unit_in_friendly_base(self, unit):
        """Check if a unit is currently in a friendly base.

        Args:
            unit: Unit to check

        Returns:
            bool: True if unit is in a friendly base
        """
        for base in self.bases:
            if base.x == unit.x and base.y == unit.y and base.owner == unit.owner:
                return True
        return False

    def _get_hq_base(self, faction_id):
        """Return the Headquarters base for a faction, or None if none exists."""
        for base in self.bases:
            if base.owner == faction_id and 'headquarters' in base.facilities:
                return base
        return None

    def _calc_bureaucracy_drones(self, faction_id):
        """Calculate total bureaucracy drones for a faction this turn.

        Formula: BaseLimit = (8 - difficulty_0idx) * (4 + max(0, efficiency)) * MapRoot / 2
        MapRoot = sqrt(map_tiles) / sqrt(3200)

        Returns a dict mapping each faction base to its bureaucracy drone share.
        Excess drones are distributed one-per-base in random order.
        """
        import math
        from game.social_engineering import calculate_se_effects

        faction_bases = [b for b in self.bases if b.owner == faction_id]
        if not faction_bases:
            return {}

        # Use actual generated map dimensions, not constructor args
        map_tiles = self.game_map.width * self.game_map.height
        map_root = math.sqrt(map_tiles) / math.sqrt(3200)

        # difficulty_0idx: our 1-6 scale maps to 0-5 (guard against None from old saves)
        difficulty_0idx = max(0, min(5, (self.difficulty or 1) - 1))

        # EFFIC rating (negative treated as 0)
        if faction_id == self.player_faction_id:
            efficiency = max(0, calculate_se_effects(self.se_selections).get('EFFIC', 0))
        else:
            efficiency = 0  # AI uses default SE

        base_limit = (8 - difficulty_0idx) * (4 + efficiency) * map_root / 2
        excess = max(0, len(faction_bases) - int(base_limit))

        if excess == 0:
            return {}

        # Distribute excess drones randomly, one per base
        import random
        shuffled = faction_bases[:]
        random.shuffle(shuffled)
        result = {b: 0 for b in faction_bases}
        for i in range(excess):
            result[shuffled[i % len(shuffled)]] += 1
        return result

    def _calc_inefficiency_loss(self, base, faction_id):
        """Calculate energy lost to inefficiency for a base.

        Formula: Energy * Distance / (64 - (4 - Efficiency) * 8)
        Capped at Energy (can't lose more than you produce).
        Distance = Manhattan distance to HQ (16 if no HQ).

        Args:
            base: Base instance to calculate for
            faction_id (int): Owner faction ID

        Returns:
            int: Energy units lost to inefficiency
        """
        from game.social_engineering import calculate_se_effects

        energy = base.energy_production
        if energy <= 0:
            return 0

        # Get EFFIC SE rating for this faction
        if faction_id == self.player_faction_id:
            efficiency = calculate_se_effects(self.se_selections).get('EFFIC', 0)
        else:
            efficiency = 0  # AI uses default SE (no choices implemented yet)

        # TODO: Children's Creche adds +2 to efficiency for this base
        # if 'childrens_creche' in base.facilities:
        #     efficiency += 2

        # Manhattan distance to HQ (with east-west map wrapping)
        hq = self._get_hq_base(faction_id)
        if hq is None:
            distance = 16
        else:
            dx = abs(base.x - hq.x)
            if dx > self.game_map.width // 2:
                dx = self.game_map.width - dx
            dy = abs(base.y - hq.y)
            distance = dx + dy

        denominator = 64 - (4 - efficiency) * 8
        if denominator <= 0:
            return energy  # All energy lost (very negative EFFIC)

        loss = energy * distance // denominator
        return min(energy, loss)

    def get_planet_rating(self, faction_id):
        """Return the PLANET social engineering rating for a faction.

        Returns 0 until SE is implemented. When SE is added, this method
        should return the faction's effective PLANET rating (base + modifiers).
        Xenoempathy Dome will add +3 here.

        Args:
            faction_id (int): Faction ID

        Returns:
            int: PLANET rating (typically -2 to +4)
        """
        # TODO: wire up to SE system when implemented
        return 0

    def has_pact_with(self, faction_id1, faction_id2):
        """Check if two factions have a pact.

        Args:
            faction_id1: First faction ID
            faction_id2: Second faction ID

        Returns:
            bool: True if factions have a pact, False otherwise
        """
        if not hasattr(self, 'ui_manager') or not hasattr(self.ui_manager, 'diplomacy'):
            return False

        # diplo_relations only stores player's perspective, so check both directions
        # If player is faction_id1, check diplo_relations[faction_id2]
        # If player is faction_id2, check diplo_relations[faction_id1]
        if faction_id1 == self.player_faction_id:
            relation = self.ui_manager.diplomacy.diplo_relations.get(faction_id2, "Uncommitted")
            return relation == 'Pact'
        elif faction_id2 == self.player_faction_id:
            relation = self.ui_manager.diplomacy.diplo_relations.get(faction_id1, "Uncommitted")
            return relation == 'Pact'
        else:
            # Neither is the player - AI factions don't have pacts with each other
            return False

    def can_see_production(self, base):
        """Check if player can see a base's production.

        Production is visible if any of these conditions are met:
        1. Base is owned by player
        2. Player has a pact with base owner
        3. Player owns Empath Guild
        4. Player is planetary governor
        5. Player has infiltrated the faction's datalinks
        6. Debug mode is enabled

        Args:
            base: Base to check

        Returns:
            bool: True if production should be visible
        """
        # Always see own bases
        if base.owner == self.player_faction_id:
            return True

        # Debug mode shows all
        if hasattr(self, 'debug') and self.debug.show_all_production:
            return True

        # Check for pact
        if self.has_pact_with(self.player_faction_id, base.owner):
            return True

        # Check for infiltrated datalinks
        if base.owner in self.infiltrated_datalinks:
            return True

        # Check for Empath Guild
        for player_base in self.bases:
            if player_base.owner == self.player_faction_id:
                if 'empath_guild' in player_base.facilities:
                    return True

        # TODO: Check for planetary governor status
        # (requires governor voting system to be implemented)

        return False

    def evacuate_units_from_former_pact(self, faction_id1, faction_id2):
        """Evacuate units from former pact partner's territory.

        When a pact ends, all units on former pact partner's tiles or bases
        are automatically moved to their nearest friendly base.

        Args:
            faction_id1: First faction ID
            faction_id2: Second faction ID (former pact partner)

        Returns:
            int: Number of units evacuated
        """
        evacuated_count = 0

        # Find all units that need to be evacuated
        units_to_evacuate = []

        for unit in self.units:
            # Check if unit belongs to faction_id1 and is on faction_id2's territory
            if unit.owner == faction_id1:
                tile = self.game_map.get_tile(unit.x, unit.y)

                # Check if on a base owned by former pact partner
                if tile.base and tile.base.owner == faction_id2:
                    units_to_evacuate.append(unit)
                    continue

                # Check if sharing tile with former pact partner's units
                if tile.units:
                    for other_unit in tile.units:
                        if other_unit != unit and other_unit.owner == faction_id2:
                            units_to_evacuate.append(unit)
                            break

        # Evacuate each unit to nearest friendly base
        for unit in units_to_evacuate:
            # Find nearest friendly base
            nearest_base = None
            min_distance = float('inf')

            for base in self.bases:
                if base.owner == faction_id1:
                    # Calculate distance (Manhattan distance with wrapping)
                    dx = abs(base.x - unit.x)
                    if dx > self.game_map.width // 2:
                        dx = self.game_map.width - dx
                    dy = abs(base.y - unit.y)
                    distance = dx + dy

                    if distance < min_distance:
                        min_distance = distance
                        nearest_base = base

            # Teleport unit to nearest base
            if nearest_base:
                # Remove from old position
                old_tile = self.game_map.get_tile(unit.x, unit.y)
                if old_tile and unit in old_tile.units:
                    old_tile.units.remove(unit)

                # Add to new position
                unit.x = nearest_base.x
                unit.y = nearest_base.y
                new_tile = self.game_map.get_tile(unit.x, unit.y)
                if new_tile and unit not in new_tile.units:
                    new_tile.units.append(unit)

                evacuated_count += 1

        return evacuated_count

    def check_faction_elimination(self):
        """Check if any faction has been eliminated and trigger popup.

        A faction is eliminated when they have no bases remaining.
        """
        # Count bases per player
        bases_per_player = {}
        for base in self.bases:
            bases_per_player[base.owner] = bases_per_player.get(base.owner, 0) + 1

        # Check each AI faction for elimination
        for faction_id in self.ai_faction_ids:
            # Skip if already marked as eliminated
            if faction_id in self.eliminated_factions:
                continue

            # Check if this faction has no bases
            # Only eliminate if they've previously founded a base — prevents false eliminations
            # before any colony pods have had a chance to settle (e.g. on turn 1)
            if bases_per_player.get(faction_id, 0) == 0 and faction_id in self.factions_that_had_bases:
                # Faction has been eliminated!
                self.eliminated_factions.add(faction_id)
                self.pending_faction_eliminations.append(faction_id)

                # Remove from faction_contacts
                if faction_id in self.faction_contacts:
                    self.faction_contacts.remove(faction_id)

                # Remove all units belonging to this faction
                units_to_remove = [u for u in self.units if u.owner == faction_id]
                for unit in units_to_remove:
                    self._remove_unit(unit)

                print(f"Faction {faction_id} has been eliminated! Removed {len(units_to_remove)} units.")

    def _spawn_production(self, base, item_name):
        """Spawn a completed production item at a base.

        Handles three types of production:
        1. Stockpile Energy - adds energy to reserves
        2. Facilities/Projects - already added to base in process_turn()
        3. Units - creates new Unit and adds to map

        For units, extracts chassis speed from name (temporary until full
        design data lookup implemented). Sets home_base for support tracking.

        Args:
            base (Base): The base that completed production
            item_name (str): Name of the unit or facility to create

        Note:
            Called from _start_new_turn() after upkeep phase completes.
            Facilities are already in base.facilities by this point.
        """
        # Handle Stockpile Energy
        if item_name == "Stockpile Energy":
            # Convert production to energy
            energy_gained = 1 + base.population
            self.energy_credits += energy_gained
            self.set_status_message(f"{base.name}: Stockpile Energy +{energy_gained}")
            print(f"{base.name} stockpiled {energy_gained} energy")
            return

        # Check if it's a facility or secret project
        facility_data = facilities.get_facility_by_name(item_name)
        if facility_data:
            # Facilities are already added to base.facilities in base.process_turn()
            # Check if it's a secret project
            project_data = facilities.get_facility_by_id(facility_data['id'])
            if project_data in facilities.SECRET_PROJECTS:
                # Mark as globally built
                self.built_projects.add(facility_data['id'])
                self.set_status_message(f"{base.name} completed {item_name}!")
                print(f"SECRET PROJECT COMPLETED: {item_name}")
            else:
                self.set_status_message(f"{base.name} built {item_name}")
            return

        # Find design for this unit
        from game.units.unit_components import generate_unit_name
        from game.units.unit import Unit
        design = None

        # Get designs from base owner's faction
        faction_designs = self.factions[base.owner].designs
        for d in faction_designs.get_designs():
            design_name = generate_unit_name(
                d['weapon'], d['chassis'], d['armor'], d['reactor'],
                d.get('ability1', 'none'), d.get('ability2', 'none')
            )
            if design_name == item_name:
                design = d
                break

        if not design:
            # Fallback: Create Scout Patrol (all factions start with this capability)
            print(f"WARNING: No design found for {item_name}, spawning Scout Patrol as fallback")
            unit = Unit(
                x=base.x, y=base.y,
                chassis='infantry',
                owner=base.owner,
                name="Scout Patrol",
                weapon='hand_weapons',
                armor='no_armor',
                reactor='fission'
            )
            unit.home_base = base
            base.supported_units.append(unit)
            self.units.append(unit)
            self.game_map.add_unit_at(base.x, base.y, unit)
            self.set_status_message(f"{base.name} completed Scout Patrol (fallback)")
            return

        # Extract components from design
        chassis = design['chassis']
        weapon = design['weapon']
        armor = design['armor']
        reactor = design['reactor']
        ability1 = design.get('ability1', 'none')
        ability2 = design.get('ability2', 'none')

        # Create unit
        unit = Unit(
            x=base.x, y=base.y,
            chassis=chassis,
            owner=base.owner,
            name=item_name,
            weapon=weapon,
            armor=armor,
            reactor=reactor,
            ability1=ability1,
            ability2=ability2
        )

        # Assign home base
        unit.home_base = base
        base.supported_units.append(unit)

        # Command Center bonus: land units start with +2 morale (additive)
        # Note: This applies after any SE/facility/project bonuses to starting morale
        if unit.type == 'land' and 'command_center' in base.facilities:
            original_morale = unit.morale_level
            unit.morale_level = min(7, unit.morale_level + 2)  # Cap at Elite (7)
            if unit.morale_level > original_morale:
                morale_gained = unit.morale_level - original_morale
                print(f"  Command Center: +{morale_gained} morale (now {unit.morale_level})")

        self.units.append(unit)
        self.game_map.add_unit_at(base.x, base.y, unit)
        self.set_status_message(f"{base.name} completed {item_name}")
        print(f"{base.name} spawned {item_name} at ({base.x}, {base.y})")

    def set_status_message(self, message, duration=3000):
        """Set a status message to display temporarily."""
        self.status_message = message
        self.status_message_timer = duration





    def update(self, dt):
        """Update game state (will be used for turn logic later)."""
        # Update status message timer
        if self.status_message_timer > 0:
            self.status_message_timer -= dt
            if self.status_message_timer <= 0:
                self.status_message = ""

        # Update battle animation (handled by Combat class)
        self.combat.update(dt)

    def get_ai_status_text(self):
        """Get text describing current AI state."""
        if self.processing_ai and self.current_ai_index < len(self.ai_players):
            ai = self.ai_players[self.current_ai_index]
            return f"AI Player {ai.player_id} is thinking..."
        return None

    def all_friendly_units_moved(self):
        """Check if all friendly units have exhausted their movement or are held.

        Returns:
            bool: True if all friendly units have moves_remaining <= 0 or are held
        """
        friendly_units = [u for u in self.units if u.is_friendly(self.player_faction_id)]
        if not friendly_units:
            return False
        return all(
            u.moves_remaining <= 0 or u.held or
            (getattr(u, 'is_former', False) and getattr(u, 'terraforming_action', None))
            for u in friendly_units
        )

    def apply_council_proposal_effect(self, proposal_id, passed=True, winner=None):
        """Apply the effects of a passed council proposal.

        Args:
            proposal_id (str): ID of the proposal
            passed (bool): Whether the proposal passed
            winner (str): Winner for candidate-type proposals
        """
        if not passed:
            return

        if proposal_id == "UNITY_CORE":
            # Award 500 energy credits to the faction that proposed/won
            self.energy_credits += 500
            self.set_status_message("Unity Fusion Core salvaged! +500 energy credits")

        elif proposal_id == "GLOBAL_TRADE":
            # Doubles commerce from treaties/pacts (commerce.py handles calculation)
            self.global_trade_pact_active = True
            self.set_status_message("Global Trade Pact enacted! Commerce doubled")
            # This would need to be tracked and applied in base calculations
            # For now, just notify the player

        elif proposal_id == "SOLAR_SHADE":
            # Lower sea levels (would need map modification logic)
            self.set_status_message("Solar Shade launched! Sea levels dropping...")
            # TODO: Implement terrain transformation from ocean to land

        elif proposal_id == "MELT_CAPS":
            # Raise sea levels (would need map modification logic)
            self.set_status_message("Polar caps melting! Sea levels rising...")
            # TODO: Implement terrain transformation from land to ocean

        elif proposal_id == "ATROCITY":
            # Remove atrocity prohibitions
            self.set_status_message("Atrocity prohibitions removed!")
            # This would affect diplomatic penalties for nerve stapling, etc.

        elif proposal_id == "GOVERNOR":
            # Elect planetary governor (diplomatic victory condition)
            if winner:
                self.set_status_message(f"{winner} elected Planetary Governor!")


    def add_faction_contact(self, faction_id):
        """Add a faction to our contacts and check if we have all contacts.

        Args:
            faction_id (int): The faction ID we've contacted (0-6)
        """
        if faction_id == self.player_faction_id:
            return  # Don't count self

        self.faction_contacts.add(faction_id)

        # Check if we have all NON-ELIMINATED factions (excluding player)
        living_factions = set()
        for faction_id in range(7):
            if faction_id != self.player_faction_id and faction_id not in self.eliminated_factions:
                living_factions.add(faction_id)

        # If we've contacted all living factions, set flag
        if living_factions.issubset(self.faction_contacts):
            self.all_contacts_obtained = True



    # Tech IDs whose discoverer immediately receives a second random tech
    SECRETS_TECHS = {'Brain', 'AlphCen', 'Create'}

    def _grant_secrets_bonus(self, completed_tech_id, tech_tree, faction_id):
        """If the completed tech is a 'Secrets of' tech, grant a free bonus tech.

        The bonus tech is chosen randomly from techs the faction could research
        next (prereqs met, not yet discovered, not the same tech).
        """
        if completed_tech_id not in self.SECRETS_TECHS:
            return

        import random
        available = [tid for tid, _ in tech_tree.get_available_techs() if tid != completed_tech_id]
        if not available:
            return

        bonus_id = random.choice(available)
        bonus_name = tech_tree.technologies[bonus_id]['name']
        tech_tree.discovered_techs.add(bonus_id)
        if tech_tree.current_research == bonus_id:
            tech_tree.current_research = None
            tech_tree.research_points = 0

        if faction_id == self.player_faction_id:
            secrets_name = tech_tree.technologies[completed_tech_id]['name']
            self.upkeep_events.append({
                'type': 'tech_complete',
                'tech_id': bonus_id,
                'tech_name': bonus_name,
                'subtitle': f'Bonus from {secrets_name}'
            })
            self._auto_generate_unit_designs(bonus_id)
            print(f"Secrets bonus: player received '{bonus_name}'")
        else:
            print(f"AI faction {faction_id} received Secrets bonus tech '{bonus_name}'")

    def _auto_generate_unit_designs(self, completed_tech_id):
        """Check if tech unlocks components and generate smart unit designs.

        Called during end_turn() when a tech is completed. Checks if the new
        tech unlocks any weapons/armor/chassis, then generates tactical unit
        variants (offensive/defensive) using the new components.

        Sets pending_new_designs_flag (not new_designs_available directly) so
        popup shows AFTER upkeep events, not during tech announcement.

        Args:
            completed_tech_id (str): The tech ID that was just completed (e.g., 'Physic')

        Side Effects:
            - Calls workshop.rebuild_available_designs() to add new designs
            - Sets self.pending_new_designs_flag if designs added
            - Flag converts to new_designs_available when upkeep ends

        Note:
            Does nothing if ui_manager not initialized. Falls back to
            designs_need_rebuild flag for later processing.
        """
        # Check if this tech unlocks anything first
        if hasattr(self, 'ui_manager') and self.ui_manager is not None:
            workshop = self.ui_manager.design_workshop_screen
            player_tech_tree = self.factions[self.player_faction_id].tech_tree

            # Check what the tech unlocks
            unlocks_components, component_types = workshop.check_if_tech_unlocks_components(
                completed_tech_id, player_tech_tree
            )

            if unlocks_components:
                print(f"Tech '{completed_tech_id}' unlocks: {component_types}")

                # Generate designs targeting the new components
                faction_designs = self.factions[self.player_faction_id].designs
                old_count = len(faction_designs.get_designs())
                workshop.rebuild_available_designs(player_tech_tree, self, completed_tech_id)
                new_count = len(faction_designs.get_designs())

                # Show popup if new designs were added (after upkeep events)
                if new_count > old_count:
                    self.pending_new_designs_flag = True  # Will show after upkeep
                    print(f"New designs available! ({old_count} -> {new_count})")
            else:
                print(f"Tech '{completed_tech_id}' doesn't unlock any new components")
        else:
            # Fallback: set flag for later rebuild
            self.designs_need_rebuild = True

    def check_victory(self):
        """Check if the game is over due to any victory condition.

        Victory conditions:
        1. Conquest: Eliminate all enemy factions
        2. Diplomatic: Elected Supreme Leader for 20+ consecutive turns
        3. Economic: 50000+ energy credits and Economic Victory project complete
        4. Transcendence: Complete Ascent to Transcendence secret project
        5. Scenario: Custom objectives (if enabled)
        """
        # Count bases by owner
        player_bases = [b for b in self.bases if b.owner == self.player_faction_id]
        enemy_bases = [b for b in self.bases if b.owner != self.player_faction_id]

        # Track if players have ever had bases
        if len(player_bases) > 0:
            self.player_ever_had_base = True
        if len(enemy_bases) > 0:
            self.enemy_ever_had_base = True

        # Check DEFEAT: Player has lost all bases
        if self.player_ever_had_base and len(player_bases) == 0:
            self.game_over = True
            self.winner = 1  # AI wins (first AI player)
            self.victory_type = "conquest"
            print("GAME OVER: Player has been defeated!")
            self.set_status_message("DEFEAT: All your bases have been destroyed!")
            return

        # Check CONQUEST VICTORY: All enemy bases destroyed
        if self.enemy_ever_had_base and len(enemy_bases) == 0:
            self.game_over = True
            self.winner = self.player_faction_id
            self.victory_type = "conquest"
            print("VICTORY: All enemy bases destroyed!")
            self.set_status_message("CONQUEST VICTORY: All enemy factions eliminated!")
            return

        # Check ECONOMIC VICTORY: 50000 credits + Economic Victory project
        if self.energy_credits >= 50000:
            if hasattr(self, 'economic_victory_complete') and self.economic_victory_complete:
                self.game_over = True
                self.winner = self.player_faction_id
                self.victory_type = "economic"
                print("VICTORY: Economic victory achieved!")
                self.set_status_message("ECONOMIC VICTORY: Economic dominance achieved!")
                return

        # Check TRANSCENDENCE VICTORY: Ascent to Transcendence complete
        if hasattr(self, 'transcendence_victory_complete') and self.transcendence_victory_complete:
            self.game_over = True
            self.winner = self.player_faction_id
            self.victory_type = "transcendence"
            print("VICTORY: Transcendence achieved!")
            self.set_status_message("TRANSCENDENCE VICTORY: Ascended to a higher plane!")
            return

        #  Check DIPLOMATIC VICTORY
        if self.diplomatic_victory_complete:
            self.game_over = True
            self.winner = self.player_faction_id
            self.victory_type = "diplomatic"
            print("VICTORY: Diplomatic achieved!")
            self.set_status_message("DIPLOMATIC VICTORY: You are supreme leader!")
            return

    def new_game(self, player_faction_id=None, player_name=None):
        """Start a fresh game.

        Args:
            player_faction_id (int): Faction ID for the player (0-6)
            player_name (str): Player's custom name (optional)
        """
        # Update player info if provided
        if player_faction_id is not None:
            self.player_faction_id = player_faction_id
        if player_name is not None:
            self.player_name = player_name

        self.game_map = GameMap(self.map_width, self.map_height)
        self.turn = 1
        self.mission_year = 2100
        self.energy_credits = 0
        self.units = []
        self.bases = []
        self.selected_unit = None
        self.processing_ai = False
        self.current_ai_index = 0
        self.ai_unit_queue = []
        self.ai_current_unit_index = 0
        self.status_message = ""
        self.status_message_timer = 0
        self.supply_pod_message = None
        self.supply_pod_tech_event = None
        self.mid_turn_upkeep = False
        self.game_over = False
        self.winner = None
        self.victory_type = None
        self.resigned = False
        self.player_ever_had_base = False
        self.enemy_ever_had_base = False
        self.diplomatic_victory_complete = False
        self.economic_victory_complete = False
        self.transcendence_victory_complete = False
        self.upkeep_phase_active = False
        self.upkeep_events = []
        self.current_upkeep_event_index = 0
        self.pending_production = []
        self.faction_contacts = set()
        self.all_contacts_obtained = False
        self.shown_all_contacts_popup = False
        self.pending_commlink_requests = []
        self.designs_need_rebuild = False

        # Recreate factions with new tech trees and designs
        from game.faction import Faction
        from game.units.unit_design import UnitDesign
        self.factions = {}
        for faction_id in range(7):
            is_player = (faction_id == self.player_faction_id)
            self.factions[faction_id] = Faction(faction_id, is_player=is_player)
            self.factions[faction_id].tech_tree = TechTree()
            self._grant_starting_tech(faction_id)
            self.factions[faction_id].tech_tree.auto_select_research()
            self.factions[faction_id].designs = UnitDesign(faction_id)
        self.territory = TerritoryManager(self.game_map)
        self.built_projects = set()
        self.se_selections = {
            'Politics': 0,
            'Economics': 0,
            'Values': 0,
            'Future Society': 0
        }
        self.ai_faction_ids = [fid for fid in range(7) if fid != self.player_faction_id]
        self.ai_players = [AIPlayer(fid) for fid in self.ai_faction_ids]
        self.center_camera_on_selected = False
        self.center_camera_on_tile = None
        self._spawn_test_units()
        # Update territory after spawning (in case any bases were created)
        self.territory.update_territory(self.bases)

    def to_dict(self):
        """Serialize entire game state to dictionary.

        Returns:
            dict: Complete game state as dictionary
        """
        from datetime import datetime

        # Build unit index map for references
        unit_index_map = {unit: idx for idx, unit in enumerate(self.units)}

        return {
            'version': '1.0',
            'save_timestamp': datetime.now().isoformat(),
            'game_state': {
                'turn': self.turn,
                'difficulty': self.difficulty,
                'mission_year': self.mission_year,
                'energy_credits': self.energy_credits,
                'player_id': self.player_faction_id,
                'player_faction_id': self.player_faction_id,
                'player_name': self.player_name,
                'built_projects': list(self.built_projects),
                'se_selections': self.se_selections.copy(),
                'game_over': self.game_over,
                'winner': self.winner,
                'player_ever_had_base': self.player_ever_had_base,
                'enemy_ever_had_base': self.enemy_ever_had_base,
                'ai_faction_ids': self.ai_faction_ids,
                'faction_contacts': list(self.faction_contacts),
                'eliminated_factions': list(self.eliminated_factions),
                'factions_that_had_bases': list(self.factions_that_had_bases),
                'infiltrated_datalinks': list(self.infiltrated_datalinks),
                'diplo_relations': self.ui_manager.diplomacy.diplo_relations.copy() if hasattr(self, 'ui_manager') and hasattr(self.ui_manager, 'diplomacy') else {},
                'atrocity_count': self.atrocity_count,
                'sanctions_turns_remaining': self.sanctions_turns_remaining,
                'permanent_vendetta_factions': list(self.permanent_vendetta_factions),
                'major_atrocity_committed': self.major_atrocity_committed,
                'integrity_level': self.integrity_level,
                'truce_expiry_turns': {str(k): v for k, v in self.truce_expiry_turns.items()},
                'global_energy_allocation': self.global_energy_allocation.copy()
            },
            'map': self.game_map.to_dict(),
            'units': [u.to_dict() for u in self.units],
            'bases': [b.to_dict(unit_index_map) for b in self.bases],
            'factions': {
                faction_id: {
                    'id': faction.id,
                    'is_player': faction.is_player,
                    'tech_tree': faction.tech_tree.to_dict() if faction.tech_tree else None,
                    'designs': faction.designs.to_dict() if faction.designs else None,
                    'energy_credits': faction.energy_credits,
                    'relations': faction.relations,
                    'contacts': list(faction.contacts)
                }
                for faction_id, faction in self.factions.items()
            },
            'selected_unit_index': unit_index_map.get(self.selected_unit, None)
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct game state from dictionary.

        Args:
            data (dict): Game state dictionary

        Returns:
            Game: Reconstructed game instance
        """
        # Create empty game without initialization
        game = cls.__new__(cls)

        # Restore simple state
        gs = data['game_state']
        game.turn = gs['turn']
        game.difficulty = gs['difficulty']
        game.mission_year = gs['mission_year']
        game.energy_credits = gs['energy_credits']
        game.player_id = gs['player_id']
        game.player_faction_id = gs['player_faction_id']
        game.player_name = gs['player_name']
        game.built_projects = set(gs['built_projects'])
        game.secret_project_notifications = []
        game.known_ai_secret_projects = set()
        game.known_ai_secret_project_warnings = set()
        game.se_selections = gs['se_selections']
        game.game_over = gs['game_over']
        game.winner = gs['winner']
        game.player_ever_had_base = gs['player_ever_had_base']
        game.enemy_ever_had_base = gs['enemy_ever_had_base']
        game.ai_faction_ids = gs['ai_faction_ids']
        game.faction_contacts = set(gs['faction_contacts'])
        game.eliminated_factions = set(gs['eliminated_factions'])
        game.factions_that_had_bases = set(gs['factions_that_had_bases'])
        game.infiltrated_datalinks = set(gs['infiltrated_datalinks'])
        game.atrocity_count = gs['atrocity_count']
        game.sanctions_turns_remaining = gs['sanctions_turns_remaining']
        game.permanent_vendetta_factions = set(gs['permanent_vendetta_factions'])
        game.major_atrocity_committed = gs['major_atrocity_committed']
        game.integrity_level = gs['integrity_level']
        game.truce_expiry_turns = {int(k): v for k, v in gs['truce_expiry_turns'].items()}
        game.global_energy_allocation = gs['global_energy_allocation']
        # Store diplo_relations for later restoration (after ui_manager is created)
        saved_diplo_relations = gs['diplo_relations']

        # Rebuild complex objects
        game.game_map = GameMap.from_dict(data['map'])
        # Store map dimensions for new_game() resets
        game.map_width = game.game_map.width
        game.map_height = game.game_map.height
        game.units = [Unit.from_dict(u) for u in data['units']]
        game.bases = [Base.from_dict(b, game.units) for b in data['bases']]

        # Rebuild tile references (units and bases)
        for unit in game.units:
            tile = game.game_map.get_tile(unit.x, unit.y)
            if tile:
                tile.units.append(unit)

        for base in game.bases:
            tile = game.game_map.get_tile(base.x, base.y)
            if tile:
                tile.base = base

        # Restore factions
        from game.faction import Faction
        from game.units.unit_design import UnitDesign
        game.factions = {}
        for faction_id_str, faction_data in data['factions'].items():
            faction_id = int(faction_id_str)
            faction = Faction(faction_id, is_player=faction_data['is_player'])
            faction.energy_credits = faction_data['energy_credits']
            faction.relations = faction_data['relations']
            faction.contacts = set(faction_data['contacts'])
            if faction_data['tech_tree']:
                faction.tech_tree = TechTree.from_dict(faction_data['tech_tree'])
            if faction_data['designs']:
                faction.designs = UnitDesign.from_dict(faction_data['designs'])
            else:
                faction.designs = UnitDesign(faction_id)
            game.factions[faction_id] = faction

        # Restore AI players
        game.ai_players = [AIPlayer(fid) for fid in game.ai_faction_ids]

        # Restore selected unit
        sel_idx = data['selected_unit_index']
        game.selected_unit = game.units[sel_idx] if sel_idx is not None else None

        # Restore territory
        game.territory = TerritoryManager(game.game_map)
        game.territory.update_territory(game.bases)

        # Initialize runtime state (not saved)
        game.running = True
        game.status_message = ""
        game.status_message_timer = 0
        game.supply_pod_message = None
        game.supply_pod_tech_event = None
        game.mid_turn_upkeep = False
        game.pending_major_atrocity_popup = False
        game.pending_artifact_link = None
        game.pending_busy_former = None
        game.pending_terraform_cost = None
        game.pending_movement_overflow_unit = None
        game.pending_treaty_break = None
        game.pending_ai_attack = None
        game.processing_ai = False
        game.current_ai_index = 0
        game.ai_unit_queue = []
        game.ai_current_unit_index = 0
        game.center_camera_on_selected = True  # Center on selected unit when loading
        game.center_camera_on_tile = None
        game.tile_cursor_mode = False
        game.cursor_x = 0
        game.cursor_y = 0
        game.last_unit_action = None
        game.pending_commlink_requests = []
        game.pending_faction_eliminations = []
        game.all_contacts_obtained = False
        game.shown_all_contacts_popup = False
        game.designs_need_rebuild = False
        game.new_designs_available = False
        game.pending_production = []
        game.upkeep_phase_active = False
        game.upkeep_events = []
        game.current_upkeep_event_index = 0
        game.auto_cycle_timer = 0
        game.debug = DebugManager()
        game.ui_manager = None  # Will be set by main.py after loading
        game._saved_diplo_relations = saved_diplo_relations  # Temporary storage until ui_manager is created

        # Initialize combat system
        game.combat = Combat(game)
        game.movement = MovementManager(game)
        game.turns = TurnManager(game)

        # Initialize auto-cycle delay
        game.auto_cycle_delay = 500  # Wait 500ms before auto-cycling

        # Initialize victory tracking
        game.victory_type = None
        game.diplomatic_victory_complete = False
        game.economic_victory_complete = False
        game.transcendence_victory_complete = False
        game.pending_new_designs_flag = False

        return game