"""Commerce system - bonus energy from peaceful trade relationships.

Commerce is calculated between faction pairs with Treaties or Pacts.
Bases are paired by energy output, and each pair generates a commerce pool
that is divided based on economic technology advancement.
"""

import math
from game.data.data import FACTION_DATA

ECONOMIC_TECHS = {
    'industrial_economics',
    'industrial_automation',
    'planetary_economics',
    'industrial_nanorobotics',
    'sentient_econometrics',
    'environmental_economics'
}

TOTAL_ECONOMIC_TECHS = 6


class CommerceCalculator:
    """Handles all commerce calculations for the game."""

    def __init__(self, game):
        self.game = game
        # Store commerce totals per faction-pair for display
        # Format: {(faction1_id, faction2_id): (amount1, amount2)}
        self.commerce_by_relationship = {}
        # Store total commerce per faction
        # Format: {faction_id: total_commerce}
        self.commerce_by_faction = {}

    def calculate_all_commerce(self):
        """Calculate commerce for all faction pairs with Treaties/Pacts.

        Called once per turn during upkeep phase.
        Distributes commerce income to all factions (player and AI).

        Returns:
            int: Total commerce income for player faction
        """
        print("\n=== COMMERCE CALCULATION ===")

        # Reset
        self.commerce_by_relationship = {}
        self.commerce_by_faction = {i: 0 for i in range(7)}

        for base in self.game.bases:
            base.commerce_income = 0

        # Check each pair of factions
        for faction1_id in range(7):
            if faction1_id in self.game.eliminated_factions:
                continue

            for faction2_id in range(faction1_id + 1, 7):
                if faction2_id in self.game.eliminated_factions:
                    continue

                # Get diplomatic relation
                relation = self._get_relation_between(faction1_id, faction2_id)

                if relation not in ['Treaty', 'Pact']:
                    continue

                print(f"  Faction {faction1_id} <-> Faction {faction2_id}: {relation}")

                # STEP 10 FIRST: Check for sanctions (skip all commerce if true)
                if self._has_sanctions(faction1_id) or self._has_sanctions(faction2_id):
                    print(f"    Sanctions active - no commerce")
                    self.commerce_by_relationship[(faction1_id, faction2_id)] = (0, 0)
                    continue

                # Calculate commerce for this faction pair
                total1, total2 = self._calculate_commerce_between_factions(
                    faction1_id, faction2_id, relation
                )

                print(f"    Faction {faction1_id} gets: {total1} energy")
                print(f"    Faction {faction2_id} gets: {total2} energy")

                # Store for display
                self.commerce_by_relationship[(faction1_id, faction2_id)] = (total1, total2)

                # Accumulate faction totals
                self.commerce_by_faction[faction1_id] += total1
                self.commerce_by_faction[faction2_id] += total2

        # Distribute commerce to all factions' energy reserves
        print("\n  Commerce Distribution:")
        for faction_id, commerce_amount in self.commerce_by_faction.items():
            if commerce_amount > 0:
                from game.data.data import FACTION_DATA
                faction_name = FACTION_DATA[faction_id]['leader']
                print(f"    {faction_name} (Faction {faction_id}): +{commerce_amount} energy")
                self.game.factions[faction_id].energy_credits += commerce_amount

        player_commerce = self.commerce_by_faction.get(self.game.player_faction_id, 0)
        print(f"\n  Player total commerce: +{player_commerce} energy")
        print("=== END COMMERCE CALCULATION ===\n")

        # Return player's total commerce income
        return player_commerce

    def _calculate_commerce_between_factions(self, faction1_id, faction2_id, relation):
        """Calculate commerce between two factions.

        Returns:
            tuple: (total_commerce_faction1, total_commerce_faction2)
        """
        # Step 1-2: Rank and pair bases by energy output
        bases1 = self._rank_bases_by_energy(faction1_id)
        bases2 = self._rank_bases_by_energy(faction2_id)
        num_pairs = min(len(bases1), len(bases2))

        print(f"    Faction {faction1_id} has {len(bases1)} bases, Faction {faction2_id} has {len(bases2)} bases")
        print(f"    Pairing {num_pairs} bases")

        total_commerce1 = 0
        total_commerce2 = 0

        # Process each pair
        for i in range(num_pairs):
            base1 = bases1[i]
            base2 = bases2[i]

            # Step 3: Calculate commerce pool
            energy1 = base1.energy_production
            energy2 = base2.energy_production
            commerce_pool = math.ceil((energy1 + energy2) / 8.0)

            print(f"      Pair {i+1}: {base1.name} ({energy1} energy) <-> {base2.name} ({energy2} energy)")
            print(f"        Pool = ceil(({energy1} + {energy2}) / 8) = {commerce_pool}")

            # Step 4: Global Trade Pact doubles the pool
            if self._global_trade_pact_active():
                commerce_pool *= 2
                print(f"        Global Trade Pact: Pool doubled to {commerce_pool}")

            # Step 5: Apply tech modifier (different for each faction)
            econ_techs1 = self._count_economic_techs(faction1_id)
            econ_techs2 = self._count_economic_techs(faction2_id)
            commerce1 = self._apply_tech_modifier(commerce_pool, faction1_id)
            commerce2 = self._apply_tech_modifier(commerce_pool, faction2_id)

            print(f"        Faction {faction1_id} econ techs: {econ_techs1}, commerce = {commerce_pool} * ({econ_techs1}+1)/7 = {commerce1}")
            print(f"        Faction {faction2_id} econ techs: {econ_techs2}, commerce = {commerce_pool} * ({econ_techs2}+1)/7 = {commerce2}")

            # Step 8: Treaty halves commerce (Pact keeps full)
            if relation == 'Treaty':
                commerce1 = commerce1 // 2
                commerce2 = commerce2 // 2
                print(f"        Treaty (not Pact): Commerce halved to {commerce1} / {commerce2}")

            # Step 9: Planetary Governor gets +1
            planetary_governor = getattr(self.game, 'planetary_governor', None)
            if planetary_governor == faction1_id:
                commerce1 += 1
                print(f"        Faction {faction1_id} is Governor: +1 = {commerce1}")
            if planetary_governor == faction2_id:
                commerce2 += 1
                print(f"        Faction {faction2_id} is Governor: +1 = {commerce2}")

            # Morgan gets +1 (faction bonus)
            if self._is_morgan(faction1_id):
                commerce1 += 1
                print(f"        Faction {faction1_id} is Morgan: +1 = {commerce1}")
            if self._is_morgan(faction2_id):
                commerce2 += 1
                print(f"        Faction {faction2_id} is Morgan: +1 = {commerce2}")

            # Store on bases (for individual base display if needed)
            base1.commerce_income = commerce1
            base2.commerce_income = commerce2

            # Accumulate totals
            total_commerce1 += commerce1
            total_commerce2 += commerce2

        return total_commerce1, total_commerce2

    def _rank_bases_by_energy(self, faction_id):
        """Return faction's bases sorted by energy output (highest first)."""
        faction_bases = [b for b in self.game.bases if b.owner == faction_id]
        return sorted(
            faction_bases,
            key=lambda b: b.energy_production,
            reverse=True
        )

    def _apply_tech_modifier(self, commerce_pool, faction_id):
        """Apply CommerceTech modifier.

        Formula: Pool * (CommerceTech + 1) / (TotalCommerceTech + 1)
        CommerceTech = number of economic techs discovered (no bonuses here)
        """
        econ_tech_count = self._count_economic_techs(faction_id)
        commerce = commerce_pool * (econ_tech_count + 1) / (TOTAL_ECONOMIC_TECHS + 1)
        return int(commerce)  # Round down

    def _count_economic_techs(self, faction_id):
        """Count economic technologies discovered by faction."""
        tech_tree = self.game.factions[faction_id].tech_tree
        return len(ECONOMIC_TECHS & tech_tree.discovered_techs)

    def _is_morgan(self, faction_id):
        """Check if faction is CEO Morgan."""
        return FACTION_DATA[faction_id]['name'] == 'The Morgan Industries'

    def _get_relation_between(self, faction1_id, faction2_id):
        """Get diplomatic relation between two factions."""
        # Relations are stored from player perspective
        if faction1_id == self.game.player_faction_id:
            return self.game.ui_manager.diplomacy.diplo_relations.get(
                faction2_id, "Uncommitted"
            )
        elif faction2_id == self.game.player_faction_id:
            return self.game.ui_manager.diplomacy.diplo_relations.get(
                faction1_id, "Uncommitted"
            )
        else:
            # AI-AI relations - not implemented yet
            return "Uncommitted"

    def _global_trade_pact_active(self):
        """Check if Global Trade Pact is active."""
        # TODO: Implement when planetary council proposals are tracked
        return getattr(self.game, 'global_trade_pact_active', False)

    def _has_sanctions(self, faction_id):
        """Check if faction has sanctions (from atrocities)."""
        # TODO: Implement when atrocities/sanctions system exists
        return False

    def get_commerce_display_data(self):
        """Get commerce breakdown for UI display.

        Returns:
            list of tuples: [(faction_name, your_amount, their_amount), ...]
            Sorted by faction name.
        """
        player_id = self.game.player_faction_id
        display_data = []

        for (f1, f2), (amount1, amount2) in self.commerce_by_relationship.items():
            if f1 == player_id:
                partner_id = f2
                your_amount = amount1
                their_amount = amount2
            elif f2 == player_id:
                partner_id = f1
                your_amount = amount2
                their_amount = amount1
            else:
                continue  # Not player's relationship

            # Get faction leader's last name
            leader = FACTION_DATA[partner_id]['leader']
            partner_name = leader.split()[-1]  # "Sister Miriam Godwinson" -> "Godwinson"

            display_data.append((partner_name, your_amount, their_amount))

        # Sort by partner name
        display_data.sort(key=lambda x: x[0])

        return display_data
