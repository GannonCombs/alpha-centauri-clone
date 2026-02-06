gaians_data = {
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