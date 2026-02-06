# Faction Data: The Human Hive
# Mapped to placeholders found in 'SMAC dialog.txt'

hive_data = {
    # --- IDENTITY & NAMING ---
    '$FACTION': "Human Hive",
    '$FACTIONNOUN': "Hive",             # Used for plural reference
    '$NAME': "Yang",                    # Short name
    '$FULLNAME': "Sheng-Ji Yang",       # From Blurb/Datalinks
    '$TITLE': "Chairman",               # $TITLE2

    # --- ADJECTIVES ---
    '$CHARACTERADJ': "ruthless",         # $CHARACTERADJ9
    '$FACTIONADJ': "Hive",               # Used for "Hive territory"
    '$PEJORATIVE': "Inhuman Monster",    # $PEJORATIVE5

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
}