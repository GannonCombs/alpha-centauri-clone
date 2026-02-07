"""Dialog system for talking with other factions.
"""

import re
from data.commlink_text_data import COMMLINK_TEXT
from data.data import FACTIONS

class DialogSubstitution:
    """Handles variable substitution in dialog text."""

    def __init__(self):
        """Initialize the substitution engine."""
        self.variables = {}
        self.current_ai_flavor = {}

    def set_context(self, player_faction, ai_faction):

        # print(f"player faction: {player_faction}")
        print(f"pf name: {player_faction['name']}")

        #print(f"enemy faction: {ai_faction}")
        print(f"enemy faction name: {ai_faction['name']}")


        # 1. Get the ID
        faction_id = ai_faction.get('id', player_faction['name'])
        #faction_id = {}

        #TODO: temp code to compile. Delete flavor and all fallbacks. Pull flavor from faction id.
        #flavor = FACTIONS.get(faction_id, {})
        flavor = {}

        # 3. Build the variable map with fallbacks
        # We use flavor.get() only if flavor is a dict
        def get_f(key, default):
            if isinstance(flavor, dict):
                return flavor.get(key, default)
            return default

        self.variables = {
            'NAME1': player_faction.get('leader_name', 'Commander'),
            'TITLE0': player_faction.get('title', 'Leader'),
            'NAME3': get_f('$NAME', 'The Leader'),
            'TITLE2': get_f('$TITLE', 'Leader'),
            'FACTION4': get_f('$FACTION', 'The Faction'),
            'FACTION3': get_f('$FACTIONNOUN', 'Citizens'),
            'CHARACTERADJ9': get_f('$CHARACTERADJ', 'strange'),
            'FACTIONPEJ5': get_f('$PEJORATIVE', 'Enemy'),
            'TO_CARRY_OUT_MY_MISSION6': get_f('$MISSION_STATEMENT', 'to survive'),
            'PET_PROJECTS6': get_f('$PET_PROJECTS', 'our goals'),
            'DANCINGNAKED3': get_f('$DANCING_NAKED_ACTION', 'plotting'),
            'BADHABITS5': get_f('$BAD_HABITS', 'stubbornness'),
            'FEE8': get_f('$FEE', 'payment'),
            'THOUGHT_POLICE4': get_f('$POLICE_NAME', 'security forces'),
            'THE_ENVIRONMENTAL_CODE9': get_f('$LAW_NAME', 'laws'),
        }

    def substitute(self, text, ai_gender_index=1):
        """
        text: The raw dialog string
        ai_gender_index: 1=Male, 2=Female (used for $<2:he:she> logic)
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

        # 2. Simple Variable Substitution ($NAME3, etc)
        for var, value in self.variables.items():
            result = result.replace(f'${var}', str(value))

        return result

    def get_dialog(self, dialog_id, player_faction, ai_faction):
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
            'text': self.substitute(text),
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
