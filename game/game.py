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
import pygame
from game.data import constants
from game import facilities
from game.map import GameMap
from game.unit import Unit
from game.base import Base
from game.ai import AIPlayer
from game.tech import TechTree
from game.territory import TerritoryManager
from game.combat import Combat
from game.data.constants import UNIT_LAND, UNIT_SEA, UNIT_AIR, UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA
from game.debug import DebugManager  # DEBUG: Remove for release


class Game:
    """Main game state manager."""

    def __init__(self, player_faction_id=0, player_name=None, ocean_percentage=None):
        """Initialize a new game.

        Args:
            player_faction_id (int): Faction ID for the player (0-6)
            player_name (str): Player's custom name (optional)
            ocean_percentage (int): Percentage of ocean tiles (30-90)
        """
        self.game_map = GameMap(constants.MAP_WIDTH, constants.MAP_HEIGHT, ocean_percentage)
        self.turn = 1
        self.running = True
        self.player_faction_id = player_faction_id  # Which faction the player chose
        self.player_name = player_name  # Player's custom name
        self.mission_year = 2100  # Starting year
        self.energy_credits = 0  # Starting credits

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

        # Battle system
        self.combat = Combat(self)
        self.pending_battle = None  # Dict with attacker, defender, target_x, target_y
        self.active_battle = None  # Dict tracking ongoing battle animation

        # Get list of AI faction IDs (all factions except player's)
        self.ai_faction_ids = [fid for fid in range(7) if fid != player_faction_id]

        # Technology
        self.tech_tree = TechTree()  # Player's tech tree
        self._grant_starting_tech()  # Grant faction's starting technology
        self.tech_tree.auto_select_research()  # Start with an active research
        self.ai_tech_trees = {}  # AI tech trees by faction_id
        for ai_faction_id in self.ai_faction_ids:
            self.ai_tech_trees[ai_faction_id] = TechTree()
            self._grant_starting_tech_for_ai(ai_faction_id)
            self.ai_tech_trees[ai_faction_id].auto_select_research()

        # Facilities and Projects
        self.built_projects = set()  # Global set of secret projects built (one per game)

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
        self.player_ever_had_base = False  # Track if player has founded at least one base
        self.enemy_ever_had_base = False  # Track if enemy has founded at least one base

        # Victory condition tracking
        self.supreme_leader_complete = False  # Turn when player became supreme leader (None if not leader)
        self.economic_victory_complete = False  # Has Economic Victory project been completed?
        self.transcendence_complete = False  # Has Ascent to Transcendence been completed?

        # Upkeep phase
        self.upkeep_phase_active = False  # Is upkeep phase currently showing?
        self.upkeep_events = []  # List of events to show during upkeep
        self.current_upkeep_event_index = 0  # Current event being displayed

        # Auto-cycle timer
        self.auto_cycle_timer = 0  # Time in ms since last unit action
        self.auto_cycle_delay = 500  # Wait 500ms (0.5 seconds) before auto-cycling

        # Production queue (for spawning at start of next turn)
        self.pending_production = []  # List of (base, item_name) tuples to spawn

        # Flag to rebuild unit designs when tech is completed
        self.designs_need_rebuild = False
        self.new_designs_available = False  # Flag for popup to view new units
        self.pending_new_designs_flag = False  # Delayed flag (shows after upkeep)

        # Commlink tracking (contacts with other factions)
        self.faction_contacts = []  # List of faction IDs we've contacted (preserves order)
        self.all_contacts_obtained = False  # Flag: have we contacted all living factions?
        self.shown_all_contacts_popup = False  # Flag: have we shown the popup?
        self.pending_commlink_requests = []  # List of {faction_id, player_id} dicts for AI contact popups
        self.eliminated_factions = set()  # Set of faction IDs that have been eliminated
        self.pending_faction_eliminations = []  # List of faction_ids for elimination popups

        # Camera control
        self.center_camera_on_selected = False  # Flag to center camera on selected unit
        self.center_camera_on_tile = None  # Tuple (x, y) to center camera on specific tile

        # DEBUG: Debug/cheat mode manager (remove for release)
        self.debug = DebugManager()

        # Spawn some initial units for testing
        self._spawn_test_units()

    def _grant_starting_tech(self):
        """Grant the player's faction starting technology (without prerequisites)."""
        from game.data.data import FACTIONS

        if self.player_faction_id < len(FACTIONS):
            starting_tech = FACTIONS[self.player_faction_id].get('starting_tech')
            if starting_tech and starting_tech in self.tech_tree.technologies:
                self.tech_tree.discovered_techs.add(starting_tech)
                tech_name = self.tech_tree.technologies[starting_tech]['name']
                print(f"Player starts with {tech_name}")

    def _grant_starting_tech_for_ai(self, ai_faction_id):
        """Grant an AI faction's starting technology (without prerequisites).

        Args:
            ai_faction_id (int): The AI faction ID (0-6, excluding player's faction)
        """
        from game.data.data import FACTIONS

        if ai_faction_id < len(FACTIONS):
            starting_tech = FACTIONS[ai_faction_id].get('starting_tech')
            if starting_tech and starting_tech in self.ai_tech_trees[ai_faction_id].technologies:
                self.ai_tech_trees[ai_faction_id].discovered_techs.add(starting_tech)
                tech_name = self.ai_tech_trees[ai_faction_id].technologies[starting_tech]['name']
                print(f"AI Faction {ai_faction_id} starts with {tech_name}")

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
                if tile.is_land() and not tile.supply_pod:  # Exclude supply pod tiles
                    land_tiles.append((x, y))
                elif not tile.is_land():
                    ocean_tiles.append((x, y))

        print(f"Found {len(land_tiles)} land tiles (no supply pods), {len(ocean_tiles)} ocean tiles")

        # Need at least 14 land tiles (7 factions * 2 units each)
        if len(land_tiles) < 14:
            print("Warning: Not enough land tiles to spawn all faction units")
            return

        # Distribute starting positions across the map
        # Each faction gets a Scout Patrol and a Colony Pod on the same tile
        import random
        random.shuffle(land_tiles)  # Randomize spawn positions

        tile_idx = 0
        # Spawn player faction first, then AI factions
        all_faction_ids = [self.player_faction_id] + self.ai_faction_ids

        for faction_id in all_faction_ids:
            # Get faction data for naming
            from game.data.data import FACTIONS
            faction_name = FACTIONS[faction_id]['name'] if faction_id < len(FACTIONS) else f"Faction{faction_id}"
            faction_prefix = "Player" if faction_id == self.player_faction_id else faction_name

            # Both units spawn on the same tile
            if tile_idx < len(land_tiles):
                x, y = land_tiles[tile_idx]
                tile_idx += 1  # Move to next tile for next faction

                # Scout Patrol (owner = faction_id)
                unit = Unit(x, y, UNIT_LAND, faction_id, f"{faction_prefix} Scout Patrol")
                self.units.append(unit)
                self.game_map.set_unit_at(x, y, unit)
                print(f"Spawned {faction_prefix} Scout Patrol at ({x}, {y})")

                # Colony Pod (same tile, owner = faction_id)
                unit = Unit(x, y, UNIT_COLONY_POD_LAND, faction_id, f"{faction_prefix} Colony Pod")
                self.units.append(unit)
                self.game_map.set_unit_at(x, y, unit)
                print(f"Spawned {faction_prefix} Colony Pod at ({x}, {y})")

        print(f"Total units spawned: {len(self.units)}")

        # Auto-select first friendly unit
        friendly_units = [u for u in self.units if u.owner == self.player_faction_id]
        if friendly_units:
            self.selected_unit = friendly_units[0]
            self.center_camera_on_selected = True  # Flag to center camera on game start
            print(f"Selected {self.selected_unit.name}")

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
        if tile.base and tile.base.garrison:
            friendly_garrison = [u for u in tile.base.garrison if u.is_friendly(self.player_faction_id)]
            if friendly_garrison:
                # If currently selected unit is in this garrison, select next one
                if self.selected_unit in friendly_garrison:
                    current_idx = friendly_garrison.index(self.selected_unit)
                    next_idx = (current_idx + 1) % len(friendly_garrison)
                    self.selected_unit = friendly_garrison[next_idx]
                    return 'unit_selected', self.selected_unit
                else:
                    # Select first garrison unit
                    self.selected_unit = friendly_garrison[0]
                    return 'unit_selected', self.selected_unit

        # If there's a base but no garrison units, clicking opens base view
        if tile.base:
            return 'base_click', tile.base

        # Check if clicked on a unit on the tile
        clicked_unit = self.game_map.get_unit_at(tile_x, tile_y)
        if clicked_unit and clicked_unit.is_friendly(self.player_faction_id):
            # Select friendly unit
            self.selected_unit = clicked_unit

        return None

    def _violates_zone_of_control(self, unit, from_x, from_y, to_x, to_y):
        """Check if a move violates zone of control rules.

        Args:
            unit: The unit attempting to move
            from_x, from_y: Starting position
            to_x, to_y: Target position

        Returns:
            bool: True if move violates ZOC, False if allowed
        """
        from game.data.constants import UNIT_LAND, UNIT_ARTIFACT

        # Only land units are affected by ZOC
        if unit.unit_type not in [UNIT_LAND, UNIT_ARTIFACT]:
            return False

        # Check if starting position has enemy ZOC
        start_has_enemy_zoc = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x = (from_x + dx) % self.game_map.width
                check_y = from_y + dy
                if not self.game_map.is_valid_position(check_x, check_y):
                    continue

                tile = self.game_map.get_tile(check_x, check_y)
                if tile and tile.units:
                    for other_unit in tile.units:
                        if other_unit.owner != unit.owner:
                            start_has_enemy_zoc = True
                            break

        # Check if target position has enemy ZOC
        target_has_enemy_zoc = False
        target_tile = self.game_map.get_tile(to_x, to_y)

        # Exception: Can move into squares with friendly units
        if target_tile and target_tile.units:
            if any(u.owner == unit.owner for u in target_tile.units):
                return False  # Friendly units present, ZOC doesn't apply

        # Exception: Can move into or out of bases
        from_tile = self.game_map.get_tile(from_x, from_y)
        if (from_tile and from_tile.base) or (target_tile and target_tile.base):
            return False

        # Exception: Can attack adjacent enemy units (this is handled elsewhere)
        if target_tile and target_tile.units:
            if any(u.owner != unit.owner for u in target_tile.units):
                return False  # This is an attack, allowed

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x = (to_x + dx) % self.game_map.width
                check_y = to_y + dy
                if not self.game_map.is_valid_position(check_x, check_y):
                    continue

                tile = self.game_map.get_tile(check_x, check_y)
                if tile and tile.units:
                    for other_unit in tile.units:
                        if other_unit.owner != unit.owner:
                            target_has_enemy_zoc = True
                            break

        # Violation: moving between two squares both in enemy ZOC
        return start_has_enemy_zoc and target_has_enemy_zoc

    def try_move_unit(self, unit, target_x, target_y):
        """Attempt to move a unit to target coordinates.

        Handles adjacency checks, terrain compatibility, zone of control,
        combat initiation, and garrison management. If moving into an enemy
        unit, initiates combat (with prediction screen for player, immediate
        for AI).

        Args:
            unit (Unit): Unit to move
            target_x (int): Target X coordinate (will be wrapped)
            target_y (int): Target Y coordinate (must be valid, no wrapping)

        Returns:
            bool: True if move succeeded or combat initiated, False if invalid move

        Side Effects:
            - May set self.pending_battle for player combat
            - May call resolve_combat() for AI combat
            - Updates unit position and map state
            - Manages garrison entry/exit
            - Sets relationship to Vendetta on combat
        """
        # Wrap X coordinate horizontally
        target_x = target_x % self.game_map.width

        # Y doesn't wrap - must be valid
        if target_y < 0 or target_y >= self.game_map.height:
            return False

        # Check if target is adjacent (one tile in any of 8 directions, with wrapping)
        dx = target_x - unit.x
        # Handle wrapping for adjacency check
        if dx > self.game_map.width // 2:
            dx -= self.game_map.width
        elif dx < -self.game_map.width // 2:
            dx += self.game_map.width

        dy = abs(target_y - unit.y)

        if abs(dx) > 1 or dy > 1:
            print(f"Cannot move: target too far (dx={dx}, dy={dy})")
            return False

        target_tile = self.game_map.get_tile(target_x, target_y)

        # Check if unit can move there
        if not unit.can_move_to(target_tile):
            return False

        # Check zone of control
        if self._violates_zone_of_control(unit, unit.x, unit.y, target_x, target_y):
            if unit.owner == self.player_faction_id:
                self.set_status_message("Cannot move: Zone of Control violation!")
            return False

        # Check if there are units at target (stacking support)
        if target_tile.units and len(target_tile.units) > 0:
            # Get first unit in stack (defender in combat, or check if friendly)
            first_unit = target_tile.units[0]

            # Check if it's an enemy unit
            if first_unit.owner != unit.owner:
                # Enemy stack - initiate combat with first unit
                if unit.owner == self.player_faction_id:
                    # Set up pending battle - UI will show prediction screen
                    self.pending_battle = {
                        'attacker': unit,
                        'defender': first_unit,
                        'target_x': target_x,
                        'target_y': target_y
                    }
                    return True  # Battle initiated
                else:
                    # AI unit attacking - resolve immediately (no prediction screen)
                    self.resolve_combat(unit, first_unit, target_x, target_y)
                    return True
            # else: Friendly unit(s) - allow stacking, continue below

        # Clear old position and remove from garrison if leaving a base
        old_tile = self.game_map.get_tile(unit.x, unit.y)
        if old_tile:
            self.game_map.remove_unit_at(unit.x, unit.y, unit)
            # Remove from garrison if was in a base
            if old_tile.base and unit in old_tile.base.garrison:
                old_tile.base.garrison.remove(unit)
                print(f"{unit.name} left {old_tile.base.name}")

        # Move unit
        unit.move_to(target_x, target_y)
        self.game_map.add_unit_at(target_x, target_y, unit)

        # If unit was held, unheld it when manually moved
        if hasattr(unit, 'held') and unit.held:
            unit.held = False
            if unit.owner == self.player_faction_id:
                self.set_status_message(f"{unit.name} unheld")

        # Reset auto-cycle timer when unit moves
        if unit.owner == self.player_faction_id:
            self.auto_cycle_timer = pygame.time.get_ticks()

        # Check for first contact with adjacent enemy units
        self._check_first_contact(unit, target_x, target_y)

        # Update displayed unit index to show the unit that just moved
        if target_tile and unit in target_tile.units:
            target_tile.displayed_unit_index = target_tile.units.index(unit)

        # Check for supply pod (air units cannot collect supply pods)
        if target_tile.supply_pod and unit.unit_type != UNIT_AIR:
            self._collect_supply_pod(target_tile, unit)

        # Check for monolith
        if target_tile.monolith:
            self._apply_monolith_effects(unit)

        # Check for base capture (enemy base with no garrison)
        if target_tile.base:
            base = target_tile.base
            if base.owner != unit.owner and len(base.garrison) == 0:
                # Capture the base!
                old_owner = base.owner

                # Reduce population by 1
                base.population -= 1

                # Check if base is destroyed
                if base.population <= 0:
                    # Base is destroyed
                    if unit.owner == self.player_faction_id:
                        self.set_status_message(f"Destroyed {base.name}!")
                        print(f"Player destroyed {base.name}!")
                    else:
                        self.set_status_message(f"AI destroyed {base.name}!")
                        print(f"AI player {unit.owner} destroyed {base.name}!")

                    # Remove base from game
                    self.bases.remove(base)
                    target_tile.base = None

                    # Check if this eliminated the faction
                    self.check_faction_elimination()

                    # Update territory
                    self.territory.update_territory(self.bases)

                    # Check for victory/defeat immediately
                    self.check_victory()
                else:
                    # Base captured successfully
                    base.owner = unit.owner
                    base.turns_since_capture = 0  # Mark as newly captured for disloyal citizens

                    # Heal unit to full health when capturing base
                    if unit.current_health < unit.max_health:
                        unit.current_health = unit.max_health
                        if unit.owner == self.player_faction_id:
                            self.set_status_message(f"{unit.name} healed to full health!")

                    # Recalculate production and growth based on new population
                    base.nutrients_needed = base._calculate_nutrients_needed()
                    base.growth_turns_remaining = base._calculate_growth_turns()
                    base.production_turns_remaining = base._calculate_production_turns()

                    # Update territory
                    self.territory.update_territory(self.bases)

                    # Show message
                    if unit.owner == self.player_faction_id:
                        self.set_status_message(f"Captured {base.name}! (Pop {base.population})")
                        print(f"Player captured {base.name}! New population: {base.population}")
                    else:
                        self.set_status_message(f"AI captured {base.name}!")
                        print(f"AI player {unit.owner} captured {base.name}! New population: {base.population}")

                    # Check for victory/defeat immediately
                    self.check_victory()

        # If moving into a base, add to garrison
        if target_tile.base and target_tile.base.owner == unit.owner:
            if unit not in target_tile.base.garrison:
                target_tile.base.garrison.append(unit)
                print(f"{unit.name} garrisoned at {target_tile.base.name}")

        return True

    def _collect_supply_pod(self, tile, unit):
        """Handle unit collecting a supply pod.

        Args:
            tile: The tile with the supply pod
            unit: The unit collecting the pod
        """
        import random
        from game.data.constants import UNIT_ARTIFACT

        # Remove the pod from the tile
        tile.supply_pod = False

        # 25% chance to find an artifact, 75% chance for energy credits
        if random.random() < 0.25:
            # Create artifact unit at this location
            from game.unit import Unit
            artifact = Unit(tile.x, tile.y, UNIT_ARTIFACT, unit.owner, "Alien Artifact")
            artifact.moves_remaining = 0  # Can't move on turn discovered
            artifact.has_moved = True
            self.units.append(artifact)
            self.game_map.add_unit_at(tile.x, tile.y, artifact)

            if unit.owner == self.player_faction_id:
                self.supply_pod_message = "Supply Pod discovered! You found an Alien Artifact!"
                print(f"Artifact found at ({tile.x}, {tile.y})")
            else:
                print(f"AI found artifact at ({tile.x}, {tile.y})")
        else:
            # Grant 500 energy credits
            if unit.owner == self.player_faction_id:
                self.energy_credits += 500
                self.supply_pod_message = "Supply Pod discovered! You gain 500 energy credits."
                print(f"Supply pod collected at ({tile.x}, {tile.y}): +500 credits")
            else:
                # AI collected it
                print(f"AI collected supply pod at ({tile.x}, {tile.y})")

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

            morale_names = ["Very Very Green", "Very Green", "Green", "Disciplined",
                          "Hardened", "Veteran", "Commando", "Elite"]
            morale_name = morale_names[unit.morale_level] if unit.morale_level < len(morale_names) else "Elite"

            if unit.owner == self.player_faction_id:
                self.set_status_message(f"{unit.name} upgraded to {morale_name} at Monolith!")
                print(f"Unit upgraded at monolith: ({unit.x}, {unit.y}) -> {morale_name}")
        elif not unit.monolith_upgrade:
            # Already at max morale, mark as upgraded so they don't try again
            unit.monolith_upgrade = True
            if unit.owner == self.player_faction_id:
                self.set_status_message(f"{unit.name} visited Monolith (already Elite)")

    def get_combat_modifiers(self, unit, is_defender=False, vs_unit=None):
        """Get all combat modifiers for a unit.

        Args:
            unit (Unit): Unit to get modifiers for
            is_defender (bool): Whether unit is defending
            vs_unit (Unit): Opponent unit (for mode bonuses)

        Returns:
            list: List of modifier dicts with 'name' and 'multiplier' keys
        """
        modifiers = []

        # Morale modifier
        if hasattr(unit, 'morale_level'):
            morale_multipliers = {
                0: 0.70,  # Very Very Green: -30%
                1: 0.85,  # Very Green: -15%
                2: 1.00,  # Green: no modifier
                3: 1.10,  # Disciplined: +10%
                4: 1.20,  # Hardened: +20%
                5: 1.30,  # Veteran: +30%
                6: 1.40,  # Commando: +40%
                7: 1.50   # Elite: +50%
            }
            multiplier = morale_multipliers.get(unit.morale_level, 1.0)
            if multiplier != 1.0:
                morale_name = unit.get_morale_name()
                percent = int((multiplier - 1.0) * 100)
                sign = '+' if percent > 0 else ''
                modifiers.append({
                    'name': f'Morale ({morale_name})',
                    'multiplier': multiplier,
                    'display': f'{sign}{percent}%'
                })

        # Defender bonuses
        if is_defender:
            tile = self.game_map.get_tile(unit.x, unit.y)

            # Base defense bonus
            if tile and tile.base:
                modifiers.append({
                    'name': 'Base Defense',
                    'multiplier': 1.25,
                    'display': '+25%'
                })

            # Trance defending vs Psi (+50%)
            if vs_unit and hasattr(unit, 'abilities'):
                if 'trance' in unit.abilities and hasattr(vs_unit, 'weapon_mode') and vs_unit.weapon_mode == 'psi':
                    modifiers.append({
                        'name': 'Trance vs Psi',
                        'multiplier': 1.50,
                        'display': '+50%'
                    })

                # AAA vs air units (+100%)
                if 'AAA' in unit.abilities and vs_unit.unit_type == UNIT_AIR:
                    modifiers.append({
                        'name': 'AAA vs Air',
                        'multiplier': 2.00,
                        'display': '+100%'
                    })

            # AAA Tracking ability (+100% vs air)
            if vs_unit and getattr(unit, 'has_aaa_tracking', False) and vs_unit.unit_type == UNIT_AIR:
                modifiers.append({
                    'name': 'AAA Tracking',
                    'multiplier': 2.00,
                    'display': '+100%'
                })

            # Blink Displacer ignores base defenses (cancel base defense if attacker has it)
            if vs_unit and getattr(vs_unit, 'has_blink_displacer', False) and tile and tile.base:
                # We'll handle this by reducing the base defense bonus, but that needs to be done
                # on the attacker side. For now, we'll add a note that defender loses base bonus.
                pass

            # Sensor range bonus (+25%) - check if there's a friendly sensor array nearby.
            # Implement once terraforming is added.
            friendly_sensor_nearby = False
            #TODO: Sensor check

            if friendly_sensor_nearby:
                modifiers.append({
                    'name': 'Sensor Range',
                    'multiplier': 1.25,
                    'display': '+25%'
                })

        # Attacker bonuses
        else:
            tile = self.game_map.get_tile(unit.x, unit.y)
            defender_tile = self.game_map.get_tile(vs_unit.x, vs_unit.y) if vs_unit else None

            # Infantry attacking base bonus
            if unit.unit_type == UNIT_LAND and defender_tile and defender_tile.base:
                modifiers.append({
                    'name': 'Infantry vs Base',
                    'multiplier': 1.25,
                    'display': '+25%'
                })

            # Airdrop penalty - check if unit has used airdrop this turn
            if hasattr(unit, 'used_airdrop') and unit.used_airdrop:
                modifiers.append({
                    'name': 'Airdrop Penalty',
                    'multiplier': 0.50,
                    'display': '-50%'
                })

            # Comm Jammer reduces enemy defense (-50% to defender's effective armor)
            if getattr(unit, 'has_comm_jammer', False):
                modifiers.append({
                    'name': 'Comm Jammer',
                    'multiplier': 1.50,  # +50% attack (equivalent to -50% enemy defense)
                    'display': '+50%'
                })

            # Blink Displacer ignores base defenses
            if getattr(unit, 'has_blink_displacer', False) and defender_tile and defender_tile.base:
                modifiers.append({
                    'name': 'Blink Displacer',
                    'multiplier': 1.25,  # Negates base defense
                    'display': '+25%'
                })

            # Empath Song attacking Psi (+50% vs psi)
            if vs_unit and hasattr(unit, 'abilities'):
                if 'empath' in unit.abilities and hasattr(vs_unit, 'armor_mode') and vs_unit.armor_mode == 'psi':
                    modifiers.append({
                        'name': 'Empath vs Psi',
                        'multiplier': 1.50,
                        'display': '+50%'
                    })

            # Empath Song (new ability system)
            if vs_unit and getattr(unit, 'has_empath_song', False):
                if hasattr(vs_unit, 'armor_mode') and vs_unit.armor_mode == 'psi':
                    modifiers.append({
                        'name': 'Empath Song',
                        'multiplier': 1.50,
                        'display': '+50%'
                    })

        # Combat mode bonuses (both attacker and defender)
        if vs_unit and hasattr(unit, 'weapon_mode') and hasattr(vs_unit, 'armor_mode'):
            # Projectile weapon vs Energy armor = +25%
            if unit.weapon_mode == 'projectile' and vs_unit.armor_mode == 'energy':
                modifiers.append({
                    'name': 'Mode: Proj vs Energy',
                    'multiplier': 1.25,
                    'display': '+25%'
                })
            # Energy weapon vs Projectile armor = +25%
            elif unit.weapon_mode == 'energy' and vs_unit.armor_mode == 'projectile':
                modifiers.append({
                    'name': 'Mode: Energy vs Proj',
                    'multiplier': 1.25,
                    'display': '+25%'
                })
            # Binary armor = no bonus for anyone
            # Missile weapons = never get mode bonus

        return modifiers

    def can_disengage(self, unit, opponent, current_hp, max_hp):
        """Check if a unit can disengage from combat.

        Args:
            unit (Unit): Unit attempting to disengage
            opponent (Unit): Opposing unit
            current_hp (int): Unit's current HP
            max_hp (int): Unit's maximum HP

        Returns:
            bool: True if unit successfully disengages
        """
        import random

        # Check if unit is damaged to 50% or less
        if current_hp > max_hp * 0.5:
            return False

        # Check if unit has speed advantage (at least 2 more movement points)
        unit_moves = unit.max_moves()
        opponent_moves = opponent.max_moves()

        if unit_moves < opponent_moves + 2:
            return False

        # Calculate disengage chance based on morale and speed advantage
        # Base 50% chance, +10% per morale level, +5% per extra move point
        base_chance = 0.5
        morale_bonus = 0.1 * unit.morale_level if hasattr(unit, 'morale_level') else 0
        speed_bonus = 0.05 * (unit_moves - opponent_moves - 2)

        disengage_chance = min(0.9, base_chance + morale_bonus + speed_bonus)

        return random.random() < disengage_chance

    def calculate_combat_odds(self, attacker, defender):
        """Calculate combat odds for battle prediction screen.

        Args:
            attacker (Unit): Attacking unit
            defender (Unit): Defending unit

        Returns:
            float: Probability of attacker winning (0.0 to 1.0)
        """
        # Base strength: weapon/armor * health
        attacker_base_strength = attacker.weapon * attacker.current_health
        defender_base_strength = defender.armor * defender.current_health

        # Apply modifiers (pass opponent for mode bonuses)
        attacker_modifiers = self.get_combat_modifiers(attacker, is_defender=False, vs_unit=defender)
        defender_modifiers = self.get_combat_modifiers(defender, is_defender=True, vs_unit=attacker)

        attacker_strength = attacker_base_strength
        for mod in attacker_modifiers:
            attacker_strength *= mod['multiplier']

        defender_strength = defender_base_strength
        for mod in defender_modifiers:
            defender_strength *= mod['multiplier']

        total_strength = attacker_strength + defender_strength
        if total_strength == 0:
            return 0.5  # 50/50 if both have 0 strength

        return attacker_strength / total_strength

    def resolve_combat(self, attacker, defender, target_x, target_y):
        """Resolve combat between two units.

        Sets up active_battle dict with pre-simulated combat rounds for
        frame-by-frame animation. Combat uses weapon vs armor with modifiers,
        damage is 1-3 HP per round. Units can disengage at 50% health loss.

        Also updates diplomatic relations to Vendetta when combat occurs.

        Args:
            attacker (Unit): The attacking unit
            defender (Unit): The defending unit
            target_x (int): Target tile X coordinate (where defender is)
            target_y (int): Target tile Y coordinate

        Side Effects:
            - Sets self.active_battle with pre-simulated combat rounds
            - Updates diplomacy relations to Vendetta
            - Does NOT modify unit HP yet (happens during animation)
            - Does NOT move attacker yet (happens after combat resolves)

        Note:
            Actual HP changes and unit removal happen in the update loop
            when active_battle animation completes.
        """
        import random

        # Save original health values
        original_attacker_hp = attacker.current_health
        original_defender_hp = defender.current_health

        # Set relationship to Vendetta when combat occurs
        if hasattr(self, 'ui_manager') and hasattr(self.ui_manager, 'diplo_manager'):
            # unit.owner IS faction_id
            attacker_faction_id = attacker.owner
            defender_faction_id = defender.owner

            # Update diplomacy relations to Vendetta
            diplo = self.ui_manager.diplo_manager
            # Both factions now have Vendetta
            if defender.owner == self.player_faction_id:
                # AI attacked player - set AI faction to Vendetta from player's perspective
                diplo.diplo_relations[attacker_faction_id] = 'Vendetta'
            elif attacker.owner == self.player_faction_id:
                # Player attacked AI - set AI faction to Vendetta
                diplo.diplo_relations[defender_faction_id] = 'Vendetta'

        # Set up active battle for animation
        self.active_battle = {
            'attacker': attacker,
            'defender': defender,
            'target_x': target_x,
            'target_y': target_y,
            'rounds': [],
            'current_round': 0,
            'round_timer': 0,
            'round_delay': 750,  # 0.75 seconds between hits in milliseconds
            'complete': False
        }

        # Get modifiers (calculated once at battle start, pass opponent for mode bonuses)
        attacker_modifiers = self.get_combat_modifiers(attacker, is_defender=False, vs_unit=defender)
        defender_modifiers = self.get_combat_modifiers(defender, is_defender=True, vs_unit=attacker)

        attacker_modifier_total = 1.0
        for mod in attacker_modifiers:
            attacker_modifier_total *= mod['multiplier']

        defender_modifier_total = 1.0
        for mod in defender_modifiers:
            defender_modifier_total *= mod['multiplier']

        # Simulate combat using temporary HP values (don't modify units yet)
        sim_attacker_hp = original_attacker_hp
        sim_defender_hp = original_defender_hp

        while sim_attacker_hp > 0 and sim_defender_hp > 0:
            # Calculate odds for this round based on current sim HP and modifiers
            attacker_strength = attacker.weapon * sim_attacker_hp * attacker_modifier_total
            defender_strength = defender.armor * sim_defender_hp * defender_modifier_total
            total_strength = attacker_strength + defender_strength

            if total_strength == 0:
                odds = 0.5
            else:
                odds = attacker_strength / total_strength

            # Determine who wins this round
            attacker_wins_round = random.random() < odds

            # Determine damage (1-3 points)
            damage = random.randint(1, 3)

            if attacker_wins_round:
                sim_defender_hp -= damage
                if sim_defender_hp < 0:
                    sim_defender_hp = 0
                self.active_battle['rounds'].append({
                    'winner': 'attacker',
                    'damage': damage,
                    'attacker_hp': sim_attacker_hp,
                    'defender_hp': sim_defender_hp
                })

                # Check if defender can disengage
                if sim_defender_hp > 0 and self.can_disengage(defender, attacker, sim_defender_hp, original_defender_hp):
                    self.active_battle['disengaged'] = 'defender'
                    break
            else:
                sim_attacker_hp -= damage
                if sim_attacker_hp < 0:
                    sim_attacker_hp = 0
                self.active_battle['rounds'].append({
                    'winner': 'defender',
                    'damage': damage,
                    'attacker_hp': sim_attacker_hp,
                    'defender_hp': sim_defender_hp
                })

                # Check if attacker can disengage
                if sim_attacker_hp > 0 and self.can_disengage(attacker, defender, sim_attacker_hp, original_attacker_hp):
                    self.active_battle['disengaged'] = 'attacker'
                    break

        # Determine final outcome
        if 'disengaged' in self.active_battle:
            self.active_battle['victor'] = 'disengage'
        elif sim_attacker_hp <= 0:
            self.active_battle['victor'] = 'defender'
        else:
            self.active_battle['victor'] = 'attacker'

    def _finish_battle(self):
        """Clean up after battle completes."""
        if not self.active_battle:
            return

        attacker = self.active_battle['attacker']
        defender = self.active_battle['defender']
        victor = self.active_battle['victor']

        # Get final HP from last round
        if self.active_battle['rounds']:
            final_round = self.active_battle['rounds'][-1]
            attacker.current_health = final_round['attacker_hp']
            defender.current_health = final_round['defender_hp']

        # Handle disengage
        if victor == 'disengage':
            disengaged_unit = attacker if self.active_battle.get('disengaged') == 'attacker' else defender

            # Find safe retreat tile (away from enemy, back toward friendly territory)
            retreat_tile = self._find_retreat_tile(disengaged_unit)

            if retreat_tile:
                # Move unit to retreat tile
                old_tile = self.game_map.get_tile(disengaged_unit.x, disengaged_unit.y)
                if old_tile:
                    self.game_map.remove_unit_at(disengaged_unit.x, disengaged_unit.y, disengaged_unit)

                disengaged_unit.x = retreat_tile[0]
                disengaged_unit.y = retreat_tile[1]

                new_tile = self.game_map.get_tile(retreat_tile[0], retreat_tile[1])
                if new_tile:
                    self.game_map.add_unit_at(retreat_tile[0], retreat_tile[1], disengaged_unit)

                # Unit has no moves left after disengaging
                disengaged_unit.moves_remaining = 0

            # Show disengage message
            if disengaged_unit.owner == self.player_faction_id:
                self.set_status_message(f"{disengaged_unit.name} disengaged from combat!")

            # Clear battle state
            self.active_battle = None
            return

        # Remove destroyed unit and award experience
        if victor == 'defender':
            # Attacker destroyed
            self._remove_unit(attacker)
            # Defender records kill and gains experience
            defender.record_kill()
            # Attacker consumed their move/turn
            # (already happened when they initiated attack)
        else:
            # Defender destroyed
            self._remove_unit(defender)
            # Attacker records kill and gains experience
            attacker.record_kill()
            # Attacker consumed their move/turn

        # Clear battle state
        self.active_battle = None

    def _find_retreat_tile(self, unit):
        """Find a safe tile for a unit to retreat to after disengaging.

        Args:
            unit (Unit): Unit that is retreating

        Returns:
            tuple: (x, y) coordinates of retreat tile, or None if no safe tile found
        """
        # Check all adjacent tiles
        adjacent_tiles = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                new_x = (unit.x + dx) % self.game_map.width
                new_y = unit.y + dy

                if not (0 <= new_y < self.game_map.height):
                    continue

                tile = self.game_map.get_tile(new_x, new_y)
                if not tile or not unit.can_move_to(tile):
                    continue

                # Check if tile has enemy units
                has_enemy = False
                if tile.units:
                    for other_unit in tile.units:
                        if other_unit.owner != unit.owner:
                            has_enemy = True
                            break

                if not has_enemy:
                    # Calculate "safety score" - prefer tiles closer to friendly bases
                    safety_score = 0
                    for base in self.bases:
                        if base.owner == unit.owner:
                            dist = abs(new_x - base.x) + abs(new_y - base.y)
                            safety_score -= dist  # Negative distance = closer is better

                    adjacent_tiles.append(((new_x, new_y), safety_score))

        # Sort by safety score (highest first)
        adjacent_tiles.sort(key=lambda x: x[1], reverse=True)

        # Return safest tile
        if adjacent_tiles:
            return adjacent_tiles[0][0]

        # No safe tiles found - stay in place
        return None

    def _remove_unit(self, unit):
        """Remove a unit from the game completely.

        Args:
            unit (Unit): Unit to remove
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

        # Deselect if this was the selected unit
        if self.selected_unit == unit:
            # Try to select next friendly unit
            friendly_units = [u for u in self.units if u.is_friendly(self.player_faction_id)]
            self.selected_unit = friendly_units[0] if friendly_units else None

    def load_unit_onto_transport(self, unit, transport):
        """Load a unit onto a transport.

        Args:
            unit (Unit): Land unit to load
            transport (Unit): Sea transport to load onto

        Returns:
            bool: True if loading succeeded
        """
        if not transport.can_load_unit(unit):
            if transport.transport_capacity == 0:
                self.set_status_message(f"{transport.name} cannot carry units")
            elif len(transport.loaded_units) >= transport.transport_capacity:
                self.set_status_message(f"{transport.name} is full!")
            else:
                self.set_status_message(f"Cannot load {unit.name}")
            return False

        # Remove unit from map (it's now inside the transport)
        tile = self.game_map.get_tile(unit.x, unit.y)
        if tile:
            self.game_map.remove_unit_at(unit.x, unit.y, unit)

        # Load unit
        transport.load_unit(unit)
        unit.x = transport.x
        unit.y = transport.y

        self.set_status_message(f"{unit.name} loaded onto {transport.name}")
        return True

    def unload_unit_from_transport(self, transport, unit, target_x, target_y):
        """Unload a unit from a transport.

        Args:
            transport (Unit): Sea transport carrying the unit
            unit (Unit): Unit to unload
            target_x (int): X coordinate to unload to
            target_y (int): Y coordinate to unload to

        Returns:
            bool: True if unloading succeeded
        """
        if unit not in transport.loaded_units:
            return False

        # Check if target tile is adjacent to transport
        dx = abs(target_x - transport.x)
        dy = abs(target_y - transport.y)
        if max(dx, dy) > 1:
            self.set_status_message("Can only unload to adjacent tiles")
            return False

        # Check if target tile is land
        target_tile = self.game_map.get_tile(target_x, target_y)
        if not target_tile or target_tile.terrain == 'ocean':
            self.set_status_message("Cannot unload into ocean")
            return False

        # Unload unit
        transport.unload_unit(unit, target_x, target_y)

        # Add unit to map
        self.game_map.add_unit_at(target_x, target_y, unit)

        self.set_status_message(f"{unit.name} unloaded")
        return True

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
        base_damage = unit.weapon * random.randint(1, 3)
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
                target_techs = self.ai_tech_trees.get(target_base.owner, self.tech_tree).discovered_techs
                stealable = target_techs - self.tech_tree.discovered_techs

                if stealable:
                    stolen_tech = random.choice(list(stealable))
                    tech_name = self.tech_tree.technologies[stolen_tech]['name']
                    self.tech_tree.discovered_techs.add(stolen_tech)
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
        """Check for first contact with adjacent enemy units and establish commlink.

        Args:
            unit: The unit that just moved
            x: Current x position
            y: Current y position
        """
        # Only check for player or AI units
        if unit.owner < 0 or unit.owner > 6:
            return

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
                    #TODO: both just printed 0 when neither was Deirdre. We are using bad ID values.
                    if unit.owner == self.player_faction_id:
                        # Player met the AI faction (owner IS faction_id)
                        other_faction_id = other_unit.owner
                        if other_faction_id not in self.faction_contacts:
                            self.faction_contacts.append(other_faction_id)  # Append to preserve contact order
                            print(f"Player established contact with faction {other_faction_id}")

                            # Show commlink request popup (player initiated contact)
                            if not hasattr(self, 'pending_commlink_requests'):
                                self.pending_commlink_requests = []
                            self.pending_commlink_requests.append({
                                'other_faction_id': other_faction_id,
                                'player_faction_id': self.player_faction_id
                            })

                            # Check if we have all living factions now
                            living_factions = set()
                            for base in self.bases:
                                if base.owner != self.player_faction_id:
                                    living_factions.add(base.owner)  # owner IS faction_id

                            if living_factions.issubset(set(self.faction_contacts)):
                                self.all_contacts_obtained = True

                    elif other_unit.owner == self.player_faction_id:
                        # AI met the player (owner IS faction_id)
                        other_faction_id = unit.owner
                        if other_faction_id not in self.faction_contacts:
                            self.faction_contacts.append(other_faction_id)  # Append to preserve contact order
                            print(f"Player established contact with faction {other_faction_id}")

                            # Show commlink request popup (AI initiated contact)
                            if not hasattr(self, 'pending_commlink_requests'):
                                self.pending_commlink_requests = []
                            self.pending_commlink_requests.append({
                                'other_faction_id': other_faction_id,
                                'player_faction_id': self.player_faction_id
                            })

                            # Check if we have all living factions now
                            living_factions = set()
                            for base in self.bases:
                                if base.owner != self.player_faction_id:
                                    living_factions.add(base.owner)  # owner IS faction_id

                            if living_factions.issubset(self.faction_contacts):
                                self.all_contacts_obtained = True

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
        from game.data.data import FACTIONS
        import random

        # Get faction ID for this player
        # player_id IS faction_id
        faction_id = player_id
        if faction_id >= len(FACTIONS):
            # Fallback if faction not found
            player_bases = [b for b in self.bases if b.owner == player_id]
            return f"Base {len(player_bases) + 1}"

        faction = FACTIONS[faction_id]
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
            base.facilities.append('Headquarters')
            print(f"First base founded - Headquarters added automatically")

        self.bases.append(base)

        # Update the tile
        if tile:
            tile.base = base
            self.game_map.remove_unit_at(unit.x, unit.y, unit)

        # Add any other friendly units at this location to the garrison
        other_units = [u for u in self.units if u != unit and u.x == unit.x and u.y == unit.y and u.owner == unit.owner]
        for other_unit in other_units:
            if other_unit not in base.garrison:
                base.garrison.append(other_unit)
                print(f"{other_unit.name} garrisoned at newly founded {base.name}")

        # Remove the unit
        self.units.remove(unit)

        # Deselect if this was the selected unit
        if self.selected_unit == unit:
            self.selected_unit = None
            # Trigger auto-cycle after delay if player unit
            if unit.owner == self.player_faction_id:
                self.auto_cycle_timer = pygame.time.get_ticks()

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
            if bases_per_player.get(faction_id, 0) == 0:
                # Faction has been eliminated!
                self.eliminated_factions.add(faction_id)
                self.pending_faction_eliminations.append(faction_id)

                # Remove from faction_contacts
                if faction_id in self.faction_contacts:
                    self.faction_contacts.remove(faction_id)

                print(f"Faction {faction_id} has been eliminated!")

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

        # Map unit names to unit types
        unit_type_map = {
            "Scout Patrol": UNIT_LAND,
            "Gunship Foil": UNIT_SEA,
            "Gunship Needlejet": UNIT_AIR,
            "Colony Pod": UNIT_COLONY_POD_LAND,
            "Sea Colony Pod": UNIT_COLONY_POD_SEA
        }

        unit_type = unit_type_map.get(item_name, UNIT_LAND)

        # Determine chassis speed based on unit name (temporary until full design lookup)
        chassis_speed = None
        if "Speeder" in item_name or "Rover" in item_name:
            chassis_speed = 2
        elif "Hovertank" in item_name or "Tank" in item_name:
            chassis_speed = 3
        elif "Foil" in item_name:
            chassis_speed = 4
        elif "Cruiser" in item_name or "Destroyer" in item_name:
            chassis_speed = 6
        elif "Needlejet" in item_name or "Copter" in item_name or "Chopper" in item_name:
            chassis_speed = 8
        elif "Gravship" in item_name:
            chassis_speed = 8

        # Spawn at the base location (stacking is now allowed)
        unit = Unit(base.x, base.y, unit_type, base.owner, item_name, chassis_speed=chassis_speed)

        # Assign home base for unit support
        unit.home_base = base
        base.supported_units.append(unit)

        self.units.append(unit)
        self.game_map.add_unit_at(base.x, base.y, unit)
        self.set_status_message(f"{base.name} completed {item_name}")
        print(f"{base.name} spawned {item_name} at ({base.x}, {base.y})")

    def set_status_message(self, message, duration=3000):
        """Set a status message to display temporarily."""
        self.status_message = message
        self.status_message_timer = duration

    def check_auto_cycle(self):
        """Check if enough time has passed to auto-cycle to next unit."""
        # Only auto-cycle for player units, not during AI turn
        if self.processing_ai or self.upkeep_phase_active:
            return

        # Check if timer is set (non-zero) and delay has elapsed
        if self.auto_cycle_timer > 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.auto_cycle_timer >= self.auto_cycle_delay:
                # Check if current unit has no moves left or unit was removed (e.g., founded base)
                if (not self.selected_unit) or (self.selected_unit.moves_remaining <= 0):
                    # Auto-cycle to next unit
                    self.cycle_units()
                # Reset timer
                self.auto_cycle_timer = 0

    def cycle_units(self):
        """Select next friendly unit (W key). Cycles only through units that still have moves."""
        friendly_units = [u for u in self.units if u.is_friendly(self.player_faction_id)]

        if not friendly_units:
            return

        # Filter to units with moves remaining and not held
        units_with_moves = [u for u in friendly_units if u.moves_remaining > 0 and not u.held]

        # If no units have moves, do nothing
        if not units_with_moves:
            return

        # Cycle through units in sequence
        if self.selected_unit in units_with_moves:
            current_idx = units_with_moves.index(self.selected_unit)
            next_idx = (current_idx + 1) % len(units_with_moves)
            self.selected_unit = units_with_moves[next_idx]
        else:
            self.selected_unit = units_with_moves[0]

        # Update displayed unit on the map tile to show the selected unit
        if self.selected_unit:
            tile = self.game_map.get_tile(self.selected_unit.x, self.selected_unit.y)
            if tile and self.selected_unit in tile.units:
                tile.displayed_unit_index = tile.units.index(self.selected_unit)
            # Center camera on newly selected unit
            self.center_camera_on_selected = True

    def end_turn(self):
        """End player turn and begin AI/upkeep sequence.

        Processing order:
        1. Reset all player units (restore moves, remove fortify)
        2. Process air unit fuel (refuel at bases, crash if no fuel)
        3. Process all player bases:
           - Production progress
           - Population growth
           - Energy allocation (economy/labs/psych)
           - Collect completed items → pending_production
        4. Add economy output to energy_credits
        5. Process tech research:
           - Add labs output to research_accumulated
           - Check for tech completion
           - If tech complete → add to upkeep_events
           - If tech complete → auto-generate unit designs (sets pending flag)
        6. Increment mission_year
        7. Start AI processing (sets processing_ai = True)

        Note:
            - Upkeep phase starts when player clicks through AI turns
            - New turn doesn't start until upkeep_events are dismissed
            - Production spawning happens at start of new turn (after upkeep)
        """
        # Reset player units
        for unit in self.units:
            if unit.owner == self.player_faction_id:
                unit.end_turn()

        # Refuel air units at bases and check for crashes
        self._process_air_unit_fuel(self.player_faction_id)

        # Process player bases at end of player turn
        total_economy = 0
        total_labs = 0
        for base in self.bases:
            if base.owner == self.player_faction_id:
                completed_item = base.process_turn(self.global_energy_allocation)
                if completed_item:
                    # Store for spawning at start of next turn (after upkeep)
                    self.pending_production.append((base, completed_item))

                # Collect energy outputs
                total_economy += base.economy_output
                total_labs += base.labs_output

        # Add economy output to energy reserves
        self.energy_credits += total_economy

        # Process player tech research with labs output
        self.tech_tree.add_research(total_labs)
        completed_tech = self.tech_tree.process_turn()

        # Store completed tech for upkeep phase announcement
        if completed_tech:
            if not hasattr(self, 'upkeep_events'):
                self.upkeep_events = []
            tech_name = self.tech_tree.technologies[completed_tech]['name']
            self.upkeep_events.append({
                'type': 'tech_complete',
                'tech_id': completed_tech,
                'tech_name': tech_name
            })

            # Auto-generate new unit designs based on newly unlocked components
            self._auto_generate_unit_designs(completed_tech)

        # Update mission year
        self.mission_year += 1

        # Start AI processing
        self.processing_ai = True
        self.current_ai_index = 0

    def process_ai_turns(self):
        """Process AI turns sequentially, one unit at a time.

        Called repeatedly from main loop with delay between units. For each
        AI player, resets their units then processes them one by one. After
        all AI players finish, collects upkeep events and starts upkeep phase.

        Returns:
            bool: True if still processing AI, False if all AI turns complete

        Flow:
        1. Setup AI player (reset units, build queue)
        2. Process one unit per call (move, attack, found bases)
        3. When player's queue empty, move to next AI player
        4. When all AIs done → collect upkeep events
        5. If upkeep events exist → start upkeep phase
        6. If no upkeep events → start new turn immediately

        Note:
            Centers camera on active AI unit for visibility.
            Checks victory conditions after all AI turns complete.
        """
        if not self.processing_ai:
            return False

        # If we don't have a unit queue, set up the next AI player
        if not self.ai_unit_queue:
            if self.current_ai_index < len(self.ai_players):
                ai_player = self.ai_players[self.current_ai_index]
                print(f"\n=== AI Player {ai_player.player_id} Turn ===")

                # Reset AI units for their turn
                for unit in self.units:
                    if unit.owner == ai_player.player_id:
                        unit.end_turn()

                # Queue up all AI units with moves
                self.ai_unit_queue = [u for u in self.units
                                     if u.owner == ai_player.player_id and u.moves_remaining > 0]
                self.ai_current_unit_index = 0
                return True
            else:
                # All AIs done, collect upkeep events and start upkeep phase
                self.processing_ai = False
                self._collect_upkeep_events()

                # If there are upkeep events, show them; otherwise start new turn immediately
                if self.upkeep_events:
                    self.upkeep_phase_active = True
                    self.current_upkeep_event_index = 0
                    print("Entering upkeep phase...")
                else:
                    self._start_new_turn()

                # Center camera on player's selected unit at start of their turn
                self.center_camera_on_selected = True

                # Check for victory/defeat
                self.check_victory()

                return False

        # Process one unit from the queue
        if self.ai_current_unit_index < len(self.ai_unit_queue):
            unit = self.ai_unit_queue[self.ai_current_unit_index]
            ai_player = self.ai_players[self.current_ai_index]

            # Center camera on AI unit
            self.center_camera_on_tile = (unit.x, unit.y)

            # Move this unit
            ai_player._move_unit(unit, self)

            self.ai_current_unit_index += 1
            return True
        else:
            # Done with this AI's units - process their bases and tech
            ai_player = self.ai_players[self.current_ai_index]

            # Process air unit fuel for this AI
            self._process_air_unit_fuel(ai_player.player_id)

            # AI energy allocation (fixed for now: 50% economy, 50% labs)
            ai_energy_allocation = {'economy': 50, 'labs': 50, 'psych': 0}
            total_labs = 0

            for base in self.bases:
                if base.owner == ai_player.player_id:
                    completed_item = base.process_turn(ai_energy_allocation)
                    if completed_item:
                        # Store for spawning at start of next turn (after upkeep)
                        self.pending_production.append((base, completed_item))
                    total_labs += base.labs_output

            # Process AI tech research with labs output
            if ai_player.player_id in self.ai_tech_trees:
                self.ai_tech_trees[ai_player.player_id].add_research(total_labs)
                self.ai_tech_trees[ai_player.player_id].process_turn()

            # Check if AI wants to call a council
            if hasattr(self, 'council_manager'):
                proposal_to_call = self.council_manager.check_ai_council_call(ai_player.player_id, self)
                if proposal_to_call:
                    self.council_manager.ai_call_council(proposal_to_call, self)

            print(f"=== AI Player {ai_player.player_id} Turn Complete ===\n")
            self.ai_unit_queue = []
            self.current_ai_index += 1
            return True

    def update(self, dt):
        """Update game state (will be used for turn logic later)."""
        # Update status message timer
        if self.status_message_timer > 0:
            self.status_message_timer -= dt
            if self.status_message_timer <= 0:
                self.status_message = ""

        # Update battle animation
        if self.active_battle and not self.active_battle['complete']:
            self.active_battle['round_timer'] += dt

            # Check if it's time for the next round
            if self.active_battle['round_timer'] >= self.active_battle['round_delay']:
                self.active_battle['round_timer'] = 0
                self.active_battle['current_round'] += 1

                # Check if battle is complete
                if self.active_battle['current_round'] >= len(self.active_battle['rounds']):
                    self.active_battle['complete'] = True
                    # Small delay before cleanup
                    self.active_battle['cleanup_timer'] = 1000  # 1 second

        # Clean up completed battle
        if self.active_battle and self.active_battle.get('complete'):
            if 'cleanup_timer' in self.active_battle:
                self.active_battle['cleanup_timer'] -= dt
                if self.active_battle['cleanup_timer'] <= 0:
                    self._finish_battle()

    def get_ai_status_text(self):
        """Get text describing current AI state."""
        if self.processing_ai and self.current_ai_index < len(self.ai_players):
            ai = self.ai_players[self.current_ai_index]
            return f"AI Player {ai.player_id} is thinking..."
        return None

    def all_friendly_units_moved(self):
        """Check if all friendly units have exhausted their movement.

        Returns:
            bool: True if all friendly units have moves_remaining <= 0
        """
        friendly_units = [u for u in self.units if u.is_friendly(self.player_faction_id)]
        if not friendly_units:
            return False
        return all(u.moves_remaining <= 0 for u in friendly_units)

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
            # Grant +1 commerce to all bases (implemented as economy bonus)
            self.set_status_message("Global Trade Pact enacted! +1 commerce in all bases")
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

    def _collect_upkeep_events(self):
        """Collect all upkeep events to display before new turn starts."""
        # Note: upkeep_events may already have tech_complete events from end_turn()
        # We just add additional events here

        # Check if we just obtained all faction contacts
        if self.all_contacts_obtained and not self.shown_all_contacts_popup:
            self.upkeep_events.append({
                'type': 'all_contacts',
                'message': "You have established contact with all factions! You may now call the Planetary Council."
            })
            self.shown_all_contacts_popup = True

        # Check player bases for riots and starvation
        for base in self.bases:
            if base.owner != self.player_faction_id:
                continue

            # Check for drone riots
            if base.drone_riot:
                self.upkeep_events.append({
                    'type': 'drone_riot',
                    'base': base,
                    'message': f"DRONE RIOT at {base.name}!"
                })

            # Check for starvation (nutrients < 0 would cause pop loss)
            # TODO: Implement starvation mechanics when food system is added
            # if base.nutrients_per_turn < 0:
            #     self.upkeep_events.append({
            #         'type': 'starvation',
            #         'base': base,
            #         'message': f"Citizens starving at {base.name}!"
            #     })

        # Note: New units/facilities available would be checked here
        # For now, just the events we've collected

    def add_faction_contact(self, faction_id):
        """Add a faction to our contacts and check if we have all contacts.

        Args:
            faction_id (int): The faction ID we've contacted (0-6)
        """
        if faction_id == self.player_faction_id:
            return  # Don't count self

        self.faction_contacts.add(faction_id)

        # Check if we have all living factions
        # Count living factions (those with at least one base)
        living_factions = set()
        for base in self.bases:
            if base.owner != self.player_faction_id:
                living_factions.add(base.owner)  # owner IS faction_id

        # If we've contacted all living factions, set flag
        if living_factions.issubset(self.faction_contacts):
            self.all_contacts_obtained = True

    def _start_new_turn(self):
        """Start a new turn after upkeep phase completes.

        Called from advance_upkeep_event() when all upkeep events dismissed.
        This is when production actually spawns (units/facilities completed
        during previous turn).

        Actions:
        1. Increment turn counter
        2. Spawn all pending_production items (units, facilities)
        3. Clear pending_production list
        4. Select first friendly unit if none selected

        Note:
            This is the actual "new turn starts" moment. end_turn() begins
            the sequence, but new turn doesn't start until after AI turns
            and upkeep phase complete.
        """
        self.turn += 1
        print(f"Turn {self.turn} started!")

        # Spawn all pending production from previous turn
        for base, item_name in self.pending_production:
            self._spawn_production(base, item_name)
        self.pending_production = []

        # Select a friendly unit if none selected
        if not self.selected_unit:
            friendly_units = [u for u in self.units if u.is_friendly(self.player_faction_id)]
            if friendly_units:
                self.selected_unit = friendly_units[0]

    def advance_upkeep_event(self):
        """Move to next upkeep event or exit upkeep phase.

        Called when player clicks through an upkeep event popup (tech discovery,
        base completion, diplomatic milestone, etc.).

        If all events shown:
        1. Exit upkeep phase (upkeep_phase_active = False)
        2. Convert pending_new_designs_flag → new_designs_available
        3. Call _start_new_turn() to spawn production and begin new turn

        Note:
            New designs popup shows AFTER upkeep, not during, to avoid
            showing units for tech the player hasn't seen announced yet.
        """
        if not self.upkeep_phase_active:
            return

        self.current_upkeep_event_index += 1

        # If we've shown all events, exit upkeep phase and start new turn
        if self.current_upkeep_event_index >= len(self.upkeep_events):
            self.upkeep_phase_active = False
            self.upkeep_events = []
            self.current_upkeep_event_index = 0

            # Show new designs popup AFTER upkeep events are complete
            if hasattr(self, 'pending_new_designs_flag') and self.pending_new_designs_flag:
                self.new_designs_available = True
                self.pending_new_designs_flag = False

            self._start_new_turn()

    def get_current_upkeep_event(self):
        """Get the current upkeep event to display.

        Returns:
            dict or None: Current event dict, or None if no events
        """
        if not self.upkeep_phase_active or not self.upkeep_events:
            return None

        if self.current_upkeep_event_index < len(self.upkeep_events):
            return self.upkeep_events[self.current_upkeep_event_index]

        return None

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
            workshop = self.ui_manager.social_screens.design_workshop_screen

            # Check what the tech unlocks
            unlocks_components, component_types = workshop.check_if_tech_unlocks_components(
                completed_tech_id, self.tech_tree
            )

            if unlocks_components:
                print(f"Tech '{completed_tech_id}' unlocks: {component_types}")

                # Generate designs targeting the new components
                old_count = len(workshop.unit_designs)
                workshop.rebuild_available_designs(self.tech_tree, completed_tech_id)
                new_count = len(workshop.unit_designs)

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
        if hasattr(self, 'transcendence_complete') and self.transcendence_complete:
            self.game_over = True
            self.winner = self.player_faction_id
            self.victory_type = "transcendence"
            print("VICTORY: Transcendence achieved!")
            self.set_status_message("TRANSCENDENCE VICTORY: Ascended to a higher plane!")
            return

        #  Check DIPLOMATIC VICTORY
        if self.supreme_leader_complete:
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

        self.game_map = GameMap(constants.MAP_WIDTH, constants.MAP_HEIGHT)
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
        self.pending_battle = None
        self.active_battle = None
        self.game_over = False
        self.winner = None
        self.victory_type = None
        self.player_ever_had_base = False
        self.enemy_ever_had_base = False
        self.supreme_leader_complete = False
        self.economic_victory_complete = False
        self.transcendence_complete = False
        self.upkeep_phase_active = False
        self.upkeep_events = []
        self.current_upkeep_event_index = 0
        self.pending_production = []
        self.faction_contacts = set()
        self.all_contacts_obtained = False
        self.shown_all_contacts_popup = False
        self.pending_commlink_requests = []
        self.designs_need_rebuild = False
        self.tech_tree = TechTree()
        self._grant_starting_tech()
        self.tech_tree.auto_select_research()
        self.ai_tech_trees = {}
        for ai_id in range(1, 7):
            self.ai_tech_trees[ai_id] = TechTree()
            self._grant_starting_tech_for_ai(ai_id)
            self.ai_tech_trees[ai_id].auto_select_research()
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
                'eliminated_factions': list(self.eliminated_factions)
            },
            'map': self.game_map.to_dict(),
            'units': [u.to_dict() for u in self.units],
            'bases': [b.to_dict(unit_index_map) for b in self.bases],
            'tech_tree': self.tech_tree.to_dict(),
            'ai_players': [
                {
                    'player_id': ai.player_id,
                    'tech_tree': self.ai_tech_trees[ai.player_id].to_dict()
                }
                for ai in self.ai_players
            ],
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
        game.mission_year = gs['mission_year']
        game.energy_credits = gs['energy_credits']
        game.player_id = gs['player_id']
        game.player_faction_id = gs.get('player_faction_id', 0)  # Default to 0 for old saves
        game.player_name = gs.get('player_name', None)
        game.built_projects = set(gs['built_projects'])
        game.se_selections = gs['se_selections']
        game.game_over = gs['game_over']
        game.winner = gs['winner']
        game.player_ever_had_base = gs['player_ever_had_base']
        game.enemy_ever_had_base = gs['enemy_ever_had_base']
        game.ai_faction_ids = gs.get('ai_faction_ids', [fid for fid in range(7) if fid != game.player_faction_id])
        game.faction_contacts = set(gs.get('faction_contacts', []))
        game.eliminated_factions = set(gs.get('eliminated_factions', []))

        # Rebuild complex objects
        game.game_map = GameMap.from_dict(data['map'])
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

        # Restore tech trees
        game.tech_tree = TechTree.from_dict(data['tech_tree'])
        game.ai_tech_trees = {}
        for ai_data in data['ai_players']:
            player_id = ai_data['player_id']
            game.ai_tech_trees[player_id] = TechTree.from_dict(ai_data['tech_tree'])

        # Restore AI players
        game.ai_players = [AIPlayer(ai_data['player_id']) for ai_data in data['ai_players']]

        # Restore selected unit
        sel_idx = data.get('selected_unit_index')
        game.selected_unit = game.units[sel_idx] if sel_idx is not None else None

        # Restore territory
        game.territory = TerritoryManager(game.game_map)
        game.territory.update_territory(game.bases)

        # Initialize runtime state (not saved)
        game.running = True
        game.status_message = ""
        game.status_message_timer = 0
        game.supply_pod_message = None
        game.pending_battle = None
        game.active_battle = None
        game.processing_ai = False
        game.current_ai_index = 0
        game.ai_unit_queue = []
        game.ai_current_unit_index = 0
        game.center_camera_on_selected = True  # Center on selected unit when loading
        game.center_camera_on_tile = None
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
        game.global_energy_allocation = {
            'economy': 50,
            'labs': 50,
            'psych': 0
        }
        game.ui_manager = None  # Will be set by main.py after loading

        return game