# game.py
import constants
import facilities
import social_engineering
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
        self.tech_tree.auto_select_research()  # Start with an active research
        self.ai_tech_trees = {1: TechTree()}  # AI tech trees by player_id
        self.ai_tech_trees[1].auto_select_research()  # AI starts researching too

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

        # AI players
        self.ai_players = [AIPlayer(1)]  # One AI opponent with player_id = 1

        # Turn state
        self.processing_ai = False
        self.current_ai_index = 0
        self.ai_unit_queue = []  # Queue of units for AI to process
        self.ai_current_unit_index = 0

        # Victory state
        self.game_over = False
        self.winner = None  # 0 = human, 1+ = AI player
        self.player_ever_had_base = False  # Track if player has founded at least one base
        self.enemy_ever_had_base = False  # Track if enemy has founded at least one base

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

        # Spawn player units: Scout Patrol and Colony Pod only (land units)
        if len(land_tiles) >= 2:
            # Scout Patrol
            x, y = land_tiles[0]
            unit = Unit(x, y, UNIT_LAND, self.player_id, "Scout Patrol")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned Scout Patrol at ({x}, {y})")

            # Colony Pod
            x, y = land_tiles[2]
            unit = Unit(x, y, UNIT_COLONY_POD_LAND, self.player_id, "Colony Pod")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned Colony Pod at ({x}, {y})")

        # Spawn AI units: Scout Patrol and Colony Pod only (land units)
        ai_player_id = 1
        if len(land_tiles) >= 10:
            # AI Scout Patrol
            x, y = land_tiles[-1]
            unit = Unit(x, y, UNIT_LAND, ai_player_id, "AI Scout Patrol")
            self.units.append(unit)
            self.game_map.set_unit_at(x, y, unit)
            print(f"Spawned AI Scout Patrol at ({x}, {y})")

            # AI Colony Pod
            if len(land_tiles) >= 12:
                x, y = land_tiles[-3]
                unit = Unit(x, y, UNIT_COLONY_POD_LAND, ai_player_id, "AI Colony Pod")
                self.units.append(unit)
                self.game_map.set_unit_at(x, y, unit)
                print(f"Spawned AI Colony Pod at ({x}, {y})")

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

        # Check if there are units at target (stacking support)
        if target_tile.units and len(target_tile.units) > 0:
            # Get first unit in stack (defender in combat, or check if friendly)
            first_unit = target_tile.units[0]

            # Check if it's an enemy unit
            if first_unit.owner != unit.owner:
                # Enemy stack - initiate combat with first unit
                if unit.owner == self.player_id:
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

        # Update displayed unit index to show the unit that just moved
        if target_tile and unit in target_tile.units:
            target_tile.displayed_unit_index = target_tile.units.index(unit)

        # Check for supply pod (air units cannot collect supply pods)
        if target_tile.supply_pod and unit.unit_type != UNIT_AIR:
            self._collect_supply_pod(target_tile, unit)

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
                    if unit.owner == self.player_id:
                        self.set_status_message(f"Destroyed {base.name}!")
                        print(f"Player destroyed {base.name}!")
                    else:
                        self.set_status_message(f"AI destroyed {base.name}!")
                        print(f"AI player {unit.owner} destroyed {base.name}!")

                    # Remove base from game
                    self.bases.remove(base)
                    target_tile.base = None

                    # Update territory
                    self.territory.update_territory(self.bases)

                    # Check for victory/defeat immediately
                    self.check_victory()
                else:
                    # Base captured successfully
                    base.owner = unit.owner

                    # Recalculate production and growth based on new population
                    base.nutrients_needed = base._calculate_nutrients_needed()
                    base.growth_turns_remaining = base._calculate_growth_turns()
                    base.production_turns_remaining = base._calculate_production_turns()

                    # Update territory
                    self.territory.update_territory(self.bases)

                    # Show message
                    if unit.owner == self.player_id:
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

            # Sensor range bonus (+25%) - check if there's a friendly sensor array nearby
            # For now, simplified: check if any friendly base is within 2 tiles
            friendly_sensor_nearby = False
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    check_x = (unit.x + dx) % self.game_map.width
                    check_y = unit.y + dy
                    if 0 <= check_y < self.game_map.height:
                        check_tile = self.game_map.get_tile(check_x, check_y)
                        if check_tile and check_tile.base and check_tile.base.owner == unit.owner:
                            friendly_sensor_nearby = True
                            break
                if friendly_sensor_nearby:
                    break

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

            # Empath Song attacking Psi (+50% vs psi)
            if vs_unit and hasattr(unit, 'abilities'):
                if 'empath' in unit.abilities and hasattr(vs_unit, 'armor_mode') and vs_unit.armor_mode == 'psi':
                    modifiers.append({
                        'name': 'Empath vs Psi',
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

        This method initiates the battle animation sequence. The actual
        combat is handled frame-by-frame in the update loop.

        Args:
            attacker (Unit): The attacking unit
            defender (Unit): The defending unit
            target_x (int): Target tile X coordinate
            target_y (int): Target tile Y coordinate
        """
        import random

        # Save original health values
        original_attacker_hp = attacker.current_health
        original_defender_hp = defender.current_health

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

        # Determine final outcome
        if sim_attacker_hp <= 0:
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
        if tile:
            self.game_map.remove_unit_at(unit.x, unit.y, unit)

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

        # Remove the unit
        self.units.remove(unit)

        # Deselect if this was the selected unit
        if self.selected_unit == unit:
            self.selected_unit = None

        # Update territory
        self.territory.update_territory(self.bases)

        print(f"Founded base '{base_name}' at ({base.x}, {base.y})")
        return True

    def _spawn_production(self, base, item_name):
        """Spawn a completed production item at a base.

        Args:
            base (Base): The base that completed production
            item_name (str): Name of the unit or facility to create
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

        # Spawn at the base location (stacking is now allowed)
        unit = Unit(base.x, base.y, unit_type, base.owner, item_name)
        self.units.append(unit)
        self.game_map.add_unit_at(base.x, base.y, unit)
        self.set_status_message(f"{base.name} completed {item_name}")
        print(f"{base.name} spawned {item_name} at ({base.x}, {base.y})")

    def set_status_message(self, message, duration=3000):
        """Set a status message to display temporarily."""
        self.status_message = message
        self.status_message_timer = duration

    def cycle_units(self):
        """Select next friendly unit (W key). Cycles through all units including stacked ones."""
        friendly_units = [u for u in self.units if u.is_friendly(self.player_id)]

        if not friendly_units:
            return

        # Cycle through all friendly units in sequence (includes stacked units)
        if self.selected_unit in friendly_units:
            current_idx = friendly_units.index(self.selected_unit)
            next_idx = (current_idx + 1) % len(friendly_units)
            self.selected_unit = friendly_units[next_idx]
        else:
            self.selected_unit = friendly_units[0]

        # Update displayed unit on the map tile to show the selected unit
        if self.selected_unit:
            tile = self.game_map.get_tile(self.selected_unit.x, self.selected_unit.y)
            if tile and self.selected_unit in tile.units:
                tile.displayed_unit_index = tile.units.index(self.selected_unit)

    def end_turn(self):
        """End current turn and start next."""
        # Reset player units
        for unit in self.units:
            if unit.owner == self.player_id:
                unit.end_turn()

        # Process player bases at end of player turn
        for base in self.bases:
            if base.owner == self.player_id:
                completed_item = base.process_turn()
                if completed_item:
                    self._spawn_production(base, completed_item)

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

                # Check for victory/defeat
                self.check_victory()

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
                    completed_item = base.process_turn()
                    if completed_item:
                        self._spawn_production(base, completed_item)

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

    def check_victory(self):
        """Check if the game is over due to conquest victory/defeat."""
        # Count bases by owner
        player_bases = [b for b in self.bases if b.owner == self.player_id]
        enemy_bases = [b for b in self.bases if b.owner != self.player_id]

        # Track if players have ever had bases
        if len(player_bases) > 0:
            self.player_ever_had_base = True
        if len(enemy_bases) > 0:
            self.enemy_ever_had_base = True

        # Check if player has lost all bases (only if they previously had at least one)
        if self.player_ever_had_base and len(player_bases) == 0:
            self.game_over = True
            self.winner = 1  # AI wins (first AI player)
            print("GAME OVER: Player has been defeated!")
            return

        # Check if all enemy bases are destroyed (only if they previously had at least one)
        if self.enemy_ever_had_base and len(enemy_bases) == 0:
            self.game_over = True
            self.winner = self.player_id
            print("VICTORY: All enemy bases destroyed!")
            return

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
        self.game_over = False
        self.winner = None
        self.player_ever_had_base = False
        self.enemy_ever_had_base = False
        self.tech_tree = TechTree()
        self.ai_tech_trees = {1: TechTree()}
        self.territory = TerritoryManager(self.game_map)
        self._spawn_test_units()
        # Update territory after spawning (in case any bases were created)
        self.territory.update_territory(self.bases)