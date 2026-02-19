"""Citizen specialist data.

Specialists are citizens who don't work tiles but provide fixed bonuses.
prereq: tech ID required to unlock (None = always available).
No nutrient cost — the cost is the foregone tile output.
"""

SPECIALISTS = [
    {'id': 'doctor',     'name': 'Doctor',     'prereq': None,      'min_pop': 1, 'economy': 0, 'labs': 0, 'psych': 2},
    {'id': 'technician', 'name': 'Technician', 'prereq': None,      'min_pop': 5, 'economy': 3, 'labs': 0, 'psych': 0},
    {'id': 'librarian',  'name': 'Librarian',  'prereq': 'PlaNets', 'min_pop': 5, 'economy': 0, 'labs': 3, 'psych': 0},
    {'id': 'empath',     'name': 'Empath',     'prereq': 'CentMed', 'min_pop': 1, 'economy': 2, 'labs': 0, 'psych': 2},
    {'id': 'engineer',   'name': 'Engineer',   'prereq': 'Fusion',  'min_pop': 5, 'economy': 3, 'labs': 2, 'psych': 0},
    {'id': 'thinker',    'name': 'Thinker',    'prereq': 'MindMac', 'min_pop': 5, 'economy': 0, 'labs': 3, 'psych': 1},
    {'id': 'transcend',  'name': 'Transcend',  'prereq': 'AlphCen', 'min_pop': 1, 'economy': 2, 'labs': 4, 'psych': 2},
]
