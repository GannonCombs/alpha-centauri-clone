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

            # Xenofungus defense bonus (+50%) — land fungus only, outside a base,
            # vs human/Progenitor factions (native life not yet implemented so always applies)
            if (tile and not tile.base and tile.is_land()
                    and getattr(tile, 'fungus', False)
                    and vs_unit is not None):
                modifiers.append({
                    'name': 'Xenofungus',
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

            # TODO: Blink Displacer ignores base defenses — cancel base defense bonus
            #       when attacker has blink displacer. Attacker-side is already implemented.

            # TODO: Sensor range bonus (+25%) — wire once sensor arrays are terraformable

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

            # Faction attack bonus (e.g. Miriam: +25% when attacking)
            from game.data.faction_data import FACTION_DATA
            faction_bonuses = FACTION_DATA[unit.owner].get('bonuses', {}) if unit.owner < len(FACTION_DATA) else {}
            attack_bonus_pct = faction_bonuses.get('attack_bonus', 0)
            if attack_bonus_pct:
                modifiers.append({
                    'name': 'Faction Bonus',
                    'multiplier': 1.0 + attack_bonus_pct / 100.0,
                    'display': f'+{attack_bonus_pct}%'
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

            # Fractional-move attack penalty (attacker only)
            # A unit that has used road/river moves may attack but at reduced strength.
            # >= 2/3 remaining: -33%  |  < 2/3 remaining: -66%
            max_mv = float(unit.max_moves())
            if max_mv > 0:
                remaining = unit.moves_remaining
                if 0.0 < remaining < max_mv - 1e-6:  # Has used at least one full-cost move
                    if remaining < (2.0 / 3.0) - 1e-6:
                        modifiers.append({'name': 'Low Moves', 'multiplier': 0.34, 'display': '-66%'})
                    else:
                        modifiers.append({'name': 'Partial Move', 'multiplier': 0.67, 'display': '-33%'})

            # PLANET rating bonus in psi combat (+/-10% per point, attacker only)
            if vs_unit and self._is_psi_combat(unit, vs_unit):
                planet_rating = self.game.get_planet_rating(unit.owner)
                if planet_rating != 0:
                    planet_mult = max(0.0, 1.0 + planet_rating * 0.10)
                    sign = '+' if planet_rating > 0 else ''
                    modifiers.append({
                        'name': f'PLANET ({sign}{planet_rating})',
                        'multiplier': planet_mult,
                        'display': f'{sign}{planet_rating * 10}%'
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

    def _is_psi_combat(self, attacker, defender):
        """Return True if this battle uses psi rules.

        Psi rules apply when the attacker has a psi weapon, the defender has
        psi armor, or either unit is a native lifeform (is_native flag).
        """
        attacker_psi = (attacker.weapon_data.get('mode') == 'psi'
                        or getattr(attacker, 'is_native', False))
        defender_psi = (defender.armor_data.get('mode') == 'psi'
                        or getattr(defender, 'is_native', False))
        return attacker_psi or defender_psi

    def _get_psi_base_strengths(self, attacker, defender):
        """Return (attacker_base, defender_base) psi strengths at full health.

        In psi combat weapon/armor values are ignored.  Both sides start with
        a flat strength of 1.0 * current_health.  The attacker then receives:
          - 3:2 terrain advantage on land (multiplier 1.5), 1:1 on sea/air
          - ±10% per PLANET rating point (attacker only)

        Morale modifiers are applied separately by get_combat_modifiers().
        """
        # Land vs sea/air terrain advantage
        defender_tile = self.game.game_map.get_tile(defender.x, defender.y)
        on_land = defender_tile is None or defender_tile.is_land()
        terrain_mult = 1.5 if on_land else 1.0

        attacker_base = attacker.current_health * terrain_mult
        defender_base = float(defender.current_health)
        return attacker_base, defender_base

    def calculate_combat_odds(self, attacker, defender):
        """Calculate combat odds for battle prediction screen.

        Args:
            attacker (Unit): Attacking unit
            defender (Unit): Defending unit

        Returns:
            float: Probability of attacker winning (0.0 to 1.0)
        """
        if self._is_psi_combat(attacker, defender):
            attacker_base, defender_base = self._get_psi_base_strengths(attacker, defender)
        else:
            # Normal combat: base strength = weapon/armor value * health
            attacker_base = attacker.weapon_data['attack'] * attacker.current_health
            defender_base = defender.armor_data['defense'] * defender.current_health

        # Apply modifiers (morale, terrain, facilities, abilities)
        attacker_modifiers = self.get_combat_modifiers(attacker, is_defender=False, vs_unit=defender)
        defender_modifiers = self.get_combat_modifiers(defender, is_defender=True, vs_unit=attacker)

        attacker_strength = attacker_base
        for mod in attacker_modifiers:
            attacker_strength *= mod['multiplier']

        defender_strength = defender_base
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
            'complete': False,
            'original_attacker_hp': original_attacker_hp,
            'original_defender_hp': original_defender_hp,
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

        # Psi combat: weapon/armor values are replaced by psi base strengths
        is_psi = self._is_psi_combat(attacker, defender)
        if is_psi:
            psi_atk_base, psi_def_base = self._get_psi_base_strengths(attacker, defender)
            # Normalize to per-HP values so the round loop can scale by current hp
            psi_atk_per_hp = psi_atk_base / original_attacker_hp if original_attacker_hp else 1.0
            psi_def_per_hp = psi_def_base / original_defender_hp if original_defender_hp else 1.0
        else:
            psi_atk_per_hp = None
            psi_def_per_hp = None

        # Get attack and defense values from component data (used in normal combat)
        attacker_weapon_value = attacker.weapon_data['attack']
        defender_armor_value = defender.armor_data['defense']

        # Simulate combat using temporary HP values (don't modify units yet)
        sim_attacker_hp = original_attacker_hp
        sim_defender_hp = original_defender_hp

        while sim_attacker_hp > 0 and sim_defender_hp > 0:
            # Calculate odds for this round based on current sim HP and modifiers
            if is_psi:
                attacker_strength = psi_atk_per_hp * sim_attacker_hp * attacker_modifier_total
                defender_strength = psi_def_per_hp * sim_defender_hp * defender_modifier_total
            else:
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

    def _apply_combat_movement_cost(self, unit, original_hp):
        """Consume movement points for a unit that survived combat.

        Always costs 1 move. Additionally, if the health fraction lost during
        combat is >= 1/max_moves, the unit loses one more move (e.g. a Speeder
        that loses 50%+ HP in a fight loses its second move too).

        Args:
            unit: The surviving unit
            original_hp: Unit's HP at the start of this combat
        """
        # Base cost: 1 move for engaging in combat
        unit.moves_remaining = max(0, unit.moves_remaining - 1)

        # Extra move loss based on health damage taken this combat
        max_moves = unit.max_moves()
        if max_moves > 0:
            health_lost = original_hp - unit.current_health
            fraction_lost = health_lost / unit.max_health if unit.max_health > 0 else 0
            threshold = 1.0 / max_moves
            if fraction_lost >= threshold:
                unit.moves_remaining = max(0, unit.moves_remaining - 1)

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

            # Cycle to next unit — disengaged unit has no moves left
            sel = self.game.selected_unit
            if sel is None or sel not in self.game.units or sel.moves_remaining <= 0:
                self.game.turns.cycle_units()
            return

        # Remove destroyed unit and award experience
        original_attacker_hp = self.active_battle.get('original_attacker_hp', attacker.max_health)
        original_defender_hp = self.active_battle.get('original_defender_hp', defender.max_health)

        if victor == 'defender':
            # Attacker destroyed
            self.game._remove_unit(attacker, killer=defender)
            defender.record_kill()
            # Defender survives — costs 1 move, plus extra if badly hurt
            self._apply_combat_movement_cost(defender, original_defender_hp)
        else:
            # Defender destroyed
            self.game._remove_unit(defender, killer=attacker)
            attacker.record_kill()
            # Attacker survives — costs 1 move, plus extra if badly hurt
            self._apply_combat_movement_cost(attacker, original_attacker_hp)

        # Clear battle state
        self.active_battle = None

        # Cycle to next unit if the selected unit can no longer act
        sel = self.game.selected_unit
        if sel is None or sel not in self.game.units or sel.moves_remaining <= 0:
            self.game.turns.cycle_units()

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
