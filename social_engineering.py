# social_engineering.py
"""Social Engineering system from Alpha Centauri alpha.txt.

This module calculates bonuses and penalties from social engineering choices
and applies them to various game systems (economy, growth, morale, etc.).
"""
from data.social_engineering_data import POLITICS_CHOICES, ECONOMICS_CHOICES, VALUES_CHOICES, FUTURE_CHOICES
def get_available_choices(category, tech_tree):
    """Get all SE choices available in a category based on techs.

    Args:
        category (str): 'Politics', 'Economics', 'Values', or 'Future Society'
        tech_tree (TechTree): Player's tech tree

    Returns:
        list: List of available choice dicts
    """
    category_map = {
        'Politics': POLITICS_CHOICES,
        'Economics': ECONOMICS_CHOICES,
        'Values': VALUES_CHOICES,
        'Future Society': FUTURE_CHOICES
    }

    choices = category_map.get(category, [])
    available = []

    for choice in choices:
        if choice['prereq'] is None or tech_tree.has_tech(choice['prereq']):
            available.append(choice)

    return available


def calculate_se_effects(se_selections):
    """Calculate total SE effects from current selections.

    Args:
        se_selections (dict): Dict mapping category to selected index

    Returns:
        dict: Total bonuses/penalties for each stat
    """
    effects = {
        'ECONOMY': 0,
        'EFFIC': 0,
        'SUPPORT': 0,
        'TALENT': 0,
        'MORALE': 0,
        'POLICE': 0,
        'GROWTH': 0,
        'PLANET': 0,
        'PROBE': 0,
        'INDUSTRY': 0,
        'RESEARCH': 0
    }

    # Get choice for each category
    categories = {
        'Politics': POLITICS_CHOICES,
        'Economics': ECONOMICS_CHOICES,
        'Values': VALUES_CHOICES,
        'Future Society': FUTURE_CHOICES
    }

    for category, choices in categories.items():
        selected_index = se_selections.get(category, 0)
        if 0 <= selected_index < len(choices):
            choice = choices[selected_index]
            for stat, value in choice['effects'].items():
                effects[stat] += value

    return effects


def apply_economy_bonus(base_energy, economy_level):
    """Apply economy SE bonus to energy production.

    Based on alpha.txt #SOCECONOMY:
    -2: -1 energy each base
    -1: -1 energy at HQ base
     0: Standard
    +1: +1 energy each base
    +2: +1 energy each square
    +3: +1 energy each square, +1 commerce
    etc.

    Args:
        base_energy (int): Base energy before bonuses
        economy_level (int): Economy SE level

    Returns:
        int: Energy with bonus applied
    """
    if economy_level == -2:
        return max(0, base_energy - 1)
    elif economy_level == -1:
        return base_energy  # -1 only at HQ, not implemented yet
    elif economy_level >= 1:
        return base_energy + economy_level
    return base_energy


def apply_growth_modifier(nutrients_needed, growth_level):
    """Apply growth SE modifier to nutrients needed for growth.

    Based on alpha.txt #SOCGROWTH:
    -2: -20% growth (nutrients needed * 1.20)
    -1: -10% growth (nutrients needed * 1.10)
     0: Normal
    +1: +10% growth (nutrients needed * 0.90)
    +2: +20% growth (nutrients needed * 0.80)
    etc.

    Args:
        nutrients_needed (int): Base nutrients needed
        growth_level (int): Growth SE level

    Returns:
        int: Modified nutrients needed
    """
    if growth_level < 0:
        multiplier = 1.0 + (abs(growth_level) * 0.10)
    elif growth_level > 0:
        multiplier = 1.0 - (growth_level * 0.10)
    else:
        multiplier = 1.0

    return max(1, int(nutrients_needed * multiplier))


def apply_support_effect(free_support_units, support_level):
    """Apply support SE effect to free unit support.

    Based on alpha.txt #SOCSUPPORT:
    -2: Support 1 unit free
    -1: Support 1 unit free
     0: Support 2 units free
    +1: Support 3 units free
    +2: Support 4 units free

    Args:
        free_support_units (int): Default free support
        support_level (int): Support SE level

    Returns:
        int: Modified free support
    """
    if support_level <= -2:
        return 1
    elif support_level == -1:
        return 1
    elif support_level == 0:
        return 2
    elif support_level == 1:
        return 3
    elif support_level >= 2:
        return 4
    return free_support_units


def get_morale_bonus(morale_level):
    """Get morale bonus from SE.

    Based on alpha.txt #SOCMORALE:
    -2: -1 Morale (+ modifiers halved)
    -1: -1 Morale
     0: Normal
    +1: +1 Morale
    +2: +1 Morale (+2 on defense)
    +3: +2 Morale (+3 on defense)

    Args:
        morale_level (int): Morale SE level

    Returns:
        int: Morale bonus (negative = penalty)
    """
    if morale_level <= -1:
        return -1
    elif morale_level == 1:
        return 1
    elif morale_level == 2:
        return 1  # +2 on defense handled separately
    elif morale_level >= 3:
        return 2  # +3 on defense handled separately
    return 0
