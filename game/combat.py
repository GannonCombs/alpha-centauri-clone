"""Combat resolution system.

This module handles all combat-related calculations and resolution including:
- Combat modifier calculation (morale, terrain, facilities, special abilities)
- Combat odds calculation for battle prediction
- Combat simulation with round-by-round damage
- Unit disengagement mechanics
- Battle cleanup and unit destruction

The Combat class maintains battle state (pending_battle, active_battle) and
coordinates with the Game class to modify units and game state.
"""

import random


class Combat:
    """Manages combat resolution and battle state."""

    def __init__(self, game):
        """Initialize combat system.

        Args:
            game (Game): Reference to main game instance
        """
        self.game = game
        self.pending_battle = None  # Dict with attacker, defender, target_x, target_y
        self.active_battle = None  # Dict tracking ongoing battle animation

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

        # Morale modifier: +12.5% per level above Green (level 2)
        # Green (level 2) is baseline 1.0
        if hasattr(unit, 'morale_level'):
            # Calculate multiplier: 1.0 + (level - 2) * 0.125
            multiplier = 1.0 + (unit.morale_level - 2) * 0.125
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
            tile = self.game.game_map.get_tile(unit.x, unit.y)

            # Rocky terrain defense bonus (+50%) — only outside a base
            # (base defense already accounts for fortifications)
            if tile and not tile.base and tile.is_land() and getattr(tile, 'rockiness', 0) == 2:
                modifiers.append({
                    'name': 'Rocky Terrain',
                    'multiplier': 1.50,
                    'display': '+50%'
                })

            # Base defense bonus
            if tile and tile.base:
                modifiers.append({
                    'name': 'Base Defense',
                    'multiplier': 1.25,
                    'display': '+25%'
                })

                # Perimeter Defense: +100% defense
                if 'perimeter_defense' in tile.base.facilities:
                    modifiers.append({
                        'name': 'Perimeter Defense',
                        'multiplier': 2.00,
                        'display': '+100%'
                    })

            # Trance defending vs Psi (+50%)
            if vs_unit and hasattr(unit, 'abilities'):
                if 'trance' in unit.abilities and vs_unit.weapon_data.get('mode', 'projectile') == 'psi':
                    modifiers.append({
                        'name': 'Trance vs Psi',
                        'multiplier': 1.50,
                        'display': '+50%'
                    })

                # AAA vs air units (+100%)
                if 'AAA' in unit.abilities and vs_unit.type == 'air':
                    modifiers.append({
                        'name': 'AAA vs Air',
                        'multiplier': 2.00,
                        'display': '+100%'
                    })

            # AAA Tracking ability (+100% vs air)
            if vs_unit and unit.has_aaa_tracking and vs_unit.type == 'air':
                modifiers.append({
                    'name': 'AAA Tracking',
                    'multiplier': 2.00,
                    'display': '+100%'
                })

            # Blink Displacer ignores base defenses (cancel base defense if attacker has it)
            if vs_unit and vs_unit.has_blink_displacer and tile and tile.base:
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

            # Artillery defending vs ship: +50%
            if unit.has_artillery and vs_unit and vs_unit.type == 'sea':
                modifiers.append({
                    'name': 'Artillery vs Ship',
                    'multiplier': 1.50,
                    'display': '+50%'
                })

        # Attacker bonuses
        else:
            tile = self.game.game_map.get_tile(unit.x, unit.y)
            defender_tile = self.game.game_map.get_tile(vs_unit.x, vs_unit.y) if vs_unit else None

            # Infantry attacking base bonus
            if unit.chassis == 'infantry' and defender_tile and defender_tile.base:
                modifiers.append({
                    'name': 'Infantry vs Base',
                    'multiplier': 1.25,
                    'display': '+25%'
                })

            # Mobile unit vs infantry in open
            if (unit.chassis in ['speeder', 'hovertank'] and
                vs_unit and vs_unit.chassis == 'infantry' and
                defender_tile and not defender_tile.base):
                modifiers.append({
                    'name': 'Mobile vs Infantry',
                    'multiplier': 1.25,
                    'display': '+25%'
                })

            # Artillery altitude bonuses
            if unit.has_artillery and vs_unit and tile and defender_tile:
                # Artillery vs ship: +50%
                if vs_unit.type == 'sea':
                    modifiers.append({
                        'name': 'Artillery vs Ship',
                        'multiplier': 1.50,
                        'display': '+50%'
                    })
                # Artillery attacking land target from higher ground: +25% per 1000m
                elif vs_unit.type == 'land':
                    altitude_diff = tile.altitude - defender_tile.altitude
                    levels_above = altitude_diff // 1000
                    if levels_above > 0:
                        bonus_multiplier = 1.0 + (0.25 * levels_above)
                        modifiers.append({
                            'name': f'Artillery High Ground (+{levels_above})',
                            'multiplier': bonus_multiplier,
                            'display': f'+{int(levels_above * 25)}%'
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
                if 'empath' in unit.abilities and vs_unit.armor_data.get('mode', 'projectile') == 'psi':
                    modifiers.append({
                        'name': 'Empath vs Psi',
                        'multiplier': 1.50,
                        'display': '+50%'
                    })

            # Empath Song (new ability system)
            if vs_unit and getattr(unit, 'has_empath_song', False):
                if vs_unit.armor_data.get('mode', 'projectile') == 'psi':
                    modifiers.append({
                        'name': 'Empath Song',
                        'multiplier': 1.50,
                        'display': '+50%'
                    })

        # Combat mode bonuses (both attacker and defender)
        if vs_unit:
            # Projectile weapon vs Energy armor = +25%
            if unit.weapon_data.get('mode', 'projectile') == 'projectile' and vs_unit.armor_data.get('mode', 'projectile') == 'energy':
                modifiers.append({
                    'name': 'Mode: Proj vs Energy',
                    'multiplier': 1.25,
                    'display': '+25%'
                })
            # Energy weapon vs Projectile armor = +25%
            elif unit.weapon_data.get('mode', 'projectile') == 'energy' and vs_unit.armor_data.get('mode', 'projectile') == 'projectile':
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
        attacker_weapon_value = attacker.weapon_data['attack']
        defender_armor_value = defender.armor_data['defense']
        attacker_base_strength = attacker_weapon_value * attacker.current_health
        defender_base_strength = defender_armor_value * defender.current_health

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
        # Save original health values
        original_attacker_hp = attacker.current_health
        original_defender_hp = defender.current_health

        # Set relationship to Vendetta when combat occurs
        if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'diplo_manager'):
            # owner IS faction_id now
            attacker_faction_id = attacker.owner
            defender_faction_id = defender.owner

            # Update diplomacy relations to Vendetta
            diplo = self.game.ui_manager.diplo_manager
            if defender.owner == self.game.player_faction_id:
                # AI attacked player - set AI faction to Vendetta from player's perspective
                diplo.diplo_relations[attacker_faction_id] = 'Vendetta'
            elif attacker.owner == self.game.player_faction_id:
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

        # Get attack and defense values from component data
        attacker_weapon_value = attacker.weapon_data['attack']
        defender_armor_value = defender.armor_data['defense']

        # Simulate combat using temporary HP values (don't modify units yet)
        sim_attacker_hp = original_attacker_hp
        sim_defender_hp = original_defender_hp

        while sim_attacker_hp > 0 and sim_defender_hp > 0:
            # Calculate odds for this round based on current sim HP and modifiers
            attacker_strength = attacker_weapon_value * sim_attacker_hp * attacker_modifier_total
            defender_strength = defender_armor_value * sim_defender_hp * defender_modifier_total
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

    def finish_battle(self):
        """Clean up after battle completes and apply results to game state."""
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
                old_tile = self.game.game_map.get_tile(disengaged_unit.x, disengaged_unit.y)
                if old_tile:
                    self.game.game_map.remove_unit_at(disengaged_unit.x, disengaged_unit.y, disengaged_unit)

                disengaged_unit.x = retreat_tile[0]
                disengaged_unit.y = retreat_tile[1]

                new_tile = self.game.game_map.get_tile(retreat_tile[0], retreat_tile[1])
                if new_tile:
                    self.game.game_map.add_unit_at(retreat_tile[0], retreat_tile[1], disengaged_unit)

                # Unit has no moves left after disengaging
                disengaged_unit.moves_remaining = 0

            # Show disengage message
            if disengaged_unit.owner == self.game.player_id:
                self.game.set_status_message(f"{disengaged_unit.name} disengaged from combat!")

            # Clear battle state
            self.active_battle = None
            return

        # Remove destroyed unit and award experience
        if victor == 'defender':
            # Attacker destroyed
            self.game._remove_unit(attacker)
            # Defender records kill and gains experience
            defender.record_kill()
            # Attacker consumed their move/turn
            # (already happened when they initiated attack)
        else:
            # Defender destroyed
            self.game._remove_unit(defender)
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

                new_x = (unit.x + dx) % self.game.game_map.width
                new_y = unit.y + dy

                if not (0 <= new_y < self.game.game_map.height):
                    continue

                tile = self.game.game_map.get_tile(new_x, new_y)
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
                    for base in self.game.bases:
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

    def update(self, dt):
        """Update battle animation state.

        Args:
            dt (int): Delta time in milliseconds since last update
        """
        # Advance combat animation
        if self.active_battle and not self.active_battle['complete']:
            self.active_battle['round_timer'] += dt

            # Advance to next round
            if self.active_battle['round_timer'] >= self.active_battle['round_delay']:
                self.active_battle['round_timer'] = 0
                self.active_battle['current_round'] += 1

                # Check if all rounds complete
                if self.active_battle['current_round'] >= len(self.active_battle['rounds']):
                    self.active_battle['complete'] = True
                    # Give a brief delay before cleanup
                    self.active_battle['cleanup_timer'] = 1000  # 1 second

        # Clean up finished battle
        if self.active_battle and self.active_battle.get('complete'):
            if 'cleanup_timer' in self.active_battle:
                self.active_battle['cleanup_timer'] -= dt
                if self.active_battle['cleanup_timer'] <= 0:
                    self.finish_battle()
