"""UI data structures and display."""

# SMAC Faction Static Data
# Each faction starts with one specific technology
# base_names: First name is always the HQ, rest are used randomly, then fallback to "Sector N"
FACTION_DATA = [
    {
        "id": 0,
        "name": "Gaians",
        "leader": "Lady Deirdre Skye",
        "gender": "F",
        "full_name": "Lady Deirdre Skye (Gaians)",
        "color": (50, 205, 50),
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
        # --- IDENTITY & NAMING ---
        '$FACTION': "Gaia's Stepdaughters",
        '$FACTIONNOUN': "Gaians",  # Used for plural reference
        '$NAME': "Deirdre",  # Short name
        '$FULLNAME': "Deirdre Skye",  # Inferred from Blurb/Datalinks
        '$TITLE': "Lady",  # $TITLE2

        # --- ADJECTIVES ---
        '$CHARACTERADJ': "beautiful",  # $CHARACTERADJ9
        '$FACTIONADJ': "Gaian",  # Used for "Gaian territory"
        '$PEJORATIVE': "Nature Loony",  # $PEJORATIVE5 / $NATURE_LOONY2

        # --- FLAVOR TEXT / VARIABLES ---
        # These map to specific placeholders in the dialog tree

        # $PET_PROJECTS / $PET_PROJECTS6
        '$PET_PROJECTS': "preserve Planet's native life",

        # $TO_CARRY_OUT_MY_MISSION6 (Statement of intent)
        '$MISSION_STATEMENT': "to guard, understand, and preserve Planet's native life",

        # $IMPLEMENTING_YOUR_EVIL_AGENDA5 (How enemies describe them)
        '$EVIL_AGENDA': "stamping out all legitimate sentient development of this planet",

        # $DANCING_NAKED_THROUGH_THE_TREES8 (Specific insult for this faction)
        '$DANCING_NAKED_ACTION': "dancing naked through the trees",

        # $SPOUTING_TREE_CRAZY_PRATTLE9 (Specific insult regarding speech)
        '$CRAZY_PRATTLE_ACTION': "spouting tree-crazy prattle",

        # $BAD_HABITS2 (Noun phrase for annoying behavior)
        '$BAD_HABITS': "tree-crazy prattle",

        # $ENVIRONMENTAL_INITIATIVES5 (Positive work description)
        '$GOOD_WORK': "environmental initiatives",

        # $BIZARRE_PRACTICES5 (Negative ritual description)
        '$BIZARRE_PRACTICES': "pagan rituals",

        # $FEE8 (What they call a bribe/demand)
        '$FEE': "ecology tax",

        # $PROVIDING_VALUABLE_SERVICES9 (Justification for the bribe)
        '$SERVICE_DESC': "preserving and cataloguing Planet's native life",

        # $THOUGHT_POLICE4 (Their enforcement agency)
        '$POLICE_NAME': "Environmental Police",

        # $THE_ENVIRONMENTAL_CODE9 (Their laws)
        '$LAW_NAME': "Planetary Ecology Code",

        # --- DIALOGUE OVERRIDES ---
        # These replace specific keys in the main dialogue tree for this faction

        '#FACTIONTRUCE': {
            'caption': '$CAPTION7',
            'text': '"This senseless destruction will surely cause irreparable harm to Planet\'s ecology. I urge we mend our differences and pledge Blood Truce."',
            'responses': [
                {'text': '"It is as you say. This violence must end."', 'action': 'diplo'},
                {'text': '"Hah! Your rocks and plants won\'t save you now, $NAME3!"', 'action': 'diplo'}
            ]
        },

        '#FACTIONTREATY': {
            'caption': '$CAPTION7',
            'text': '"I sense you are a friend of Planet, $TITLE0 $NAME1. I suggest we sign a Treaty of Friendship, that our peoples may live side by side in peace."',
            'responses': [
                {'text': '"Agreed. Walk with Planet, $NAME3."', 'action': 'diplo'},
                {'text': '"No. This \'Friend of Planet\' stuff gives me the creeps."', 'action': 'diplo'}
            ]
        },
    },
    {
        "id": 1,
        "name": "The Hive",
        "leader": "Chairman Yang",
        "gender": "M",
        "full_name": "Chairman Yang (The Hive)",
        "color": (100, 100, 255),
        "starting_tech": "DocLoy",
        "bonuses": {
            "GROWTH": 1,
            "INDUSTRY": 1,
            "ECONOMY": -2,
            "free_facility": "Perimeter Defense",  # Free at each base
            "forbidden_politics": "Democratic"
        },
        "base_names": ["The Hive", "Sheng-ji Yang Base", "Worker's Nest", "People's Teeming", "Great Clustering", "The Colony", "Industrial Crawling", "Manufacturing Warrens", "Discipline Tubes", "Laborer's Throng", "Unification Cavern", "Social Engineering Den", "The Labyrinth", "Paradise Swarming", "Communal Nexus", "Social Artery", "Factory Maze", "Unity Lair", "Society Grid", "Great Collective", "Proletarian Knot", "Socialism Tunnels", "The Drone Mound", "Plex Anthill", "Watcher's Eye", "Working Man Hold", "Huddling of the People", "Yang Mine", "Seat of Proper Thought", "The Leader's Horde", "Chairman's Burrow", "Labor Network", "Deep Passages", "Fellowship City", "People's Endeavor", "Fecundity Tower", "Hole of Aspiration"],
        # --- IDENTITY & NAMING ---
        '$FACTION': "Human Hive",
        '$FACTIONNOUN': "Hive",  # Used for plural reference
        '$NAME': "Yang",  # Short name
        '$FULLNAME': "Sheng-Ji Yang",  # From Blurb/Datalinks
        '$TITLE': "Chairman",  # $TITLE2

        # --- ADJECTIVES ---
        '$CHARACTERADJ': "ruthless",  # $CHARACTERADJ9
        '$FACTIONADJ': "Hive",  # Used for "Hive territory"
        '$PEJORATIVE': "Inhuman Monster",  # $PEJORATIVE5

        # --- FLAVOR TEXT / VARIABLES ---
        # $PET_PROJECTS / $PET_PROJECTS6
        '$PET_PROJECTS': "properly control our followers",

        # $TO_CARRY_OUT_MY_MISSION6 (Statement of intent)
        '$MISSION_STATEMENT': "to found a society on the principles of security and control",

        # $IMPLEMENTING_YOUR_EVIL_AGENDA5 (How enemies describe them)
        '$EVIL_AGENDA': "reducing us all to mindless servants of your diabolical schemes",

        # $DANCING_NAKED_THROUGH_THE_TREES8 (Specific insult for this faction)
        # Context: "I see you're very busy [ACTION]"
        '$DANCING_NAKED_ACTION': "torturing the wretched fools who chose to follow you",

        # $SPOUTING_TREE_CRAZY_PRATTLE9 (Specific insult regarding speech)
        # Context: "accused of [ACTION]"
        '$CRAZY_PRATTLE_ACTION': "preaching brutal nihilism",

        # $BAD_HABITS2 (Noun phrase for annoying behavior)
        '$BAD_HABITS': "brutal nihilism",

        # $ENVIRONMENTAL_INITIATIVES5 (Positive work description)
        '$GOOD_WORK': "social experiments",

        # $BIZARRE_PRACTICES5 (Negative ritual description)
        '$BIZARRE_PRACTICES': "mind control experiments",

        # $FEE8 (What they call a bribe/demand)
        '$FEE': "fee",

        # $PROVIDING_VALUABLE_SERVICES9 (Justification for the bribe)
        '$SERVICE_DESC': "keeping an eye on the workers",

        # $THOUGHT_POLICE4 (Their enforcement agency)
        '$POLICE_NAME': "Hive Security",

        # $THE_ENVIRONMENTAL_CODE9 (Their laws)
        '$LAW_NAME': "Hive Law",

        # --- DIALOGUE OVERRIDES ---
        '#FACTIONTRUCE': {
            'caption': '$CAPTION7',
            'text': '"As I see no need for this Vendetta to continue, $NAME1, a pledge of Blood Truce would seem in order."',
            'responses': [
                {'text': '"Indeed. Blood Truce would be most satisfactory."', 'action': 'diplo'},
                {'text': '"Never! I plan to put an end to your scheming once and for all!"', 'action': 'diplo'}
            ]
        },

        '#FACTIONTREATY': {
            'caption': '$CAPTION7',
            'text': '"$TITLE0 $NAME1, your ideals are admirable if a bit misguided and your faction need not pose a threat to Hive policy. Shall we sign a Treaty of Friendship to formalize our symbiotic relationship?"',
            'responses': [
                {'text': '"As you wish. The Hive seems a valuable friend."', 'action': 'diplo'},
                {'text': '"No. Your social experiments are a bit too bizarre for me, $NAME3."', 'action': 'diplo'}
            ]
        },
    },
    {
        "id": 2,
        "name": "University",
        "leader": "Provost Zakharov",
        "gender": "M",
        "full_name": "Provost Zakharov (University)",
        "color": (255, 255, 255),
        "starting_tech": "InfNet",
        "bonuses": {
            "RESEARCH": 2,
            "PROBE": -2,
            "free_facility": "Network Node",  # Free at each base
            "extra_drone_per_4": True,  # Extra drone for every 4 citizens
            "forbidden_politics": "Fundamentalist"
        },
        "base_names": ["University Base", "Academy Park", "Lab Three", "Library of Planet", "Planetary Archives", "Razvitia-Progress Base", "Cosmograd", "Budushii Dvor", "Tsiolkovsky Institute", "Mendelev College", "Nauk Science Center", "Zarya-Sunrise", "Nadezjda-Hope", "Academgorodok", "Koppernigk Observatory", "Svobodny-Free Base", "Zvedny Gorodok", "Baikonur", "Climactic Research", "Monitoring Station", "Buran Prospect", "Mir Lab", "Relativity School", "Pavlov Biolab", "Lomonosov Park", "Korolev Center", "Gagarin Memorial", "New Arzamas", "Otkrietia-Discovery", "Zoloto-Gold", "Edinstvo-Unity"],
        # --- IDENTITY & NAMING ---
        '$FACTION': "University of Planet",
        '$FACTIONNOUN': "University",  # Used for plural reference
        '$NAME': "Zakharov",  # Short name
        '$FULLNAME': "Prokhor Zakharov",  # From Blurb/Datalinks
        '$TITLE': "Provost",  # $TITLE2

        # --- ADJECTIVES ---
        '$CHARACTERADJ': "brilliant",  # $CHARACTERADJ9
        '$FACTIONADJ': "University",  # Used for "University territory"
        '$PEJORATIVE': "Madman",  # $PEJORATIVE5

        # --- FLAVOR TEXT / VARIABLES ---
        # These map to specific placeholders in the dialog tree

        # $PET_PROJECTS / $PET_PROJECTS6
        '$PET_PROJECTS': "pursue unfettered research",

        # $TO_CARRY_OUT_MY_MISSION6 (Statement of intent)
        '$MISSION_STATEMENT': "to pursue pure research unfettered by outside motives and meddling",

        # $IMPLEMENTING_YOUR_EVIL_AGENDA5 (How enemies describe them)
        '$EVIL_AGENDA': "conducting all manner of unethical, immoral, and evil research",

        # $DANCING_NAKED_THROUGH_THE_TREES8 (Specific insult for this faction)
        # Context: "I see you're very busy [ACTION]"
        '$DANCING_NAKED_ACTION': "conduct your unspeakable experiments",

        # $SPOUTING_TREE_CRAZY_PRATTLE9 (Specific insult regarding speech)
        # Context: "accused of [ACTION]"
        '$CRAZY_PRATTLE_ACTION': "dreaming up new ways to exterminate our species",

        # $BAD_HABITS2 (Noun phrase for annoying behavior)
        '$BAD_HABITS': "dreaming up new ways to exterminate our species",

        # $ENVIRONMENTAL_INITIATIVES5 (Positive work description)
        '$GOOD_WORK': "conducting unethical research",

        # $BIZARRE_PRACTICES5 (Negative ritual description)
        '$BIZARRE_PRACTICES': "unethical methods",

        # $FEE8 (What they call a bribe/demand)
        '$FEE': "research grant",

        # $PROVIDING_VALUABLE_SERVICES9 (Justification for the bribe)
        '$SERVICE_DESC': "pushing the boundaries of science",

        # $THOUGHT_POLICE4 (Their enforcement agency)
        '$POLICE_NAME': "University Enforcement",

        # $THE_ENVIRONMENTAL_CODE9 (Their laws)
        '$LAW_NAME': "University Policy",

        # --- DIALOGUE OVERRIDES ---
        '#FACTIONTRUCE': {
            'caption': '$CAPTION7',
            'text': '"Call off your dogs, $NAME1. I am ready to pledge Blood Truce if you will leave me to my research."',
            'responses': [
                {'text': '"Very well, but do not provoke me further."', 'action': 'diplo'},
                {'text': '"Too bad, $NAME3. Your fate is already sealed."', 'action': 'diplo'}
            ]
        },

        '#FACTIONTREATY': {
            'caption': '$CAPTION7',
            'text': '"We are peaceful researchers, $TITLE0 $NAME1. Will you sign a Treaty of Friendship and leave us to study in peace?"',
            'responses': [
                {'text': '"Of course. We must certainly strive to increase our knowledge."', 'action': 'diplo'},
                {'text': '"No. I don\'t trust your unethical approach to research, $NAME3."', 'action': 'diplo'}
            ]
        },
    },
    {
        "id": 3,
        "name": "Morganites",
        "leader": "CEO Morgan",
        "gender": "M",
        "full_name": "CEO Morgan (Morganites)",
        "color": (255, 215, 0),
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
        # --- IDENTITY & NAMING ---
        '$FACTION': "Morgan Industries",
        '$FACTIONNOUN': "Morganites",  # Used for plural reference
        '$NAME': "Morgan",  # Short name
        '$FULLNAME': "Nwabudike Morgan",  # From Blurb/Datalinks
        '$TITLE': "CEO",  # $TITLE2

        # --- ADJECTIVES ---
        '$CHARACTERADJ': "shrewd",  # $CHARACTERADJ9
        '$FACTIONADJ': "Morganic",  # Used for "Morganic territory"
        '$PEJORATIVE': "Filthy Money Grubber",  # $PEJORATIVE5

        # --- FLAVOR TEXT / VARIABLES ---
        # These map to specific placeholders in the dialog tree

        # $PET_PROJECTS / $PET_PROJECTS6
        '$PET_PROJECTS': "dominate Planet's economy",

        # $TO_CARRY_OUT_MY_MISSION6 (Statement of intent)
        '$MISSION_STATEMENT': "to reap the rightful rewards of skillful investment and planning",

        # $IMPLEMENTING_YOUR_EVIL_AGENDA5 (How enemies describe them)
        '$EVIL_AGENDA': "achieving total monopolistic control of all of Planet's resources",

        # $DANCING_NAKED_THROUGH_THE_TREES8 (Specific insult for this faction)
        # Context: "I see you're very busy [ACTION]"
        '$DANCING_NAKED_ACTION': "counting your ill-gotten energy tokens",

        # $SPOUTING_TREE_CRAZY_PRATTLE9 (Specific insult regarding speech)
        # Context: "accused of [ACTION]"
        '$CRAZY_PRATTLE_ACTION': "monopolistic grasping",

        # $BAD_HABITS2 (Noun phrase for annoying behavior)
        '$BAD_HABITS': "monopolistic grasping",

        # $ENVIRONMENTAL_INITIATIVES5 (Positive work description)
        '$GOOD_WORK': "business plans",

        # $BIZARRE_PRACTICES5 (Negative ritual description)
        '$BIZARRE_PRACTICES': "corporate empire-building",

        # $FEE8 (What they call a bribe/demand)
        '$FEE': "investment",

        # $PROVIDING_VALUABLE_SERVICES9 (Justification for the bribe)
        '$SERVICE_DESC': "exploiting Planet's natural wealth",

        # $THOUGHT_POLICE4 (Their enforcement agency)
        '$POLICE_NAME': "Corporate Security",

        # $THE_ENVIRONMENTAL_CODE9 (Their laws)
        '$LAW_NAME': "Morgan Corporate Policy",

        # --- DIALOGUE OVERRIDES ---
        '#FACTIONTRUCE': {
            'caption': '$CAPTION7',
            'text': '"Vendetta is bad for business, $NAME1. I suggest we pledge Blood Truce and get back to work."',
            'responses': [
                {'text': '"Fair enough. I shall order hostilities to cease."', 'action': 'diplo'},
                {'text': '"Sorry, $NAME3, but I plan to put you out of business."', 'action': 'diplo'}
            ]
        },

        '#FACTIONTREATY': {
            'caption': '$CAPTION7',
            'text': '"Friend $NAME1, I can offer lucrative trading arrangements if you will agree to a Treaty of Friendship. Shall we become business partners?"',
            'responses': [
                {'text': '"By all means. Let us prosper together in peace."', 'action': 'diplo'},
                {'text': '"No. All of the profit would find its way into your pocket."', 'action': 'diplo'}
            ]
        },
    },
    {
        "id": 4,
        "name": "Spartans",
        "leader": "Colonel Santiago",
        "gender": "F",
        "full_name": "Colonel Santiago (Spartans)",
        "color": (139, 69, 19),
        "starting_tech": "Mobile",
        "bonuses": {
            "MORALE": 2,
            "POLICE": 1,
            "INDUSTRY": -1,
            "forbidden_values": "Wealth"
        },
        "base_names": ["Sparta Command", "Survival Base", "Commander's Keep", "War Outpost", "Militia Station", "Fort Legion", "Janissary Rock", "Blast Rifle Crag", "Hawk of Chiron", "Assassin's Redoubt", "Centurion Cave", "Bunker 118", "Hommel's Citadel", "Training Camp", "Defiance Freehold", "Hero's Waypoint", "Fort Liberty", "Ironholm", "Fort Survivalist", "Fort Superiority", "Halls of Discipline", "Parade Ground"],
        # --- IDENTITY & NAMING ---
        '$FACTION': "Spartan Federation",
        '$FACTIONNOUN': "Spartans",  # Used for plural reference
        '$NAME': "Santiago",  # Short name
        '$FULLNAME': "Corazon Santiago",  # From Blurb/Datalinks
        '$TITLE': "Colonel",  # $TITLE2

        # --- ADJECTIVES ---
        '$CHARACTERADJ': "vigilant",  # $CHARACTERADJ9
        '$FACTIONADJ': "Spartan",  # Used for "Spartan territory"
        '$PEJORATIVE': "Right-Wing Lunatic",  # $PEJORATIVE5

        # --- FLAVOR TEXT / VARIABLES ---
        # These map to specific placeholders in the dialog tree

        # $PET_PROJECTS / $PET_PROJECTS6
        '$PET_PROJECTS': "exercise our rights to keep and bear arms",

        # $TO_CARRY_OUT_MY_MISSION6 (Statement of intent)
        '$MISSION_STATEMENT': "to exercise freely the God-given right to keep and bear arms",

        # $IMPLEMENTING_YOUR_EVIL_AGENDA5 (How enemies describe them)
        '$EVIL_AGENDA': "equipping your private army to seize control of Planet",

        # $DANCING_NAKED_THROUGH_THE_TREES8 (Specific insult for this faction)
        # Context: "I see you're very busy [ACTION]"
        '$DANCING_NAKED_ACTION': "polishing your beloved artillery pieces",

        # $SPOUTING_TREE_CRAZY_PRATTLE9 (Specific insult regarding speech)
        # Context: "accused of [ACTION]"
        '$CRAZY_PRATTLE_ACTION': "having paranoid delusions",

        # $BAD_HABITS2 (Noun phrase for annoying behavior)
        '$BAD_HABITS': "paranoid delusions",

        # $ENVIRONMENTAL_INITIATIVES5 (Positive work description)
        '$GOOD_WORK': "military preparations",

        # $BIZARRE_PRACTICES5 (Negative ritual description)
        '$BIZARRE_PRACTICES': "right-wing fantasies",

        # $FEE8 (What they call a bribe/demand)
        '$FEE': "stipend",

        # $PROVIDING_VALUABLE_SERVICES9 (Justification for the bribe)
        '$SERVICE_DESC': "keeping the peace",

        # $THOUGHT_POLICE4 (Their enforcement agency)
        '$POLICE_NAME': "the Spartan Paramilitary Legion",

        # $THE_ENVIRONMENTAL_CODE9 (Their laws)
        '$LAW_NAME': "the Spartan Military Code",

        # --- DIALOGUE OVERRIDES ---
        '#FACTIONTRUCE': {
            'caption': '$CAPTION7',
            'text': '"You cannot hope to stand against me, $NAME1. Pledge Blood Truce now or face total destruction."',
            'responses': [
                {'text': '"Truce it is, then. I thank you."', 'action': 'diplo'},
                {'text': '"Bluffing will get you nowhere, $NAME3. Prepare to be obliterated!"', 'action': 'diplo'}
            ]
        },

        '#FACTIONTREATY': {
            'caption': '$CAPTION7',
            'text': '"$TITLE0 $NAME1. My survivalist followers are content to guard their homes in armed peace. I suggest we sign a Treaty of Friendship and stay out of each others\' way."',
            'responses': [
                {'text': '"Fair enough, but I shall guard my borders carefully."', 'action': 'diplo'},
                {'text': '"Hardly. A faction armed to the teeth hardly seems friendly to me."', 'action': 'diplo'}
            ]
        },
    },
    {
        "id": 5,
        "name": "Believers",
        "leader": "Sister Miriam",
        "gender": "F",
        "full_name": "Sister Miriam (Believers)",
        "color": (255, 165, 0),
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
        # --- IDENTITY & TITLES ---
        '$FACTION': "The Lord's Believers",
        '$NAME': "Miriam",  # Short name
        '$TITLE': "Sister",  # The leader's specific title
        '$SPECIAL5': "The Fundamentalist",  # From the first line of stats

        # --- ADJECTIVES & PEJORATIVES ---
        '$FACTIONADJ0': "Believing",  # Faction adjective (territory, etc.)
        '$FACTIONADJ1': "Believing",
        '$CHARACTERADJ9': "pious",  # Character trait for introductions
        '$PEJORATIVE5': "Religious Freak",  # Used by enemies in reports

        # --- ACTION STRINGS & DIALOGUE FILLERS ---
        # $TO_CARRY_OUT_MY_MISSION6 / $TO_CARRY_OUT_OUR_MISSION6
        '$TO_CARRY_OUT_MY_MISSION6': "to embrace the truth of the good Lord's Scripture",

        # $PET_PROJECTS6
        '$PET_PROJECTS6': "embrace the truth of the Lord's Scripture",

        # $DANCINGNAKED3 (The 3rd person variant is used in #REPORTWINNING)
        '$DANCINGNAKED3': "pounding her cherished bible",

        # $BADHABITS5
        '$BADHABITS5': "bible thumping extremism",

        # $ENVIRONMENTAL_INITIATIVES5 (The 'positive' version of their work)
        '$ENVIRONMENTAL_INITIATIVES5': "life of worship",

        # $BIZARRE_PRACTICES5 (The 'negative' version of their work)
        '$BIZARRE_PRACTICES5': "bizarre religious practices",

        # $FEE8
        '$FEE8': "tithe",

        # $PROVIDING_VALUABLE_SERVICES9
        '$PROVIDING_VALUABLE_SERVICES9': "upholding standards of decency and morality",

        # $THOUGHT_POLICE4
        '$THOUGHT_POLICE4': "my Angels of Justice",

        # $THE_ENVIRONMENTAL_CODE9
        '$THE_ENVIRONMENTAL_CODE9': "Conclave Oral Law",

        # --- UNIQUE FACTION OVERRIDES ---
        # These hard-coded blocks replace generic dialogue tree sections

        '#FACTIONTRUCE': {
            'caption': '$CAPTION7',
            'text': '"$NAME1, it is the Lord\'s Will that we end this immoral conflict. Pledge Blood Truce with me and I shall pray for your soul\'s redemption."',
            'responses': [
                {'text': '"As you wish. Truce pledged."', 'action': 'diplo'},
                {'text': '"I\'ll see you in hell first, $NAME3."', 'action': 'diplo'}
            ]
        },

        '#FACTIONTREATY': {
            'caption': '$CAPTION7',
            'text': '"I have been praying for you lately, $TITLE0 $NAME1. The Lord wishes us to live side by side as brothers and sisters; we must sign a Treaty of Friendship and worship together in peace."',
            'responses': [
                {'text': '"Amen, $NAME3. Lasting peace is a great gift indeed."', 'action': 'diplo'},
                {'text': '"No. Your fanaticism makes me shiver, $NAME3."', 'action': 'diplo'}
            ]
        },
    },
    {
        "id": 6,
        "name": "Peacekeepers",
        "leader": "Commissioner Lal",
        "gender": "M",
        "full_name": "Commissioner Lal (Peacekeepers)",
        "color": (180, 140, 230),
        "starting_tech": "Biogen",
        "bonuses": {
            "EFFIC": -1,
            "extra_talent_per_4": True,  # Extra talent for every 4 citizens
            "hab_complex_bonus": 2,  # May exceed HAB COMPLEX by 2
            "double_votes": True,  # Double votes in elections
            "forbidden_politics": "Police State"
        },
        "base_names": ["U.N. Headquarters", "U.N. High Commission", "U.N. Temple of Sol", "U.N. Haven City", "U.N. Great Refuge", "U.N. Amnesty Town", "U.N. Pillar of Rights", "U.N. Humanity Base", "U.N. Aid Station", "U.N. Equality Village", "U.N. Settlement Agency", "U.N. Enforcement Base", "U.N. Health Authority", "U.N. Planning Authority", "U.N. Education Agency", "U.N. Social Council", "U.N. Commerce Committee", "U.N. Court of Justice", "U.N. Information Agency", "U.N. Planetary Trust", "U.N. Data Aquisition", "U.N. Disaster Relief", "U.N. Criminal Tribunal"],
        # --- IDENTITY & NAMING ---
        '$FACTION': "Peacekeeping Forces",
        '$FACTIONNOUN': "Peacekeepers",     # Used for plural reference
        '$NAME': "Lal",                     # Short name
        '$FULLNAME': "Pravin Lal",          # From Blurb/Datalinks
        '$TITLE': "Brother",                # $TITLE2 (as per the #PEACE block)

        # --- ADJECTIVES ---
        '$CHARACTERADJ': "humane",          # $CHARACTERADJ9
        '$FACTIONADJ': "Peace",             # Used for "Peace territory"
        '$PEJORATIVE': "Pusillanimous Wimp", # $PEJORATIVE5

        # --- FLAVOR TEXT / VARIABLES ---
        # These map to specific placeholders in the dialog tree

        # $PET_PROJECTS / $PET_PROJECTS6
        '$PET_PROJECTS': "defend the principles of our U.N. Charter",

        # $TO_CARRY_OUT_MY_MISSION6 (Statement of intent)
        '$MISSION_STATEMENT': "to defend the humanitarian principles of our original U.N. Charter",

        # $IMPLEMENTING_YOUR_EVIL_AGENDA5 (How enemies describe them)
        '$EVIL_AGENDA': "setting yourself up as the only 'legitimate' authority on Planet",

        # $DANCING_NAKED_THROUGH_THE_TREES8 (Specific insult for this faction)
        # Context: "I see you're very busy [ACTION]"
        '$DANCING_NAKED_ACTION': "kissing up to your precious U.N. Charter",

        # $SPOUTING_TREE_CRAZY_PRATTLE9 (Specific insult regarding speech)
        # Context: "accused of [ACTION]"
        '$CRAZY_PRATTLE_ACTION': "humanitarian whimpering",

        # $BAD_HABITS2 (Noun phrase for annoying behavior)
        '$BAD_HABITS': "humanitarian whimpering",

        # $ENVIRONMENTAL_INITIATIVES5 (Positive work description)
        '$GOOD_WORK': "humanitarian initiatives",

        # $BIZARRE_PRACTICES5 (Negative ritual description)
        '$BIZARRE_PRACTICES': "whimpering social programs",

        # $FEE8 (What they call a bribe/demand)
        '$FEE': "contribution",

        # $PROVIDING_VALUABLE_SERVICES9 (Justification for the bribe)
        '$SERVICE_DESC': "providing a legitimate government for this Planet",

        # $THOUGHT_POLICE4 (Their enforcement agency)
        '$POLICE_NAME': "Peacekeeping Forces",

        # $THE_ENVIRONMENTAL_CODE9 (Their laws)
        '$LAW_NAME': "the U.N. Charter",

        # --- DIALOGUE OVERRIDES ---
        '#FACTIONTRUCE': {
            'caption': '$CAPTION7',
            'text': '"This squabbling amongst ourselves accomplishes nothing, $NAME1. Let us forswear our differences and refocus our efforts on the goals of this mission."',
            'responses': [
                {'text': '"Fair enough. I shall order hostilities to cease."', 'action': 'diplo'},
                {'text': '"Hah! I shall enjoy watching your bases burn!"', 'action': 'diplo'}
            ]
        },

        '#FACTIONTREATY': {
            'caption': '$CAPTION7',
            'text': '"The fragmentation of this mission has been a disaster, $TITLE0 $NAME1. Won\'t you sign a Treaty of Friendship and help me to reunite the others?"',
            'responses': [
                {'text': '"A lofty goal, $TITLE4--I am with you."', 'action': 'diplo'},
                {'text': '"No. What\'s done is done, $NAME3."', 'action': 'diplo'}
            ]
        },
    }
]

