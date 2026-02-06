# Faction Data: The Lord's Believers
# Mapping exact strings from GAIANS.txt to the $ variables in SMAC dialog.txt

believers_data = {
    # --- IDENTITY & TITLES ---
    '$FACTION': "The Lord's Believers",
    '$FACTION3': "Believers",  # Plural noun for faction members
    '$FACTION4': "The Lord's Believers",  # Full name for formal intros
    '$NAME': "Miriam",  # Short name
    '$NAME1': "Miriam",  # Short name used in intros
    '$NAME2': "Miriam",  # Name used in reports
    '$NAME3': "Miriam",  # Speaker's name
    '$TITLE2': "Sister",  # The leader's specific title
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
}