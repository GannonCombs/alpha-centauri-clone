# Faction Data: The Spartan Federation
# Mapped to placeholders found in 'SMAC dialog.txt'

spartan_data = {
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
}