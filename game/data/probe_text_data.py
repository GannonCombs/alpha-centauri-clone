"""Probe team dialog text data.

All text is keyed by the SMAC Script.txt label (e.g. 'RISKEXCUSE').

Each entry may contain:
  text       (str)       — body text with {placeholder} variables
  responses  (list[str]) — button labels; absent means a single OK button suffices
  speaker    (str)       — who is speaking; defaults to 'Operations Director'
                           Other values: 'Protocol Director', 'faction_leader'

Variables used across entries:
  {player_title}    — player leader's $TITLE
  {player_name}     — player leader's $FULLNAME
  {leader_title}    — TARGET faction leader's $TITLE
  {leader_name}     — TARGET faction leader's $FULLNAME
  {faction}         — target faction's $FACTION (full name)
  {faction_adj}     — target faction's $FACTIONADJ (adjective form)
  {base_name}       — name of the relevant base
  {probe_team}      — unit name of the probe team
  {morale}          — morale level name (e.g. "Commando")
  {tech_name}       — technology name
  {facility_name}   — facility name
  {unit_type}       — unit type name
  {item_name}       — production item name
  {energy_cost}     — energy credit cost
  {energy_have}     — player's current energy reserves
  {energy_amount}   — energy credits drained
  {research_lost}   — research points lost to assassination
  {chance_abort}    — success chance display string if aborting (e.g. "60%")
  {chance_proceed}  — success chance display string if proceeding
  {chance_quick}    — success chance for quick general search
  {chance_targeted} — success chance for targeted search
  {chance_general}  — success chance for untargeted sabotage
  {chance_probe}    — success chance for Mind Control Probe
  {chance_total}    — success chance for Total Thought Control
  {chance_normal}   — success chance for standard subversion
  {chance_untrace}  — success chance for untraceable subversion
  {chances}         — generic success chance display string

Note: the dialog code handles all action routing; this file contains text only.
"""

