# design_data.py
"""Per-faction unit design storage.

This module defines the DesignData class that contains all unit designs
for a single faction. Each faction maintains their own design slots based
on their discovered technologies.
"""


class DesignData:
    """Represents all unit designs for a single faction.

    Each faction maintains up to 64 design slots where they can store
    custom unit configurations. Designs are created in the Design Workshop
    UI and used for production at bases.

    Attributes:
        design_slots (list): Array of 64 design dictionaries (or None for empty slots)
        Each design is a dict with: chassis, weapon, armor, reactor, ability1, ability2
    """

    def __init__(self, faction_id=None):
        """Initialize empty design storage.

        Args:
            faction_id (int): Faction ID for faction-specific starting designs
        """
        # SMAC-style design slots (64 total, each can hold a design or be None)
        self.design_slots = [None] * 64

        # Initialize default designs (Scout Patrol and Colony Pod)
        self._initialize_default_designs(faction_id)

    def _initialize_default_designs(self, faction_id=None):
        """Initialize default unit designs based on faction.

        Args:
            faction_id (int): Faction ID for faction-specific designs
        """
        # Slot 0: Scout Patrol - basic infantry unit (everyone gets this)
        self.design_slots[0] = {
            "chassis": "infantry",
            "weapon": "hand_weapons",
            "armor": "no_armor",
            "reactor": "fission",
            "ability1": "none",
            "ability2": "none"
        }

        # Slot 1: Colony Pod - for founding new bases (everyone gets this)
        self.design_slots[1] = {
            "chassis": "infantry",
            "weapon": "colony_pod",
            "armor": "no_armor",
            "reactor": "fission",
            "ability1": "none",
            "ability2": "none"
        }

        # Slot 2: Faction-specific starting designs (SMAC-style)
        if faction_id == 0:  # Gaians - starts with Centauri Ecology (terraforming)
            # Former
            self.design_slots[2] = {
                "chassis": "infantry",
                "weapon": "terraforming",
                "armor": "no_armor",
                "reactor": "fission",
                "ability1": "none",
                "ability2": "none"
            }
        elif faction_id == 3:  # Morgan - starts with Biogenetics (synthmetal armor)
            # Upgraded infantry (1-2-1)
            self.design_slots[2] = {
                "chassis": "infantry",
                "weapon": "hand_weapons",
                "armor": "synthmetal",
                "reactor": "fission",
                "ability1": "none",
                "ability2": "none"
            }
        elif faction_id == 4:  # Santiago - starts with Doctrine: Mobility (speeder chassis)
            # Rover (1-1-2)
            self.design_slots[2] = {
                "chassis": "speeder",
                "weapon": "hand_weapons",
                "armor": "no_armor",
                "reactor": "fission",
                "ability1": "none",
                "ability2": "none"
            }

    def get_designs(self):
        """Get list of all non-None designs.

        Returns:
            list: All active designs (excludes None slots)
        """
        return [d for d in self.design_slots if d is not None]

    def find_first_empty_slot(self):
        """Find the first empty slot (None) in design_slots.

        Returns:
            int: Index of first empty slot, or 0 if all slots are full
        """
        for i, slot in enumerate(self.design_slots):
            if slot is None:
                return i
        return 0  # If all full, return first slot

    def add_design(self, design):
        """Add a new design to the first empty slot.

        Args:
            design (dict): Design dictionary with chassis, weapon, armor, reactor, abilities

        Returns:
            int: Index where design was added, or None if no empty slots
        """
        slot_index = self.find_first_empty_slot()
        if self.design_slots[slot_index] is None:
            self.design_slots[slot_index] = design
            return slot_index
        return None

    def remove_design(self, slot_index):
        """Remove a design from a slot.

        Args:
            slot_index (int): Index of slot to clear (0-63)
        """
        if 0 <= slot_index < 64:
            self.design_slots[slot_index] = None

    def get_design(self, slot_index):
        """Get design at a specific slot.

        Args:
            slot_index (int): Index of slot (0-63)

        Returns:
            dict or None: Design at that slot, or None if empty
        """
        if 0 <= slot_index < 64:
            return self.design_slots[slot_index]
        return None

    def set_design(self, slot_index, design):
        """Set design at a specific slot.

        Args:
            slot_index (int): Index of slot (0-63)
            design (dict or None): Design to set, or None to clear slot
        """
        if 0 <= slot_index < 64:
            self.design_slots[slot_index] = design

    def to_dict(self):
        """Serialize design data for saving.

        Returns:
            dict: Serialized design data
        """
        return {
            'design_slots': self.design_slots
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize design data from saved game.

        Args:
            data (dict): Serialized design data

        Returns:
            DesignData: Reconstructed design data
        """
        designs = cls.__new__(cls)
        designs.design_slots = data.get('design_slots', [None] * 64)

        # Ensure we have exactly 64 slots
        if len(designs.design_slots) < 64:
            designs.design_slots.extend([None] * (64 - len(designs.design_slots)))
        elif len(designs.design_slots) > 64:
            designs.design_slots = designs.design_slots[:64]

        return designs
