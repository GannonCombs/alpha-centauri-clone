"""Main game loop and entry point.

This is the entry point for the Alpha Centauri clone game. It handles:
- Pygame initialization and window setup
- Main game loop with event handling
- Frame rate management and timing
- Intro screen and game state transitions
- Input handling for game and UI interactions
- Rendering coordination between game state and UI

The game loop runs at 60 FPS and processes input, updates game state,
and renders the screen each frame.
"""
import pygame
import sys
from game.data import display_data as display
from game.game import Game
from game.renderer import Renderer
from game.ui import UIManager
from game.ui.screens.intro_screen import IntroScreen
from game.ui.dialogs.save_load_dialog import SaveLoadDialog
from game.ui.dialogs.exit_dialog import ExitDialog

def has_blocking_popup(game, ui_panel):
    """Return True if any popup or modal is waiting for player input during AI processing."""
    return (bool(game.pending_commlink_requests) or
            ui_panel.commlink_request_dialog.active or
            ui_panel.commlink_open or
            ui_panel.elimination_dialog.active or
            ui_panel.new_designs_dialog.active or
            ui_panel.surprise_attack_dialog.active or
            ui_panel.break_treaty_dialog.active or
            ui_panel.pact_evacuation_dialog.active or
            ui_panel.active_screen == "DIPLOMACY" or
            ui_panel.renounce_pact_dialog.active or
            ui_panel.pact_pronounce_dialog.active or
            ui_panel.major_atrocity_dialog.active or
            ui_panel.raze_base_dialog.active or
            ui_panel.encroachment_dialog.active or
            game.upkeep_phase_active or
            game.combat.pending_battle is not None or
            game.combat.active_battle is not None)


