"""Unit movement system.

Handles all movement-related logic including:
- Movement cost calculation (roads, mag-tubes, rivers, fungus)
- Zone of control enforcement
- Unit movement execution (position updates, garrison management, base capture)
- Transport loading/unloading
"""

import random
import pygame


class MovementManager:
    """Manages unit movement, transport operations, and zone of control."""

    _RIVER_EDGE_DIRS = {
        ( 0, -1): ('N', 'S'),
        ( 0,  1): ('S', 'N'),
        ( 1,  0): ('E', 'W'),
        (-1,  0): ('W', 'E'),
    }

    def __init__(self, game):
        """Initialize movement system.

        Args:
            game (Game): Reference to main game instance
        """
        self.game = game

    def _tiles_share_river(self, from_tile, to_tile, dx, dy):
        """Return True if there is a river on the edge between two adjacent tiles."""
        dir_pair = self._RIVER_EDGE_DIRS.get((dx, dy))
        if not dir_pair:
            return False  # Diagonal — no shared river edge
        from_dir, to_dir = dir_pair
        return (from_dir in getattr(from_tile, 'river_edges', set()) and
                to_dir   in getattr(to_tile,   'river_edges', set()))

    def _get_movement_cost(self, unit, from_tile, to_tile, dx, dy):
        """Return movement cost (float) for one step.

        Returns:
            0.0  — both tiles have mag_tube (free)
            1/3  — both tiles have road (or a base acts as road), or a shared river edge
            1.0  — standard cost (extra terrain costs applied separately)
        """
        from_imps = getattr(from_tile, 'improvements', set())
        to_imps   = getattr(to_tile,   'improvements', set())

        # Bases act as road and mag-tube terminuses (infrastructure assumed)
        from_has_base = bool(from_tile.base)
        to_has_base   = bool(to_tile.base)

        # Mag-tube (or base) to mag-tube (or base) is free
        from_magtube = 'mag_tube' in from_imps or from_has_base
        to_magtube   = 'mag_tube' in to_imps   or to_has_base
        if from_magtube and to_magtube:
            return 0.0

        # Road (or base) on both endpoints — 1/3 move cost
        from_road = 'road' in from_imps or from_has_base
        to_road   = 'road' in to_imps   or to_has_base
        if from_road and to_road:
            return 1.0 / 3.0

        # Shared river edge
        if self._tiles_share_river(from_tile, to_tile, dx, dy):
            return 1.0 / 3.0

        return 1.0

    def _violates_zone_of_control(self, unit, from_x, from_y, to_x, to_y):
        """Check if a move violates zone of control rules.

        Args:
            unit: The unit attempting to move
            from_x, from_y: Starting position
            to_x, to_y: Target position

        Returns:
            bool: True if move violates ZOC, False if allowed
        """
        game_map = self.game.game_map

        # Only land units are affected by ZOC
        if unit.type != 'land':
            return False

        # Check if starting position has enemy ZOC
        start_has_enemy_zoc = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x = (from_x + dx) % game_map.width
                check_y = from_y + dy
                if not game_map.is_valid_position(check_x, check_y):
                    continue

                tile = game_map.get_tile(check_x, check_y)
                if tile and tile.units:
                    for other_unit in tile.units:
                        if other_unit.owner != unit.owner and not self.game.has_pact_with(unit.owner, other_unit.owner):
                            start_has_enemy_zoc = True
                            break

        # Check if target position has enemy ZOC
        target_has_enemy_zoc = False
        target_tile = game_map.get_tile(to_x, to_y)

        # Exception: Can move into squares with friendly units
        if target_tile and target_tile.units:
            if any(u.owner == unit.owner for u in target_tile.units):
                return False  # Friendly units present, ZOC doesn't apply

        # Exception: Can move into or out of bases
        from_tile = game_map.get_tile(from_x, from_y)
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
                check_x = (to_x + dx) % game_map.width
                check_y = to_y + dy
                if not game_map.is_valid_position(check_x, check_y):
                    continue

                tile = game_map.get_tile(check_x, check_y)
                if tile and tile.units:
                    for other_unit in tile.units:
                        if other_unit.owner != unit.owner and not self.game.has_pact_with(unit.owner, other_unit.owner):
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
            - May set combat.pending_battle for player combat
            - May call resolve_combat() for AI combat
            - Updates unit position and map state
            - Manages garrison entry/exit
            - Sets relationship to Vendetta on combat
        """
        game = self.game
        game_map = game.game_map

        # Moving cancels any in-progress terraforming
        if getattr(unit, 'terraforming_action', None):
            from game.terraforming import cancel_terraforming
            cancel_terraforming(unit)

        # Wrap X coordinate horizontally
        target_x = target_x % game_map.width

        # Y doesn't wrap - must be valid and not a void (border) tile
        if target_y < 0 or target_y >= game_map.height:
            return False
        target_tile_check = game_map.get_tile(target_x, target_y)
        if target_tile_check and getattr(target_tile_check, 'void', False):
            return False

        # Check if target is adjacent (one tile in any of 8 directions, with wrapping)
        dx = target_x - unit.x
        # Handle wrapping for adjacency check
        if dx > game_map.width // 2:
            dx -= game_map.width
        elif dx < -game_map.width // 2:
            dx += game_map.width

        dy = abs(target_y - unit.y)

        if abs(dx) > 1 or dy > 1:
            print(f"Cannot move: target too far (dx={dx}, dy={dy})")
            return False

        target_tile = game_map.get_tile(target_x, target_y)

        # Land unit boarding a transport on an adjacent ocean tile via movement.
        # This intercepts before can_move_to (which would reject land-on-ocean).
        if unit.type == 'land' and target_tile.is_ocean() and unit.moves_remaining > 0:
            transport = next(
                (u for u in target_tile.units
                 if getattr(u, 'transport_capacity', 0) > 0
                 and u.owner == unit.owner
                 and u.can_load_unit(unit)),
                None
            )
            if transport:
                unit.moves_remaining = max(0.0, unit.moves_remaining - 1.0)
                unit.held = True  # Remove from cycle (boarding is a terminal action)
                return self.load_unit_onto_transport(unit, transport)

        # Check if unit can move there
        from_tile = game_map.get_tile(unit.x, unit.y)
        if not unit.can_move_to(target_tile):
            # Exception: sea units can dock at a friendly land base they're adjacent to
            # (the unit must be coming from an ocean tile — the "sea port" mechanic).
            sea_port_entry = (
                unit.type == 'sea'
                and target_tile.is_land()
                and target_tile.base is not None
                and target_tile.base.owner == unit.owner
                and unit.moves_remaining > 0
                and from_tile is not None and from_tile.is_ocean()
            )
            if not sea_port_entry:
                return False

        # Land unit on an ocean tile (e.g. garrisoned in a sea base) cannot walk
        # directly to a land tile — needs amphibious ability or a transport.
        if (unit.type == 'land'
                and from_tile is not None and from_tile.is_ocean()
                and target_tile.is_land()
                and not unit.has_amphibious_pods):
            if unit.owner == game.player_faction_id:
                game.set_status_message("Need amphibious pods or a transport to exit sea base to land")
            return False

        # Check zone of control
        if self._violates_zone_of_control(unit, unit.x, unit.y, target_x, target_y):
            if unit.owner == game.player_faction_id:
                game.set_status_message("Cannot move: Zone of Control violation!")
            return False

        # Check if there are units at target (stacking support)
        if target_tile.units and len(target_tile.units) > 0:
            # Get first unit in stack (defender in combat, or check if friendly)
            first_unit = target_tile.units[0]

            # Check if it's an enemy unit (not friendly, not pact partner)
            if first_unit.owner != unit.owner and not game.has_pact_with(unit.owner, first_unit.owner):
                # Enemy stack - initiate combat with first unit
                if unit.owner == game.player_faction_id:
                    # Player attacking - check if this would break a treaty
                    # (Pass to UI manager for handling)
                    game.pending_treaty_break = {
                        'attacker': unit,
                        'defender': first_unit,
                        'target_x': target_x,
                        'target_y': target_y
                    }
                    return True  # Will be handled by UI manager
                else:
                    # AI unit attacking player - check if this breaks a treaty
                    if first_unit.owner == game.player_faction_id:
                        # AI attacking player - check for surprise attack
                        game.pending_ai_attack = {
                            'attacker': unit,
                            'defender': first_unit,
                            'ai_faction': unit.owner
                        }
                    # Resolve combat immediately (no prediction screen for AI)
                    game.combat.resolve_combat(unit, first_unit, target_x, target_y)
                    return True
            # else: Friendly unit(s) - allow stacking, continue below

        # ---- Movement cost and fractional-move RNG ----
        # Compute signed dy for river-direction check
        _signed_dy = target_y - unit.y
        from_tile_mv = game_map.get_tile(unit.x, unit.y)
        move_cost = self._get_movement_cost(unit, from_tile_mv, target_tile, dx, _signed_dy)

        # Fractional-move RNG: if moves_remaining < 1 full move and we're trying a
        # full-cost tile, the move succeeds only with probability = moves_remaining.
        if move_cost >= 1.0 and 0.0 < unit.moves_remaining < 1.0:
            if random.random() >= unit.moves_remaining:
                return False  # Failed fractional-move attempt

        # Clear old position and remove from garrison if leaving a base
        old_tile = game_map.get_tile(unit.x, unit.y)
        if old_tile:
            game_map.remove_unit_at(unit.x, unit.y, unit)
            # Remove from garrison if was in a base
            if old_tile.base and unit in old_tile.base.garrison:
                old_tile.base.garrison.remove(unit)
                print(f"{unit.name} left {old_tile.base.name}")

        # Move unit (position only; cost applied below)
        unit.move_to(target_x, target_y)
        game_map.add_unit_at(target_x, target_y, unit)

        # Apply base movement cost (road=1/3, magtube=0, regular=1)
        unit.moves_remaining = max(0.0, round(unit.moves_remaining - move_cost, 9))

        # Rocky terrain: +1 extra move cost — but only on full-cost (non-road) moves
        if move_cost >= 1.0 and target_tile.is_land() and getattr(target_tile, 'rockiness', 0) == 2:
            unit.moves_remaining = max(0.0, unit.moves_remaining - 1.0)

        # Overflow protection: >100 moves in one turn = likely infinite loop
        unit.moves_this_turn += 1
        if unit.moves_this_turn > 100 and game.pending_movement_overflow_unit is None:
            game.pending_movement_overflow_unit = unit
            unit.moves_remaining = 0.0

        # Fungus movement costs (skip if magtube is free)
        if move_cost > 0.0 and getattr(target_tile, 'fungus', False):
            if target_tile.is_land():
                # Land fungus: probabilistic movement drain.
                # Exception: if any unit is already on the tile, entry is always free
                # (only costs the normal 1 move that was already spent).
                tile_already_occupied = len(target_tile.units) > 1  # >1 because unit was just added
                if not tile_already_occupied:
                    # Probability all remaining moves are consumed:
                    # Base 50%, reduced 10% per PLANET SE point (min 0%).
                    # Xenoempathy Dome (TODO) will grant an additional -30%.
                    planet_rating = game.get_planet_rating(unit.owner)
                    consume_chance = max(0.0, 0.50 - planet_rating * 0.10)
                    if consume_chance > 0 and random.random() < consume_chance:
                        unit.moves_remaining = 0.0
            else:
                # Sea fungus: flat 3 movement cost (subtract 2 extra on top of base 1)
                unit.moves_remaining = max(0.0, unit.moves_remaining - 2.0)

        # If unit was held, unheld it when manually moved
        if hasattr(unit, 'held') and unit.held:
            unit.held = False
            if unit.owner == game.player_faction_id:
                game.set_status_message(f"{unit.name} unheld")

        # Reset auto-cycle timer when unit moves
        if unit.owner == game.player_faction_id:
            game.auto_cycle_timer = pygame.time.get_ticks()
            # Track that last action was an action (not hold)
            game.last_unit_action = 'action'

        # Check for first contact with adjacent enemy units
        game._check_first_contact(unit, target_x, target_y)

        # Update displayed unit index to show the unit that just moved
        if target_tile and unit in target_tile.units:
            target_tile.displayed_unit_index = target_tile.units.index(unit)

        # Check for supply pod (air units cannot collect supply pods)
        if target_tile.supply_pod and unit.type != 'air':
            if unit.weapon == 'artifact':
                #If an artifact lands on a supply pod, both are destroyed.
                target_tile.supply_pod = False
                game._remove_unit(unit)
                if unit.owner == game.player_faction_id:
                    game.supply_pod_message = "The Artifact was destroyed when it encountered the Supply Pod!"
                return True
            game._collect_supply_pod(target_tile, unit)

        # Check for monolith
        if target_tile.monolith:
            game._apply_monolith_effects(unit)

        # Artifacts adjacent to enemy units get stolen
        if unit.weapon == 'artifact':
            game._check_artifact_stolen_by_proximity(unit)

        # Check for base capture (enemy base with no garrison)
        if target_tile.base:
            base = target_tile.base
            # Can't capture pact partner bases
            if base.owner != unit.owner and not game.has_pact_with(unit.owner, base.owner) and len(base.get_garrison_units(game)) == 0:
                # Capture the base!
                old_owner = base.owner

                # Reduce population by 1
                base.population -= 1

                # Heal unit to full health whenever it takes or destroys a base
                unit.current_health = unit.max_health

                # Check if base is destroyed
                if base.population <= 0:
                    # Base is destroyed
                    if unit.owner == game.player_faction_id:
                        game.set_status_message(f"Destroyed {base.name}!")
                        print(f"Player destroyed {base.name}!")
                    else:
                        game.set_status_message(f"AI destroyed {base.name}!")
                        print(f"AI player {unit.owner} destroyed {base.name}!")

                    # Remove base from game
                    game.bases.remove(base)
                    target_tile.base = None

                    # Check if this eliminated the faction
                    game.check_faction_elimination()

                    # Update territory
                    game.territory.update_territory(game.bases)

                    # Check for victory/defeat immediately
                    game.check_victory()
                else:
                    # Base captured successfully
                    base.owner = unit.owner
                    base.turns_since_capture = 0  # Mark as newly captured for disloyal citizens

                    # Recalculate production and growth based on new population
                    base.nutrients_needed = base._calculate_nutrients_needed()
                    base.growth_turns_remaining = base._calculate_growth_turns()
                    base.production_turns_remaining = base._calculate_production_turns()

                    # Update territory
                    game.territory.update_territory(game.bases)

                    # Show message
                    if unit.owner == game.player_faction_id:
                        game.set_status_message(f"Captured {base.name}! (Pop {base.population})")
                        print(f"Player captured {base.name}! New population: {base.population}")
                    else:
                        game.set_status_message(f"AI captured {base.name}!")
                        print(f"AI player {unit.owner} captured {base.name}! New population: {base.population}")

                    # Check for victory/defeat immediately
                    game.check_victory()

        # If moving into a base, add to garrison
        if target_tile.base and target_tile.base.owner == unit.owner:
            if unit not in target_tile.base.garrison:
                target_tile.base.garrison.append(unit)
                print(f"{unit.name} garrisoned at {target_tile.base.name}")

            # Sea transport docking at a land base: auto-unload all cargo
            if unit.type == 'sea' and target_tile.is_land() and getattr(unit, 'loaded_units', []):
                for cargo_unit in list(unit.loaded_units):
                    unit.unload_unit(cargo_unit, target_tile.base.x, target_tile.base.y)
                    game_map.add_unit_at(target_tile.base.x, target_tile.base.y, cargo_unit)
                    cargo_unit.held = False  # Restore to normal cycling next turn
                    if cargo_unit not in target_tile.base.garrison:
                        target_tile.base.garrison.append(cargo_unit)
                    print(f"{cargo_unit.name} auto-unloaded from {unit.name} at {target_tile.base.name}")
                if unit.owner == game.player_faction_id:
                    game.set_status_message(f"{unit.name} docked — cargo unloaded at {target_tile.base.name}")

            # Artifact + Network Node: prompt to link if base has an unlinked network node
            if (unit.weapon == 'artifact'
                    and unit.owner == game.player_faction_id
                    and 'network_node' in target_tile.base.facilities
                    and not getattr(target_tile.base, 'network_node_linked', False)):
                game.pending_artifact_link = {
                    'artifact': unit,
                    'base': target_tile.base
                }

        return True

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
                self.game.set_status_message(f"{transport.name} cannot carry units")
            elif len(transport.loaded_units) >= transport.transport_capacity:
                self.game.set_status_message(f"{transport.name} is full!")
            else:
                self.game.set_status_message(f"Cannot load {unit.name}")
            return False

        # Remove unit from map (it's now inside the transport)
        tile = self.game.game_map.get_tile(unit.x, unit.y)
        if tile:
            self.game.game_map.remove_unit_at(unit.x, unit.y, unit)

        # Load unit
        transport.load_unit(unit)
        unit.x = transport.x
        unit.y = transport.y

        self.game.set_status_message(f"{unit.name} loaded onto {transport.name}")
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
            self.game.set_status_message("Can only unload to adjacent tiles")
            return False

        # Check if target tile is land
        target_tile = self.game.game_map.get_tile(target_x, target_y)
        if not target_tile or not target_tile.is_land():
            self.game.set_status_message("Cannot unload into ocean")
            return False

        # Unload unit
        transport.unload_unit(unit, target_x, target_y)

        # Add unit to map
        self.game.game_map.add_unit_at(target_x, target_y, unit)

        self.game.set_status_message(f"{unit.name} unloaded")
        return True
