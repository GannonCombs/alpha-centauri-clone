# faction.py
"""Faction state management.

This module defines the Faction class that contains all per-faction game state
including tech trees, unit designs, economy, diplomacy, and AI personalities.
"""


class Faction:
    """Represents all state for a single faction (player or AI).

    Each faction maintains its own tech tree, unit designs, economy, diplomatic
    relations, and (if AI) personality and strategic state.

    Attributes:
        id (int): Faction ID (0-6, matches FACTION_DATA index)
        is_player (bool): True if this is the human player
        tech_tree: TechTree instance for this faction
        designs: DesignData instance for this faction's unit designs
        energy_credits (int): Current energy credits
        bases (list): References to bases owned by this faction
        units (list): References to units owned by this faction
    """

    def __init__(self, faction_id, is_player=False):
        """Initialize a faction with default starting state.

        Args:
            faction_id (int): Faction ID (0-6)
            is_player (bool): Whether this is the human player
        """
        # Identity
        self.id = faction_id
        self.is_player = is_player

        # Tech tree (will be initialized by Game)
        self.tech_tree = None

        # Unit designs (will be initialized by Game)
        self.designs = None

        # Economy
        self.energy_credits = 0

        # Units and bases (references, actual storage in Game)
        self.bases = []  # List of Base objects
        self.units = []  # List of Unit objects

        # Diplomacy (this faction's view of others)
        # Key: other_faction_id, Value: status ('Vendetta', 'Treaty', 'Pact', etc.)
        self.relations = {}

        # Contact status (which factions have been discovered)
        self.contacts = set()  # Set of faction_ids

        # AI-specific state (only used if not is_player)
        self.ai_personality = None  # Will be AIPersonality if AI
        self.ai_strategic_state = None  # Will be StrategicState if AI

    def get_static_data(self):
        """Get static faction data from FACTION_DATA.

        Returns:
            dict: Static faction data (name, leader, color, bonuses, etc.)
        """
        from game.data.data import FACTION_DATA
        return FACTION_DATA[self.id]

    @property
    def name(self):
        """Get faction name from static data."""
        return self.get_static_data()['name']

    @property
    def leader(self):
        """Get leader name from static data."""
        return self.get_static_data()['leader']

    @property
    def color(self):
        """Get faction color from static data."""
        return self.get_static_data()['color']

    @property
    def bonuses(self):
        """Get faction bonuses from static data."""
        return self.get_static_data().get('bonuses', {})

    def has_met(self, other_faction_id):
        """Check if this faction has met another faction.

        Args:
            other_faction_id (int): ID of other faction

        Returns:
            bool: True if factions have met
        """
        return other_faction_id in self.contacts

    def get_relation(self, other_faction_id):
        """Get diplomatic relation with another faction.

        Args:
            other_faction_id (int): ID of other faction

        Returns:
            str: Relation status ('Vendetta', 'Treaty', 'Pact', etc.) or None
        """
        return self.relations.get(other_faction_id)

    def set_relation(self, other_faction_id, status):
        """Set diplomatic relation with another faction.

        Args:
            other_faction_id (int): ID of other faction
            status (str): Relation status ('Vendetta', 'Treaty', 'Pact', etc.)
        """
        self.relations[other_faction_id] = status

    def get_voting_power(self, game=None):
        """Calculate voting power based on total population across all bases.

        Votes = Sum of base populations + bonuses:
        - Empath Guild: +25% votes
        - Clinical Immortality tech: 2x votes
        - Lal's faction perk: 2x votes

        Args:
            game: Game instance (needed to check for facilities/techs/bases)

        Returns:
            int: Number of votes this faction has
        """
        if not game:
            return 0

        # Get all bases owned by this faction
        faction_bases = [b for b in game.bases if b.owner == self.id]

        if len(faction_bases) == 0:
            return 0

        # Base votes = sum of all base population
        total_votes = sum(base.population for base in faction_bases)

        # Bonus 1: Empath Guild (+25%)
        has_empath_guild = any('Empath Guild' in base.facilities for base in faction_bases)
        if has_empath_guild:
            total_votes = int(total_votes * 1.25)

        # Bonus 2: Clinical Immortality tech (2x votes)
        has_clinical_immortality = False
        if game and hasattr(self, 'tech_tree'):
            has_clinical_immortality = 'clinical_immortality' in self.tech_tree.discovered_techs

        if has_clinical_immortality:
            total_votes *= 2

        # Bonus 3: Lal's double votes perk (2x votes)
        from game.data.data import FACTION_DATA
        faction_data = FACTION_DATA[self.id]
        if faction_data.get('double_votes', False):
            total_votes *= 2

        return total_votes
