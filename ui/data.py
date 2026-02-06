"""UI data structures and constants."""

# SMAC Factions
# Each faction starts with one specific technology
# base_names: First name is always the HQ, rest are used randomly, then fallback to "Sector N"
FACTIONS = [
    {
        "name": "Gaians",
        "leader": "Lady Deirdre Skye",
        "full_name": "Lady Deirdre Skye (Gaians)",
        "color": (50, 205, 50),
        "short": "Gaians",
        "votes": 45,
        "starting_tech": "Ecology",
        "bonuses": {
            "PLANET": 1,
            "EFFIC": 2,
            "MORALE": -1,
            "POLICE": -1,
            "fungus_nutrients": 1,  # +1 nutrients in fungus squares
            "forbidden_economics": "FreeMarket"
        },
        "base_names": ["Gaia's Landing", "Gaia's High Garden", "Forest Primeval", "Children of Earth", "Vale of Winds", "Mindworm Pass", "Blackroot Palace", "Greenhouse Gate", "Razorbeak Wood", "Last Rose of Summer", "Lucky Autumn", "Dreams of Green", "The Pines", "Velvetgrass Point", "Song of Planet", "Nessus Shining", "Silverbird Park", "Fallow Time", "Autumn Grove", "The Flowers Preach", "Resplendent Oak", "Lily of the Valley", "Virgin Soil", "Garden of Paradise", "Thorny Vineyard", "Chiron Preserve", "Memory of Earth"],
        # Dialog personality
        "title": "Lady",
        "leader_name": "Deirdre",
        "gender": "female",
        "adjective": "Gaian",
        "pejorative_adj": "tree-crazy",
        "pet_projects": "environmental initiatives",
        "bad_habits": "tree-hugging sentimentality",
        "dancing_naked": "communing with Planet",
        "pact_name": "Pact of Sisterhood",
        "pact_of_bors": "Pact of Brotherhood or Sisterhood",
        "heshe": "she",
        "hisher": "her",
        "himher": "her"
    },
    {
        "name": "The Hive",
        "leader": "Chairman Yang",
        "full_name": "Chairman Yang (The Hive)",
        "color": (100, 100, 255),
        "short": "Hive",
        "votes": 78,
        "starting_tech": "DocLoy",
        "bonuses": {
            "GROWTH": 1,
            "INDUSTRY": 1,
            "ECONOMY": -2,
            "free_facility": "Perimeter Defense",  # Free at each base
            "forbidden_politics": "Democratic"
        },
        "base_names": ["The Hive", "Sheng-ji Yang Base", "Worker's Nest", "People's Teeming", "Great Clustering", "The Colony", "Industrial Crawling", "Manufacturing Warrens", "Discipline Tubes", "Laborer's Throng", "Unification Cavern", "Social Engineering Den", "The Labyrinth", "Paradise Swarming", "Communal Nexus", "Social Artery", "Factory Maze", "Unity Lair", "Society Grid", "Great Collective", "Proletarian Knot", "Socialism Tunnels", "The Drone Mound", "Plex Anthill", "Watcher's Eye", "Working Man Hold", "Huddling of the People", "Yang Mine", "Seat of Proper Thought", "The Leader's Horde", "Chairman's Burrow", "Labor Network", "Deep Passages", "Fellowship City", "People's Endeavor", "Fecundity Tower", "Hole of Aspiration"],
        # Dialog personality
        "title": "Chairman",
        "leader_name": "Yang",
        "gender": "male",
        "adjective": "Hive",
        "pejorative_adj": "drone",
        "pet_projects": "social engineering programs",
        "bad_habits": "authoritarian excess",
        "dancing_naked": "managing the teeming masses",
        "pact_name": "Pact of Brotherhood",
        "pact_of_bors": "Pact of Brotherhood or Sisterhood",
        "heshe": "he",
        "hisher": "his",
        "himher": "him"
    },
    {
        "name": "University",
        "leader": "Provost Zakharov",
        "full_name": "Provost Zakharov (University)",
        "color": (255, 255, 255),
        "short": "University",
        "votes": 52,
        "starting_tech": "InfNet",
        "bonuses": {
            "RESEARCH": 2,
            "PROBE": -2,
            "free_facility": "Network Node",  # Free at each base
            "extra_drone_per_4": True,  # Extra drone for every 4 citizens
            "forbidden_politics": "Fundamentalist"
        },
        "base_names": ["University Base", "Academy Park", "Lab Three", "Library of Planet", "Planetary Archives", "Razvitia-Progress Base", "Cosmograd", "Budushii Dvor", "Tsiolkovsky Institute", "Mendelev College", "Nauk Science Center", "Zarya-Sunrise", "Nadezjda-Hope", "Academgorodok", "Koppernigk Observatory", "Svobodny-Free Base", "Zvedny Gorodok", "Baikonur", "Climactic Research", "Monitoring Station", "Buran Prospect", "Mir Lab", "Relativity School", "Pavlov Biolab", "Lomonosov Park", "Korolev Center", "Gagarin Memorial", "New Arzamas", "Otkrietia-Discovery", "Zoloto-Gold", "Edinstvo-Unity"],
        # Dialog personality
        "title": "Provost",
        "leader_name": "Zakharov",
        "gender": "male",
        "adjective": "University",
        "pejorative_adj": "intellectual",
        "pet_projects": "scientific research",
        "bad_habits": "arrogant intellectualism",
        "dancing_naked": "pursuing pure knowledge",
        "pact_name": "Pact of Brotherhood",
        "pact_of_bors": "Pact of Brotherhood or Sisterhood",
        "heshe": "he",
        "hisher": "his",
        "himher": "him"
    },
    {
        "name": "Morganites",
        "leader": "CEO Morgan",
        "full_name": "CEO Morgan (Morganites)",
        "color": (255, 215, 0),
        "short": "Morganites",
        "votes": 34,
        "starting_tech": "Indust",
        "bonuses": {
            "ECONOMY": 1,
            "SUPPORT": -1,
            "commerce_bonus": True,  # Increases value of treaties, pacts, loans
            "starting_credits": 100,
            "hab_complex_limit": 4,  # Need HAB COMPLEX for bases > 4
            "forbidden_economics": "Planned"
        },
        "base_names": ["Morgan Industries", "Morgan Metagenics", "Morgan Bank", "Morgan Trade Center", "Morgan Biochemical", "Morgan Data Systems", "Morgan Hydroponics", "Morgan Mines", "Morgan Processing", "Morgan Solarfex", "Morgan Entertainment", "Morgan Distribution", "Morgan Pharmaceuticals", "Morgan Metallurgy", "Morgan Transport", "Morgan Antimatter", "Morgan Energy Monopoly", "Morgan Collections", "Morgan Construction", "Morgan Interstellar", "Morgan Aerodynamics", "Morgan Robotics", "Morgan Studios", "Morgan Gravitonics"],
        # Dialog personality
        "title": "CEO",
        "leader_name": "Morgan",
        "gender": "male",
        "adjective": "Morganite",
        "pejorative_adj": "profiteering",
        "pet_projects": "commercial ventures",
        "bad_habits": "shameless greed",
        "dancing_naked": "counting credits",
        "pact_name": "Pact of Brotherhood",
        "pact_of_bors": "Pact of Brotherhood or Sisterhood",
        "heshe": "he",
        "hisher": "his",
        "himher": "him"
    },
    {
        "name": "Spartans",
        "leader": "Colonel Santiago",
        "full_name": "Colonel Santiago (Spartans)",
        "color": (139, 69, 19),
        "short": "Spartans",
        "votes": 61,
        "starting_tech": "Mobile",
        "bonuses": {
            "MORALE": 2,
            "POLICE": 1,
            "INDUSTRY": -1,
            "forbidden_values": "Wealth"
        },
        "base_names": ["Sparta Command", "Survival Base", "Commander's Keep", "War Outpost", "Militia Station", "Fort Legion", "Janissary Rock", "Blast Rifle Crag", "Hawk of Chiron", "Assassin's Redoubt", "Centurion Cave", "Bunker 118", "Hommel's Citadel", "Training Camp", "Defiance Freehold", "Hero's Waypoint", "Fort Liberty", "Ironholm", "Fort Survivalist", "Fort Superiority", "Halls of Discipline", "Parade Ground"],
        # Dialog personality
        "title": "Colonel",
        "leader_name": "Santiago",
        "gender": "female",
        "adjective": "Spartan",
        "pejorative_adj": "militaristic",
        "pet_projects": "military readiness",
        "bad_habits": "warmongering",
        "dancing_naked": "drilling troops",
        "pact_name": "Pact of Sisterhood",
        "pact_of_bors": "Pact of Brotherhood or Sisterhood",
        "heshe": "she",
        "hisher": "her",
        "himher": "her"
    },
    {
        "name": "Believers",
        "leader": "Sister Miriam",
        "full_name": "Sister Miriam (Believers)",
        "color": (255, 165, 0),
        "short": "Believers",
        "votes": 28,
        "starting_tech": "Psych",
        "bonuses": {
            "PROBE": 1,
            "SUPPORT": 2,
            "RESEARCH": -2,
            "PLANET": -1,
            "attack_bonus": 25,  # +25% when attacking
            "forbidden_values": "Knowledge"
        },
        "base_names": ["New Jerusalem", "Great Conclave", "Great Zion", "Far Jericho", "Redemption Base", "Children of God", "Noah's Rainbow", "The Voice of God", "Judgement Seat", "Valley of the Faithful", "Blessed Redeemer", "The Glory of God", "New Eden", "Terrible Swift Sword", "Time of Salvation", "Eternal Reward", "The Lord's Mercy", "Righteous Sentence", "Throne of God", "The Rapture", "The Lord's Wrath", "The Lord's Grace", "The Hand of God", "The Coming of the Lord", "Sanctity Base", "The Lord's Chosen", "Hallowed Ground", "The Lord's Gift", "Divinity Base", "The Word of God", "Revelation Base", "The Holy Fire", "The Lord's Truth", "Blessed Saviour", "From On High", "Godwinson's Hope", "House of Martyrs"],
        # Dialog personality
        "title": "Sister",
        "leader_name": "Miriam",
        "gender": "female",
        "adjective": "Believer",
        "pejorative_adj": "fanatical",
        "pet_projects": "spiritual salvation",
        "bad_habits": "religious fanaticism",
        "dancing_naked": "preaching the Word",
        "pact_name": "Pact of Sisterhood",
        "pact_of_bors": "Pact of Brotherhood or Sisterhood",
        "heshe": "she",
        "hisher": "her",
        "himher": "her"
    },
    {
        "name": "Peacekeepers",
        "leader": "Commissioner Lal",
        "full_name": "Commissioner Lal (Peacekeepers)",
        "color": (180, 140, 230),
        "short": "Peacekeepers",
        "votes": 89,
        "starting_tech": "Biogen",
        "bonuses": {
            "EFFIC": -1,
            "extra_talent_per_4": True,  # Extra talent for every 4 citizens
            "hab_complex_bonus": 2,  # May exceed HAB COMPLEX by 2
            "double_votes": True,  # Double votes in elections
            "forbidden_politics": "Police State"
        },
        "base_names": ["U.N. Headquarters", "U.N. High Commission", "U.N. Temple of Sol", "U.N. Haven City", "U.N. Great Refuge", "U.N. Amnesty Town", "U.N. Pillar of Rights", "U.N. Humanity Base", "U.N. Aid Station", "U.N. Equality Village", "U.N. Settlement Agency", "U.N. Enforcement Base", "U.N. Health Authority", "U.N. Planning Authority", "U.N. Education Agency", "U.N. Social Council", "U.N. Commerce Committee", "U.N. Court of Justice", "U.N. Information Agency", "U.N. Planetary Trust", "U.N. Data Aquisition", "U.N. Disaster Relief", "U.N. Criminal Tribunal"],
        # Dialog personality
        "title": "Commissioner",
        "leader_name": "Lal",
        "gender": "male",
        "adjective": "Peacekeeper",
        "pejorative_adj": "bureaucratic",
        "pet_projects": "humanitarian efforts",
        "bad_habits": "idealistic naivety",
        "dancing_naked": "championing human rights",
        "pact_name": "Pact of Brotherhood",
        "pact_of_bors": "Pact of Brotherhood or Sisterhood",
        "heshe": "he",
        "hisher": "his",
        "himher": "him"
    }
]

