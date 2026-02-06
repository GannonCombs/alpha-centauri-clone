# Faction Data: The University of Planet
# Mapped to placeholders found in 'SMAC dialog.txt'

university_data = {
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
}