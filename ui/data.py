"""UI data structures and constants."""

# SMAC Factions
FACTIONS = [
    {"name": "Lady Deirdre Skye (Gaians)", "color": (50, 205, 50), "short": "Gaians", "votes": 45},
    {"name": "Chairman Yang (The Hive)", "color": (100, 100, 255), "short": "Hive", "votes": 78},
    {"name": "Provost Zakharov (University)", "color": (255, 255, 255), "short": "University", "votes": 52},
    {"name": "CEO Morgan (Morganites)", "color": (255, 215, 0), "short": "Morganites", "votes": 34},
    {"name": "Colonel Santiago (Spartans)", "color": (139, 69, 19), "short": "Spartans", "votes": 61},
    {"name": "Sister Miriam (Believers)", "color": (255, 165, 0), "short": "Believers", "votes": 28},
    {"name": "Commissioner Lal (Peacekeepers)", "color": (180, 140, 230), "short": "Peacekeepers", "votes": 89}
]

# Council Proposals
PROPOSALS = [
    {"id": "GOVERNOR", "name": "Elect Planetary Governor", "type": "candidate", "cooldown": 0},
    {"id": "SOLAR_SHADE", "name": "Launch Solar Shade", "desc": "(Sea levels drop)", "type": "yesno", "cooldown": 0},
    {"id": "ATROCITY", "name": "Remove Atrocity Prohibitions", "type": "yesno", "cooldown": 20, "last_voted": 1}
]

# Diplomacy conversation trees
DIPLOMACY_GREETINGS = [
    "Greetings. Our sensors indicate you wish to communicate. State your business.",
    "Ah, another transmission. I trust this will be more productive than our last exchange.",
    "You have reached my private channel. Make this brief.",
    "Welcome. Perhaps today we can find common ground where before there was only static."
]

DIPLOMACY_RESPONSES = [
    {"text": "Request pact of friendship", "next": "pact_request"},
    {"text": "Discuss technology exchange", "next": "tech_discuss"},
    {"text": "Propose trade agreement", "next": "trade_discuss"},
    {"text": "End transmission", "next": "exit"}
]
