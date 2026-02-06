# Faction Data: Morgan Industries
# Mapped to placeholders found in 'SMAC dialog.txt'

morgan_data = {
    # --- IDENTITY & NAMING ---
    '$FACTION': "Morgan Industries",
    '$FACTIONNOUN': "Morganites",       # Used for plural reference
    '$NAME': "Morgan",                  # Short name
    '$FULLNAME': "Nwabudike Morgan",    # From Blurb/Datalinks
    '$TITLE': "CEO",                    # $TITLE2

    # --- ADJECTIVES ---
    '$CHARACTERADJ': "shrewd",          # $CHARACTERADJ9
    '$FACTIONADJ': "Morganic",          # Used for "Morganic territory"
    '$PEJORATIVE': "Filthy Money Grubber", # $PEJORATIVE5

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

    '#ALIENFACTIONTRUCE': {
        'caption': '$CAPTION7',
        'text': '"Vendetta must be bad for Progenitor business as much as humans, $NAME1. I suggest we pledge Blood Truce and get back to work."',
        'responses': [
            {'text': '"Economy: important. Death: to be avoided. Truce: agreed."', 'action': 'diplo'},
            {'text': '"$NAME3: believes money can save. Progenitor: disagree. War: continues!"', 'action': 'diplo'}
        ]
    },

    '#ALIENFACTIONTREATY': {
        'caption': '$CAPTION7',
        'text': '"$NAME1, your lack of interest in human commerce makes you a natural ally, for we have no point of contention. Shall we sign a Treaty of Friendship and work toward other common goals?"',
        'responses': [
            {'text': '"Commerce: not the only result. Friendship: valued. Treaty: agreed."', 'action': 'diplo'},
            {'text': '"Progenitor: no benefit: human treaty policies. Decline: politely."', 'action': 'diplo'}
        ]
    }
}