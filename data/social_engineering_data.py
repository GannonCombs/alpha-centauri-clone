
# Social Engineering choices with tech prerequisites and effects
# Format: {name, prereq, bonuses}
# Bonuses use format: ++STAT = +2, +STAT = +1, --STAT = -2, ---STAT = -3, etc.

POLITICS_CHOICES = [
    {'name': 'Frontier', 'prereq': None, 'effects': {}},
    {'name': 'Police State', 'prereq': 'DocLoy', 'effects': {'POLICE': 2, 'SUPPORT': 2, 'EFFIC': -2}},
    {'name': 'Democratic', 'prereq': 'EthCalc', 'effects': {'EFFIC': 2, 'GROWTH': 2, 'SUPPORT': -2}},
    {'name': 'Fundamentalist', 'prereq': 'Brain', 'effects': {'MORALE': 1, 'PROBE': 2, 'RESEARCH': -2}},
]

ECONOMICS_CHOICES = [
    {'name': 'Simple', 'prereq': None, 'effects': {}},
    {'name': 'Free Market', 'prereq': 'IndEcon', 'effects': {'ECONOMY': 2, 'PLANET': -3, 'POLICE': -5}},
    {'name': 'Planned', 'prereq': 'PlaNets', 'effects': {'GROWTH': 2, 'INDUSTRY': 1, 'EFFIC': -2}},
    {'name': 'Green', 'prereq': 'CentEmp', 'effects': {'PLANET': 2, 'EFFIC': 2, 'GROWTH': -2}},
]

VALUES_CHOICES = [
    {'name': 'Survival', 'prereq': None, 'effects': {}},
    {'name': 'Power', 'prereq': 'MilAlg', 'effects': {'MORALE': 2, 'SUPPORT': 2, 'INDUSTRY': -2}},
    {'name': 'Knowledge', 'prereq': 'Cyber', 'effects': {'RESEARCH': 2, 'EFFIC': 1, 'PROBE': -2}},
    {'name': 'Wealth', 'prereq': 'IndAuto', 'effects': {'INDUSTRY': 1, 'ECONOMY': 1, 'MORALE': -2}},
]

FUTURE_CHOICES = [
    {'name': 'None', 'prereq': None, 'effects': {}},
    {'name': 'Cybernetic', 'prereq': 'DigSent', 'effects': {'EFFIC': 2, 'PLANET': 2, 'RESEARCH': 2, 'POLICE': -3}},
    {'name': 'Eudaimonic', 'prereq': 'Eudaim', 'effects': {'GROWTH': 2, 'ECONOMY': 2, 'INDUSTRY': 2, 'MORALE': -2}},
    {'name': 'Thought Control', 'prereq': 'WillPow', 'effects': {'POLICE': 2, 'MORALE': 2, 'PROBE': 2, 'SUPPORT': -3}},
]

