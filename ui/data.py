"""UI data structures and constants."""

# SMAC Factions
FACTIONS = [
    {"name": "Gaians", "leader": "Lady Deirdre Skye", "full_name": "Lady Deirdre Skye (Gaians)", "color": (50, 205, 50), "short": "Gaians", "votes": 45},
    {"name": "The Hive", "leader": "Chairman Yang", "full_name": "Chairman Yang (The Hive)", "color": (100, 100, 255), "short": "Hive", "votes": 78},
    {"name": "University", "leader": "Provost Zakharov", "full_name": "Provost Zakharov (University)", "color": (255, 255, 255), "short": "University", "votes": 52},
    {"name": "Morganites", "leader": "CEO Morgan", "full_name": "CEO Morgan (Morganites)", "color": (255, 215, 0), "short": "Morganites", "votes": 34},
    {"name": "Spartans", "leader": "Colonel Santiago", "full_name": "Colonel Santiago (Spartans)", "color": (139, 69, 19), "short": "Spartans", "votes": 61},
    {"name": "Believers", "leader": "Sister Miriam", "full_name": "Sister Miriam (Believers)", "color": (255, 165, 0), "short": "Believers", "votes": 28},
    {"name": "Peacekeepers", "leader": "Commissioner Lal", "full_name": "Commissioner Lal (Peacekeepers)", "color": (180, 140, 230), "short": "Peacekeepers", "votes": 89}
]

# Council Proposals
PROPOSALS = [
    {"id": "GOVERNOR", "name": "Elect Planetary Governor", "type": "candidate", "cooldown": 0, "required_tech": None},  # Always available
    {"id": "SOLAR_SHADE", "name": "Launch Solar Shade", "desc": "(Sea levels drop)", "type": "yesno", "cooldown": 0, "required_tech": "orbital_spaceflight"},
    {"id": "ATROCITY", "name": "Remove Atrocity Prohibitions", "type": "yesno", "cooldown": 20, "last_voted": 1, "required_tech": "nerve_stapling"}
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
