# main.py
import pygame
import sys
from game import Game
from renderer import Renderer
from ui import UIPanel


def main():
    """Initialize and run the game."""
    # Initialize Pygame
    pygame.init()

    # Get display info for sizing
    display_info = pygame.display.Info()
    screen_width = display_info.current_w
    screen_height = display_info.current_h

    # Update constants with actual screen dimensions
    import constants
    constants.SCREEN_WIDTH = screen_width
    constants.SCREEN_HEIGHT = screen_height
    constants.UI_PANEL_Y = screen_height - constants.UI_PANEL_HEIGHT  # Panel at BOTTOM
    constants.MAP_AREA_HEIGHT = constants.UI_PANEL_Y  # Map area is everything above panel

    # Calculate map size to fit screen exactly
    constants.MAP_HEIGHT = constants.MAP_AREA_HEIGHT // constants.TILE_SIZE
    # Width fills entire screen
    constants.MAP_WIDTH = screen_width // constants.TILE_SIZE

    # Create window (not fullscreen, but maximized size)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Alpha Centauri Clone")

    # Create game clock for frame rate control
    clock = pygame.time.Clock()

    # Initialize core systems
    game = Game()
    renderer = Renderer(screen)
    ui_panel = UIPanel()

    # AI turn processing
    ai_turn_delay = 500  # milliseconds between AI unit moves
    last_ai_action = 0

    # Map scrolling
    scroll_delay = 750  # milliseconds between scroll ticks (0.75 seconds)
    last_scroll_time = 0

    # Main game loop
    while game.running:
        # Event handling
        # main.py - Inside the event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.KEYDOWN:
                # Let UI handle keys first (for overlay controls)
                ui_handled = ui_panel.handle_event(event, game)
                if not ui_handled:
                    # UI didn't handle it - process game keys
                    if event.key == pygame.K_ESCAPE:
                        game.running = False
                    elif event.key == pygame.K_n:
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
                mouse_x, mouse_y = event.pos
                # Let UI handle click first (for drop-up menu, overlays, and buttons)
                if not ui_panel.handle_event(event, game):
                    # UI didn't handle it - pass to game if in map area
                    if mouse_y < constants.MAP_AREA_HEIGHT:
                        result = game.handle_click(mouse_x, mouse_y, renderer)
                        if result and result[0] == 'base_click':
                            clicked_base = result[1]
                            if clicked_base.is_friendly(game.player_id):
                                ui_panel.show_base_view(clicked_base)

            # Let UI handle hover events (MOUSEMOTION), but NOT clicks again
            if event.type == pygame.MOUSEMOTION:
                ui_panel.handle_event(event, game)

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

                if mouse_x < edge_zone_width:
                    # Scroll left (decrease camera offset)
                    renderer.scroll_camera(-1)
                    last_scroll_time = current_time
                elif mouse_x > constants.SCREEN_WIDTH - edge_zone_width:
                    # Scroll right (increase camera offset)
                    renderer.scroll_camera(1)
                    last_scroll_time = current_time

        # Update game state
        dt = clock.get_time()
        game.update(dt)

        # Render (ORDER MATTERS!)
        screen.fill((0, 0, 0))  # Clear screen first
        renderer.draw_map(game.game_map, game.territory)  # Draw map tiles and territory
        renderer.draw_bases(game.bases, game.player_id, game.game_map)  # Draw bases
        renderer.draw_units(game.units, game.selected_unit, game.player_id, game.game_map)  # Draw units on top
        renderer.draw_status_message(game)  # Draw status message
        ui_panel.draw(screen, game)  # Draw UI last
        pygame.display.flip()  # Update display

        # Cap frame rate
        clock.tick(constants.FPS)

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()