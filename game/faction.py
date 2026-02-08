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

    def get_voting_power(self):
        """Calculate voting power based on total population across all bases.

        In SMAC, voting power equals total population. For now, we'll use a hardcoded
        value but the infrastructure is in place for when we implement proper calculation.

        Returns:
            int: Number of votes this faction has
        """
        # TODO: Calculate from actual base populations when that system is implemented
        # For now, return a hardcoded value based on number of bases
        if len(self.bases) == 0:
            return 0
        # Placeholder: each base contributes votes based on its population
        total_votes = sum(base.population for base in self.bases)
        return total_votes
