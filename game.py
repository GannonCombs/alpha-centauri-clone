# game.py
import constants
from map import GameMap
from unit import Unit
from base import Base
from ai import AIPlayer
from tech import TechTree
from territory import TerritoryManager
from constants import UNIT_LAND, UNIT_SEA, UNIT_AIR, UNIT_COLONY_POD_LAND, UNIT_COLONY_POD_SEA


class Game:
    """Main game state manager."""

    def __init__(self):
        self.game_map = GameMap(constants.MAP_WIDTH, constants.MAP_HEIGHT)
        self.turn = 1
        self.running = True
        self.player_id = 0  # Human player
        self.mission_year = 2100  # Starting year
        self.energy_credits = 0  # Starting credits

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
        self.pending_battle = None  # Dict with attacker, defender, target_x, target_y
        self.active_battle = None  # Dict tracking ongoing battle animation

        # Technology
        self.tech_tree = TechTree()  # Player's tech tree
        self.ai_tech_trees = {1: TechTree()}  # AI tech trees by player_id

        # Territory
        self.territory = TerritoryManager(self.game_map)

        # AI players
        self.ai_players = [AIPlayer(1)]  # One AI opponent with player_id = 1

        # Turn state
        self.processing_ai = False
        self.current_ai_index = 0
        self.ai_unit_queue = []  # Queue of units for AI to process
        self.ai_current_unit_index = 0

        # Spawn some initial units for testing
        self._spawn_test_units()

    def _spawn_test_units(self):
        """Create some test units on the map."""
        # Find some land tiles for land units
        land_tiles = []
        ocean_tiles = []

        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                tile = self.game_map.get_tile(x, y)
                if tile.is_land():
                    land_tiles.append((x, y))
                else:
                    ocean_tiles.append((x, y))

        print(f"Found {len(land_tiles)} land tiles, {len(ocean_tiles)} ocean tiles")

        # Spawn player units: 1 land unit, 1 land colony pod, 1 sea unit, 1 sea colony pod
        if len(land_tiles) >= 2:
            # Land unit
            x, y = land_tiles[0]
            unit = Unit(x, y, UNIT_LAND, self.player_id, "Scout")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned Scout at ({x}, {y})")

            # Land colony pod
            x, y = land_tiles[2]
            unit = Unit(x, y, UNIT_COLONY_POD_LAND, self.player_id, "Colony Pod")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned Colony Pod at ({x}, {y})")

        # Spawn player sea units
        if len(ocean_tiles) >= 2:
            # Sea unit
            x, y = ocean_tiles[0]
            unit = Unit(x, y, UNIT_SEA, self.player_id, "Foil")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned Foil at ({x}, {y})")

            # Sea colony pod
            x, y = ocean_tiles[1]
            unit = Unit(x, y, UNIT_COLONY_POD_SEA, self.player_id, "Sea Colony Pod")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned Sea Colony Pod at ({x}, {y})")

        # Spawn player air unit (for testing - fast movement)
        if len(land_tiles) >= 4:
            x, y = land_tiles[1]
            unit = Unit(x, y, UNIT_AIR, self.player_id, "Needlejet")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned Needlejet at ({x}, {y})")

        # Spawn AI units (same as player: 1 land unit, 1 land colony pod, 1 sea unit, 1 sea colony pod, 1 air)
        ai_player_id = 1
        if len(land_tiles) >= 10:
            # AI land unit
            x, y = land_tiles[-1]
            unit = Unit(x, y, UNIT_LAND, ai_player_id, "AI Scout")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned AI Scout at ({x}, {y})")

            # AI Colony Pod
            if len(land_tiles) >= 12:
                x, y = land_tiles[-3]
                unit = Unit(x, y, UNIT_COLONY_POD_LAND, ai_player_id, "AI Colony Pod")
                self.units.append(unit)
                self.game_map.set_unit_at(x, y, unit)
                print(f"Spawned AI Colony Pod at ({x}, {y})")

        # AI sea units
        if len(ocean_tiles) >= 5:
            # AI sea unit
            x, y = ocean_tiles[-1]
            unit = Unit(x, y, UNIT_SEA, ai_player_id, "AI Foil")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned AI Foil at ({x}, {y})")

            # AI sea colony pod
            if len(ocean_tiles) >= 6:
                x, y = ocean_tiles[-2]
                unit = Unit(x, y, UNIT_COLONY_POD_SEA, ai_player_id, "AI Sea Colony Pod")
                self.units.append(unit)
                self.game_map.set_unit_at(x, y, unit)
                print(f"Spawned AI Sea Colony Pod at ({x}, {y})")

        # AI air unit (for testing)
        if len(land_tiles) >= 14:
            x, y = land_tiles[-5]
            unit = Unit(x, y, UNIT_AIR, ai_player_id, "AI Needlejet")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned AI Needlejet at ({x}, {y})")

        print(f"Total units spawned: {len(self.units)}")

        # Auto-select first friendly unit
        friendly_units = [u for u in self.units if u.is_friendly(self.player_id)]
        if friendly_units:
            self.selected_unit = friendly_units[0]
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
            return ('base_click', tile.base)

        # If there's a base with garrisoned units, clicking elsewhere cycles through units
        if tile.base and tile.base.garrison:
            friendly_garrison = [u for u in tile.base.garrison if u.is_friendly(self.player_id)]
            if friendly_garrison:
                # If currently selected unit is in this garrison, select next one
                if self.selected_unit in friendly_garrison:
                    current_idx = friendly_garrison.index(self.selected_unit)
                    next_idx = (current_idx + 1) % len(friendly_garrison)
                    self.selected_unit = friendly_garrison[next_idx]
                    return ('unit_selected', self.selected_unit)
                else:
                    # Select first garrison unit
                    self.selected_unit = friendly_garrison[0]
                    return ('unit_selected', self.selected_unit)

        # If there's a base but no garrison units, clicking opens base view
        if tile.base:
            return ('base_click', tile.base)

        # Check if clicked on a unit on the tile
        clicked_unit = self.game_map.get_unit_at(tile_x, tile_y)
        if clicked_unit and clicked_unit.is_friendly(self.player_id):
            # Select friendly unit
            self.selected_unit = clicked_unit

        return None

    def try_move_unit(self, unit, target_x, target_y):
        """Attempt to move a unit to target coordinates."""
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

        # Check if there's already a unit there
        if target_tile.unit and target_tile.unit != unit:
            # Check if it's an enemy unit
            if target_tile.unit.owner != unit.owner:
                # Only player units trigger battle prediction (AI auto-attacks)
                if unit.owner == self.player_id:
                    # Set up pending battle - UI will show prediction screen
                    self.pending_battle = {
                        'attacker': unit,
                        'defender': target_tile.unit,
                        'target_x': target_x,
                        'target_y': target_y
                    }
                    return True  # Battle initiated
                else:
                    # AI unit attacking - resolve immediately (no prediction screen)
                    self.resolve_combat(unit, target_tile.unit, target_x, target_y)
                    return True
            else:
                # Friendly unit - can't move there
                return False

        # Clear old position and remove from garrison if leaving a base
        old_tile = self.game_map.get_tile(unit.x, unit.y)
        if old_tile:
            old_tile.unit = None
            # Remove from garrison if was in a base
            if old_tile.base and unit in old_tile.base.garrison:
                old_tile.base.garrison.remove(unit)
                print(f"{unit.name} left {old_tile.base.name}")

        # Move unit
        unit.move_to(target_x, target_y)
        target_tile.unit = unit

        # Check for supply pod
        if target_tile.supply_pod:
            self._collect_supply_pod(target_tile, unit)

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
        # Remove the pod from the tile
        tile.supply_pod = False

        # Grant 500 energy credits
        if unit.owner == self.player_id:
            self.energy_credits += 500
            self.supply_pod_message = "Supply Pod discovered! You gain 500 energy credits."
            print(f"Supply pod collected at ({tile.x}, {tile.y}): +500 credits")
        else:
            # AI collected it
            print(f"AI collected supply pod at ({tile.x}, {tile.y})")

    def calculate_combat_odds(self, attacker, defender):
        """Calculate combat odds for battle prediction screen.

        Args:
            attacker (Unit): Attacking unit
            defender (Unit): Defending unit

        Returns:
            float: Probability of attacker winning (0.0 to 1.0)
        """
        attacker_strength = attacker.weapon
        defender_strength = defender.armor

        total_strength = attacker_strength + defender_strength
        if total_strength == 0:
            return 0.5  # 50/50 if both have 0 strength

        return attacker_strength / total_strength

    def resolve_combat(self, attacker, defender, target_x, target_y):
        """Resolve combat between two units.

        This method initiates the battle animation sequence. The actual
        combat is handled frame-by-frame in the update loop.

        Args:
            attacker (Unit): The attacking unit
            defender (Unit): The defending unit
            target_x (int): Target tile X coordinate
            target_y (int): Target tile Y coordinate
        """
        import random

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

        # Simulate all combat rounds upfront
        while not attacker.is_destroyed() and not defender.is_destroyed():
            # Calculate odds for this round
            odds = self.calculate_combat_odds(attacker, defender)

            # Determine who wins this round
            attacker_wins_round = random.random() < odds

            # Determine damage (1-3 points)
            damage = random.randint(1, 3)

            if attacker_wins_round:
                defender.take_damage(damage)
                self.active_battle['rounds'].append({
                    'winner': 'attacker',
                    'damage': damage,
                    'attacker_hp': attacker.current_health,
                    'defender_hp': defender.current_health
                })
            else:
                attacker.take_damage(damage)
                self.active_battle['rounds'].append({
                    'winner': 'defender',
                    'damage': damage,
                    'attacker_hp': attacker.current_health,
                    'defender_hp': defender.current_health
                })

        # Determine final outcome
        if attacker.is_destroyed():
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

        # Remove destroyed unit
        if victor == 'defender':
            # Attacker destroyed
            self._remove_unit(attacker)
            # Attacker consumed their move/turn
            # (already happened when they initiated attack)
        else:
            # Defender destroyed
            self._remove_unit(defender)
            # Attacker consumed their move/turn

        # Clear battle state
        self.active_battle = None

    def _remove_unit(self, unit):
        """Remove a unit from the game completely.

        Args:
            unit (Unit): Unit to remove
        """
        # Remove from units list
        if unit in self.units:
            self.units.remove(unit)

        # Remove from map
        tile = self.game_map.get_tile(unit.x, unit.y)
        if tile and tile.unit == unit:
            tile.unit = None

        # Remove from base garrison if present
        if tile and tile.base and unit in tile.base.garrison:
            tile.base.garrison.remove(unit)

        # Deselect if this was the selected unit
        if self.selected_unit == unit:
            # Try to select next friendly unit
            friendly_units = [u for u in self.units if u.is_friendly(self.player_id)]
            self.selected_unit = friendly_units[0] if friendly_units else None

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
        self.bases.append(base)

        # Update the tile
        if tile:
            tile.base = base
            tile.unit = None

        # Remove the unit
        self.units.remove(unit)

        # Deselect if this was the selected unit
        if self.selected_unit == unit:
            self.selected_unit = None

        # Update territory
        self.territory.update_territory(self.bases)

        print(f"Founded base '{base_name}' at ({base.x}, {base.y})")
        return True

    def set_status_message(self, message, duration=3000):
        """Set a status message to display temporarily."""
        self.status_message = message
        self.status_message_timer = duration

    def cycle_units(self):
        """Select next friendly unit (W key)."""
        friendly_units = [u for u in self.units if u.is_friendly(self.player_id)]

        if not friendly_units:
            return

        if self.selected_unit in friendly_units:
            current_idx = friendly_units.index(self.selected_unit)
            next_idx = (current_idx + 1) % len(friendly_units)
            self.selected_unit = friendly_units[next_idx]
        else:
            self.selected_unit = friendly_units[0]

    def end_turn(self):
        """End current turn and start next."""
        # Reset player units
        for unit in self.units:
            if unit.owner == self.player_id:
                unit.end_turn()

        # Process player bases at end of player turn
        for base in self.bases:
            if base.owner == self.player_id:
                base.process_turn()

        # Process player tech research
        self.tech_tree.process_turn()

        # Update mission year and energy credits
        self.mission_year += 1
        self.energy_credits += 10

        # Start AI processing
        self.processing_ai = True
        self.current_ai_index = 0

    def process_ai_turns(self):
        """Process AI turns sequentially, one unit at a time."""
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
                # All AIs done, start new turn
                self.processing_ai = False
                self.turn += 1
                print(f"Turn {self.turn} started!")
                return False

        # Process one unit from the queue
        if self.ai_current_unit_index < len(self.ai_unit_queue):
            unit = self.ai_unit_queue[self.ai_current_unit_index]
            ai_player = self.ai_players[self.current_ai_index]

            # Move this unit
            ai_player._move_unit(unit, self)

            self.ai_current_unit_index += 1
            return True
        else:
            # Done with this AI's units - process their bases and tech
            ai_player = self.ai_players[self.current_ai_index]
            for base in self.bases:
                if base.owner == ai_player.player_id:
                    base.process_turn()

            # Process AI tech research
            if ai_player.player_id in self.ai_tech_trees:
                self.ai_tech_trees[ai_player.player_id].process_turn()

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

    def new_game(self):
        """Start a fresh game."""
        self.game_map = GameMap(constants.MAP_WIDTH, constants.MAP_HEIGHT)
        self.turn = 1
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
        self.tech_tree = TechTree()
        self.ai_tech_trees = {1: TechTree()}
        self.territory = TerritoryManager(self.game_map)
        self._spawn_test_units()
        # Update territory after spawning (in case any bases were created)
        self.territory.update_territory(self.bases)