PROBE_TEXT = {

    # ------------------------------------------------------------------ #
    # PRE-ACTION CONFIRMATION                                              #
    # ------------------------------------------------------------------ #

    # Shown when probe moves onto non-enemy base (not at war).
    'RISKEXCUSE': {
        'text': (
            "If our probe team is detected, it will provide "
            "{leader_title} {leader_name} with justification to move against us!"
        ),
        'responses': [
            "Abort mission.",
            "I am quite aware of that.",
        ],
    },

    # Shown after confirming (RISKEXCUSE) or when already at war.
    # Leads directly into the action menu.
    'PROBE': {
        'text': (
            "Our probe team has linked to the {faction_adj} network "
            "and is awaiting instructions."
        ),
    },

    # ------------------------------------------------------------------ #
    # MAIN ACTION MENU                                                     #
    # ------------------------------------------------------------------ #

    # The eight (nine with Free Captured Leader) options shown after PROBE.
    'PROBEMENU': {
        'responses': [
            "Infiltrate Datalinks",
            "Procure Research Data",
            "Activate Sabotage Virus",
            "Drain Energy Reserves",
            "Incite Drone Riots",
            "Assassinate Prominent Researchers",
            "Engage Mind Control Probe",
            "Introduce Genetic Plague (Atrocity)",
        ],
    },

    # ------------------------------------------------------------------ #
    # PROBE TEAM OUTCOME — SURVIVAL / CAPTURE                             #
    # ------------------------------------------------------------------ #

    # Mission success, team returned safely.
    'PROBESURVIVAL0': {
        'text': "Our {probe_team} has returned to {base_name}: mission complete.",
    },

    # Mission success, team returned and promoted.
    'PROBESURVIVAL1': {
        'text': (
            "Our {probe_team} has returned to {base_name}: mission complete.\n"
            "The team has been promoted to {morale} status."
        ),
    },

    # Mission succeeded but team was captured.
    'PROBECAUGHT': {
        'text': (
            "I have received the code signal for mission success, "
            "but our probe team has been lost."
        ),
    },

    # Mind Control succeeded but team succumbed to side effects.
    'PROBESUCCUMB': {
        'text': (
            "Although the mission was successful, our probe team succumbed "
            "to the side effects of the Mind Control Probe."
        ),
    },

    # Total failure — team eliminated.
    'BUSTED': {
        'text': (
            "I regret to inform you that our probe team has been compromised "
            "and eliminated."
        ),
    },

    # ------------------------------------------------------------------ #
    # ENEMY PROBE CAPTURED — shown when OUR defenses catch a hostile team #
    # ------------------------------------------------------------------ #

    'BUSTED1': {
        'text': (
            "We have captured a {faction_adj} probe team attempting to "
            "infiltrate our research datalinks at {base_name}!"
        ),
    },
    'BUSTED2': {
        'text': (
            "We have captured a {faction_adj} probe team attempting to "
            "sabotage facilities at {base_name}!"
        ),
    },
    'BUSTED3': {
        'text': (
            "We have captured a {faction_adj} probe team attempting to "
            "drain energy reserves at {base_name}!"
        ),
    },
    'BUSTED4': {
        'text': (
            "We have captured a {faction_adj} probe team attempting to "
            "incite drone riots at {base_name}!"
        ),
    },
    'BUSTED5': {
        'text': (
            "We have captured a {faction_adj} probe team attempting to "
            "assassinate prominent researchers at {base_name}!"
        ),
    },
    'BUSTED6': {
        'text': (
            "We have captured a {faction_adj} probe team attempting to "
            "activate some sort of mind control device at {base_name}!"
        ),
    },
    'BUSTED7': {
        'text': (
            "We have captured a {faction_adj} probe team attempting to "
            "unleash a genetic plague at {base_name}!"
        ),
    },

    # ------------------------------------------------------------------ #
    # ENEMY PROBE DETECTED (before action — player decides response)       #
    # ------------------------------------------------------------------ #

    # Enemy probe found inside our territory.
    'ENEMYPROBE': {
        'text': (
            "We have detected a {faction_adj} {probe_team}, {player_title}. "
            "Your instructions?"
        ),
        'responses': [
            "Leave them unmolested.",
            "Interrogate them, then return them unharmed.",
            "Eliminate them!",
        ],
    },

    # Enemy probe detected outside our territory (can't legally detain).
    'ENEMYPROBE2': {
        'text': (
            "We have detected a {faction_adj} {probe_team}, {player_title}. "
            "It is not in our territory, so we cannot legally capture and interrogate them."
        ),
        'responses': [
            "Leave them unmolested.",
            "Eliminate them!",
        ],
    },

    # Our probe was captured by the enemy and has been returned.
    'GOTMYPROBE': {
        'text': (
            "The {faction} has captured one of our probe teams inside its territory, "
            "{player_title}. The team has been returned safely to {base_name} "
            "after being interrogated and warned."
        ),
    },

    # We returned an enemy probe team after interrogating them.
    'GOTYOURPROBE': {
        'text': (
            "The {faction_adj} probe team has been interrogated and repatriated, "
            "{player_title}. Relations with the {faction} may suffer."
        ),
    },

    # ------------------------------------------------------------------ #
    # DRAIN ENERGY RESERVES                                                #
    # ------------------------------------------------------------------ #

    # Advanced security interlock found — proceed at risk?
    'ADVENERGY': {
        'text': (
            "Our probe team believes the energy grid at {base_name} to be newly "
            "equipped with a high security interlock! Continued tampering risks exposure."
        ),
        'responses': [
            "Abort mission. ({chance_abort})",
            "Break in at all costs. ({chance_proceed})",
        ],
    },

    # Security interlock found but team lacks experience to bypass.
    'ADVENERGY1': {
        'text': (
            "Our probe team has found the energy grid at {base_name} to be newly "
            "equipped with a high security interlock! This probe team does not have "
            "sufficient experience to bypass such a countermeasure."
        ),
    },

    # Success — energy drained.
    'GOTENERGY': {
        'text': (
            "Our probe team has successfully drained {energy_amount} energy units "
            "from the {faction_adj} energy grid!"
        ),
    },

    # Reached the grid but nothing to drain.
    'GOTNOENERGY': {
        'text': (
            "Our probe team reached the {faction_adj} energy grid "
            "but was unable to drain any energy."
        ),
    },

    # Notification — enemy drained OUR energy.
    'TOOKENERGY': {
        'text': (
            "A {faction_adj} probe team has drained {energy_amount} energy units "
            "from our reserves network!"
        ),
    },

    # Notification — enemy tried to drain us but found nothing.
    'TOOKNOENERGY': {
        'text': (
            "A {faction_adj} probe team was detected tapping into our energy grid, "
            "but discovered to its chagrin that we have little energy available to drain."
        ),
    },

    # ------------------------------------------------------------------ #
    # PROCURE RESEARCH DATA                                                #
    # ------------------------------------------------------------------ #

    # Nothing found — target has no unknown techs or search failed.
    'NODECIPHER': {
        'text': "Our probe team's search engines have failed to uncover any useful data.",
    },

    # Security interlock on network — proceed at risk?
    'ADVDECIPHER': {
        'text': (
            "Our probe team believes the network at {base_name} to be newly "
            "equipped with a high security interlock! Continued tampering risks exposure."
        ),
        'responses': [
            "Abort mission. ({chance_abort})",
            "Break in at all costs. ({chance_proceed})",
        ],
    },

    # Security interlock found but insufficient experience.
    'ADVDECIPHER1': {
        'text': (
            "Our probe team has found the network at {base_name} to be newly "
            "equipped with a high security interlock. This probe team does not have "
            "sufficient experience to bypass such a countermeasure."
        ),
    },

    # Choose search strategy — quick/general vs thorough/risky.
    'DECIPHER': {
        'text': "Do you wish a quick, general search, or a thorough, risky targeted search?",
        'responses': [
            "Just get me something useful. ({chance_quick})",
            "I need an accurate search. ({chance_targeted})",
        ],
    },

    # Tech successfully stolen.
    'DECIPHERED0': {
        'text': "Our probe team has successfully extracted the {faction_adj} files on {tech_name}!",
    },

    # Notification — enemy stole a tech from us.
    'DECIPHERED1': {
        'text': "The {faction_adj} probe team has downloaded our files on {tech_name}!",
    },

    # Search returned no usable data.
    'STOLENOTHING': {
        'text': "Our probe team found nothing of interest.",
    },

    # World map successfully stolen.
    'STOLEMAP0': {
        'text': "Our probe team has successfully downloaded the {faction_adj} world map!",
    },

    # Notification — enemy stole our world map.
    'STOLEMAP1': {
        'text': "The {faction_adj} probe team has downloaded our world map!",
    },

    # ------------------------------------------------------------------ #
    # ACTIVATE SABOTAGE VIRUS                                              #
    # ------------------------------------------------------------------ #

    # Choose sabotage approach — broad or targeted.
    'ADVVIRUS': {
        'text': "Do you require a targeted virus, or will widespread havoc be sufficient?",
        'responses': [
            "Just stir things up in there. ({chance_general})",
            "I have a specific target in mind. ({chance_targeted})",
        ],
    },

    # Targeted: probe team is inside — select a facility to destroy.
    'VIRUS': {
        'text': (
            "Our probe team has entered the compound and requests instructions "
            "on how to proceed. Select a target:"
        ),
    },

    # Abort option label (appears as a list item in VIRUS target selection).
    'ABORTSTRING': {
        'responses': ["Attempt to abort mission."],
    },

    # Abort succeeded.
    'VIRUSABORT': {
        'text': "Our probe team has successfully aborted.",
    },

    # HQ has heavy security — extra confirmation required.
    'HQVIRUS': {
        'text': (
            "{base_name} is the {faction_adj} Headquarters and is protected "
            "by high security interlocks! Advise caution."
        ),
        'responses': [
            "Abort mission.",
            "No more excuses! Proceed to viral activation! ({chance_proceed})",
        ],
    },

    # Military facility has security — confirmation required.
    'MILVIRUS': {
        'text': (
            "Our probe team reports that the {facility_name} at {base_name} "
            "is protected by high security interlocks! Advise extreme caution."
        ),
        'responses': [
            "Abort mission.",
            "Proceed to viral activation. ({chance_proceed})",
        ],
    },

    # Production item sabotaged successfully.
    'PRODVIRUS0': {
        'text': "Virus activated! {item_name} production has been terminated at {base_name}.",
    },

    # Notification — enemy sabotaged our production.
    'PRODVIRUS1': {
        'text': "A {faction_adj} virus has dealt a severe blow to {item_name} production at {base_name}.",
    },

    # Facility destroyed successfully.
    'FACVIRUS0': {
        'text': "Virus activated! {facility_name} disabled at {base_name}!",
    },

    # Notification — enemy destroyed our facility.
    'FACVIRUS1': {
        'text': "A {faction_adj} virus has destroyed the {facility_name} at {base_name}!",
    },

    # ------------------------------------------------------------------ #
    # ASSASSINATE PROMINENT RESEARCHERS                                    #
    # ------------------------------------------------------------------ #

    # Success — researcher killed, research points lost.
    'ASSASSINATED': {
        'text': (
            "Prominent {faction_adj} researcher assassinated at {base_name}!\n"
            "{research_lost} research points lost!"
        ),
    },

    # Team lacks sufficient morale for assassination.
    'NOASSASSIN': {
        'text': (
            "Assassination missions are tricky. This probe team does not yet have "
            "sufficient experience to undertake such a mission."
        ),
    },

    # Team capable — requires explicit player authorization.
    'ASSASSIN': {
        'text': (
            "Assassination missions are tricky. I will need your personal "
            "authorization before I can risk the probe team."
        ),
        'responses': [
            "Abort mission.",
            "Authorize mission. ({chances})",
        ],
    },

    # ------------------------------------------------------------------ #
    # ENGAGE MIND CONTROL PROBE                                            #
    # ------------------------------------------------------------------ #

    # Energy cost breakdown and choice of probe type.
    'THOUGHTCONTROL': {
        'text': (
            "{energy_cost} energy credits are required for successful "
            "mind control at {base_name}. We presently have {energy_have} "
            "energy credits in reserve."
        ),
        'responses': [
            "Abort mission.",
            "Engage Mind Control Probe. ({chance_probe})",
            "Attempt Total Thought Control. ({chance_total})",
        ],
    },

    # Success — base captured.
    'MINDCONTROL0': {
        'text': "The Mind Control operation is a success, {player_title}! {base_name} is ours!",
    },

    # Notification — enemy mind-controlled one of OUR bases.
    'MINDCONTROL1': {
        'text': (
            "{player_title} {player_name}! The {faction} has used some kind of "
            "mind control probe to seize control of {base_name}!"
        ),
    },

    # Notification — AI faction mind-controlled a third party's base.
    'MINDCONTROL2': {
        'text': (
            "{leader_title} {leader_name} of the {faction} has seized control "
            "of {base_name} with a mind control probe."
        ),
    },

    # Subvert (capture) an enemy unit — cost and risk.
    'SUBVERT': {
        'text': (
            "Our probe team can subvert and capture this {unit_type} unit, but the "
            "energy cost to penetrate the security interlocks will be {energy_cost}."
        ),
        'responses': [
            "Abort mission.",
            "Expend {energy_cost} credits. ({chance_normal})",
            "Spend {energy_cost} and attempt untraceable capture. ({chance_untrace})",
        ],
    },

    # Notification — enemy subverted one of our units.
    'SUBVERTED': {
        'text': (
            "The {faction} has captured our {probe_team} unit! "
            "A virus was used to penetrate the security interlocks!"
        ),
    },

    # ------------------------------------------------------------------ #
    # INTRODUCE GENETIC PLAGUE (ATROCITY)                                  #
    # ------------------------------------------------------------------ #

    # Success — plague released.
    'GENETICWARFARE0': {
        'text': "Our gene-tailored retrovirus has caused mass casualties at {base_name}!",
    },

    # Notification — enemy released plague against us.
    'GENETICWARFARE1': {
        'text': (
            "A gene-tailored retrovirus launched by the {faction} "
            "has caused mass casualties at {base_name}!"
        ),
    },

    # Notification — enemy faction infiltrated OUR datalinks (Infiltrate Datalinks result).
    'DETECTINFILTRATE': {
        'text': (
            "{leader_title} {leader_name} of the {faction} "
            "has infiltrated our data networks!"
        ),
    },

    # ------------------------------------------------------------------ #
    # INCITE DRONE RIOTS                                                   #
    # ------------------------------------------------------------------ #

    # Full drone riot triggered.
    'DRONEINCITE0': {
        'text': "Drone riots incited at {base_name}!",
    },

    # Drone activity increased (partial effect).
    'DRONEINCITE1': {
        'text': "Drone activity increased at {base_name}!",
    },

    # ------------------------------------------------------------------ #
    # DIPLOMATIC AFTERMATH — Protocol Director                             #
    # These are shown to the player as a Protocol Director notification    #
    # after a detected probe action affects a pact/treaty relationship.    #
    # ------------------------------------------------------------------ #

    # Detected action against pact partner gives excuse to renounce pact.
    'PACTEXCUSE': {
        'speaker': 'Protocol Director',
        'text': (
            "{leader_title} {leader_name}'s action is sufficient excuse to "
            "renounce our {pact_term} with the {faction}."
        ),
        'responses': [
            "Send a stern rebuke. I shall tolerate their act for now.",
            "Renounce the {pact_term}!",
        ],
    },

    # Detected action against non-pact faction gives excuse for Vendetta.
    'EXCUSE': {
        'speaker': 'Protocol Director',
        'text': "{leader_title} {leader_name}'s action is sufficient cause for Vendetta.",
        'responses': [
            "I shall overlook the offense for now.",
            "Vendetta upon the {faction}!",
        ],
    },

    # ------------------------------------------------------------------ #
    # ENEMY FACTION LEADER RESPONSES                                       #
    # Shown as a quote from the target faction leader after detection.     #
    # speaker='faction_leader' means the dialog renders with their portrait#
    # ------------------------------------------------------------------ #

    # Pact partner warns: espionage detected, pact still intact (first offence).
    'KEPTPACT1': {
        'speaker': 'faction_leader',
        'text': (
            '"I shall not condone industrial espionage, {player_title} {player_name}. '
            'Do not jeopardize our {pact_term}."'
        ),
    },

    # Pact partner warns: sabotage detected, pact still intact.
    'KEPTPACT2': {
        'speaker': 'faction_leader',
        'text': (
            '"I shall not condone industrial sabotage, {player_title} {player_name}. '
            'Do not jeopardize our {pact_term}."'
        ),
    },

    # Pact partner has had enough — renounces pact.
    'EXCUSEDPACT': {
        'speaker': 'faction_leader',
        'text': (
            '"That was the last straw, {player_title} {player_name}. '
            'Our {pact_term} is at an end."'
        ),
    },

    # Non-pact faction warns: espionage detected, no vendetta yet.
    'KEPT1': {
        'speaker': 'faction_leader',
        'text': (
            '"Be warned, {player_title} {player_name}, that I do not condone '
            'industrial espionage. Do not force me to take action against you."'
        ),
    },

    # Non-pact faction warns: sabotage detected, no vendetta yet.
    'KEPT2': {
        'speaker': 'faction_leader',
        'text': (
            '"Be warned, {player_title} {player_name}, that I do not condone '
            'industrial sabotage. Do not force me to take action against you."'
        ),
    },

    # Faction declares Vendetta after repeated or severe probe actions.
    'USEDEXCUSE': {
        'speaker': 'faction_leader',
        'text': (
            '"Vendetta upon you, {player_title} {player_name}. '
            'You shall pay for your persistent meddling."'
        ),
    },
}
