"""Dialog for selecting a Planetary Council proposal."""

import pygame
from game.data import display_data as display
from game.data.display_data import (COLOR_TEXT, COLOR_COUNCIL_BG, COLOR_COUNCIL_ACCENT,
                                 COLOR_COUNCIL_BORDER, COLOR_COUNCIL_BOX)
from game.data.council_proposal_data import PROPOSALS
from game.ui.components import Dialog


class CouncilProposalDialog(Dialog):
    """Full-screen proposal selection for Planetary Council.

    draw() renders the proposal list filtered by discovered techs.
    handle_click() returns:
      ('selected', proposal_dict) — player clicked a proposal
      'close'                     — player clicked Exit
      None                        — no action
    """

    def __init__(self, font, small_font):
        super().__init__(font, small_font)
        self.proposal_rects = []
        self.exit_rect = None

    def draw(self, screen, game):
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
        self.exit_rect = pygame.Rect(display.SCREEN_WIDTH // 2 - 100, display.SCREEN_HEIGHT - 100, 200, 55)
        is_hover = self.exit_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (50, 35, 35) if is_hover else (35, 25, 25), self.exit_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 100, 100), self.exit_rect, 3, border_radius=8)
        exit_text = self.font.render("Exit", True, COLOR_TEXT)
        screen.blit(exit_text, (self.exit_rect.centerx - exit_text.get_width() // 2,
                                self.exit_rect.centery - 10))

    def handle_click(self, pos, game):
        if self.exit_rect and self.exit_rect.collidepoint(pos):
            return 'close'

        for rect, prop in self.proposal_rects:
            if rect.collidepoint(pos):
                return ('selected', prop)

        return None
