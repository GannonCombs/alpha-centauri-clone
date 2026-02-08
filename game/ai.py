# ai.py
"""AI player controller with 1990s-style decision-making.

This module implements a simple but effective AI using if/then logic,
distance calculations, and basic pathfinding. The AI can move units,
found bases, and make strategic decisions without using modern ML techniques.
"""
import random


class AIPlayer:
    """AI controller for computer players using classic rule-based logic.

    Uses simple heuristics and greedy algorithms to play the game:
    - Colony pods seek good founding locations with proper spacing
    - Military units pursue player targets or explore randomly
    - Movement uses basic pathfinding toward objectives

    Attributes:
        player_id (int): The AI player's ID (1+)
    """

    def __init__(self, player_id):
        """Initialize AI player.

        Args:
            player_id (int): Player ID for this AI (1+)
        """
        self.player_id = player_id

    def _move_unit(self, unit, game):
        """Decide how to move a unit based on its type.

        Args:
            unit (Unit): The unit to move
            game (Game): Current game state
        """
        if unit.is_colony_pod():
            self._move_colony_pod(unit, game)
        else:
            self._move_military_unit(unit, game)

    def _move_colony_pod(self, unit, game):
        """Move colony pod and potentially found a base."""
        # Check if current location is good for founding
        if self._is_good_base_location(unit.x, unit.y, game):
            # Found a base here
            base_name = game.generate_base_name(self.player_id)
            game.found_base(unit, base_name)
            print(f"AI founded base '{base_name}' at ({unit.x}, {unit.y})")
            return

        # Otherwise, move toward a good location
        target = self._find_base_location(unit, game)
        if target:
            self._move_toward(unit, target[0], target[1], game)
        else:
            # No good location found, move randomly
            self._move_randomly(unit, game)

    def _move_military_unit(self, unit, game):
        """Move military unit - balance offense, defense, and exploration."""
        # First, check for adjacent enemies we can attack
        player_units = [u for u in game.units if u.owner == 0]

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                check_x = (unit.x + dx) % game.game_map.width
                check_y = unit.y + dy

                if check_y < 0 or check_y >= game.game_map.height:
                    continue

                check_tile = game.game_map.get_tile(check_x, check_y)
                if check_tile and len(check_tile.units) > 0:
                    # Check first unit in stack (defender)
                    target_unit = check_tile.units[0]
                    if target_unit.owner == 0:  # Player unit
                        # Found adjacent enemy - consider attacking
                        if self._should_attack(unit, target_unit):
                            # Attack by moving onto their tile
                            target_x = check_x
                            target_y = check_y
                            game.try_move_unit(unit, target_x, target_y)
                            return

        # Check for ungarrisoned bases that need defending
        garrison_target = self._find_nearest_ungarrisoned_base(unit, game)
        if garrison_target:
            base_x, base_y, distance = garrison_target
            if self._should_garrison(unit, distance):
                # Move toward undefended base
                self._move_toward(unit, base_x, base_y, game)
                return

        # No immediate defensive needs - find nearest player unit or base
        player_bases = [b for b in game.bases if b.owner == 0]

        targets = []
        map_width = game.game_map.width
        for u in player_units:
            targets.append((u.x, u.y, self._distance(unit.x, unit.y, u.x, u.y, map_width)))
        for b in player_bases:
            targets.append((b.x, b.y, self._distance(unit.x, unit.y, b.x, b.y, map_width)))

        if targets and random.random() < 0.6:  # 60% chance to pursue player
            # Find nearest target
            targets.sort(key=lambda t: t[2])
            nearest = targets[0]
            self._move_toward(unit, nearest[0], nearest[1], game)
        else:
            # Explore randomly
            self._move_randomly(unit, game)

    def _move_toward(self, unit, target_x, target_y, game):
        """Move unit one step toward target (with horizontal wrapping)."""
        dx = target_x - unit.x
        dy = target_y - unit.y

        # Handle horizontal wrapping - take the shortest path
        map_width = game.game_map.width
        if dx > map_width // 2:
            dx -= map_width
        elif dx < -map_width // 2:
            dx += map_width

        # Normalize to -1, 0, or 1
        move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        move_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        # Try diagonal first
        if move_x != 0 and move_y != 0:
            if self._try_move_with_combat_check(unit, move_x, move_y, game):
                return

        # Try horizontal
        if move_x != 0:
            if self._try_move_with_combat_check(unit, move_x, 0, game):
                return

        # Try vertical
        if move_y != 0:
            if self._try_move_with_combat_check(unit, 0, move_y, game):
                return

        # Stuck - try random
        self._move_randomly(unit, game)

    def _try_move_with_combat_check(self, unit, dx, dy, game):
        """Try to move, but check combat odds if there's an enemy.

        Args:
            unit (Unit): Unit to move
            dx (int): Delta X (-1, 0, or 1)
            dy (int): Delta Y (-1, 0, or 1)
            game (Game): Game state

        Returns:
            bool: True if move succeeded (or attack initiated)
        """
        target_x = (unit.x + dx) % game.game_map.width
        target_y = unit.y + dy

        if target_y < 0 or target_y >= game.game_map.height:
            return False

        target_tile = game.game_map.get_tile(target_x, target_y)
        if not target_tile:
            return False

        # Check if there's an enemy unit in the stack
        if len(target_tile.units) > 0:
            # Check first unit in stack
            target_unit = target_tile.units[0]
            if target_unit.owner != unit.owner:
                # Enemy unit - only attack if odds are favorable
                if self._should_attack(unit, target_unit):
                    return self._try_move(unit, dx, dy, game)
                else:
                    # Don't attack - bad odds
                    return False
            # else: Friendly unit, allow stacking (continue below)

        # No enemy, proceed with normal move
        return self._try_move(unit, dx, dy, game)

    def _move_randomly(self, unit, game):
        """Move unit to a random valid adjacent tile."""
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),           (1, 0),
            (-1, 1),  (0, 1),  (1, 1)
        ]
        random.shuffle(directions)

        for dx, dy in directions:
            if self._try_move(unit, dx, dy, game):
                return

    def _try_move(self, unit, dx, dy, game):
        """Attempt to move unit by offset, return True if successful."""
        target_x = unit.x + dx
        target_y = unit.y + dy

        if game.try_move_unit(unit, target_x, target_y):
            return True
        return False

    def _is_good_base_location(self, x, y, game):
        """Check if a location is good for founding a base.

        Validates spacing rules: no adjacent bases and minimum 2 tile separation.

        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            game (Game): Current game state

        Returns:
            bool: True if location is suitable for a new base
        """
        # Don't found if there's already a base here
        tile = game.game_map.get_tile(x, y)
        if tile and tile.base:
            return False

        # Check for adjacent bases (including diagonals) - same rule as player
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x = x + dx
                check_y = y + dy
                check_tile = game.game_map.get_tile(check_x, check_y)
                if check_tile and check_tile.base:
                    return False

        # Also prefer some spacing - minimum 2 tiles away from other bases
        for base in game.bases:
            dist = self._distance(x, y, base.x, base.y, game.game_map.width)
            if dist < 2:
                return False

        # Location is good!
        return True

    def _find_base_location(self, unit, game):
        """Find a nearby good location for a base."""
        # Search in expanding radius
        for radius in range(1, 8):
            candidates = []
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    check_x = (unit.x + dx) % game.game_map.width  # Wrap X
                    check_y = unit.y + dy

                    # Y doesn't wrap - check bounds
                    if check_y < 0 or check_y >= game.game_map.height:
                        continue

                    tile = game.game_map.get_tile(check_x, check_y)
                    if not tile:
                        continue

                    # Check if unit can exist on this terrain
                    if unit.weapon == 'colony_pod' and unit.weapon.chassis in ['foil', 'cruiser', 'gravship'] and tile.is_ocean():
                        continue
                    if unit.weapon == 'colony_pod' and unit.weapon.chassis in ['infantry', 'rover', 'hovertank', 'gravship'] and tile.is_land():
                        continue

                    if self._is_good_base_location(check_x, check_y, game):
                        candidates.append((check_x, check_y))

            if candidates:
                # Pick random candidate at this radius
                return random.choice(candidates)

        return None

    def _find_nearest_ungarrisoned_base(self, unit, game):
        """Find the nearest AI base without any garrison.

        Args:
            unit (Unit): The unit looking for a base to garrison
            game (Game): Current game state

        Returns:
            tuple: (base_x, base_y, distance) or None if no ungarrisoned bases
        """
        ai_bases = [b for b in game.bases if b.owner == self.player_id]
        ungarrisoned_bases = [b for b in ai_bases if len(b.garrison) == 0]

        if not ungarrisoned_bases:
            return None

        # Find nearest ungarrisoned base
        map_width = game.game_map.width
        nearest = None
        nearest_dist = float('inf')

        for base in ungarrisoned_bases:
            dist = self._distance(unit.x, unit.y, base.x, base.y, map_width)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = (base.x, base.y, dist)

        return nearest

    def _should_garrison(self, unit, base_distance):
        """Decide if unit should prioritize garrisoning over other actions.

        Uses distance-based priority system:
        - 1-2 tiles (CRITICAL): Always garrison
        - 3-4 tiles (MODERATE): 50% chance to garrison
        - 5+ tiles (LOW): Continue mission, don't garrison
        - Damaged units (<75% HP): Always prefer garrison

        Args:
            unit (Unit): The unit considering garrison
            base_distance (int): Distance to nearest ungarrisoned base

        Returns:
            bool: True if unit should move to garrison
        """
        # Damaged units prefer safety of garrison
        if unit.get_health_percentage() < 0.75:
            return True

        # Distance-based priority
        if base_distance <= 2:
            return True  # CRITICAL range - always garrison

        if base_distance <= 4:
            return random.random() < 0.5  # MODERATE range - 50% chance

        return False  # LOW priority - continue mission

    def _distance(self, x1, y1, x2, y2, map_width):
        """Calculate Manhattan distance with horizontal wrapping."""
        dx = abs(x2 - x1)
        # Account for wrapping - take the shortest path
        if dx > map_width // 2:
            dx = map_width - dx
        dy = abs(y2 - y1)
        return dx + dy

    def _calculate_attack_odds(self, attacker, defender):
        """Calculate probability of attacker winning combat.

        Factors in both combat strength (weapon vs armor) and current health.

        Args:
            attacker (Unit): Attacking unit
            defender (Unit): Defending unit

        Returns:
            float: Probability of attacker winning (0.0 to 1.0)
        """
        # Factor in both combat strength and current health
        attacker_weapon_value = attacker.weapon_data['attack']
        defender_armor_value = defender.armor_data['defense']
        attacker_strength = attacker_weapon_value * attacker.current_health
        defender_strength = defender_armor_value * defender.current_health

        total_strength = attacker_strength + defender_strength
        if total_strength == 0:
            return 0.5  # 50/50 if both have 0 strength

        return attacker_strength / total_strength

    def _should_attack(self, unit, target_unit):
        """Decide if unit should attack target based on odds and health.

        Args:
            unit (Unit): AI unit considering attack
            target_unit (Unit): Potential target

        Returns:
            bool: True if AI should attack
        """
        # Colony pods should never attack
        if unit.is_colony_pod():
            return False

        # Don't attack if we have no weapon
        if unit.weapon == 0:
            return False

        # Calculate odds
        odds = self._calculate_attack_odds(unit, target_unit)

        # Get health status
        unit_health_pct = unit.get_health_percentage()
        target_health_pct = target_unit.get_health_percentage()

        # Decision matrix:
        # - If odds > 0.7 (70%+), always attack
        # - If odds > 0.5 (50%+) and we're at full health, attack
        # - If odds > 0.4 (40%+) and we're healthy (>75%) and target is weak (<50%), attack
        # - Otherwise, don't attack

        if odds >= 0.7:
            return True

        if odds >= 0.5 and unit_health_pct >= 0.9:
            return True

        if odds >= 0.4 and unit_health_pct >= 0.75 and target_health_pct <= 0.5:
            return True

        return False
