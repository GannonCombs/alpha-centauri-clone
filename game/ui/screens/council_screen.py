"""Planetary Council voting system."""

import pygame
import random
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_COUNCIL_BG, COLOR_COUNCIL_ACCENT,
                                 COLOR_COUNCIL_BOX)
from game.data.faction_data import FACTION_DATA


class CouncilScreen:
    """Manages the Planetary Council voting and results stages.

    Proposal selection and cooldown are handled by separate Dialog subclasses
    (CouncilProposalDialog and CouncilCooldownDialog) wired in ui_manager.
    """

    def __init__(self, font, small_font):
        """Initialize council manager with fonts."""
        self.font = font
        self.small_font = small_font

        # State
        self.selected_proposal = None
        self.player_vote = None
        self.council_votes = []
        self.council_stage = "voting"  # voting, results

        # UI elements
        self.vote_option_rects = []
        self.council_ok_rect = None

    def open_council(self, proposal):
        """Start a council voting session for the given proposal."""
        self.selected_proposal = proposal
        self.council_stage = "voting"
        self.player_vote = None
        self._generate_ai_votes()

    def draw(self, screen, game):
        """Render the appropriate council screen based on stage."""
        if self.council_stage == "voting":
            self._draw_council_voting(screen, game)
        elif self.council_stage == "results":
            self._draw_council_results(screen)

    def handle_click(self, pos, game):
        """Process clicks on council interface. Returns 'close' if should exit, None otherwise."""
        if self.council_stage == "results":
            if self.council_ok_rect and self.council_ok_rect.collidepoint(pos):
                return 'close'

        elif self.council_stage == "voting" and not self.player_vote:
            for rect, val in self.vote_option_rects:
                if rect.collidepoint(pos):
                    self.player_vote = val
                    self.council_votes.insert(0, {"name": "You", "color": FACTION_DATA[0]['color'], "vote": val,
                                                  "votes": FACTION_DATA[0]['votes']})
                    self.selected_proposal['last_voted'] = game.turn
                    pygame.time.wait(300)
                    self.council_stage = "results"
                    return None

        return None

    def _draw_council_voting(self, screen, game):
        """Draw voting interface for selected council proposal."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (20, 40, 30), (0, 20, display.SCREEN_WIDTH, 60))
        t = self.font.render(f"COUNCIL - {self.selected_proposal['name'].upper()}", True, COLOR_COUNCIL_ACCENT)
        screen.blit(t, (display.SCREEN_WIDTH // 2 - t.get_width() // 2, 40))

        box_w, box_h = 180, 100
        start_x = display.SCREEN_WIDTH // 2 - (4 * box_w + 3 * 20) // 2
        for i, f in enumerate(FACTION_DATA):
            x = start_x + (i % 4) * (box_w + 20)
            y = 120 + (i // 4) * (box_h + 25)
            rect = pygame.Rect(x, y, box_w, box_h)
            pygame.draw.rect(screen, COLOR_COUNCIL_BOX, rect, border_radius=6)
            pygame.draw.rect(screen, f['color'], rect, 3, border_radius=6)
            screen.blit(self.small_font.render(f['leader'], True, f['color']), (x + 68, y + 12))

        vote_y = 400
        if not self.player_vote:
            self.vote_option_rects = []
            opts = ["YES", "NO", "ABSTAIN"] if self.selected_proposal['type'] == 'yesno' else self._get_top_candidates()
            for i, opt in enumerate(opts):
                rect = pygame.Rect(display.SCREEN_WIDTH // 2 - (len(opts) * 100) + i * 210, vote_y, 180, 55)
                self.vote_option_rects.append((rect, opt))
                pygame.draw.rect(screen, (25, 50, 35), rect, border_radius=8)
                txt = self.font.render(opt, True, COLOR_TEXT)
                screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - 10))
        else:
            self._show_vote_tally(screen, vote_y)

    def _draw_council_results(self, screen):
        """Draw final voting results with all faction votes tallied."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (20, 40, 30), (0, 20, display.SCREEN_WIDTH, 60))
        t = self.font.render("COUNCIL VOTE - RESULTS", True, COLOR_COUNCIL_ACCENT)
        screen.blit(t, (display.SCREEN_WIDTH // 2 - t.get_width() // 2, 40))

        for i, entry in enumerate(self.council_votes):
            x = display.SCREEN_WIDTH // 2 + (-400 if i < 4 else 50)
            y = 160 + (i % 4) * 40
            rect = pygame.Rect(x, y - 5, 400, 35)
            pygame.draw.rect(screen, COLOR_COUNCIL_BOX, rect, border_radius=5)
            pygame.draw.rect(screen, entry["color"], rect, 2, border_radius=5)
            screen.blit(self.small_font.render(f"{entry['name']} → {entry['vote']}", True, entry["color"]), (x + 10, y))

        self.council_ok_rect = pygame.Rect(display.SCREEN_WIDTH // 2 - 80, display.SCREEN_HEIGHT - 80, 160, 50)
        pygame.draw.rect(screen, (25, 50, 35), self.council_ok_rect, border_radius=8)
        ok_t = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_t, (self.council_ok_rect.centerx - ok_t.get_width() // 2, self.council_ok_rect.centery - 10))

    def _show_vote_tally(self, screen, y):
        """Display player's vote and calculating message."""
        screen.blit(self.font.render(f"You voted: {self.player_vote}", True, (0, 255, 255)), (50, y))
        screen.blit(self.small_font.render("Calculating results...", True, (100, 150, 100)), (50, y + 40))

    def _generate_ai_votes(self):
        """Generate votes for all AI factions based on their preferences."""
        self.council_votes = []
        is_yesno = self.selected_proposal['type'] == 'yesno'
        opts = ["YES", "NO", "ABSTAIN"] if is_yesno else self._get_top_candidates()

        for f in FACTION_DATA[1:]:
            if is_yesno:
                v = random.choices(["YES", "NO", "ABSTAIN"], weights=[40, 40, 20])[0]
            else:
                # Candidate vote - random for now (could be based on alliances)
                v = random.choice(opts)

            self.council_votes.append(
                {"name": f["leader"], "color": f["color"], "vote": v, "votes": f["votes"]})

    def _get_top_candidates(self):
        """Get top two faction candidates for leader elections."""
        sorted_f = sorted(FACTION_DATA, key=lambda x: x['votes'], reverse=True)
        return [sorted_f[0]['leader'], sorted_f[1]['leader']]
