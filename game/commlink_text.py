"""Dialog system for talking with other factions.
"""

import re
from game.data.commlink_text_data import COMMLINK_TEXT


class DialogSubstitution:
    """Handles variable substitution in dialog text."""

    def __init__(self):
        """Initialize the substitution engine."""
        self.variables = {}
        self.current_ai_flavor = {}

    def set_context(self, player_faction, ai_faction):
        """Set up substitution context for dialog with a specific faction.

        Args:
            player_faction: The player's faction dict from FACTION_DATA
            ai_faction: The AI faction dict from FACTION_DATA (contains all flavor text)
        """
        print(f"Setting dialog context - Player: {player_faction['name']}, AI: {ai_faction['name']}")

        # ai_faction IS the flavor source - it contains all the $-prefixed keys
        flavor = ai_faction

        # Store faction-specific dialog overrides (keys starting with #)
        self.current_ai_flavor = {k: v for k, v in flavor.items() if k.startswith('#')}

        # Build the variable map using faction flavor text
        def get_f(key, default):
            """Get a flavor key from the faction data with fallback."""
            return flavor.get(key, default)

        self.variables = {
            'NAME0': player_faction.get('$NAME', 'I am'),
            'NAME1': player_faction.get('leader', 'Commander'),
            'TITLE0': player_faction.get('$TITLE', 'Leader'),
            'NAME3': get_f('$NAME', 'The Leader'),
            'TITLE2': get_f('$TITLE', 'Leader'),
            'FACTION2': get_f('$FACTION', 'The Faction'),  # AI's faction name
            'FACTION3': get_f('$FACTIONNOUN', 'Citizens'),
            'FACTION4': get_f('$FACTION', 'The Faction'),
            'FACTION5': get_f('$FACTION', 'The Faction'),  # AI's faction name (alternate)
            'CHARACTERADJ9': get_f('$CHARACTERADJ', 'strange'),
            'FACTIONPEJ5': get_f('$PEJORATIVE', 'Enemy'),
            'TO_CARRY_OUT_MY_MISSION6': get_f('$MISSION_STATEMENT', 'to survive'),
            'PET_PROJECTS6': get_f('$PET_PROJECTS', 'our goals'),
            'PET_PROJECTS7': get_f('$PET_PROJECTS', 'our goals'),  # Alternate variant
            'DANCINGNAKED3': get_f('$DANCING_NAKED_ACTION', 'plotting'),
            'BADHABITS5': get_f('$BAD_HABITS', 'stubbornness'),
            'FEE8': get_f('$FEE', 'payment'),
            'THOUGHT_POLICE4': get_f('$POLICE_NAME', 'security forces'),
            'THE_ENVIRONMENTAL_CODE9': get_f('$LAW_NAME', 'laws'),
        }

    def substitute(self, text, ai_gender_index=1, numbers=None):
        """
        text: The raw dialog string
        ai_gender_index: 1=Male, 2=Female (used for $<2:he:she> logic)
        numbers: Dict of numeric placeholders {0: value, 1: value, ...} for $NUM0, $NUM1, etc.
        """
        result = text

        # 1. Handle Faction-Specific Conditionals $<index:opt1:opt2:opt3:opt4>
        # Typical SMAC usage: $<2:he:she:it> or $<4:its:their>
        def replace_conditional(match):
            index = int(match.group(1))
            options = match.group(2).split(':')
            # For simplicity, if index is 2, use gender. If 4, use plurality.
            if index == 2:  # Gender
                return options[0] if ai_gender_index == 1 else options[1]
            return options[0]  # Fallback to first option

        result = re.sub(r'\$<(\d):([^>]+)>', replace_conditional, result)

        # 2. Numeric Placeholders ($NUM0, $NUM1, etc)
        if numbers:
            for num_index, value in numbers.items():
                result = result.replace(f'$NUM{num_index}', str(value))

        # 3. Simple Variable Substitution ($NAME3, etc)
        for var, value in self.variables.items():
            result = result.replace(f'${var}', str(value))

        return result

    def get_dialog(self, dialog_id, player_faction, ai_faction, numbers=None):
        """Get dialog with variable substitution.

        Args:
            dialog_id: Dialog ID to retrieve
            player_faction: Player's faction dict
            ai_faction: AI faction dict
            numbers: Optional dict of numeric placeholders {0: value, 1: value, ...}

        Returns:
            Dict with 'text' (substituted) and 'responses'
        """
        self.set_context(player_faction, ai_faction)

        # Look for override (e.g., #FACTIONTRUCE)
        # Note: SMAC files use #, but your code might look for 'FACTIONTRUCE'
        # Let's check both just in case.
        raw_id = dialog_id if dialog_id.startswith('#') else f'#{dialog_id}'

        if raw_id in self.current_ai_flavor:
            dialog_data = self.current_ai_flavor[raw_id]
            # Standardize 'options' vs 'responses'
            text = dialog_data.get('text', '')
            res = dialog_data.get('responses', dialog_data.get('options', []))
        else:
            #TODO: I should never need this.
            # Fallback to generic text.
            dialog_data = COMMLINK_TEXT.get(dialog_id, COMMLINK_TEXT.get('GENERIC', {'text': '...', 'responses': []}))
            text = dialog_data['text']
            res = dialog_data['responses']

        return {
            'text': self.substitute(text, numbers=numbers),
            'responses': res
        }

def select_greeting_dialog(relationship, is_first_meeting=False):
    """Select appropriate greeting dialog.

    For now, always use first meeting dialog until we implement tracking.
    """
    return 'INTRONEW0'


def select_farewell_dialog(relationship):
    """No dialog on normal exit - just close."""
    return None