# Council Proposals
PROPOSALS = [
    {"id": "GOVERNOR", "name": "Elect Planetary Governor", "type": "candidate", "cooldown": 0, "required_tech": None},  # Always available
    {"id": "SUPREME_LEADER", "name": "Unite Behind Me As Supreme Leader", "desc": "(Diplomatic Victory; Game Ends)", "type": "yesno", "cooldown": 0, "required_tech": "MindMac"},
    {"id": "UNITY_CORE", "name": "Salvage Unity Fusion Core", "desc": "(+500 energy credits to all factions)", "type": "yesno", "cooldown": 0, "required_tech": "Orbital"},
    {"id": "GLOBAL_TRADE", "name": "Global Trade Pact", "desc": "(Commerce rates doubled)", "type": "yesno", "cooldown": 20, "required_tech": "PlaEcon"},
    {"id": "REPEAL_TRADE", "name": "Repeal Global Trade Pact", "desc": "(Commerce rates halved)", "type": "yesno", "cooldown": 20, "required_tech": "PlaEcon"},
    {"id": "SOLAR_SHADE", "name": "Launch Solar Shade", "desc": "(Global cooling; Sea levels drop)", "type": "yesno", "cooldown": 30, "required_tech": "Space"},
    {"id": "INCREASE_SHADE", "name": "Increase Solar Shade", "desc": "(Global cooling; Sea levels drop)", "type": "yesno", "cooldown": 30, "required_tech": "Space"},
    {"id": "MELT_CAPS", "name": "Melt Polar Caps", "desc": "(Global warming; Sea levels rise)", "type": "yesno", "cooldown": 30, "required_tech": "EcoEng2"},
    {"id": "REPEAL_CHARTER", "name": "Repeal U.N. Charter", "desc": "(Atrocity prohibitions lifted)", "type": "yesno", "cooldown": 20, "required_tech": "MilAlg"},
    {"id": "REINSTATE_CHARTER", "name": "Reinstate U.N. Charter", "desc": "(Atrocity prohibitions return)", "type": "yesno", "cooldown": 20, "required_tech": "MilAlg"}
]

# Social Engineering Effects
# Format: [("STAT_NAME", value), ...] where value can be 1-5 for positive, -1 to -5 for negative
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