def main():
    """Initialize and run the game."""
    # Initialize Pygame
    pygame.init()

    # Create saves directory
    import os
    os.makedirs('game/saves', exist_ok=True)

    # Get display info for sizing
    display_info = pygame.display.Info()
    display.SCREEN_WIDTH = display_info.current_w
    display.SCREEN_HEIGHT = display_info.current_h

    # Calculate MAP_AREA_HEIGHT to be an exact multiple of TILE_SIZE
    # This ensures no partial tiles or gaps
    available_height = display.SCREEN_HEIGHT - display.UI_PANEL_HEIGHT
    num_complete_tiles = available_height // display.TILE_SIZE
    display.MAP_AREA_HEIGHT = num_complete_tiles * display.TILE_SIZE
    display.UI_PANEL_Y = display.MAP_AREA_HEIGHT  # Panel starts right after last complete tile

    # Calculate map size to be double screen size (both width and height)
    map_height = (display.MAP_AREA_HEIGHT // display.TILE_SIZE) * 2
    map_width = (display.SCREEN_WIDTH // display.TILE_SIZE) * 2

    # Create window (not fullscreen, but maximized size)
    screen = pygame.display.set_mode((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
    pygame.display.set_caption("Alpha Centauri Clone")

    # Create game clock for frame rate control
    clock = pygame.time.Clock()

    # Initialize intro screen
    intro_screen = IntroScreen(pygame.font.Font(None, 24), pygame.font.Font(None, 18))
    intro_load_dialog = SaveLoadDialog(pygame.font.Font(None, 24), pygame.font.Font(None, 18))
    exit_dialog = ExitDialog(pygame.font.Font(None, 24), "Are you sure you want to exit?")
    menu_dialog = ExitDialog(pygame.font.Font(None, 24), "Return to main menu?")

    # Game will be None until player starts a game
    game = None
    renderer = None
    ui_panel = None

    # AI turn processing
    last_ai_action = 0

    # Map scrolling
    last_scroll_time = 0

    running = True

    # Main game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                if game:
                    game.running = False

            # Handle intro screen events (before game starts)
            if game is None:
                # Handle intro load dialog if open
                if intro_load_dialog.mode is not None:
                    result = intro_load_dialog.handle_event(event, None)
                    if isinstance(result, tuple) and result[0] == 'load_complete':
                        # Game loaded - start game with loaded state
                        game = result[1]
                        renderer = Renderer(screen)
                        ui_panel = UIManager()
                        # Give game reference to UI for accessing design workshop
                        game.ui_manager = ui_panel
                        intro_screen.mode = None
                        intro_load_dialog.mode = None
                    elif result == 'close':
                        intro_load_dialog.mode = None
                    continue

                # Handle intro screen events
                intro_result = intro_screen.handle_event(event)
                if intro_result == 'load_game':
                    # Show load dialog
                    intro_load_dialog.show_load_dialog()
                elif intro_result == 'exit':
                    # Exit the game
                    running = False
                elif isinstance(intro_result, tuple) and intro_result[0] == 'start_game':
                    # Start new game with selected faction, name, ocean percentage, cloud cover, erosive forces, and native life
                    _, faction_id, player_name, ocean_percentage, cloud_cover, erosive_forces, native_life, skill_level = intro_result
                    game = Game(faction_id, player_name, ocean_percentage, map_width, map_height, cloud_cover, erosive_forces, native_life, difficulty=skill_level)
                    renderer = Renderer(screen)
                    ui_panel = UIManager()
                    # Give game reference to UI for accessing design workshop
                    game.ui_manager = ui_panel
                    intro_screen.mode = None
                continue

            # Game is active - handle game events
            elif event.type == pygame.KEYDOWN:
                # Block all input during AI processing unless a popup needs attention
                if game.processing_ai:
                    if not has_blocking_popup(game, ui_panel):
                        continue

                # Check for exit dialog first
                if exit_dialog.show_dialog:
                    exit_result = exit_dialog.handle_event(event)
                    if exit_result == 'exit':
                        running = False
                        game.running = False
                    continue

                # Check for menu dialog
                if menu_dialog.show_dialog:
                    menu_result = menu_dialog.handle_event(event)
                    if menu_result == 'exit':
                        # Return to main menu
                        game = None
                        renderer = None
                        ui_panel = None
                        intro_screen.mode = 'intro'
                        menu_dialog.hide()
                    continue

                # Check if design workshop rename popup is open
                if ui_panel.active_screen == "DESIGN_WORKSHOP":
                    if ui_panel.design_workshop_screen.rename_popup_open:
                        if ui_panel.design_workshop_screen.handle_design_workshop_keypress(event):
                            continue

                # Check for Escape - close overlays first, then show exit dialog
                if event.key == pygame.K_ESCAPE:
                    # Check if base view has any popups open
                    if ui_panel.active_screen == "BASE_VIEW":
                        if (ui_panel.base_screen.hurry_production_open or
                            ui_panel.base_screen.production_selection_open or
                            ui_panel.base_screen.queue_management_open or
                            ui_panel.base_screen.nerve_staple_popup_open):
                            # Let the base view handler close the popup
                            ui_panel.handle_event(event, game)
                            continue

                    # Check if design workshop has a popup/panel open
                    if ui_panel.active_screen == "DESIGN_WORKSHOP":
                        if ui_panel.design_workshop_screen.rename_popup_open:
                            # Close rename popup
                            ui_panel.design_workshop_screen.rename_popup_open = False
                            continue
                        if ui_panel.design_workshop_screen.dw_editing_panel is not None:
                            # Let the ui_panel handler close the component panel
                            ui_panel.handle_event(event, game)
                            continue

                    # Diplomacy screen
                    if ui_panel.active_screen == "DIPLOMACY":
                        continue

                    # Check if any overlay is active and close it instead of exiting
                    if ui_panel.active_screen != "GAME":
                        ui_panel.handle_event(event, game)
                        continue
                    # Check if save/load dialog is open
                    if ui_panel.save_load_dialog.mode is not None:
                        ui_panel.handle_event(event, game)
                        continue
                    # No overlay active - show exit dialog
                    exit_dialog.show()
                    continue

                # Check for Ctrl+Shift+Q to show menu dialog
                mods = pygame.key.get_mods()
                if event.key == pygame.K_q and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_SHIFT):
                    menu_dialog.show()
                    continue

                # Check for Ctrl+Shift+D to toggle debug mode
                if event.key == pygame.K_d and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_SHIFT):
                    game.debug.toggle()
                    continue

                # Let debug mode handle events first (if enabled)
                if game.debug.handle_event(event, game):
                    continue

                # Let UI handle keys first (for overlay controls)
                ui_handled = ui_panel.handle_event(event, game)
                # Check if it's a load game result
                if isinstance(ui_handled, tuple) and ui_handled[0] == 'load_game':
                    game = ui_handled[1]  # Replace game instance
                    renderer = Renderer(screen)  # Recreate renderer with new game
                    game.ui_manager = ui_panel  # Restore UI reference
                    # Restore diplomatic relations from saved data
                    if hasattr(game, '_saved_diplo_relations'):
                        ui_panel.diplomacy.diplo_relations = game._saved_diplo_relations.copy()
                        delattr(game, '_saved_diplo_relations')  # Clean up temporary storage
                elif not ui_handled:
                    # UI didn't handle it - process game keys
                    if event.key == pygame.K_w:
                        game.turns.cycle_units(allow_auto_end=False)
                    elif event.key == pygame.K_b:
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id:
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            base_at_tile = tile.base if tile else None
                            if unit.is_colony_pod():
                                # Found a new base
                                can_found, error_msg = game.can_found_base(unit)
                                if can_found:
                                    territory_owner = game.territory.get_tile_owner(unit.x, unit.y)
                                    if (territory_owner is not None
                                            and territory_owner != game.player_faction_id
                                            and not game.has_pact_with(game.player_faction_id, territory_owner)
                                            and territory_owner not in game.eliminated_factions):
                                        ui_panel.encroachment_dialog.activate(territory_owner, unit)
                                    else:
                                        ui_panel.show_base_naming_dialog(unit, game)
                                else:
                                    game.set_status_message(f"Cannot found base: {error_msg}")
                            elif (base_at_tile and base_at_tile.owner == game.player_faction_id):
                                # Raze the base the unit is standing in
                                ui_panel.raze_base_dialog.activate(base_at_tile)
                    elif event.key == pygame.K_f:
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id:
                            if getattr(unit, 'is_former', False):
                                # Shift+F = Forest
                                # F without shift = context-smart:
                                #   fungus present  → Remove Fungus
                                #   farm present    → Soil Enricher
                                #   otherwise       → Farm
                                from game.terraforming import get_available_actions, start_terraforming
                                from game.data.terraforming_data import IMPROVEMENTS
                                tile = game.game_map.get_tile(unit.x, unit.y)
                                available = get_available_actions(unit, tile, game)
                                if mods & pygame.KMOD_SHIFT:
                                    action = 'forest'
                                elif 'remove_fungus' in available:
                                    action = 'remove_fungus'
                                elif 'soil_enricher' in available:
                                    action = 'soil_enricher'
                                else:
                                    action = 'farm'
                                if action in available:
                                    start_terraforming(unit, action, game)
                                    game.set_status_message(f"{unit.name}: {IMPROVEMENTS[action]['name']} ({unit.terraforming_turns_left} turns)")
                                    game.last_unit_action = 'action'
                                    game.turns.cycle_units()
                                else:
                                    game.set_status_message(f"Cannot build {IMPROVEMENTS[action]['name']} here.")
                            else:
                                # Toggle artillery mode for non-former units
                                game.toggle_artillery_mode(unit)
                    elif event.key == pygame.K_s:
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id and getattr(unit, 'is_former', False):
                            from game.terraforming import get_available_actions, start_terraforming
                            from game.data.terraforming_data import IMPROVEMENTS
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            available = get_available_actions(unit, tile, game)
                            if 'solar' in available:
                                start_terraforming(unit, 'solar', game)
                                game.set_status_message(f"{unit.name}: Solar Collector ({unit.terraforming_turns_left} turns)")
                                game.last_unit_action = 'action'
                                game.turns.cycle_units()
                            else:
                                game.set_status_message("Cannot build Solar Collector here.")
                    elif event.key == pygame.K_m:
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id and getattr(unit, 'is_former', False):
                            from game.terraforming import get_available_actions, start_terraforming
                            from game.data.terraforming_data import IMPROVEMENTS
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            available = get_available_actions(unit, tile, game)
                            if 'mine' in available:
                                start_terraforming(unit, 'mine', game)
                                game.set_status_message(f"{unit.name}: Mine ({unit.terraforming_turns_left} turns)")
                                game.last_unit_action = 'action'
                                game.turns.cycle_units()
                            else:
                                game.set_status_message("Cannot build Mine here.")
                    elif event.key == pygame.K_r:
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id and getattr(unit, 'is_former', False):
                            from game.terraforming import get_available_actions, start_terraforming
                            from game.data.terraforming_data import IMPROVEMENTS
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            available = get_available_actions(unit, tile, game)
                            # Prefer mag_tube if road already present, else road
                            action = 'mag_tube' if 'mag_tube' in available else ('road' if 'road' in available else None)
                            if action:
                                start_terraforming(unit, action, game)
                                game.set_status_message(f"{unit.name}: {IMPROVEMENTS[action]['name']} ({unit.terraforming_turns_left} turns)")
                                game.last_unit_action = 'action'
                                game.turns.cycle_units()
                            else:
                                game.set_status_message("Cannot build Road or Mag Tube here.")
                    elif event.key == pygame.K_o:
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id and getattr(unit, 'is_former', False):
                            from game.terraforming import get_available_actions, start_terraforming
                            from game.data.terraforming_data import IMPROVEMENTS
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            available = get_available_actions(unit, tile, game)
                            if 'sensor_array' in available:
                                start_terraforming(unit, 'sensor_array', game)
                                game.set_status_message(f"{unit.name}: Sensor Array ({unit.terraforming_turns_left} turns)")
                                game.last_unit_action = 'action'
                                game.turns.cycle_units()
                            else:
                                game.set_status_message("Cannot build Sensor Array here.")
                    elif event.key == pygame.K_l:
                        # Board a transport on the same tile
                        if (game.selected_unit
                                and game.selected_unit.owner == game.player_faction_id
                                and game.selected_unit.type == 'land'):
                            unit = game.selected_unit
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            transport = next(
                                (u for u in tile.units
                                 if u != unit and u.transport_capacity > 0
                                 and u.owner == game.player_faction_id),
                                None
                            ) if tile else None
                            if transport:
                                game.movement.load_unit_onto_transport(unit, transport)
                                unit.held = True  # Remove from cycle without zeroing moves
                                game.selected_unit = None
                                game.turns.cycle_units()
                            else:
                                game.set_status_message("No transport here to board")
                    elif event.key == pygame.K_h:
                        # Toggle hold status for selected unit
                        if game.selected_unit and game.selected_unit.owner == game.player_faction_id:
                            held_unit = game.selected_unit
                            held_unit.held = not held_unit.held

                            if held_unit.held:
                                # When holding, skip to next unit (but don't end turn)
                                game.set_status_message(f"{held_unit.name} held (will skip in cycling)")

                                # Track that last action was a hold
                                game.last_unit_action = 'hold'

                                # Auto-cycle to next unit
                                game.turns.cycle_units()

                                # If we're still on the held unit (no other units with moves), deselect
                                if game.selected_unit == held_unit:
                                    game.selected_unit = None
                            else:
                                # Unheld - unit can now be cycled to again
                                game.set_status_message(f"{held_unit.name} unheld")
                    elif event.key == pygame.K_SPACE:
                        # End movement and skip turn (healing happens automatically at end of turn)
                        # Do NOT set has_moved = True here — a unit that skips its turn in place
                        # should remain repair-eligible (repair_eligible = not has_moved).
                        if game.selected_unit and game.selected_unit.owner == game.player_faction_id:
                            # Drain moves so the unit won't be auto-cycled back, but leave
                            # has_moved untouched so it stays heal-eligible.
                            game.selected_unit.moves_remaining = 0
                            game.set_status_message(f"{game.selected_unit.name} movement ended")

                            # Track that last action was an action (not hold)
                            game.last_unit_action = 'action'

                            # Auto-cycle to next unit
                            game.turns.cycle_units()
                    elif event.key == pygame.K_v:
                        # Toggle tile cursor mode
                        if game.tile_cursor_mode:
                            game.tile_cursor_mode = False
                            if not game.selected_unit:
                                game.turns.cycle_units()
                            if game.selected_unit:
                                game.center_camera_on_selected = True
                        else:
                            game.tile_cursor_mode = True
                            if game.selected_unit:
                                game.cursor_x = game.selected_unit.x
                                game.cursor_y = game.selected_unit.y
                            else:
                                game.cursor_x = game.game_map.width // 2
                                game.cursor_y = game.game_map.height // 2
                    elif event.key == pygame.K_RIGHTBRACKET:
                        # ] = Raise Land (former only, costs energy)
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id and getattr(unit, 'is_former', False):
                            from game.terraforming import get_available_actions
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            available = get_available_actions(unit, tile, game)
                            if 'raise_land' in available:
                                game.pending_terraform_cost = {'unit': unit, 'action': 'raise_land', 'cost': 12}
                            else:
                                game.set_status_message("Cannot raise terrain here.")
                    elif event.key == pygame.K_LEFTBRACKET:
                        # [ = Lower Land (former only, costs energy)
                        unit = game.selected_unit
                        if unit and unit.owner == game.player_faction_id and getattr(unit, 'is_former', False):
                            from game.terraforming import get_available_actions
                            tile = game.game_map.get_tile(unit.x, unit.y)
                            available = get_available_actions(unit, tile, game)
                            if 'lower_land' in available:
                                game.pending_terraform_cost = {'unit': unit, 'action': 'lower_land', 'cost': 12}
                            else:
                                game.set_status_message("Cannot lower terrain here.")
                    # Arrow/numpad movement — routes to cursor or unit depending on mode
                    elif game.tile_cursor_mode or game.selected_unit:
                        dx, dy = 0, 0
                        # Arrow keys
                        if event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                        elif event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        # Numpad
                        elif event.key == pygame.K_KP8:  # Up
                            dy = -1
                        elif event.key == pygame.K_KP2:  # Down
                            dy = 1
                        elif event.key == pygame.K_KP4:  # Left
                            dx = -1
                        elif event.key == pygame.K_KP6:  # Right
                            dx = 1
                        elif event.key == pygame.K_KP7:  # Up-Left
                            dx, dy = -1, -1
                        elif event.key == pygame.K_KP9:  # Up-Right
                            dx, dy = 1, -1
                        elif event.key == pygame.K_KP1:  # Down-Left
                            dx, dy = -1, 1
                        elif event.key == pygame.K_KP3:  # Down-Right
                            dx, dy = 1, 1

                        if dx != 0 or dy != 0:
                            if game.tile_cursor_mode:
                                # Move cursor; scroll camera only if it drifts off-screen
                                game.cursor_x = (game.cursor_x + dx) % game.game_map.width
                                game.cursor_y = max(0, min(game.cursor_y + dy, game.game_map.height - 1))
                                if not renderer.is_tile_on_screen(game.cursor_x, game.cursor_y, game.game_map):
                                    game.center_camera_on_tile = (game.cursor_x, game.cursor_y)
                            elif game.selected_unit:
                                target_x = game.selected_unit.x + dx
                                target_y = game.selected_unit.y + dy
                                wrapped_x = target_x % game.game_map.width
                                unit = game.selected_unit
                                # Debark popup: sea transport with cargo moving toward land
                                if (0 <= target_y < game.game_map.height
                                        and unit.type == 'sea'
                                        and getattr(unit, 'loaded_units', [])):
                                    tgt = game.game_map.get_tile(wrapped_x, target_y)
                                    debarkable = [u for u in unit.loaded_units
                                                  if u.moves_remaining > 0]
                                    if (tgt and tgt.is_land()
                                            and not (tgt.base and tgt.base.owner == unit.owner)
                                            and debarkable):
                                        ui_panel.debark_dialog.activate(unit, wrapped_x, target_y)
                                    else:
                                        was_held = getattr(unit, 'held', False)
                                        game.movement.try_move_unit(unit, target_x, target_y)
                                        if not was_held and getattr(unit, 'held', False):
                                            game.turns.cycle_units()
                                else:
                                    was_held = getattr(unit, 'held', False)
                                    game.movement.try_move_unit(unit, target_x, target_y)
                                    if not was_held and getattr(unit, 'held', False):
                                        game.turns.cycle_units()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Block all input during AI processing unless a popup needs attention
                if game.processing_ai:
                    if not has_blocking_popup(game, ui_panel):
                        continue

                # Check for exit dialog first
                if exit_dialog.show_dialog:
                    exit_result = exit_dialog.handle_event(event)
                    if exit_result == 'exit':
                        running = False
                        game.running = False
                    continue

                # Check for menu dialog
                if menu_dialog.show_dialog:
                    menu_result = menu_dialog.handle_event(event)
                    if menu_result == 'exit':
                        # Return to main menu
                        game = None
                        renderer = None
                        ui_panel = None
                        intro_screen.mode = 'intro'
                        menu_dialog.hide()
                    continue

                mouse_x, mouse_y = event.pos
                # Let UI handle click first (for drop-up menu, overlays, and buttons)
                ui_handled = ui_panel.handle_event(event, game)
                # Check if it's a load game result
                if isinstance(ui_handled, tuple) and ui_handled[0] == 'load_game':
                    game = ui_handled[1]  # Replace game instance
                    renderer = Renderer(screen)  # Recreate renderer with new game
                    game.ui_manager = ui_panel  # Restore UI reference
                    # Restore diplomatic relations from saved data
                    if hasattr(game, '_saved_diplo_relations'):
                        ui_panel.diplomacy.diplo_relations = game._saved_diplo_relations.copy()
                        delattr(game, '_saved_diplo_relations')  # Clean up temporary storage
                elif isinstance(ui_handled, tuple) and ui_handled[0] == 'return_to_menu':
                    game = None
                    renderer = None
                    ui_panel = None
                    intro_screen.mode = 'intro'
                elif not ui_handled:
                    # UI didn't handle it - pass to game if in map area
                    if mouse_y < display.MAP_AREA_HEIGHT:
                        # Right-click - show context menu for artillery
                        if event.button == 3:  # Right mouse button
                            # Convert screen coordinates to map coordinates
                            map_x, map_y = renderer.screen_to_tile(mouse_x, mouse_y, game.game_map)

                            # Check if we have artillery unit selected
                            if (game.selected_unit and
                                game.selected_unit.owner == game.player_faction_id and
                                hasattr(game.selected_unit, 'has_artillery') and
                                game.selected_unit.has_artillery):

                                # Check if target is valid for artillery
                                can_fire, _ = game.can_artillery_fire_at(game.selected_unit, map_x, map_y)
                                if can_fire:
                                    # Show context menu with Long Range Fire option
                                    def fire_artillery():
                                        game.execute_artillery_fire(game.selected_unit, map_x, map_y)

                                    ui_panel.context_menu.show(mouse_x, mouse_y, [
                                        ("Long Range Fire", fire_artillery)
                                    ])
                        # Left-click - regular game handling
                        else:
                            result = game.handle_click(mouse_x, mouse_y, renderer)
                            if result and result[0] == 'base_click':
                                clicked_base = result[1]
                                ui_panel.show_base_view(clicked_base)

            # Let UI handle hover events (MOUSEMOTION), but NOT clicks again
            elif event.type == pygame.MOUSEMOTION:
                ui_panel.handle_event(event, game)

        # Update and render based on game state
        dt = clock.get_time()

        if game is None:
            # Intro screen active
            intro_screen.update(dt)
            intro_load_dialog.update(dt)

            # Render intro screen
            screen.fill((0, 0, 0))
            intro_screen.draw(screen, display.SCREEN_WIDTH, display.SCREEN_HEIGHT)

            # Draw load dialog if open
            if intro_load_dialog.mode is not None:
                intro_load_dialog.draw(screen)

            pygame.display.flip()
            clock.tick(display.FPS)
            continue

        # Game is active
        # Handle continuous input (camera movement)
        game.handle_input(renderer)

        # Check for auto-cycle to next unit after delay
        game.turns.check_auto_cycle()

        # Process AI turns with delay (but not if popup is blocking)
        if game.processing_ai:
            # Check if any blocking popup is active
            popups_blocking = has_blocking_popup(game, ui_panel)

            if not popups_blocking:
                current_time = pygame.time.get_ticks()
                if current_time - last_ai_action >= display.AI_TURN_DELAY:
                    game.turns.process_ai_turns()
                    last_ai_action = current_time

        # Handle map scrolling when mouse is at edges (only in map area)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_y < display.MAP_AREA_HEIGHT:
            current_time = pygame.time.get_ticks()
            if current_time - last_scroll_time >= display.SCROLL_DELAY:
                # Calculate 5% edge zones
                edge_zone_width = int(display.SCREEN_WIDTH * 0.05)
                edge_zone_height = int(display.MAP_AREA_HEIGHT * 0.05)

                # Horizontal scrolling (wraps)
                if mouse_x < edge_zone_width:
                    # Scroll left (decrease camera offset)
                    renderer.scroll_camera(-1, 0)
                    last_scroll_time = current_time
                elif mouse_x > display.SCREEN_WIDTH - edge_zone_width:
                    # Scroll right (increase camera offset)
                    renderer.scroll_camera(1, 0)
                    last_scroll_time = current_time

                # Vertical scrolling (hard borders)
                if mouse_y < edge_zone_height:
                    # Scroll up
                    renderer.scroll_camera(0, -1)
                    last_scroll_time = current_time
                elif mouse_y > display.MAP_AREA_HEIGHT - edge_zone_height:
                    # Scroll down
                    renderer.scroll_camera(0, 1)
                    last_scroll_time = current_time

        # Update game state
        game.update(dt)
        ui_panel.save_load_dialog.update(dt)

        # Handle camera centering
        if game.center_camera_on_selected and game.selected_unit:
            renderer.center_on_tile(game.selected_unit.x, game.selected_unit.y, game.game_map)
            game.center_camera_on_selected = False
        elif game.center_camera_on_tile:
            renderer.center_on_tile(game.center_camera_on_tile[0], game.center_camera_on_tile[1], game.game_map)
            game.center_camera_on_tile = None

        # Hide cursor during AI turns (unless a popup is waiting for player input)
        if game.processing_ai:
            pygame.mouse.set_visible(has_blocking_popup(game, ui_panel))
        else:
            pygame.mouse.set_visible(True)

        # Render (ORDER MATTERS!)
        screen.fill((0, 0, 0))  # Clear screen first
        renderer.draw_map(game.game_map, game.territory)  # Draw map tiles and territory
        renderer.draw_bases(game.bases, game.player_faction_id, game.game_map, game)  # Draw bases
        renderer.draw_units(game.units, game.selected_unit, game.player_faction_id, game.game_map)  # Draw units on top
        if game.tile_cursor_mode:
            renderer.draw_tile_cursor(game.cursor_x, game.cursor_y, game.game_map)
        renderer.draw_status_message(game)  # Draw status message
        ui_panel.draw(screen, game, renderer)  # Draw UI last

        # Draw debug overlay if enabled
        if game.debug.enabled:
            game.debug.draw_overlay(screen, pygame.font.Font(None, 20))

        # Draw exit dialog on top of everything if showing
        if exit_dialog.show_dialog:
            exit_dialog.draw(screen, display.SCREEN_WIDTH, display.SCREEN_HEIGHT)

        # Draw menu dialog on top of everything if showing
        if menu_dialog.show_dialog:
            menu_dialog.draw(screen, display.SCREEN_WIDTH, display.SCREEN_HEIGHT)

        pygame.display.flip()  # Update display

        # Cap frame rate
        clock.tick(display.FPS)

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()