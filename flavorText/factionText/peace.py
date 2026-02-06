# Faction Data: Peacekeeping Forces
# Mapped to placeholders found in 'SMAC dialog.txt'

peace_data = {
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