"""Combat-related UI (prediction and animation)."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER)
from game.ui.components import Dialog


class CombatDialog(Dialog):
    """Manages combat UI - battle prediction modal and battle animation."""

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.battle_prediction_ok_rect = None
        self.battle_prediction_cancel_rect = None

    def draw_battle_prediction(self, screen, game):
        """Draw battle prediction dialog before combat."""
        if not game.combat.pending_battle:
            return

        attacker = game.combat.pending_battle['attacker']
        defender = game.combat.pending_battle['defender']

        self.draw_overlay(screen)

        # Prediction box (taller to fit modifiers)
        box_w, box_h = 500, 400
        box_x = (display.SCREEN_WIDTH - box_w) // 2
        box_y = (display.SCREEN_HEIGHT - box_h) // 2

        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (40, 30, 30), box_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 100, 100), box_rect, 3, border_radius=10)

        # Title
        title_text = self.font.render("BATTLE PREDICTION", True, (255, 200, 200))
        title_rect = title_text.get_rect(centerx=box_x + box_w // 2, top=box_y + 20)
        screen.blit(title_text, title_rect)

        # Attacker info (left side)
        att_x = box_x + 40
        att_y = box_y + 80
        att_name = self.font.render(f"{attacker.name}", True, (255, 255, 255) ) #TODO: Fix color to be faction color
        screen.blit(att_name, (att_x, att_y))

        att_stats = self.small_font.render(f"{attacker.get_stats_string()}", True, COLOR_TEXT)
        screen.blit(att_stats, (att_x, att_y + 30))

        att_hp = self.small_font.render(f"HP: {attacker.current_health}/{attacker.max_health}", True, COLOR_TEXT)
        screen.blit(att_hp, (att_x, att_y + 55))

        # Attacker modifiers
        att_modifiers = game.combat.get_combat_modifiers(attacker, is_defender=False, vs_unit=defender)
        mod_y = att_y + 75
        for mod in att_modifiers:
            mod_text = self.small_font.render(f"{mod['name']}: {mod['display']}", True, (150, 255, 150))
            screen.blit(mod_text, (att_x, mod_y))
            mod_y += 18

        # VS in center
        vs_text = self.font.render("VS", True, (255, 255, 255))
        vs_rect = vs_text.get_rect(center=(box_x + box_w // 2, att_y + 40))
        screen.blit(vs_text, vs_rect)

        # Defender info (right side)
        def_x = box_x + box_w - 200
        def_y = box_y + 80
        def_name = self.font.render(f"{defender.name}", True, (255, 255, 255)) #TODO: Fix to be faction color
        screen.blit(def_name, (def_x, def_y))

        def_stats = self.small_font.render(f"{defender.get_stats_string()}", True, COLOR_TEXT)
        screen.blit(def_stats, (def_x, def_y + 30))

        def_hp = self.small_font.render(f"HP: {defender.current_health}/{defender.max_health}", True, COLOR_TEXT)
        screen.blit(def_hp, (def_x, def_y + 55))

        # Defender modifiers
        def_modifiers = game.combat.get_combat_modifiers(defender, is_defender=True, vs_unit=attacker)
        mod_y = def_y + 75
        for mod in def_modifiers:
            mod_text = self.small_font.render(f"{mod['name']}: {mod['display']}", True, (150, 255, 150))
            screen.blit(mod_text, (def_x, mod_y))
            mod_y += 18

        # Combat odds
        odds = game.combat.calculate_combat_odds(attacker, defender)
        odds_text = self.font.render(f"Win Chance: {int(odds * 100)}%", True, (255, 255, 100))
        odds_rect = odds_text.get_rect(centerx=box_x + box_w // 2, top=box_y + 240)
        screen.blit(odds_text, odds_rect)

        # OK and Cancel buttons
        button_y = box_y + box_h - 60
        ok_w, ok_h = 100, 40
        cancel_w, cancel_h = 100, 40

        ok_x = box_x + box_w // 2 - ok_w - 10
        cancel_x = box_x + box_w // 2 + 10

        ok_rect = pygame.Rect(ok_x, button_y, ok_w, ok_h)
        cancel_rect = pygame.Rect(cancel_x, button_y, cancel_w, cancel_h)

        mouse_pos = pygame.mouse.get_pos()
        ok_hover = ok_rect.collidepoint(mouse_pos)
        cancel_hover = cancel_rect.collidepoint(mouse_pos)

        # OK button
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        ok_text_rect = ok_text.get_rect(center=ok_rect.center)
        screen.blit(ok_text, ok_text_rect)

        # Cancel button
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        screen.blit(cancel_text, cancel_text_rect)

        # Store rects for clicking
        self.battle_prediction_ok_rect = ok_rect
        self.battle_prediction_cancel_rect = cancel_rect

    def handle_battle_prediction_click(self, pos):
        """Handle click on battle prediction modal. Returns 'ok', 'cancel', or None."""
        if self.battle_prediction_ok_rect and self.battle_prediction_ok_rect.collidepoint(pos):
            return 'ok'
        elif self.battle_prediction_cancel_rect and self.battle_prediction_cancel_rect.collidepoint(pos):
            return 'cancel'
        return None

    def draw_battle_animation(self, screen, game):
        """Draw battle/info panel - always visible with constant border."""
        # Battle/info panel - right of unit panel
        panel_w = 360
        panel_h = 130  # Fixed height to make room for unit stack panel below
        panel_x = 680  # Position to right of unit panel
        panel_y = display.UI_PANEL_Y + 10

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Always draw constant border
        if game.combat.active_battle:
            # Battle in progress - red theme
            pygame.draw.rect(screen, (30, 20, 20), panel_rect, border_radius=8)
            pygame.draw.rect(screen, (150, 50, 50), panel_rect, 3, border_radius=8)

            battle = game.combat.active_battle
            attacker = battle['attacker']
            defender = battle['defender']

            # Title
            title = self.small_font.render("BATTLE IN PROGRESS", True, (255, 200, 200))
            title_rect = title.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 10)
            screen.blit(title, title_rect)

            # Show current round HP
            current_round_idx = battle['current_round'] - 1
            if 0 <= current_round_idx < len(battle['rounds']):
                round_data = battle['rounds'][current_round_idx]
                att_hp = round_data['attacker_hp']
                def_hp = round_data['defender_hp']
            else:
                att_hp = attacker.current_health
                def_hp = defender.current_health

            # Attacker HP (left)
            att_y = panel_y + 50
            att_text = self.small_font.render(f"{attacker.name}", True, (255, 255, 255) ) #TODO: Fix to be faction color
            screen.blit(att_text, (panel_x + 10, att_y))
            att_hp_text = self.small_font.render(f"HP: {att_hp}/{attacker.max_health}", True, COLOR_TEXT)
            screen.blit(att_hp_text, (panel_x + 10, att_y + 20))

            # Defender HP (right)
            def_text = self.small_font.render(f"{defender.name}", True, (255, 255, 255) ) #TODO: Fix to be faction color
            def_text_rect = def_text.get_rect(right=panel_x + panel_w - 10, top=att_y)
            screen.blit(def_text, def_text_rect)
            def_hp_text = self.small_font.render(f"HP: {def_hp}/{defender.max_health}", True, COLOR_TEXT)
            def_hp_rect = def_hp_text.get_rect(right=panel_x + panel_w - 10, top=att_y + 20)
            screen.blit(def_hp_text, def_hp_rect)

            # Show modifiers compactly
            mod_y = panel_y + 90

            # Attacker modifiers (left side)
            att_modifiers = game.combat.get_combat_modifiers(attacker, is_defender=False, vs_unit=defender)
            for mod in att_modifiers:
                mod_text = self.small_font.render(f"{mod['name']}: {mod['display']}", True, (150, 255, 150))
                screen.blit(mod_text, (panel_x + 10, mod_y))
                mod_y += 15

            # Defender modifiers (right side)
            mod_y = panel_y + 90
            def_modifiers = game.combat.get_combat_modifiers(defender, is_defender=True, vs_unit=attacker)
            for mod in def_modifiers:
                mod_text = self.small_font.render(f"{mod['name']}: {mod['display']}", True, (150, 255, 150))
                mod_text_rect = mod_text.get_rect(right=panel_x + panel_w - 10, top=mod_y)
                screen.blit(mod_text, mod_text_rect)
                mod_y += 15
        else:
            # No battle - neutral theme, show AI status or other info
            pygame.draw.rect(screen, (25, 30, 35), panel_rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_BUTTON_BORDER, panel_rect, 3, border_radius=8)

            # Show AI status if processing
            ai_status = game.get_ai_status_text()
            if ai_status:
                ai_text = self.font.render(ai_status, True, (255, 200, 100))
                ai_rect = ai_text.get_rect(centerx=panel_x + panel_w // 2, centery=panel_y + panel_h // 2)
                screen.blit(ai_text, ai_rect)
