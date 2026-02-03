# main.py
import pygame
import sys
import constants
from game import Game
from renderer import Renderer
from ui import UIManager
from ui.intro_screen import IntroScreenManager
from ui.save_load_dialog import SaveLoadDialogManager
from ui.exit_dialog import ExitDialogManager
import save_load


def main():
    """Initialize and run the game."""
    # Initialize Pygame
    pygame.init()

    # Create saves directory
    import os
    os.makedirs('saves', exist_ok=True)

    # Get display info for sizing
    display_info = pygame.display.Info()
    screen_width = display_info.current_w
    screen_height = display_info.current_h

    # Update constants with actual screen dimensions
    constants.SCREEN_WIDTH = screen_width
    constants.SCREEN_HEIGHT = screen_height

    # Calculate MAP_AREA_HEIGHT to be an exact multiple of TILE_SIZE
    # This ensures no partial tiles or gaps
    available_height = screen_height - constants.UI_PANEL_HEIGHT
    num_complete_tiles = available_height // constants.TILE_SIZE
    constants.MAP_AREA_HEIGHT = num_complete_tiles * constants.TILE_SIZE
    constants.UI_PANEL_Y = constants.MAP_AREA_HEIGHT  # Panel starts right after last complete tile

    # Calculate map size to be double screen size (both width and height)
    constants.MAP_HEIGHT = (constants.MAP_AREA_HEIGHT // constants.TILE_SIZE) * 2
    # Width double of screen
    constants.MAP_WIDTH = (screen_width // constants.TILE_SIZE) * 2

    # Create window (not fullscreen, but maximized size)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Alpha Centauri Clone")

    # Create game clock for frame rate control
    clock = pygame.time.Clock()

    # Initialize intro screen
    intro_screen = IntroScreenManager(pygame.font.Font(None, 24), pygame.font.Font(None, 18))
    intro_load_dialog = SaveLoadDialogManager(pygame.font.Font(None, 24), pygame.font.Font(None, 18))
    exit_dialog = ExitDialogManager(pygame.font.Font(None, 24), "Are you sure you want to exit?")
    menu_dialog = ExitDialogManager(pygame.font.Font(None, 24), "Return to main menu?")

    # Game will be None until player starts a game
    game = None
    renderer = None
    ui_panel = None

    # AI turn processing
    ai_turn_delay = 500  # milliseconds between AI unit moves
    last_ai_action = 0

    # Map scrolling
    scroll_delay = 750  # milliseconds between scroll ticks (0.75 seconds)
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
                    # Start new game with selected faction, name, and land percentage
                    _, faction_id, player_name, land_percentage = intro_result
                    game = Game(faction_id, player_name, land_percentage)
                    renderer = Renderer(screen)
                    ui_panel = UIManager()
                    intro_screen.mode = None
                continue

            # Game is active - handle game events
            elif event.type == pygame.KEYDOWN:
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

                # Check for Escape - close overlays first, then show exit dialog
                if event.key == pygame.K_ESCAPE:
                    # Check if any overlay is active and close it instead of exiting
                    if ui_panel.active_screen != "GAME":
                        ui_panel.active_screen = "GAME"
                        continue
                    # No overlay active - show exit dialog
                    exit_dialog.show()
                    continue

                # Check for Ctrl+Shift+Q to show menu dialog
                mods = pygame.key.get_mods()
                if event.key == pygame.K_q and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_SHIFT):
                    menu_dialog.show()
                    continue

                # Let UI handle keys first (for overlay controls)
                ui_handled = ui_panel.handle_event(event, game)
                # Check if it's a load game result
                if isinstance(ui_handled, tuple) and ui_handled[0] == 'load_game':
                    game = ui_handled[1]  # Replace game instance
                    renderer = Renderer(screen)  # Recreate renderer with new game
                elif not ui_handled:
                    # UI didn't handle it - process game keys
                    if event.key == pygame.K_n:
                        game.new_game()
                    elif event.key == pygame.K_w:
                        game.cycle_units()
                    elif event.key == pygame.K_b:
                        # Found a base if colony pod is selected
                        if game.selected_unit and game.selected_unit.is_colony_pod():
                            can_found, error_msg = game.can_found_base(game.selected_unit)
                            if can_found:
                                ui_panel.show_base_naming_dialog(game.selected_unit)
                            else:
                                game.set_status_message(f"Cannot found base: {error_msg}")
                    # Arrow key movement (8 directions)
                    elif game.selected_unit:
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
                        # Numpad (with num lock OFF, these are the directional keys)
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

                        # Try to move unit
                        if dx != 0 or dy != 0:
                            target_x = game.selected_unit.x + dx
                            target_y = game.selected_unit.y + dy
                            game.try_move_unit(game.selected_unit, target_x, target_y)

            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                elif not ui_handled:
                    # UI didn't handle it - pass to game if in map area
                    if mouse_y < constants.MAP_AREA_HEIGHT:
                        result = game.handle_click(mouse_x, mouse_y, renderer)
                        if result and result[0] == 'base_click':
                            clicked_base = result[1]
                            if clicked_base.is_friendly(game.player_id):
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
            intro_screen.draw(screen, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

            # Draw load dialog if open
            if intro_load_dialog.mode is not None:
                intro_load_dialog.draw(screen)

            pygame.display.flip()
            clock.tick(constants.FPS)
            continue

        # Game is active
        # Handle continuous input (camera movement)
        game.handle_input(renderer)

        # Process AI turns with delay
        if game.processing_ai:
            current_time = pygame.time.get_ticks()
            if current_time - last_ai_action >= ai_turn_delay:
                game.process_ai_turns()
                last_ai_action = current_time

        # Handle map scrolling when mouse is at edges (only in map area)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_y < constants.MAP_AREA_HEIGHT:
            current_time = pygame.time.get_ticks()
            if current_time - last_scroll_time >= scroll_delay:
                # Calculate 5% edge zones
                edge_zone_width = int(constants.SCREEN_WIDTH * 0.05)
                edge_zone_height = int(constants.MAP_AREA_HEIGHT * 0.05)

                # Horizontal scrolling (wraps)
                if mouse_x < edge_zone_width:
                    # Scroll left (decrease camera offset)
                    renderer.scroll_camera(-1, 0)
                    last_scroll_time = current_time
                elif mouse_x > constants.SCREEN_WIDTH - edge_zone_width:
                    # Scroll right (increase camera offset)
                    renderer.scroll_camera(1, 0)
                    last_scroll_time = current_time

                # Vertical scrolling (hard borders)
                if mouse_y < edge_zone_height:
                    # Scroll up
                    renderer.scroll_camera(0, -1)
                    last_scroll_time = current_time
                elif mouse_y > constants.MAP_AREA_HEIGHT - edge_zone_height:
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

        # Render (ORDER MATTERS!)
        screen.fill((0, 0, 0))  # Clear screen first
        renderer.draw_map(game.game_map, game.territory)  # Draw map tiles and territory
        renderer.draw_bases(game.bases, game.player_id, game.game_map, game.faction_assignments)  # Draw bases
        renderer.draw_units(game.units, game.selected_unit, game.player_id, game.game_map, game.faction_assignments)  # Draw units on top
        renderer.draw_status_message(game)  # Draw status message
        ui_panel.draw(screen, game, renderer)  # Draw UI last

        # Draw exit dialog on top of everything if showing
        if exit_dialog.show_dialog:
            exit_dialog.draw(screen, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

        # Draw menu dialog on top of everything if showing
        if menu_dialog.show_dialog:
            menu_dialog.draw(screen, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

        pygame.display.flip()  # Update display

        # Cap frame rate
        clock.tick(constants.FPS)

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()