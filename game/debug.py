# debug.py
"""Debug/Cheat mode for testing game features.

This module provides debug commands for testing without playing through many turns.
All debug code is isolated here for easy removal before release.

Usage: Press Ctrl+Shift+D to toggle debug mode, then use hotkeys.
"""

import pygame
from game.units.unit import Unit
from game.base import Base


class DebugManager:
    """Manages debug/cheat mode functionality."""

    def __init__(self):
        """Initialize debug manager."""
        self.enabled = False
        self.show_help = True  # Show help overlay when debug mode first enabled
        self.cursor_spawn_mode = None  # 'unit' or 'base' when waiting for cursor click
        self.tech_selection_active = False
        self.unit_selection_active = False
        self.show_all_production = False  # See all faction production

    def toggle(self):
        """Toggle debug mode on/off."""
        self.enabled = not self.enabled
        if self.enabled:
            self.show_help = True
            print("=== DEBUG MODE ENABLED ===")
            print("Press Ctrl+Shift+H to toggle help overlay")
        else:
            self.show_help = False
            self.cursor_spawn_mode = None
            print("=== DEBUG MODE DISABLED ===")

    def handle_event(self, event, game):
        """Handle debug mode keyboard events.

        Args:
            event: Pygame event
            game: Game instance

        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.enabled:
            return False

        if event.type != pygame.KEYDOWN:
            return False

        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL
        shift = mods & pygame.KMOD_SHIFT

        # Ctrl+Shift+H - Toggle help overlay
        if ctrl and shift and event.key == pygame.K_h:
            self.show_help = not self.show_help
            return True

        # Ctrl+E - Add energy credits
        if ctrl and event.key == pygame.K_e:
            game.energy_credits += 1000
            game.set_status_message("DEBUG: +1000 Energy Credits")
            print("DEBUG: Added 1000 energy credits")
            return True

        # Ctrl+T - Grant all technologies
        if ctrl and event.key == pygame.K_t:
            self._grant_all_techs(game)
            return True

        # Ctrl+U - Spawn unit at selected location
        if ctrl and event.key == pygame.K_u:
            if game.selected_unit:
                self._show_unit_spawn_menu(game)
            else:
                game.set_status_message("DEBUG: Select a location first")
            return True

        # Ctrl+M - Upgrade selected unit morale
        if ctrl and event.key == pygame.K_m:
            if game.selected_unit and game.selected_unit.owner == game.player_id:
                self._upgrade_morale(game.selected_unit, game)
            else:
                game.set_status_message("DEBUG: Select your unit first")
            return True

        # Ctrl+H - Heal selected unit
        if ctrl and event.key == pygame.K_h:
            if game.selected_unit and game.selected_unit.owner == game.player_id:
                game.selected_unit.current_health = game.selected_unit.max_health
                game.set_status_message(f"DEBUG: {game.selected_unit.name} healed to full")
                print(f"DEBUG: Healed {game.selected_unit.name}")
            else:
                game.set_status_message("DEBUG: Select your unit first")
            return True

        # Ctrl+K - Kill selected unit
        if ctrl and event.key == pygame.K_k:
            if game.selected_unit:
                self._kill_unit(game.selected_unit, game)
            else:
                game.set_status_message("DEBUG: Select a unit first")
            return True

        # Ctrl+B - Create base at selected location
        if ctrl and event.key == pygame.K_b:
            if game.selected_unit:
                self._create_base_at_unit(game.selected_unit, game)
            else:
                game.set_status_message("DEBUG: Select a location first")
            return True

        # Ctrl+N - Skip to next turn
        if ctrl and event.key == pygame.K_n:
            game.turns.end_turn()
            game.set_status_message("DEBUG: Turn skipped")
            print("DEBUG: Skipped to next turn")
            return True

        # Ctrl+P - Toggle show all production
        if ctrl and event.key == pygame.K_p:
            self.show_all_production = not self.show_all_production
            status = "ON" if self.show_all_production else "OFF"
            game.set_status_message(f"DEBUG: Show all production {status}")
            print(f"DEBUG: Show all production {status}")
            return True

        # Ctrl+X - Add experience/kills to selected unit
        if ctrl and event.key == pygame.K_x:
            if game.selected_unit and game.selected_unit.owner == game.player_id:
                game.selected_unit.kills += 5
                game.selected_unit.experience += 100
                game.set_status_message(f"DEBUG: {game.selected_unit.name} +5 kills, +100 XP")
                print(f"DEBUG: Added experience to {game.selected_unit.name}")
            else:
                game.set_status_message("DEBUG: Select your unit first")
            return True

        # Ctrl+I - Toggle invincibility for selected unit
        if ctrl and event.key == pygame.K_i:
            if game.selected_unit and game.selected_unit.owner == game.player_id:
                # Set max health to 1000 as "invincibility"
                if game.selected_unit.max_health < 100:
                    game.selected_unit.max_health = 1000
                    game.selected_unit.current_health = 1000
                    game.set_status_message(f"DEBUG: {game.selected_unit.name} invincible")
                else:
                    game.selected_unit.max_health = 10
                    game.selected_unit.current_health = 10
                    game.set_status_message(f"DEBUG: {game.selected_unit.name} normal")
            else:
                game.set_status_message("DEBUG: Select your unit first")
            return True

        # Number keys 1-4 for quick unit spawning when in spawn mode
        if self.cursor_spawn_mode == 'unit':
            chassis_map = {
                pygame.K_1: 'infantry',
                pygame.K_2: 'foil',
                pygame.K_3: 'needlejet',
                pygame.K_4: 'artifact'  # Special case - will use infantry chassis with artifact weapon
            }
            if event.key in chassis_map:
                self._spawn_unit_at_location(game, chassis_map[event.key])
                self.cursor_spawn_mode = None
                return True

        return False

    def _grant_all_techs(self, game):
        """Grant all available technologies."""
        # Get player's tech tree
        player_tech_tree = game.factions[game.player_faction_id].tech_tree

        # Get all tech IDs
        all_techs = list(player_tech_tree.techs.keys())
        count = 0
        for tech_id in all_techs:
            if not player_tech_tree.has_tech(tech_id):
                player_tech_tree.discovered_techs.add(tech_id)
                count += 1

        game.set_status_message(f"DEBUG: Granted {count} technologies")
        print(f"DEBUG: Granted {count} technologies")

    def _show_unit_spawn_menu(self, game):
        """Show quick spawn menu."""
        self.cursor_spawn_mode = 'unit'
        game.set_status_message("DEBUG: Press 1=Infantry, 2=Foil, 3=Needlejet, 4=Artifact")
        print("DEBUG: Unit spawn mode - press number key to spawn")

    def _spawn_unit_at_location(self, game, chassis):
        """Spawn unit at selected location.

        Args:
            chassis: Chassis ID ('infantry', 'foil', 'needlejet', 'artifact')
        """
        if not game.selected_unit:
            return

        x, y = game.selected_unit.x, game.selected_unit.y

        # Map chassis to test weapons and names
        test_configs = {
            'infantry': ('hand_weapons', "Debug Scout"),
            'foil': ('laser', "Debug Foil"),
            'needlejet': ('missile_launcher', "Debug Needlejet"),
            'artifact': ('artifact', "Debug Artifact"),  # Special case
        }

        weapon, name = test_configs.get(chassis, ('hand_weapons', "Debug Unit"))

        unit = Unit(
            x=x, y=y,
            chassis=chassis if chassis != 'artifact' else 'infantry',  # Artifacts use infantry chassis
            owner=game.player_faction_id,
            name=name,
            weapon=weapon,
            armor='no_armor',
            reactor='fission'
        )

        # Give land units artillery for testing
        if unit.type == 'land':
            unit.has_artillery = True

        game.units.append(unit)
        game.game_map.add_unit_at(x, y, unit)
        game.set_status_message(f"DEBUG: Spawned {unit.name} at ({x}, {y})")
        print(f"DEBUG: Spawned {name} at ({x}, {y})")

    def _upgrade_morale(self, unit, game):
        """Upgrade unit morale by one level."""
        if unit.morale_level < 7:
            unit.morale_level += 1
            morale_name = unit.get_morale_name()
            game.set_status_message(f"DEBUG: {unit.name} -> {morale_name}")
            print(f"DEBUG: Upgraded {unit.name} to {morale_name}")
        else:
            game.set_status_message(f"DEBUG: {unit.name} already at max morale")

    def _kill_unit(self, unit, game):
        """Remove a unit from the game."""
        # Remove from map
        game.game_map.remove_unit_at(unit.x, unit.y, unit)
        # Remove from game units list
        if unit in game.units:
            game.units.remove(unit)
        # Deselect if it was selected
        if game.selected_unit == unit:
            game.selected_unit = None
        game.set_status_message(f"DEBUG: Killed {unit.name}")
        print(f"DEBUG: Removed {unit.name} from game")

    def _create_base_at_unit(self, unit, game):
        """Create a base at the unit's location."""
        x, y = unit.x, unit.y
        tile = game.game_map.get_tile(x, y)

        # Check if there's already a base here
        if tile.base:
            game.set_status_message("DEBUG: Base already exists here")
            return

        # Check if it's land
        if not tile.is_land():
            game.set_status_message("DEBUG: Can only build bases on land")
            return

        # Create base
        base_name = f"Debug Base {len(game.bases) + 1}"
        base = Base(x, y, game.player_id, base_name)
        game.bases.append(base)
        tile.base = base

        # Update territory
        game.territory.update_territory(game.bases)

        game.set_status_message(f"DEBUG: Created {base_name} at ({x}, {y})")
        print(f"DEBUG: Created base at ({x}, {y})")

    def draw_overlay(self, screen, font):
        """Draw debug mode overlay with available commands.

        Args:
            screen: Pygame screen surface
            font: Font to use for text
        """
        if not self.enabled or not self.show_help:
            return

        # Semi-transparent background
        overlay = pygame.Surface((400, 450))
        overlay.set_alpha(220)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (10, 10))

        # Title
        title = font.render("DEBUG MODE", True, (255, 100, 100))
        screen.blit(title, (20, 20))

        # Command list
        commands = [
            "Ctrl+Shift+D - Toggle debug mode",
            "Ctrl+Shift+H - Toggle this help",
            "",
            "Ctrl+E - Add 1000 energy credits",
            "Ctrl+T - Grant all technologies",
            "Ctrl+U - Spawn unit at location",
            "Ctrl+M - Upgrade unit morale",
            "Ctrl+H - Heal unit to full",
            "Ctrl+K - Kill selected unit",
            "Ctrl+B - Create base at location",
            "Ctrl+N - Skip to next turn",
            "Ctrl+P - Toggle show all production",
            "Ctrl+X - Add kills/XP to unit",
            "Ctrl+I - Toggle unit invincibility",
            "",
            "Select a unit first for unit commands",
        ]

        small_font = pygame.font.Font(None, 18)
        y = 55
        for cmd in commands:
            if cmd:  # Skip empty lines
                text = small_font.render(cmd, True, (200, 200, 200))
            else:
                text = small_font.render("", True, (200, 200, 200))
            screen.blit(text, (20, y))
            y += 22

        # Show current spawn mode
        if self.cursor_spawn_mode:
            mode_text = font.render("SPAWN MODE ACTIVE", True, (255, 255, 100))
            screen.blit(mode_text, (20, y + 10))
