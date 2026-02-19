"""Turn sequencing and unit cycling system.

Handles the game clock: when things happen, in what order, and who acts next.
Covers end-of-turn, AI turn processing, upkeep phase, and unit cycling.
"""

import pygame


class TurnManager:
    """Manages turn sequencing, AI processing, upkeep phase, and unit cycling."""

    def __init__(self, game):
        """Initialize turn manager.

        Args:
            game (Game): Reference to main game instance
        """
        self.game = game

    # -----------------------------------------------------------------------
    # Unit cycling
    # -----------------------------------------------------------------------

    def check_auto_cycle(self):
        """Check if enough time has passed to auto-cycle to next unit."""
        game = self.game
        # Only auto-cycle for player units, not during AI turn or while popups need attention
        if game.processing_ai or game.upkeep_phase_active:
            return
        if (game.pending_commlink_requests or game.supply_pod_message or
                game.supply_pod_tech_event or game.pending_artifact_link or
                game.pending_faction_eliminations or game.pending_treaty_break or
                game.pending_ai_attack):
            return
        if (hasattr(game, 'ui_manager') and game.ui_manager is not None
                and game.ui_manager.has_any_blocking_popup()):
            return

        # Check if timer is set (non-zero) and delay has elapsed
        if game.auto_cycle_timer > 0:
            current_time = pygame.time.get_ticks()
            if current_time - game.auto_cycle_timer >= game.auto_cycle_delay:
                # Check if current unit has no moves left or unit was removed (e.g., founded base)
                if (not game.selected_unit) or (game.selected_unit.moves_remaining <= 0):
                    # Auto-cycle to next unit
                    self.cycle_units()
                # Reset timer
                game.auto_cycle_timer = 0

    def cycle_units(self, allow_auto_end=True):
        """Select next friendly unit. Cycles only through unheld units that still have moves.

        Args:
            allow_auto_end: If False, skip auto-end-turn check (use when player manually
                            presses W — they're explicitly asking to cycle, not end turn).
        """
        game = self.game
        friendly_units = [u for u in game.units if u.is_friendly(game.player_faction_id)]

        if not friendly_units:
            return

        # Filter to units with moves remaining, not held, and not actively terraforming
        units_with_moves = [u for u in friendly_units
                            if u.moves_remaining > 0 and not u.held
                            and not (getattr(u, 'is_former', False) and u.terraforming_action)]

        # If no units need attention, optionally check for auto-end
        if not units_with_moves:
            if allow_auto_end:
                self.check_auto_end_turn()
            return

        # Cycle through units in sequence
        if game.selected_unit in units_with_moves:
            current_idx = units_with_moves.index(game.selected_unit)
            next_idx = (current_idx + 1) % len(units_with_moves)
            game._select_unit(units_with_moves[next_idx])
        else:
            game._select_unit(units_with_moves[0])

        # Center camera on newly selected unit
        if game.selected_unit:
            game.center_camera_on_selected = True

    # -----------------------------------------------------------------------
    # Turn end / auto-end
    # -----------------------------------------------------------------------

    def check_auto_end_turn(self):
        """Check if turn should auto-end or require manual button press.

        Auto-ends turn if all units have been processed (moved or held),
        UNLESS:
        - Last action was a hold (signals player might do more)
        - All units are held (player hasn't committed to any actions)
        """
        game = self.game
        # Don't auto-end during AI turn, upkeep, or while a battle is animating
        if game.processing_ai or game.upkeep_phase_active or game.combat.active_battle:
            return

        # Don't auto-end while any game-state event is pending player attention
        if (game.pending_commlink_requests or
                game.supply_pod_message or
                game.supply_pod_tech_event or
                game.pending_artifact_link or
                game.pending_busy_former or
                game.pending_terraform_cost or
                game.pending_movement_overflow_unit or
                game.pending_faction_eliminations or
                game.pending_treaty_break or
                game.pending_ai_attack):
            return

        # Don't auto-end while the UI has any modal popup open
        if (hasattr(game, 'ui_manager') and game.ui_manager is not None
                and game.ui_manager.has_any_blocking_popup()):
            return

        friendly_units = [u for u in game.units if u.is_friendly(game.player_faction_id)]
        if not friendly_units:
            return

        # Check if all units are "handled" — either held, or a former actively terraforming.
        # Terraforming formers don't need player attention this turn.
        all_handled = all(
            u.held or (getattr(u, 'is_former', False) and getattr(u, 'terraforming_action', None))
            for u in friendly_units
        )

        # Require manual end if:
        # 1. Last action was a hold, OR
        # 2. All units are handled (held or working — nobody voluntarily moved)
        if game.last_unit_action == 'hold' or all_handled:
            # Manual end required - button will continue glowing
            return

        # Otherwise, auto-end turn
        self.end_turn()

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
        game = self.game
        # Reset player units
        for unit in game.units:
            if unit.owner == game.player_faction_id:
                unit.end_turn()

        # Refuel air units at bases and check for crashes
        game._process_air_unit_fuel(game.player_faction_id)

        # Note: Player base processing moved to upkeep phase (after AI turns)
        # Note: Healing moved to _start_new_turn so it fires during upkeep, not here
        # This ensures production, growth, and credits are shown during upkeep

        # Update mission year
        game.mission_year += 1

        # Start AI processing
        game.processing_ai = True
        game.current_ai_index = 0

    # -----------------------------------------------------------------------
    # AI turn processing
    # -----------------------------------------------------------------------

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
        game = self.game
        if not game.processing_ai:
            return False

        # If we don't have a unit queue, set up the next AI player
        if not game.ai_unit_queue:
            # Skip eliminated AI factions
            while game.current_ai_index < len(game.ai_players):
                ai_player = game.ai_players[game.current_ai_index]

                # Check if this faction has been eliminated
                if ai_player.player_id in game.eliminated_factions:
                    print(f"Skipping eliminated AI Player {ai_player.player_id}")
                    game.current_ai_index += 1
                    continue

                # Process this AI player
                print(f"\n=== AI Player {ai_player.player_id} Turn ===")

                # Reset AI units for their turn
                for unit in game.units:
                    if unit.owner == ai_player.player_id:
                        unit.end_turn()

                # Advance terraforming for AI formers
                from game.terraforming import process_terraforming
                for unit in game.units:
                    if unit.owner == ai_player.player_id and unit.terraforming_action:
                        process_terraforming(unit, game)

                # Heal AI units
                game._process_unit_repair(ai_player.player_id)

                # Queue up all AI units with moves
                game.ai_unit_queue = [u for u in game.units
                                      if u.owner == ai_player.player_id and u.moves_remaining > 0]
                game.ai_current_unit_index = 0
                if game.ai_unit_queue:
                    return True
                # No units - break out so the completion block below handles
                # base processing and advances current_ai_index
                break

            # If we get here, all AI players are done (or eliminated)
            else:
                # All AIs done, process player bases and calculate commerce
                game.processing_ai = False

                # Process player bases (deferred from end_turn for upkeep display)
                total_economy = 0
                total_labs = 0
                bureaucracy_map = game._calc_bureaucracy_drones(game.player_faction_id)
                for base in game.bases:
                    if base.owner == game.player_faction_id:
                        # Reset hurry flag at start of turn
                        base.hurried_this_turn = False
                        player_faction = game.factions[game.player_faction_id]
                        ineff_loss = game._calc_inefficiency_loss(base, game.player_faction_id)
                        b_drones = bureaucracy_map.get(base, 0)
                        completed_item = base.process_turn(game.global_energy_allocation, player_faction, game, inefficiency_loss=ineff_loss, bureaucracy_drones=b_drones)
                        if completed_item:
                            # Store for spawning at start of next turn (after upkeep)
                            game.pending_production.append((base, completed_item))

                        # Collect energy outputs
                        total_economy += base.economy_output
                        total_labs += base.labs_output

                # Add economy output to energy reserves
                game.energy_credits += total_economy
                print(f"Player earned {total_economy} energy credits from economy")

                # Process player tech research with labs output
                player_tech_tree = game.factions[game.player_faction_id].tech_tree
                player_tech_tree.add_research(total_labs)
                completed_tech = player_tech_tree.process_turn()

                # Store completed tech for upkeep phase announcement
                if completed_tech:
                    if not hasattr(game, 'upkeep_events'):
                        game.upkeep_events = []
                    tech_name = player_tech_tree.technologies[completed_tech]['name']
                    game.upkeep_events.append({
                        'type': 'tech_complete',
                        'tech_id': completed_tech,
                        'tech_name': tech_name
                    })

                    # Auto-generate new unit designs based on newly unlocked components
                    game._auto_generate_unit_designs(completed_tech)

                    # 'Secrets of' techs grant an immediate bonus tech
                    game._grant_secrets_bonus(completed_tech, player_tech_tree, game.player_faction_id)

                # Calculate commerce for all factions (distributes to player and AI energy_credits)
                # Initialize commerce system if not present (for old saves)
                if not hasattr(game, 'commerce'):
                    from game.commerce import CommerceCalculator
                    game.commerce = CommerceCalculator(game)
                    game.global_trade_pact_active = False

                player_commerce = game.commerce.calculate_all_commerce()

                # Add commerce to upkeep events if player received any
                if player_commerce > 0:
                    if not hasattr(game, 'upkeep_events'):
                        game.upkeep_events = []
                    game.upkeep_events.append({
                        'type': 'commerce',
                        'amount': player_commerce,
                        'details': game.commerce.get_commerce_display_data()
                    })

                self._collect_upkeep_events()

                # If there are upkeep events, show them; otherwise start new turn immediately
                if game.upkeep_events:
                    game.upkeep_phase_active = True
                    game.current_upkeep_event_index = 0
                    print("Entering upkeep phase...")
                else:
                    self._start_new_turn()

                # Center camera on player's selected unit at start of their turn
                game.center_camera_on_selected = True

                # Check for victory/defeat
                game.check_victory()

                return False

        # Process one unit from the queue
        if game.ai_current_unit_index < len(game.ai_unit_queue):
            unit = game.ai_unit_queue[game.ai_current_unit_index]
            ai_player = game.ai_players[game.current_ai_index]

            # Center camera on AI unit
            game.center_camera_on_tile = (unit.x, unit.y)

            # Move this unit
            ai_player._move_unit(unit, game)

            game.ai_current_unit_index += 1
            return True
        else:
            # Done with this AI's units - process their bases and tech
            ai_player = game.ai_players[game.current_ai_index]

            # Skip if this faction was eliminated during their turn
            if ai_player.player_id in game.eliminated_factions:
                print(f"AI Player {ai_player.player_id} was eliminated - skipping base processing")
                game.ai_unit_queue = []
                game.current_ai_index += 1
                return True

            # Process air unit fuel for this AI
            game._process_air_unit_fuel(ai_player.player_id)

            # AI energy allocation (fixed for now: 50% economy, 50% labs)
            ai_energy_allocation = {'economy': 50, 'labs': 50, 'psych': 0}
            total_labs = 0

            ai_bureaucracy_map = game._calc_bureaucracy_drones(ai_player.player_id)
            from game.data.facility_data import SECRET_PROJECTS
            _secret_project_names = {p['name'] for p in SECRET_PROJECTS}
            for base in game.bases:
                if base.owner == ai_player.player_id:
                    # Reset hurry flag at start of AI turn
                    base.hurried_this_turn = False
                    ai_faction = game.factions[ai_player.player_id]
                    ineff_loss = game._calc_inefficiency_loss(base, ai_player.player_id)
                    b_drones = ai_bureaucracy_map.get(base, 0)
                    completed_item = base.process_turn(ai_energy_allocation, ai_faction, game, inefficiency_loss=ineff_loss, bureaucracy_drones=b_drones)
                    if completed_item:
                        # Store for spawning at start of next turn (after upkeep)
                        game.pending_production.append((base, completed_item))
                    total_labs += base.labs_output

                    # Notify player when an AI faction starts or is 1 turn from finishing a secret project
                    prod = base.current_production
                    if prod in _secret_project_names:
                        start_key = (ai_player.player_id, prod)
                        if start_key not in game.known_ai_secret_projects:
                            game.known_ai_secret_projects.add(start_key)
                            game.secret_project_notifications.append({
                                'type': 'started',
                                'project_name': prod,
                                'faction_id': ai_player.player_id,
                            })
                        warn_key = (ai_player.player_id, prod)
                        if (base.production_turns_remaining <= 1
                                and warn_key not in game.known_ai_secret_project_warnings):
                            game.known_ai_secret_project_warnings.add(warn_key)
                            player_also = any(
                                b.current_production == prod
                                for b in game.bases
                                if b.owner == game.player_faction_id
                            )
                            game.secret_project_notifications.append({
                                'type': 'warning',
                                'project_name': prod,
                                'faction_id': ai_player.player_id,
                                'player_also_building': player_also,
                            })

            # Process AI tech research with labs output
            ai_tech_tree = game.factions[ai_player.player_id].tech_tree
            ai_tech_tree.add_research(total_labs)
            ai_completed_tech = ai_tech_tree.process_turn()

            # 'Secrets of' techs grant an immediate bonus tech
            if ai_completed_tech:
                game._grant_secrets_bonus(ai_completed_tech, ai_tech_tree, ai_player.player_id)

            # Check if AI wants to call a council
            if hasattr(game, 'council_manager'):
                proposal_to_call = game.council_manager.check_ai_council_call(ai_player.player_id, game)
                if proposal_to_call:
                    game.council_manager.ai_call_council(proposal_to_call, game)

            print(f"=== AI Player {ai_player.player_id} Turn Complete ===\n")
            game.ai_unit_queue = []
            game.current_ai_index += 1
            return True

    # -----------------------------------------------------------------------
    # Upkeep phase
    # -----------------------------------------------------------------------

    def _collect_upkeep_events(self):
        """Collect all upkeep events to display before new turn starts."""
        game = self.game
        # Note: upkeep_events may already have tech_complete events from end_turn()
        # We just add additional events here

        # Check if we just obtained all faction contacts
        if game.all_contacts_obtained and not game.shown_all_contacts_popup:
            game.upkeep_events.append({
                'type': 'all_contacts',
                'message': "You have established contact with all factions! You may now call the Planetary Council."
            })
            game.shown_all_contacts_popup = True

        # Check player bases for riots and starvation
        for base in game.bases:
            if base.owner != game.player_faction_id:
                continue

            # Check for drone riots
            if base.drone_riot:
                game.upkeep_events.append({
                    'type': 'drone_riot',
                    'base': base,
                    'message': f"DRONE RIOT at {base.name}!"
                })

            # Check for starvation (nutrients < 0 would cause pop loss)
            # TODO: Implement starvation mechanics when food system is added
            # if base.nutrients_per_turn < 0:
            #     game.upkeep_events.append({
            #         'type': 'starvation',
            #         'base': base,
            #         'message': f"Citizens starving at {base.name}!"
            #     })

        # Note: New units/facilities available would be checked here
        # For now, just the events we've collected

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
        game = self.game
        # Reset auto-end turn tracking
        game.last_unit_action = None

        # Count down commerce sanctions
        if game.sanctions_turns_remaining > 0:
            game.sanctions_turns_remaining -= 1
            if game.sanctions_turns_remaining == 0:
                game.set_status_message("Economic sanctions against us have been lifted.")

        # Expire Blood Truces that have run their course
        if game.truce_expiry_turns and hasattr(game, 'ui_manager') and game.ui_manager:
            diplo = game.ui_manager.diplomacy
            expired = [fid for fid, expiry in game.truce_expiry_turns.items()
                       if game.turn >= expiry]
            for fid in expired:
                if diplo.diplo_relations.get(fid) == 'Truce':
                    diplo.diplo_relations[fid] = 'Uncommitted'
                del game.truce_expiry_turns[fid]

        # Advance terraforming for player formers
        from game.terraforming import process_terraforming
        for unit in game.units:
            if unit.owner == game.player_faction_id and unit.terraforming_action:
                process_terraforming(unit, game)

        # Heal player units (upkeep phase — only units that skipped last turn)
        game._process_unit_repair(game.player_faction_id)

        game.turn += 1
        print(f"Turn {game.turn} started!")

        # Spawn all pending production from previous turn
        for base, item_name in game.pending_production:
            game._spawn_production(base, item_name)
        game.pending_production = []

        # Deselect if the current selection is a former still actively terraforming
        if (game.selected_unit
                and getattr(game.selected_unit, 'is_former', False)
                and game.selected_unit.terraforming_action):
            game.selected_unit = None

        # Select a friendly unit if none selected, using cycle logic to skip
        # terraforming formers and held units
        if not game.selected_unit:
            self.cycle_units()

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
        game = self.game
        if not game.upkeep_phase_active:
            return

        game.current_upkeep_event_index += 1

        # If we've shown all events, exit upkeep phase and start new turn
        if game.current_upkeep_event_index >= len(game.upkeep_events):
            game.upkeep_phase_active = False
            game.upkeep_events = []
            game.current_upkeep_event_index = 0

            # Show new designs popup AFTER upkeep events are complete
            if hasattr(game, 'pending_new_designs_flag') and game.pending_new_designs_flag:
                game.new_designs_available = True
                game.pending_new_designs_flag = False

            if game.mid_turn_upkeep:
                # Mid-turn popup (e.g. supply pod tech): just close, don't start a new turn
                game.mid_turn_upkeep = False
            else:
                self._start_new_turn()

    def get_current_upkeep_event(self):
        """Get the current upkeep event to display.

        Returns:
            dict or None: Current event dict, or None if no events
        """
        game = self.game
        if not game.upkeep_phase_active or not game.upkeep_events:
            return None

        if game.current_upkeep_event_index < len(game.upkeep_events):
            return game.upkeep_events[game.current_upkeep_event_index]

        return None
