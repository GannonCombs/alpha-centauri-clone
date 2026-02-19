"""Planetary Council voting system."""

import pygame
import random
from game.data import display
from game.data.display import (COLOR_TEXT, COLOR_COUNCIL_BG, COLOR_COUNCIL_ACCENT,
                                 COLOR_COUNCIL_BORDER, COLOR_COUNCIL_BOX)
from game.data.data import FACTION_DATA, PROPOSALS


class CouncilManager:
    """Manages the Planetary Council voting system."""

    def __init__(self, font, small_font):
        """Initialize council manager with fonts."""
        self.font = font
        self.small_font = small_font

        # State
        self.council_stage = "select_proposal"  # select_proposal, too_recent, voting, results
        self.selected_proposal = None
        self.player_vote = None
        self.proposal_history = {}  # {proposal_id: last_voted_turn}
        self.council_votes = []

        # UI elements
        self.proposal_rects = []
        self.vote_option_rects = []
        self.council_too_recent_ok_rect = None
        self.council_ok_rect = None
        self.council_exit_rect = None

    def open_council(self):
        """Start a council session."""
        self.council_stage = "select_proposal"
        self.selected_proposal = None
        self.player_vote = None

    def draw(self, screen, game):
        """Render the appropriate council screen based on stage."""
        if self.council_stage == "select_proposal":
            self._draw_council_selection(screen, game)
        elif self.council_stage == "too_recent":
            self._draw_council_too_recent(screen, game)
        elif self.council_stage == "voting":
            self._draw_council_voting(screen, game)
        elif self.council_stage == "results":
            self._draw_council_results(screen)

    def handle_click(self, pos, game):
        """Process clicks on council interface. Returns 'close' if should exit, None otherwise."""
        if self.council_stage == "select_proposal":
            # Check exit button first
            if self.council_exit_rect and self.council_exit_rect.collidepoint(pos):
                return 'close'

            for rect, prop in self.proposal_rects:
                if rect.collidepoint(pos):
                    self.selected_proposal = prop
                    self.council_stage = "voting" if game.turn - prop.get('last_voted', -99) >= prop[
                        'cooldown'] else "too_recent"
                    if self.council_stage == "voting":
                        self._generate_ai_votes()
                    return None

        elif self.council_stage == "too_recent":
            if self.council_too_recent_ok_rect.collidepoint(pos):
                self.council_stage = "select_proposal"
                return None

        elif self.council_stage == "results":
            if self.council_ok_rect.collidepoint(pos):
                self.council_stage = "select_proposal"
                return 'close'

        elif self.council_stage == "voting" and not self.player_vote:
            for rect, val in self.vote_option_rects:
                if rect.collidepoint(pos):
                    self.player_vote = val
                    self.council_votes.insert(0, {"name": "You", "color": FACTION_DATA[0]['color'], "vote": val,
                                                  "votes": FACTION_DATA[0]['votes']})
                    pygame.time.wait(300)
                    self.council_stage = "results"
                    return None

        return None

    def _draw_council_selection(self, screen, game=None):
        """Draw Planetary Council proposal selection screen."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (20, 40, 30), (0, 40, display.SCREEN_WIDTH, 60))
        t = self.font.render("PLANETARY COUNCIL - SELECT PROPOSAL", True, COLOR_COUNCIL_ACCENT)
        screen.blit(t, (display.SCREEN_WIDTH // 2 - t.get_width() // 2, 60))

        # Filter proposals by discovered techs
        available_proposals = []
        for prop in PROPOSALS:
            required_tech = prop.get('required_tech')
            player_tech_tree = game.factions[game.player_faction_id].tech_tree if game else None
            if required_tech is None or (player_tech_tree and player_tech_tree.has_tech(required_tech)):
                available_proposals.append(prop)

        if not available_proposals:
            # No proposals available
            no_prop_text = self.font.render("No motions available at this time.", True, COLOR_TEXT)
            screen.blit(no_prop_text, (display.SCREEN_WIDTH // 2 - no_prop_text.get_width() // 2, 300))

        self.proposal_rects = []
        for i, prop in enumerate(available_proposals):
            rect = pygame.Rect(display.SCREEN_WIDTH // 2 - 400, 150 + i * 90, 800, 75)
            self.proposal_rects.append((rect, prop))
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (35, 55, 45) if is_hover else COLOR_COUNCIL_BOX, rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_COUNCIL_BORDER if is_hover else COLOR_COUNCIL_ACCENT, rect, 3,
                             border_radius=8)
            screen.blit(self.font.render(prop["name"], True, COLOR_COUNCIL_ACCENT), (rect.x + 25, rect.y + 18))
            if "desc" in prop:
                screen.blit(self.small_font.render(prop["desc"], True, (180, 220, 200)), (rect.x + 25, rect.y + 45))

        # Exit button
        self.council_exit_rect = pygame.Rect(display.SCREEN_WIDTH // 2 - 100, display.SCREEN_HEIGHT - 100, 200, 55)
        is_hover = self.council_exit_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (50, 35, 35) if is_hover else (35, 25, 25), self.council_exit_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 100, 100), self.council_exit_rect, 3, border_radius=8)
        exit_text = self.font.render("Exit", True, COLOR_TEXT)
        screen.blit(exit_text, (self.council_exit_rect.centerx - exit_text.get_width() // 2,
                                self.council_exit_rect.centery - 10))

    def _draw_council_too_recent(self, screen, game):
        """Draw error screen when trying to vote on proposal in cooldown."""
        screen.fill(COLOR_COUNCIL_BG)
        pygame.draw.rect(screen, (40, 25, 25), (0, 180, display.SCREEN_WIDTH, 60))
        t = self.font.render("PLANETARY COUNCIL - MOTION DENIED", True, (255, 140, 120))
        screen.blit(t, (display.SCREEN_WIDTH // 2 - t.get_width() // 2, 200))

        box = pygame.Rect(display.SCREEN_WIDTH // 2 - 350, 280, 700, 180)
        pygame.draw.rect(screen, COLOR_COUNCIL_BOX, box, border_radius=10)
        pygame.draw.rect(screen, (255, 140, 120), box, 3, border_radius=10)

        rem = max(0, self.selected_proposal['cooldown'] - (game.turn - self.selected_proposal.get('last_voted', 0)))
        msgs = [f"Motion '{self.selected_proposal['name']}' was recent.",
                f"Cooldown: {self.selected_proposal['cooldown']} turns.", f"Remaining: {rem}"]
        for i, m in enumerate(msgs):
            s = self.font.render(m, True, COLOR_TEXT)
            screen.blit(s, (display.SCREEN_WIDTH // 2 - s.get_width() // 2, 310 + i * 40))

        self.council_too_recent_ok_rect = pygame.Rect(display.SCREEN_WIDTH // 2 - 80, display.SCREEN_HEIGHT - 120,
                                                      160, 50)
        pygame.draw.rect(screen, (40, 30, 25), self.council_too_recent_ok_rect, border_radius=8)
        ok_t = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_t, (self.council_too_recent_ok_rect.centerx - ok_t.get_width() // 2,
                           self.council_too_recent_ok_rect.centery - 10))

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
                # Get faction preference for this proposal
                preference = self._get_faction_preference(f['name'], self.selected_proposal['id'])

                # Vote based on preference with some randomness
                if preference >= 1:
                    # Strongly favor - 80% yes, 15% abstain, 5% no
                    v = random.choices(["YES", "ABSTAIN", "NO"], weights=[80, 15, 5])[0]
                elif preference <= -1:
                    # Strongly oppose - 80% no, 15% abstain, 5% yes
                    v = random.choices(["NO", "ABSTAIN", "YES"], weights=[80, 15, 5])[0]
                else:
                    # Neutral - 40% yes, 40% no, 20% abstain
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

    def check_ai_council_call(self, ai_player_id, game):
        """Check if an AI player wants to call a council this turn.

        AI will call council if:
        - They have a strong preference (>=1) for an available proposal
        - The proposal is not on cooldown
        - Random chance based on preference strength

        Args:
            ai_player_id (int): The AI player's ID (1-6)
            game: The game state object

        Returns:
            str or None: Proposal ID to call, or None if not calling
        """
        # AI only calls council occasionally (20% base chance per turn)
        if random.random() > 0.2:
            return None

        # Get faction for this AI
        faction_id = ai_player_id  # ai_player_id IS faction_id
        if faction_id is None or faction_id >= len(FACTION_DATA):
            return None

        faction = FACTION_DATA[faction_id]
        faction_name = faction['name']

        # Get available proposals
        available_proposals = []
        for prop in PROPOSALS:
            # Check tech requirement
            required_tech = prop.get('required_tech')
            if required_tech and ai_player_id in game.factions:
                ai_tech_tree = game.factions[ai_player_id].tech_tree
                if ai_tech_tree and not ai_tech_tree.has_tech(required_tech):
                    continue

            # Check cooldown
            last_voted = prop.get('last_voted', -99)
            if game.turn - last_voted < prop['cooldown']:
                continue

            available_proposals.append(prop)

        if not available_proposals:
            return None

        # Find proposals this faction strongly favors
        favored_proposals = []
        for prop in available_proposals:
            preference = self._get_faction_preference(faction_name, prop['id'])
            if preference >= 1:  # Favor or strongly favor
                # Add multiple times for strong preference (increases chance)
                for _ in range(abs(preference)):
                    favored_proposals.append(prop)

        if not favored_proposals:
            return None

        # Randomly select a favored proposal to call
        selected = random.choice(favored_proposals)
        print(f"AI {faction_name} calling council for: {selected['name']}")
        return selected['id']

    def ai_call_council(self, proposal_id, game):
        """AI initiates a council vote for a specific proposal.

        Args:
            proposal_id (str): The ID of the proposal to vote on
            game: The game state object

        Returns:
            bool: True if council was called successfully
        """
        # Find the proposal
        proposal = None
        for prop in PROPOSALS:
            if prop['id'] == proposal_id:
                proposal = prop
                break

        if not proposal:
            return False

        # Set up the council vote
        self.selected_proposal = proposal
        self.council_stage = "voting"
        self.player_vote = None

        # Generate AI votes
        self._generate_ai_votes()

        # Auto-generate player vote (neutral/abstain for AI-called councils)
        if proposal['type'] == 'yesno':
            self.player_vote = "ABSTAIN"
        else:
            # For candidate votes, pick one of the top candidates randomly
            candidates = self._get_top_candidates()
            self.player_vote = random.choice(candidates)

        # Add player vote to results
        self.council_votes.insert(0, {
            "name": "You",
            "color": FACTION_DATA[0]['color'],
            "vote": self.player_vote,
            "votes": FACTION_DATA[0]['votes']
        })

        # Mark proposal as voted
        proposal['last_voted'] = game.turn

        # Move to results immediately (no player interaction needed)
        self.council_stage = "results"

        # Add to upkeep events so player sees the results
        game.upkeep_events.append({
            'type': 'ai_council',
            'proposal_name': proposal['name'],
            'results': list(self.council_votes)  # Copy the results
        })

        return True
