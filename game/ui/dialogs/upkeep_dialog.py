"""Upkeep event notification dialog (shown between turns)."""

import pygame
from game.data.display_data import COLOR_TEXT
from game.ui.components import Dialog


class UpkeepEventDialog(Dialog):
    """Modal popup for between-turn events: tech breakthroughs, drone riots, etc.

    Does not own an `active` flag — UIManager gates with `game.upkeep_phase_active`.

    handle_click returns:
      ('zoom', base)  — Zoom to Base clicked; base may be None
      'continue'      — Continue/Proceed clicked
      True            — click blocked (didn't hit a button)
    """

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.zoom_rect = None
        self.continue_rect = None

    def draw(self, screen, game):
        event = game.turns.get_current_upkeep_event()
        if not event:
            return

        self.draw_overlay(screen)

        box = self.centered_rect(600, 360)
        box_x, box_y, box_w, box_h = box.x, box.y, box.w, box.h
        self.draw_box(screen, box, border_color=(100, 180, 220), bg_color=(40, 45, 50))

        # Title
        etype = event['type']
        if etype == 'tech_complete':
            title_text, title_color = "TECHNOLOGY BREAKTHROUGH", (100, 255, 100)
        elif etype == 'all_contacts':
            title_text, title_color = "DIPLOMATIC MILESTONE",    (100, 200, 255)
        elif etype == 'drone_riot':
            title_text, title_color = "CIVIL UNREST",            (255, 100, 100)
        elif etype == 'golden_age':
            title_text, title_color = "GOLDEN AGE",              (255, 220,  80)
        elif etype == 'starvation':
            title_text, title_color = "FOOD SHORTAGE",           (255, 180, 100)
        elif etype == 'ai_council':
            title_text, title_color = "PLANETARY COUNCIL VOTE",  (180, 200, 255)
        else:
            title_text, title_color = "UPKEEP REPORT",           (200, 220, 240)

        title_surf = self.font.render(title_text, True, title_color)
        screen.blit(title_surf, (box_x + box_w // 2 - title_surf.get_width() // 2, box_y + 20))

        # Body lines
        message = event.get('message', 'Event occurred.')
        if etype == 'tech_complete':
            msg_lines = [
                "Your researchers have discovered:",
                "",
                event['tech_name'],
                "",
            ]
            tech_id = event.get('tech_id')
            if tech_id:
                from game.data.unit_data import CHASSIS, WEAPONS, ARMOR, REACTORS, SPECIAL_ABILITIES
                from game.data.facility_data import FACILITIES, SECRET_PROJECTS
                unit_types = [i['name'] for i in CHASSIS + WEAPONS + ARMOR + REACTORS
                              if i.get('prereq') == tech_id]
                abilities  = [a['name'] for a in SPECIAL_ABILITIES
                              if a.get('prereq') == tech_id and a['id'] != 'none']
                facilities = [f['name'] for f in FACILITIES + SECRET_PROJECTS
                              if f.get('prereq') == tech_id]
                if unit_types:
                    msg_lines.append(f"Units: {', '.join(unit_types)}")
                if abilities:
                    msg_lines.append(f"Abilities: {', '.join(abilities)}")
                if facilities:
                    msg_lines.append(f"Facilities: {', '.join(facilities)}")
                if not unit_types and not abilities and not facilities:
                    msg_lines.append("No new units or facilities.")
            else:
                msg_lines.append("New units and facilities may be available.")
        elif etype == 'all_contacts':
            msg_lines = [
                "You have established contact with",
                "all living factions on Planet!",
                "",
                "You may now call the Planetary Council",
                "to propose global resolutions.",
            ]
        elif etype == 'drone_riot':
            msg_lines = [
                message,
                "",
                "Production has halted due to civil unrest.",
                "Increase psych allocation or build facilities",
                "to restore order.",
            ]
        elif etype == 'golden_age':
            msg_lines = [
                f"{event['base_name']} has entered a Golden Age!",
                "",
                "Talents now equal or outnumber all other citizens.",
                "Growth and economy bonuses will apply",
                "once the full formula is implemented.",
            ]
        elif etype == 'ai_council':
            msg_lines = [
                "The Planetary Council has voted on:",
                event['proposal_name'],
                "",
                "Voting Results:",
            ]
            for vote_entry in event.get('results', [])[:5]:
                msg_lines.append(f"  {vote_entry['name']}: {vote_entry['vote']}")
        else:
            msg_lines = [message]

        y_offset = box_y + 80
        for line in msg_lines:
            line_surf = self.small_font.render(line, True, COLOR_TEXT)
            screen.blit(line_surf, (box_x + box_w // 2 - line_surf.get_width() // 2, y_offset))
            y_offset += 25

        # Buttons
        btn_y = box_y + box_h - 70
        btn_w, btn_h = 180, 50
        mouse = pygame.mouse.get_pos()

        if 'base' in event:
            zoom_x = box_x + box_w // 2 - btn_w - 10
            self.zoom_rect = pygame.Rect(zoom_x, btn_y, btn_w, btn_h)
            hover = self.zoom_rect.collidepoint(mouse)
            pygame.draw.rect(screen, (65, 85, 100) if hover else (45, 55, 65),
                             self.zoom_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 140, 160), self.zoom_rect, 3, border_radius=8)
            zoom_surf = self.font.render("Zoom to Base", True, COLOR_TEXT)
            screen.blit(zoom_surf, (self.zoom_rect.centerx - zoom_surf.get_width() // 2,
                                    self.zoom_rect.centery - zoom_surf.get_height() // 2))
        else:
            self.zoom_rect = None

        continue_x = (box_x + box_w // 2 + 10 if self.zoom_rect
                      else box_x + box_w // 2 - btn_w // 2)
        self.continue_rect = pygame.Rect(continue_x, btn_y, btn_w, btn_h)
        hover = self.continue_rect.collidepoint(mouse)
        pygame.draw.rect(screen, (65, 85, 100) if hover else (45, 55, 65),
                         self.continue_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 160), self.continue_rect, 3, border_radius=8)
        btn_label = "Proceed" if etype == 'golden_age' else "Continue"
        cont_surf = self.font.render(btn_label, True, COLOR_TEXT)
        screen.blit(cont_surf, (self.continue_rect.centerx - cont_surf.get_width() // 2,
                                self.continue_rect.centery - cont_surf.get_height() // 2))

    def handle_click(self, pos, game):
        """Returns ('zoom', base), 'continue', or True (click blocked)."""
        if self.zoom_rect and self.zoom_rect.collidepoint(pos):
            event_data = game.turns.get_current_upkeep_event()
            base = event_data['base'] if event_data and 'base' in event_data else None
            game.turns.advance_upkeep_event()
            return ('zoom', base)
        if self.continue_rect and self.continue_rect.collidepoint(pos):
            game.turns.advance_upkeep_event()
            return 'continue'
        return True  # block click-through