# Council Proposals
PROPOSALS = [
    {"id": "GOVERNOR", "name": "Elect Planetary Governor", "type": "candidate", "cooldown": 0, "required_tech": None},  # Always available
    {"id": "UNITY_CORE", "name": "Salvage Unity Fusion Core", "desc": "(+500 energy credits to winner)", "type": "yesno", "cooldown": 0, "required_tech": None},
    {"id": "GLOBAL_TRADE", "name": "Global Trade Pact", "desc": "(+1 commerce in all bases)", "type": "yesno", "cooldown": 20, "required_tech": "planetary_economics"},
    {"id": "SOLAR_SHADE", "name": "Launch Solar Shade", "desc": "(Sea levels drop)", "type": "yesno", "cooldown": 30, "required_tech": "orbital_spaceflight"},
    {"id": "MELT_CAPS", "name": "Melt Polar Caps", "desc": "(Sea levels rise)", "type": "yesno", "cooldown": 30, "required_tech": "advanced_ecological_engineering"},
    {"id": "ATROCITY", "name": "Remove Atrocity Prohibitions", "type": "yesno", "cooldown": 20, "last_voted": 1, "required_tech": "nerve_stapling"}
]

# Social Engineering Effects
# Format: [("STAT_NAME", value), ...] where value can be 1-5 for positive, -1 to -5 for negative
# Based on SMAC notation: +++++ = 5, +++ = 3, ++ = 2, + = 1, and their negatives
SE_EFFECTS = {
    "Politics": {
        "Frontier": [],  # No effects
        "Police State": [("POLICE", 2), ("SUPPORT", 2), ("EFFIC", -2)],
        "Democratic": [("EFFIC", 2), ("GROWTH", 2), ("SUPPORT", -2)],
        "Fundamentalist": [("MORALE", 1), ("PROBE", 2), ("RESEARCH", -2)]
    },
    "Economics": {
        "Simple": [],  # No effects
        "Free Market": [("ECONOMY", 2), ("PLANET", -3), ("POLICE", -5)],
        "Planned": [("GROWTH", 2), ("INDUSTRY", 1), ("EFFIC", -2)],
        "Green": [("PLANET", 2), ("EFFIC", 2), ("GROWTH", -2)]
    },
    "Values": {
        "Survival": [],  # No effects
        "Power": [("MORALE", 2), ("SUPPORT", 2), ("INDUSTRY", -2)],
        "Knowledge": [("RESEARCH", 2), ("EFFIC", 1), ("PROBE", -2)],
        "Wealth": [("INDUSTRY", 1), ("ECONOMY", 1), ("MORALE", -2)]
    },
    "Future Society": {
        "None": [],  # No effects
        "Cybernetic": [("EFFIC", 2), ("PLANET", 2), ("RESEARCH", 2), ("POLICE", -3)],
        "Eudaimonic": [("GROWTH", 2), ("ECONOMY", 2), ("INDUSTRY", 2), ("MORALE", -2)],
        "Thought Control": [("POLICE", 2), ("MORALE", 2), ("PROBE", 2), ("SUPPORT", -3)]
    }
}
