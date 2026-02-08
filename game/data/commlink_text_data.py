COMMLINK_TEXT = {
# Generic fallback
    'GENERIC': {
        'text': '"I see."',
        'responses': [
            {'text': 'Continue', 'action': 'diplo'}
        ]
    },
# Main diplomacy menu
    'DIPLO': {
        'text': '"Have you any further business?"',
        'responses': [
            {'text': '"I believe we are finished here. $NAME0 out."', 'action': 'exit'},
            {'text': '"I have a proposal to make."', 'action': 'proposal'},
        ]
    },
    #
    # Proposal menu
    'PROPOSAL': {
        'text': '"Very well, what do you desire from me?"',
        'responses': [
            {'text': '"Never mind."', 'action': 'diplo'},
            {'text': '"That we swear a $PACTOFBORS1 and join forces!"', 'action': 'propose_pact', 'requires': 'has_treaty'},
            {'text': '"Let us sign a Treaty of Friendship."', 'action': 'propose_treaty', 'requires': 'no_treaty'},
            {'text': '"I desire access to your research data."', 'action': 'propose_tech'},
            {'text': '"I have urgent need of energy credits."', 'action': 'propose_loan'},
        ]
    },
    'INTRONEW0': {
        'text': '"Ah, the $CHARACTERADJ9 $TITLE0 $NAME1. I have heard many tales of your exploits. As to myself, I remain $TITLE2 $NAME3 of the $FACTION4. My intention is $TO_CARRY_OUT_MY_MISSION6."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRONEW1': {
        'text': '"Welcome to Planet, $TITLE0 $NAME1. You bring many unique talents to our new world. Permit me to reintroduce myself; I now style myself $NAME3, $TITLE2 of the $FACTION4, and on this world I plan $TO_CARRY_OUT_MY_MISSION6."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRONEW2': {
        'text': '"Ah, the $CHARACTERADJ9 $TITLE0 $NAME1, first among $SPECIAL5. I lead the $FACTION4, and am honored to be $<4:its:their> $TITLE2, $NAME3. We intend $TO_CARRY_OUT_OUR_MISSION6."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRONEW3': {
        'text': '"$TITLE0 $NAME1, I presume. $TITLE2 $NAME3 of the $FACTION4 at your service. I am told you have built yourself $SPECIAL5 empire here on this rocky planet. Be aware that I plan $TO_CARRY_OUT_OUR_MISSION6, and I will brook no interference in this matter."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRONEW4': {
        'text': '"Well met, $TITLE0 $NAME1. I am now called $TITLE2 $NAME3, and act as the voice of the $FACTION4, whose intent is $TO_CARRY_OUT_MY_MISSION6. I see you and your minions have flourished on this unforgiving world."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRONEW5': {
        'text': '"So, the familiar face of $TITLE0 $NAME1. I, $TITLE2 $NAME3 of the $FACTION4, offer greetings. Word of your accomplishments has spread since the time of Planetfall. You may be aware that I plan $TO_CARRY_OUT_MY_MISSION6. Do not attempt to interfere."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRO0': {
        'text': '"So we meet again, $TITLE0 $NAME1. I trust your $ENVIRONMENTAL_INITIATIVES5 $<5:is:are> proceeding to your satisfaction. I am, as always, $TITLE2 $NAME3 of the $FACTION4."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRO1': {
        'text': '"Ah, $TITLE0 $NAME1 the $CHARACTERADJ9. It is ever a pleasure to match wits with you. I, $TITLE2 $NAME3 of the $FACTION4, am at your service."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRO2': {
        'text': '"Hello again, $TITLE0 $NAME1. Your $FOLLOWERADJ5 followers remain a force to be reckoned with. Greetings from $TITLE2 $NAME3 of the $FACTION4."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTRO3': {
        'text': '"Greetings to you, $TITLE0 $NAME1. You are as always the most $CHARACTERADJ9 of us all, and your followers the most $FOLLOWERADJ5. $NAME3, $TITLE2 of the $FACTION4, salutes you."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTROMAD0': {
        'text': '"Ah, I see it is my old nemesis, $TITLE0 $NAME1, whose $RUTHLESS_METHODS6 my $FACTIONADJ8 subjects have learned to detest. You are addressing $NAME3, their $TITLE2, who intends to stop you from $IMPLEMENTING_YOUR_EVIL_AGENDA5."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTROMAD1': {
        'text': '"Greetings, $TITLE0 $NAME1, and beware! Though you are bent on $IMPLEMENTING_YOUR_EVIL_AGENDA6, you and your $FOLLOWPEJORATIVE5 followers cannot stand before the wrath of $TITLE2 $NAME3 of the $FACTION4!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTROMAD2': {
        'text': '"Do not trifle with me, $TITLE0 $NAME1. I, $TITLE2 $NAME3 of the $FACTION4, am not impressed by your $RUTHLESSMETHODS6."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTROMAD3': {
        'text': '"$TITLE0 $NAME1. I see you\'re very busy $DANCING_NAKED_THROUGH_THE_TREES8, But are you prepared once again to face your old enemy $NAME3, $TITLE2 of the $FACTION4?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INTROMAD4': {
        'text': '"Well, well, if it isn\'t the $PEJORATIVE5 $TITLE0 $NAME1, our very own $ECO_LOONY6. Perhaps you had best stop $DANCING_NAKED_THROUGH_THE_TREES8 for a moment, for I am $NAME3, $TITLE2 of the $FACTION4!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BUYPROTO0': {
        'text': '"It cost me a pretty penny to develop the $LASERCRAWLERPROTOTYPE0. Are you willing to part with $NUM0 energy credits for the plans?"',
        'responses': [
            {'text': '"Never mind."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 energy credits.', 'action': 'diplo'}
        ]
    },
    'BUYPROTOHIGH0': {
        'text': '"It cost me a pretty penny to develop the $LASERCRAWLERPROTOTYPE0. You\'ll have to come up with $NUM0 energy credits before I\'ll part with those plans."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BUYCOMMLINKHIGH0': {
        'text': '"I will gladly share the $<M1:$FACTIONADJ0> commlink frequency, but you\'ll have to come up with {$NUM0 energy credits} first."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BUYCOMMLINK0': {
        'text': '"I would be happy to share the $<M1:$FACTIONADJ0> commlink frequency in exchange for a mere {$NUM0 energy credits."}',
        'responses': [
            {'text': '"No thanks."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 energy credits.', 'action': 'diplo'}
        ]
    },
    'EXTORTCOMMLINK': {
        'text': '"Very well. I shall transmit the $<M1:$FACTIONADJ0> commlink frequency at once."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BUYTECH0': {
        'text': '"Knowledge is power, as the saying goes, and can be bought but dearly. I shall transmit our knowledge of {$TECH0} in exchange for {$NUM0 energy credits.} Agreed?"',
        'responses': [
            {'text': '"No thanks."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 energy credits.', 'action': 'diplo'}
        ]
    },
    'BUYTECH1': {
        'text': '"For my files on {$TECH0,} the price is {$NUM0 energy credits."}',
        'responses': [
            {'text': '"What are you trying to pull?"', 'action': 'diplo'},
            {'text': 'Pay $NUM0 energy credits.', 'action': 'diplo'}
        ]
    },
    'BUYTECHHIGH0': {
        'text': '"Knowledge is power, as the saying goes, and can be bought but dearly. I am willing to discuss sale of our $TECH0 information, but only if you can accumulate $NUM0 energy credits."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BUYTECHHIGH1': {
        'text': '"Although I pity the sad state of your energy reserves, knowledge is a scarce commodity. I could not possibly offer $TECH0 for less than $NUM0 energy credits."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHHATE0': {
        'text': '"$TITLE0 $NAME1, my followers call you a $NATURE_LOONY2. I hardly think you\'re trustworthy enough to share confidential data."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHHATE1': {
        'text': '"And watch while your $FOLLOWERPEJORATIVE3 minions twist the fruits of my labor into instruments of vile treachery? I think you overestimate my gullibility, my dear $TITLE0!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHHATE2': {
        'text': '"And aid you in $IMPLEMENTING_YOUR_EVIL_AGENDA4? I think not."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHFEAR0': {
        'text': '"$TITLE0 $NAME1, you seem bent on $IMPLEMENTING_YOUR_EVIL_AGENDA2. I\'m not sure that sharing critical knowledge with you would be entirely wise."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHFEAR1': {
        'text': '"$TITLE0 $NAME1, I am aware that $IMPLEMENTING_YOUR_EVIL_AGENDA2 is not an easy task. But do not expect me to assist you with my own advanced technology."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHADVANCED0': {
        'text': '"I\'m afraid I have no use for any knowledge your $FOLLOWERPEJ0 researchers could produce."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHADVANCED1': {
        'text': '"Your $FOLLOWERPEJ0 minions\' notions of research are of little use to me."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHADVANCED2': {
        'text': '"I am unwilling to exchange state-of-the-art technology for your obsolete research data."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHPROJ0': {
        'text': '"My research data is currently classified. Let us speak again after the completion of my secret project, $PROJECT0."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHPROJ1': {
        'text': '"My networks are running at full capacity as I approach completion of $PROJECT0. Why don\'t you bring this up again later?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHPROJ2': {
        'text': '"I think not, $TITLE1 $NAME2, for I should not like to see $PROJECT0 fall into your hands."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TECHFREEBIE': {
        'text': '"As part of my grand planetary vision I shall transmit to you, gratis, my data on {$TECH0.} Guard this knowledge carefully, and do not forget my generousity."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TECHSLAVE': {
        'text': '"It shall be my great pleasure to transmit to you information on {$TECH0} which I believe you will find most useful."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHLATER0': {
        'text': '"I am not prepared to authorize access to my research at this time."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHLATER1': {
        'text': '"For now, my secrets shall remain my own."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHLATER2': {
        'text': '"I have no technical data to share at this time."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHLATER3': {
        'text': '"Sadly, I have no technical data in which you would be interested."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHLATER4': {
        'text': '"It appears you currently have no technical data in which I am interested. Another time, perhaps?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJCOMMLINK': {
        'text': '"I am not prepared to divulge commlink information at this time."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TRADETECH0': {
        'text': '"Through cooperation we can achieve mutual satisfaction of needs. Will you transmit your files on {$TECH0} in exchange for my information on {$TECH1?} Think how your $PET_PROJECTS5 could be enhanced by proper use of such knowledge."',
        'responses': [
            {'text': '"Out of the question."', 'action': 'diplo'},
            {'text': '"That is satisfactory."', 'action': 'diplo'}
        ]
    },
    'TRADETECH1': {
        'text': '"$TITLE3 $NAME4, I know I have been accused of $BEHAVING_BADLY9, but I think you will find that I am $<8:a man:a woman:x:x> of reason. Let us exchange knowledge on a quid pro quo basis: I will share my files on {$TECH1;} you must, in return, fully disclose your data on {$TECH0."',
        'responses': [
            {'text': '"Out of the question."', 'action': 'diplo'},
            {'text': '"That is satisfactory."', 'action': 'diplo'}
        ]
    },
    'TRADETECH2': {
        'text': '"I believe your data on {$TECH0} could have important implications for my $PET_PROJECTS6. I propose that you exchange this knowledge for my own files on {$TECH1.} Interested?"',
        'responses': [
            {'text': '"No."', 'action': 'diplo'},
            {'text': '"It\'s a deal."', 'action': 'diplo'}
        ]
    },
    'TRADETECH3': {
        'text': '"Your information on {$TECH0} intrigues me. Are you willing to exchange it for a copy of {my world map}?"',
        'responses': [
            {'text': '"No."', 'action': 'diplo'},
            {'text': '"It\'s a deal."', 'action': 'diplo'}
        ]
    },
    'TRADETECH4': {
        'text': '"My cartographers are attempting to compile a complete map of this planet. Will you exchange a copy of your own {maps} for my information on {$TECH1?"}',
        'responses': [
            {'text': '"No. My maps are highly classified."', 'action': 'diplo'},
            {'text': '"That is acceptable."', 'action': 'diplo'}
        ]
    },
    'TRADETECH5': {
        'text': '"Many areas of this world remain unexplored and dangerous. Would you care to exchange cartographic information to insure our mutual safety?"',
        'responses': [
            {'text': '"No. My maps are highly classified."', 'action': 'diplo'},
            {'text': '"That seems prudent."', 'action': 'diplo'}
        ]
    },
    'TRADETECHOPT': {
        'text': '"Give me {$TECH9} instead and you\'ve got a deal."',
        'responses': [
            {'text': '"No, but I could divulge information on {$TECH2."', 'action': 'diplo'},
            {'text': '"Pardon, I must consult the {Datalinks."', 'action': 'diplo'}
        ]
    },
    'REJTECHINSTEAD': {
        'text': '"Sorry, $TITLE3 $TITLE4. It\'s {$TECH0} or nothing."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHSECOND': {
        'text': '"I did not come here to discuss $TECH2. Do not presume to clutter our networks with useless garbage."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'ENERGYFREEBIE0': {
        'text': '"Very well, here are {$NUM0 energy credits.} Spend them wisely and do NOT come crying to me for more."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'ENERGYFREEBIE1': {
        'text': '"How it must gall you to be reduced to the status of a beggar! Very well, accept {$NUM0 energy credits} as a token of my sympathy."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJENERGY0': {
        'text': '"I\'m sorry, I have no energy to spare at this time."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJENERGY1': {
        'text': '"Sadly, my energy reserves are already allocated. I have none to give."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'ENERGYLOAN1': {
        'text': '"Your credit is good, $TITLE0 $NAME1, and I can spare you {$NUM0 energy credits.} My terms are generous: you must pay me $NUM1 credit per year for $NUM2 years."',
        'responses': [
            {'text': 'Refuse loan.', 'action': 'diplo'},
            {'text': 'Accept loan of $NUM0 energy credits.', 'action': 'diplo'}
        ]
    },
    'ENERGYLOAN2': {
        'text': '"Your credit is good, $TITLE0 $NAME1, and I can spare you {$NUM0 energy credits.} My terms are generous: you must pay me $NUM1 credits per year for $NUM2 years."',
        'responses': [
            {'text': 'Refuse loan.', 'action': 'diplo'},
            {'text': 'Accept loan of $NUM0 energy credits.', 'action': 'diplo'}
        ]
    },
    'REJSELLNONE': {
        'text': '"I fear you have no knowledge which interests me, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJSELLAFFORD': {
        'text': '"Alas, I cannot afford to buy your knowledge, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'ENERGYTECH0': {
        'text': '"Your information on {$TECH0} is of interest to me, but I can only pay you {$NUM0 energy credits.} Is this satisfactory?"',
        'responses': [
            {'text': '"Sorry, not interested."', 'action': 'diplo'},
            {'text': 'Transmit information on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'ENERGYTECH1': {
        'text': '"Hmm... I could certainly benefit from {$TECH0} if the price were right. How would {$NUM0 energy credits} strike you?"',
        'responses': [
            {'text': '"Sorry, not interested."', 'action': 'diplo'},
            {'text': 'Transmit information on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'ENERGYTECH2': {
        'text': '"Your information on {$TECH0} is of interest to me, but I can only pay you {$NUM0 energy credits.} Is this satisfactory?"',
        'responses': [
            {'text': '"Sorry, not interested."', 'action': 'diplo'},
            {'text': 'Transmit information on $TECH0.', 'action': 'diplo'},
            {'text': '"No, but I will sell you $TECH1 for the same price."', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'REJSELLSECOND': {
        'text': '"I have no interest in $TECH1. Sorry."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SELLSECOND': {
        'text': '"Sold. $TECH1 for $NUM0 credits."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAKEPACT': {
        'text': '"Then I, $TITLE0 $NAME1 of the $FACTION2 greet you formally as $PACTBROTHERORSISTER3! Together we shall both $YOURGOAL4 and $MYGOAL5. May our plans and forces converge to victory!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAKETREATY0': {
        'text': '"Excellent. $TITLE0 $NAME1, this Treaty demonstrates that Planet is large enough both for your $PET_PROJECTS6 and for my $PET_PROJECTS7. It also opens the door for trade and commerce between our peoples. May the friendship between the $FACTION2 and the $FACTION5 last forever!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAKETREATY1': {
        'text': '"Splendid. My $PET_PROJECTS7 and your $PET_PROJECTS6 complement one another nicely. The $FACTION5 and the $FACTION2 have much to gain from this friendship. We shall commence trade and commerce at once!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAKETRUCE': {
        'text': '"I pledge myself, $NAME4 of the $FACTION5, to Blood Truce with the $FACTION2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TRUCEMEPAY': {
        'text': '"Now that our Vendetta is at an end, I shall expect prompt resumption of your $NUM0 energy credit {loan} payments. Your balance remaining has grown, with interest and penalties, to $NUM1 credits."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TRUCEYOUPAY': {
        'text': '"Since our Vendetta has been resolved satisfactorily, I shall now resume my $NUM0 energy credit loan payments."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'AIDSTHEM': {
        'text': 'The $FACTION0 $<0:intervenes:intervene> on behalf of the $FACTION1! $TITLE2 $NAME3 pronounces Vendetta against you!',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'AIDSUS': {
        'text': 'The $FACTION0 $<0:is:are> intervening on our behalf. $TITLE2 $NAME3 pronounces Vendetta against $TITLE4 $NAME5 of the $FACTION6!',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTMEEK': {
        'text': '"With all due respect, your previous actions do not recommend you as a worthy $PACTBROTHERORSISTER0."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTHATE': {
        'text': '"You have shown yourself to be most unworthy of trust, $TITLE1, and you are mistaken if you think me disposed to speak Pact with one known mostly for $DANCING_NAKED_THROUGH_THE_TREES3."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTAHEAD0': {
        'text': '"Beg pardon, my dear $TITLE1, but I suspect that to speak Pact with you now would be to cement your designs for planetary supremacy!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTAHEAD1': {
        'text': '"Beg pardon, my dear $TITLE1, but I suspect that to speak Pact with you now would be to cement your designs for $IMPLEMENTING_YOUR_EVIL_AGENDA3."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTPOWER': {
        'text': '"Thank you, but I believe I can effect my $PET_PROJECTS3 quite handily on my own."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTNOBRIBE': {
        'text': '"Then I regret I cannot consent to such a lop-sided bargain."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTBADBRIBE': {
        'text': '"I am not interested under those terms."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACTNOHELP': {
        'text': '"Your actions speak louder than words; $PACTBROTHERSORSISTERS2 we are not."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJPACT': {
        'text': '"My $PET_PROJECTS3 are proceeding smoothly. I see no need to speak Pact at this time."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'GIMMETECH0': {
        'text': '"I am intrigued by your offer, but can accept only if it is made on the basis of equal access to data. Will you transmit to me all of your data on {$TECH2} as a token of our future friendship?"',
        'responses': [
            {'text': '"That information is classified, $TITLE1."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH2.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'GIMMETECH1': {
        'text': '"Your proposal suits my $PET_PROJECTS3 perfectly. However, I find myself in urgent need of information on {$TECH2.} Can you transmit it to me at once?"',
        'responses': [
            {'text': '"Nice try, $TITLE1, but that\'s classified."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH2.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'GIMMEENERGY0': {
        'text': '"I see that cooperation could be profitable. In fact, recent events have left my energy budget with a {$NUM0 credit} shortfall. Can you spare the reserves to make it up?"',
        'responses': [
            {'text': '"What you describe is larceny, not profit!"', 'action': 'diplo'},
            {'text': 'Wire $NUM0 credits.', 'action': 'diplo'}
        ]
    },
    'GIMMEENERGY1': {
        'text': '"An admirable sentiment. But are you willing to part with {$NUM0 energy credits} to make it reality?"',
        'responses': [
            {'text': '"Indeed not, $TITLE1."', 'action': 'diplo'},
            {'text': 'Wire $NUM0 credits.', 'action': 'diplo'}
        ]
    },
    'GIMMEHELP': {
        'text': '"Bold words, $TITLE5, but will you back them by pronouncing Vendetta on my bitter foes the {$FACTION6?"}',
        'responses': [
            {'text': '"I fear I cannot honorably do so."', 'action': 'diplo'},
            {'text': '"So be it! We shall crush the $FACTION6 beneath our boots!"', 'action': 'diplo'}
        ]
    },
    'REJTREATYMEEK': {
        'text': '"With respect, $TITLE1, it appears there is little future in \'permanent\' agreements with the $FACTION2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTREATYHATE': {
        'text': '"A Treaty of Friendship? Yes, I\'m sure you would find that most convenient, $TITLE1. But do not ask for my friendship when your own followers call you a $NATURE_LOONY4."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTREATYAHEAD': {
        'text': '"Your faction has grown far too powerful, $TITLE1 $NAME0, and as you proceed with $IMPLEMENTING_YOUR_EVIL_AGENDA5 I see no desirable place for myself in your fearsome $<M1:$FACTIONADJ3> scheme. Even in \'friendship,\' my $PET_PROJECTS4 would be threatened."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTREATYNOBRIBE': {
        'text': '"It seems you and I place a different emphasis on the meaning of the word friendship, $TITLE1 $NAME0. I must say I find yours most, er, unappetizing."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTREATYBADBRIBE': {
        'text': '"I\'m afraid I\'m not interested under the terms you offer."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTREATYNOHELP': {
        'text': '"Then do not expect my friendship."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTREATY': {
        'text': '"My friendship cannot be bought, my good $TITLE1, it must be earned."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'PROVOKED0': {
        'text': '"I have endured your $BAD_HABITS2 for far too long; now I demand satisfaction. Vendetta be upon you, $TITLE0 $NAME1, and I guarantee I\'ll make you suffer!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'PROVOKED1': {
        'text': '"That, $TITLE0 $NAME1, was your final provocation. Now I shall give you cause to long regret your $BAD_HABITS2: I pronounce Vendetta upon you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'COLLABORATOR': {
        'text': '"$TITLE0 $NAME1, your collaboration with my mortal enemy, $TITLE2 $NAME3, has gone on long enough. From this day forward, my Vendetta extends to you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BULLY0': {
        'text': '"So be it. I have given you numerous chances to be reasonable. Now it is time for us to settle our differences by other means: Vendetta!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BULLY1': {
        'text': '"What you fail to understand, my $<1:$CHARACTERADJ3> $TITLE0, is that I have the power to take what I demand by force. It is time I gave you a lesson in Vendetta!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BULLY2': {
        'text': '"That is just as well, $TITLE0 $NAME1, for I was looking forward to dismembering your $<M1:$FACTIONPEJ2> faction piece by piece. Soon you shall realize the magnitude of your mistake!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BULLY3': {
        'text': '"You are no longer useful to me, $NAME1. It is time for you to die."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BULLY4': {
        'text': '"Have it your way, then. Exterminating each and every one of your $<M1:$FACTIONPEJ2> minions will provide great sport for my $THOUGHT_POLICE4."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BULLY5': {
        'text': '"Always the insouciant one, eh, $NAME1? It is sad that exterminating your pathetic faction will provide so little sport."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BULLY6': {
        'text': '"I almost hoped you would say something like that. Stamping out your $BIZARRE_PRACTICES5 once and for all will bring me great joy."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'OUTRAGE0': {
        'text': '"I shall make you bleed for this, $NAME0! Such treachery shall not go unpunished!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'OUTRAGE1': {
        'text': '"Then I shall sweep aside your $<M1:$FACTIONPEJ3> faction, and when you lie chained at my feet I shall savor each and every one of your pathetic cries for mercy. Vendetta be upon you, $TITLE0 $NAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'OUTRAGE2': {
        'text': '"So, you are nothing but a $NATURE_LOONY2 after all! I pronounce Vendetta upon you, $TITLE0 $NAME1, and I shall never forget your treachery!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA0': {
        'text': '"Then I shall sweep aside your $<M1:$FACTIONPEJ3> faction, and when you lie chained at my feet I shall savor each and every one of your pathetic cries for mercy. Vendetta be upon you, $TITLE0 $NAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA1': {
        'text': '"Your impudent and $<M1:$FACTIONPEJ3> faction is barely worth my attention, $TITLE1. Soon I shall crush you like the bug that you are!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA2': {
        'text': '"Have it your way, then. Exterminating each and every one of your $<M1:$FACTIONPEJ3> minions will provide great sport for my $THOUGHT_POLICE6."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA3': {
        'text': '"You are a blight upon this planet, $NAME1. Destroying you will be a service to humanity."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA4': {
        'text': '"You are insufferable and $<1:$CHARPEJ2>, $NAME1, and I shall gladly cleanse Planet of your $BADHABITS4."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA5': {
        'text': '"This world has no further need for a $NATURE_LOONY9, $NAME1. I look forward to terminating your contract personally."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA6': {
        'text': '"You are a contemptuous parasite, $NAME1, and I shall gleefully purge Planet of your filth."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA7': {
        'text': '"Take a good last look at your empire, $NAME1, for there will be little left of it when next we meet."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA8': {
        'text': '"It will be an honor to exterminate your faction, $NAME1. The world will be a better place without you."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA9': {
        'text': '"You are a cruel and inhuman monster, $NAME1. Now you shall pay for your crimes!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA10': {
        'text': '"Your crimes against humanity are unforgiveable, $NAME1. The world shall soon rejoice at your destruction."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA11': {
        'text': '"You are a brutal murderer, $NAME1. Justice, when it comes, will be lethal and merciless."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA12': {
        'text': '"You have butchered thousands of my people, $NAME1, and I\'ll see that you choke on your own bile."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA13': {
        'text': '"You are a murderous abomination, $NAME1. When I am finished with you the victims of your atrocities will revel in your suffering."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA14': {
        'text': '"Nothing personal, my dear $TITLE1, but Planet simply isn\'t big enough for the two of us. I shall ruthlessly crush your faction, of course, and shall derive great pleasure from having you executed."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA15': {
        'text': '"You may dream of $IMPLEMENTING_YOUR_EVIL_AGENDA5, $TITLE1, but I shall soon cut you down to size! Vendetta upon you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA16': {
        'text': '"I shall not simply stand here while you $IMPLEMENT_YOUR_EVIL_AGENDA8. If Vendetta is what you want, then Vendetta is what you will get!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA17': {
        'text': '"Your faction has grown fat and careless, $TITLE0 $NAME1. Now I shall carve a piece of it for myself!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'VENDETTA18': {
        'text': '"Your people have become decadent and weak, $NAME1. It is time I sliced the fat from your bones!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'ATROCIOUS': {
        'text': '"You shall suffer for this outrage, $TITLE1! I will make you pay for each and every one of your atrocities!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'ATROCIOUSITY': {
        'text': '"I have warned you against such atrocities, $TITLE0 $NAME1. Now I shall make you pay!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'NEVER': {
        'text': '"We shall soon see whose territory this is! Vendetta upon you, $PLAYERTITLE0 $PLAYERNAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'RUNNINGDOG': {
        'text': '"You would deny me the right to cross your land and attack my mortal enemy $TITLE2 $NAME3? In that case I shall now extend my Vendetta to you as well!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'NOWAYJOSE': {
        'text': '"I may have pledged Blood Truce with you, $TITLE0 $NAME1, but do not presume to dictate where I shall station my forces."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TURNABOUT': {
        'text': '"Let me offer a counter proposal, $TITLE0. If you will first withdraw all of your forces from MY territory, I will happily do likewise."',
        'responses': [
            {'text': '"Never mind. Let our forces remain in place."', 'action': 'diplo'},
            {'text': '"Agreed. My forces shall withdraw as well."', 'action': 'diplo'}
        ]
    },
    'WITHDRAWPACT': {
        'text': '"Of course, $PACTBROTHERORSISTER2. If you wish, I shall withdraw."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WITHDRAW': {
        'text': '"Many apologies, my $<0:$CHARACTERADJ1> friend, for this unintentional transgression. My forces shall pull back at once."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WITHDRAWTRUCE': {
        'text': '"Very well. Since I do not wish to provoke a renewal of Vendetta, I shall withdraw my forces from the areas you claim as your territory. See that you respect my boundaries as well."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'NOWITHDRAW': {
        'text': '"As you must surely be aware, my $<0:$CHARACTERADJ1> friend, I have no military units inside your borders."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'EXTORTTECH': {
        'text': '"But my good $PACTBORS0, I was at this very moment preparing to transmit to you our complete file on $TECH1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'EXTORTENERGY': {
        'text': '"Temper, temper, $TITLE0 $NAME1! I can spare $NUM0 energy credits, and no more."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'FEND': {
        'text': '"Do what you must, $TITLE0, for I have nothing to spare."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'ENDPACT': {
        'text': '"Enough! Your threatening tone disappoints me, $TITLE0 $NAME1. From this day you are no longer my $PACTBROTHERORSISTER2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'IGNOREPACT': {
        'text': '"Silence! I shall not suffer such whimpering to continue, $TITLE0."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'IGNORE': {
        'text': '"Is that a threat, $TITLE0 $NAME1? I suggest that you pronounce Vendetta and have done with it, for I am scarcely intimidated."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REALLYBROKE': {
        'text': '"Null and void!? $PACTBROTHERORSISTER0, do you truly intend to turn your back on our years of friendship!?"',
        'responses': [
            {'text': '"Heavens, no! I meant to say \'full of droids.\'"', 'action': 'diplo'},
            {'text': '"Yes. I have had my fill of your whining incompetence."', 'action': 'diplo'}
        ]
    },
    'DROIDS': {
        'text': '"Ah, droids. Yes, recent advances in automation and artificial intelligence have given rise to social trends on which we must maintain a careful eye."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'BROKEPACT': {
        'text': '"I have little use for a false $PACTBROTHERORSISTER0, $TITLE1 $NAME2. Tread carefully when next we meet."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'YOUATTACK': {
        'text': '"Upon whose head would you have me pronounce Vendetta, $TITLE0?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJWARFAR': {
        'text': '"I\'m afraid I cannot help you, $TITLE0, as my forces are not positioned near $<M1:$FACTIONADJ2> territory."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJWARALREADY': {
        'text': '"You need speak no further, for already I pursue Vendetta against $TITLE0 $NAME1 with utmost vigor!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJWARTRUST': {
        'text': '"I see. And once my forces are committed to attacking the $FACTION3 your veteran $UNITTYPES0 descend on my unguarded flank? No thank you, $TITLE1 $NAME2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJWAR': {
        'text': '"This is foolishness. $TITLE0 $NAME1 has done me no wrong, and I shall not be bribed into attacking $HIMHER2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJWARNOBRIBE': {
        'text': '"I certainly shall not undertake an expensive war for your \'goodwill,\' $NAME0."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAYBEWARENERGYPACT': {
        'text': '"The $FACTION0? You wish me to betray openly my own $PACTBROTHERORSISTER1? That would be an infamous act indeed! Just between us, I might consider such a course, but never for less than {$NUM0 energy credits!"}',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAYBEWARENERGY': {
        'text': '"Vendetta upon the $<0:$FACTIONPEJ2> $FACTION0!? Have you even the first inkling of what such a war would cost me? {$NUM0 energy credits} would scarcely begin to compensate!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAYBEWARENERGYFAR': {
        'text': '"Where $<0:is this:are these> $FACTION0 you speak about? My forces are not positioned near $<M1:$FACTIONADJ6> lands, but I am willing to pronounce Vendetta in exchange for {$NUM0 energy credits."}',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MAYBEWARPRICE': {
        'text': '"You know I could never raise such a sum!"',
        'responses': [{'text': '"I shall wire $NUM0 credits with great pleasure."', 'action': 'diplo'}]
    },
    'MAYBEWARTECH4': {
        'text': '"Ah, the $FACTION0. $TITLE1 $NAME2 would be a formidable opponent, as I\'m sure you\'re well aware. I might do this thing, but only in exchange for your data on {$TECH3,} {$TECH4,} {$TECH8,} and {$TECH9."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECH3': {
        'text': '"Ah, the $FACTION0. $TITLE1 $NAME2 would be a formidable opponent, as I\'m sure you\'re well aware. I might do this thing, but only in exchange for your data on {$TECH3,} {$TECH4,} and {$TECH8."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECH2': {
        'text': '"Ah, the $FACTION0. $TITLE1 $NAME2 would be a formidable opponent, as I\'m sure you\'re well aware. I might do this thing, but only in exchange for your data on {$TECH3} and {$TECH4."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECH': {
        'text': '"Ah, the $FACTION0. $TITLE1 $NAME2 would be a formidable opponent, as I\'m sure you\'re well aware. I might do this thing, but only in exchange for your data on {$TECH3."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHFAR': {
        'text': '"Vendetta upon the $FACTION0 could be a dangerous proposition. My forces are not in position for an assault on $<M1:$FACTIONADJ6> lands, but I am willing to pronounce Vendetta in exchange for your data on {$TECH3."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHFAR2': {
        'text': '"Vendetta upon the $FACTION0 could be a dangerous proposition. My forces are not in position for an assault on $<M1:$FACTIONADJ6> lands, but I am willing to pronounce Vendetta in exchange for your data on {$TECH3} and {$TECH4."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHFAR3': {
        'text': '"Vendetta upon the $FACTION0 could be a dangerous proposition. My forces are not in position for an assault on $<M1:$FACTIONADJ6> lands, but I am willing to pronounce Vendetta in exchange for your data on {$TECH3,} {$TECH4,} and {$TECH8."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHFAR4': {
        'text': '"Vendetta upon the $FACTION0 could be a dangerous proposition. My forces are not in position for an assault on $<M1:$FACTIONADJ6> lands, but I am willing to pronounce Vendetta in exchange for your data on {$TECH3,} {$TECH4,} {$TECH8,} and {$TECH9."}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHPACT': {
        'text': '"Break my Pact with the $FACTION0? I might do this thing, but only in exchange for your data on {$TECH3!"}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHPACT2': {
        'text': '"Break my Pact with the $FACTION0? I might do this thing, but only in exchange for your data on {$TECH3} and {$TECH4!"}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHPACT3': {
        'text': '"Break my Pact with the $FACTION0? I might do this thing, but only in exchange for your data on {$TECH3,} {$TECH4,} and {$TECH8!"}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'MAYBEWARTECHPACT4': {
        'text': '"Break my Pact with the $FACTION0? I might do this thing, but only in exchange for your data on {$TECH3,} {$TECH4,} {$TECH8,} and {$TECH9!"}',
        'responses': [
            {'text': '"Nice try, $TITLE5, but that\'s classified."', 'action': 'diplo'},
            {'text': '"Very well, begin transmission!"', 'action': 'diplo'}
        ]
    },
    'WARTHREAT': {
        'text': '"Very well. At your insistence I shall conduct vendetta against $TITLE0 $NAME1 and the $FACTION2. But be warned that I shall pull my forces out at the first sign you are not fully supporting me with your own troops!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WARPACT': {
        'text': '"Of course I shall aid you in this endeavor, $PACTBROorSIS3! I shall mobilize my troops at once and move against $TITLE0 $NAME1 in force."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INCITEDPACT': {
        'text': 'Your $PACTBROTHERSORSISTERS3 the $FACTION2 $<2:has:have> learned of your treachery and abrogated the Pact!',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INCITEDTREATY': {
        'text': 'The $FACTION2 $<2:has:have> learned of your treachery and $<2:has:have> pronounced Vendetta upon you!',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INCITED0': {
        'text': '"Very well. I shall proceed with Vendetta against the $FACTION2 at once! $TITLE0 $NAME1\'s days of $DANCING_NAKED_THROUGH_THE_TREES4 will soon be at an end."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'INCITED1': {
        'text': '"Excellent. I shall gleefully annihilate $TITLE0 $NAME1\'s $<M1:$FACTIONPEJ3> faction!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'HERESTHEMAP': {
        'text': '"$PACTBROTHERORSISTER0, I am now uploading my most recent world map exploration data to your central computer."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJMAPS': {
        'text': '"$<M1:$FACTIONADJ0> survey data is a closely guarded secret and will not be shared lightly."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TRADEMAPS': {
        'text': '"A fine exchange; we shall trade you map for map."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REJTECHNOTHING': {
        'text': '"As much as I might appreciate the gesture, you possess no information of use to me."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'OFFERTECH': {
        'text': '"Information on {$TECH0} could prove most useful to certain of my $PET_PROJECT2. You will transmit this data at once?"',
        'responses': [
            {'text': '"No. Never mind."', 'action': 'diplo'},
            {'text': '"Yes. Beginning transmission."', 'action': 'diplo'}
        ]
    },
    'OFFERTECH2': {
        'text': '"Information on {$TECH0} could prove most useful to certain of my $PET_PROJECTS2. You will transmit this data at once?"',
        'responses': [
            {'text': '"No. Never mind."', 'action': 'diplo'},
            {'text': '"Yes. Beginning transmission."', 'action': 'diplo'},
            {'text': '"No, but we shall provide you data on $TECH1."', 'action': 'diplo'}
        ]
    },
    'GAVETECH': {
        'text': '"Your data has been received and judged most useful. My thanks."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'GAVETECH1': {
        'text': '"A most generous gift indeed! My thanks!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'GAVETECH2': {
        'text': '"A most generous gift indeed! My thanks! I may have to rethink my opinion of you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'OFFERENERGY': {
        'text': '"And just what manner of sum are we talking about here?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'GAVEENERGY': {
        'text': '"My thanks, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'GAVEENERGY1': {
        'text': '"A most generous sum indeed! My thanks, $TITLE0 $NAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'GAVEENERGY2': {
        'text': '"A most generous sum indeed! My thanks, $TITLE0 $NAME1! I may have to rethink my opinion of you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'NOPATIENCE': {
        'text': 'The $FACTION0 $<0:is:are> ignoring our transmissions, $TITLE2 $NAME3.',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'NOPATIENCEFRIEND': {
        'text': '$TITLE0 $NAME1 has politely declined to speak with you, $TITLE2 $NAME3.',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'PLEA': {
        'text': '"I am under attack by the forces of the $<1:$CHARPEJ8> $TITLE0 $NAME1 of the $FACTION2, who is bent on $EVILAGENDA9. If you will join me in resisting this ruthless invasion I shall speak a $PACTOFBROTHERHOODSISTERHOOD3 with you and provide you with {$NUM0 energy credits} to cover your expenses."',
        'responses': [
            {'text': '"Too bad. You\'re on your own."', 'action': 'diplo'},
            {'text': '"Done. Vendetta upon the $FACTION2!"', 'action': 'diplo'}
        ]
    },
    'PLEATECH': {
        'text': '"I am under attack by the forces of the $<1:$CHARPEJ8> $TITLE0 $NAME1 of the $FACTION2, who is bent on $EVILAGENDA9. If you will join me in resisting this ruthless invasion I shall speak a $PACTOFBORS3 with you and provide you with $NUM0 energy credits to cover your expenses. I shall also share with you all of my information on {$TECH4.}"',
        'responses': [
            {'text': '"Too bad. You\'re on your own."', 'action': 'diplo'},
            {'text': '"Agreed. Vendetta upon the $FACTION2!"', 'action': 'diplo'}
        ]
    },
    'PLEAPACT': {
        'text': '"I appeal to you as a victim of the $<1:$CHARPEJ8> $TITLE0 $NAME1 of the $FACTION2, who has sworn a false $PACTOFBORS5 with you and is actually bent on $EVILAGENDA9. Will you not swear a true Pact with me and help resist $HISHER6 aggression before it is too late and you become $HISHER6 next victim? I shall even provide {$NUM0 credits} to cover your expenses."',
        'responses': [
            {'text': '"You must be joking."', 'action': 'diplo'},
            {'text': '"Well spoken. Vendetta upon the $FACTION2!"', 'action': 'diplo'}
        ]
    },
    'PLEAPACTTECH': {
        'text': '"I appeal to you as a victim of the $<1:$CHARPEJ8> $TITLE0 $NAME1 of the $FACTION2, who has sworn a false $PACTOFBORS5 with you and is actually bent on $EVILAGENDA9. Will you not swear a true Pact with me and help resist $HISHER6 aggression before it is too late and you become $HISHER6 next victim? I shall even provide {$NUM0 credits} to cover your expenses and transmit to you all of my data on {$TECH4.}"',
        'responses': [
            {'text': '"You must be joking."', 'action': 'diplo'},
            {'text': '"Well spoken. Vendetta upon the $FACTION2!"', 'action': 'diplo'}
        ]
    },
    'PROPOSE': {
        'text': '"The $<2:$FACTIONPEJ8> $FACTION2 $<2:has:have> become a serious menace, and meanwhile $TITLE0 $NAME1 spends $<1:his:her:x:x> time $DANCINGNAKED9. I suggest we join forces to crush $HIMHER3 while the time is ripe! We should speak a $PACTOFBORS4 on the matter at once."',
        'responses': [
            {'text': '"Not interested."', 'action': 'diplo'},
            {'text': '"A cunning plan! Vendetta upon the $FACTION2!"', 'action': 'diplo'}
        ]
    },
    'PROPOSEPACT': {
        'text': '"$TITLE5, I have evidence suggesting your so-called $PACTBORS6, $TITLE0 $NAME1 of the $FACTION2 is bent on $EVILAGENDA9 and plans to betray you most ruthlessly. Let us swear our own Pact and teach $HIMHER3 a valuable lesson!"',
        'responses': [
            {'text': '"Enough of your trickery, $TITLE8."', 'action': 'diplo'},
            {'text': '"Agreed. I shall put my forces in motion at once."', 'action': 'diplo'}
        ]
    },
    'INTRODUCEENEMY': {
        'text': '"I have located the settlements of our former colleague $NAME1, who now styles $<1:himself:herself:x:x> \'$TITLE0\' of the $FACTION2 and as far as I can tell spends most of $<1:his:her:x:x> time $DANCINGNAKED3. Having now made several attempts to reason with $<1:him:her:x:x>, I have decided to take action to eliminate this heavily armed menace. If you are willing to provide assistance, I shall speak a $PACTOFBORS4 on the matter."',
        'responses': [
            {'text': '"Having not yet spoken to $NAME1, I must decline."', 'action': 'diplo'},
            {'text': '"Very well, provide me with map data and we shall begin!"', 'action': 'diplo'}
        ]
    },
    'BETRAYFRIEND': {
        'text': '"$NAME0, I need a private word with you. I have pretended friendship to our former colleague $NAME2, but I dislike $<2:his:her:x:x> $<M2:$FACTIONPEJ3> minions and I fear $<2:he:she:x:x> is bent on $EVILAGENDA4. I propose that we speak a $PACTOFBORS5 and together launch a surprise attack against the $FACTION6."',
        'responses': [
            {'text': '"I fear I must decline."', 'action': 'diplo'},
            {'text': '"Agreed. $TITLE1 $NAME2 will never know what hit $<2:him:her:x:x>!"', 'action': 'diplo'}
        ]
    },
    'ENEMYMAP1': {
        'text': '"So, $TITLE0 $NAME1, I see you\'ve run afoul of our little friend $TITLE2 $NAME3. Just between you and me, I\'ve recently obtained a complete map of every major $<M1:$FACTIONADJ4> installation, and I would be more than happy to provide you with a copy in exchange for $NUM0 energy credits."',
        'responses': [
            {'text': '"No thank you, I can deal with $NAME3 myself."', 'action': 'diplo'},
            {'text': '"It\'s a deal."', 'action': 'diplo'}
        ]
    },
    'ENEMYMAP2': {
        'text': '"So, $TITLE0 $NAME1, I see you\'ve run afoul of our little friend $TITLE2 $NAME3. Just between you and me, I\'ve recently obtained a complete map of every major $<M1:$FACTIONADJ4> installation, and I would be more than happy to provide you with a copy in exchange for your files on {$TECH5.}"',
        'responses': [
            {'text': '"No thank you, I can deal with $NAME3 myself."', 'action': 'diplo'},
            {'text': '"It\'s a deal."', 'action': 'diplo'}
        ]
    },
    'METFRIEND0': {
        'text': '"You may be interested to know that I\'ve been in touch with our former colleague $NAME3, who lately has been styling $<3:himself:herself:x:x> $TITLE2 of the $FACTION4. $NAME3 has become quite obsessed with $<3:his:her:x:x> $PETPROJECTS5, but I have had several fruitful conversations with $<3:him:her:x:x>. If you like, I can provide you with $<3:his:her:x:x> commlink frequency."',
        'responses': [
            {'text': '"No thank you, I see no need to speak with $NAME3."', 'action': 'diplo'},
            {'text': '"Yes, that would be most helpful."', 'action': 'diplo'}
        ]
    },
    'METFRIEND0a': {
        'text': '"You may be interested to know that I\'ve been in touch with our former colleague $NAME3, who lately has been styling $<3:himself:herself:x:x> $TITLE2 of the $FACTION4. $NAME3 has become quite obsessed with $<3:his:her:x:x> $PETPROJECTS5, but we have had several fruitful conversations and I believe $<3:he:she:x:x> could provide you with information on {$TECH8.} If you like, I can provide you with $<3:his:her:x:x> commlink frequency."',
        'responses': [
            {'text': '"No thank you, I see no need to speak with $NAME3."', 'action': 'diplo'},
            {'text': '"Yes, that would be most helpful."', 'action': 'diplo'}
        ]
    },
    'METFRIEND1': {
        'text': '"You may be interested to know that I\'ve been in touch with our former colleague $NAME3, who lately has been styling $<3:himself:herself:x:x> $TITLE2 of the $FACTION4. $NAME3 has become quite obsessed with $<3:his:her:x:x> $PETPROJECTS5, but I have had several fruitful conversations with $<3:him:her:x:x>. If you like, I can provide you with $<3:his:her:x:x> commlink frequency in exchange for your files on {$TECH6.}"',
        'responses': [
            {'text': '"No thank you, I see no need to speak with $NAME3."', 'action': 'diplo'},
            {'text': '"Very well, I am transmitting my files on {$TECH6} now."', 'action': 'diplo'}
        ]
    },
    'METFRIEND1a': {
        'text': '"You may be interested to know that I\'ve been in touch with our former colleague $NAME3, who lately has been styling $<3:himself:herself:x:x> $TITLE2 of the $FACTION4. $NAME3 has become quite obsessed with $<3:his:her:x:x> $PETPROJECTS5, but we have had several fruitful conversations and I believe $<3:he:she:x:x> could provide you with information on {$TECH8.} If you like, I can provide you with $<3:his:her:x:x> commlink frequency in exchange for your files on {$TECH6.}"',
        'responses': [
            {'text': '"No thank you, I see no need to speak with $NAME3."', 'action': 'diplo'},
            {'text': '"Very well, I am transmitting my files on {$TECH6} now."', 'action': 'diplo'}
        ]
    },
    'METFRIEND2': {
        'text': '"You may be interested to know that I\'ve been in touch with our former colleague $NAME3, who lately has been styling $<3:himself:herself:x:x> $TITLE2 of the $FACTION4. $NAME3 has become quite obsessed with $<3:his:her:x:x> $PETPROJECTS5, but I have had several fruitful conversations with $<3:him:her:x:x>. If you like, I can provide you with $<3:his:her:x:x> commlink frequency in exchange for a mere $NUM0 energy credits."',
        'responses': [
            {'text': '"No thank you, I see no need to speak with $NAME3."', 'action': 'diplo'},
            {'text': '"Excellent. $NUM0 credits it is, then."', 'action': 'diplo'}
        ]
    },
    'METFRIEND2a': {
        'text': '"You may be interested to know that I\'ve been in touch with our former colleague $NAME3, who lately has been styling $<3:himself:herself:x:x> $TITLE2 of the $FACTION4. $NAME3 has become quite obsessed with $<3:his:her:x:x> $PETPROJECTS5, but we have had several fruitful conversations and I believe $<3:he:she:x:x> could provide you with information on {$TECH8.} If you like, I can provide you with $<3:his:her:x:x> commlink frequency in exchange for a mere {$NUM0 energy credits.}"',
        'responses': [
            {'text': '"No thank you, I see no need to speak with $NAME3."', 'action': 'diplo'},
            {'text': '"Excellent. $NUM0 credits it is, then."', 'action': 'diplo'}
        ]
    },
    'BOTHFRIEND': {
        'text': '"So, I hear you\'ve been in touch with our old colleague $NAME3. Just between us, I find $<3:his:her:x:x> $<M2:$FACTIONPEJ4> minions a bit creepy, but so far we\'ve been able to cooperate and $<3:he:she:x:x> has not tried to interfere in my affairs. Speaking of which, I have a nice {map of $<M1:$FACTIONADJ5> territory} which I\'d be happy to exchange for your information on {$TECH6.}"',
        'responses': [
            {'text': '"No, I don\'t think that will be necessary."', 'action': 'diplo'},
            {'text': '"Yes, actually that would be quite useful."', 'action': 'diplo'}
        ]
    },
    'ANYNEWS': {
        'text': '"Have you heard from $NAME1, recently? I have not been able to locate $<1:him:her:x:x> or $<1:his:her:x:x> $<M1:$FACTIONADJ2> faction since the time of Planetfall, and wanted to continue some of our earlier conversations. If you have $<1:his:her:x:x> comm frequency I could offer $NUM0 energy credits for your trouble."',
        'responses': [
            {'text': '"Nope, haven\'t heard a word."', 'action': 'diplo'},
            {'text': '"Yes, I\'m forwarding $<1:his:her:x:x> comm frequency now."', 'action': 'diplo'}
        ]
    },
    'COMMLINKTECH': {
        'text': '"If you like, I can provide you with the $<M1:$FACTIONADJ2> commlink frequency in exchange for your files on {$TECH0.}"',
        'responses': [
            {'text': '"Never mind."', 'action': 'diplo'},
            {'text': '"Very well, I am transmitting my files on {$TECH0} now."', 'action': 'diplo'}
        ]
    },
    'COMMLINKFREE': {
        'text': '"But of course! I will happily provide you with the $<M1:$FACTIONADJ2> commlink frequency."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'DEMANDATTACK0': {
        'text': '"Your so-called $PACTBROTHERORSISTER0, \'$TITLE1\' $NAME2, has gone mad, and now spends $<2:his:her:x:x> time $DANCINGNAKED9. Won\'t you renounce your Pact with the $FACTION3 to gain my friendship?"',
        'responses': [
            {'text': '"No. The $FACTION3 $<3:is a loyal ally:are loyal allies>."', 'action': 'diplo'},
            {'text': '"Agreed. $TITLE1 $NAME2 will soon find my knife in $HISHER4 back!"', 'action': 'diplo'}
        ]
    },
    'DEMANDATTACK1A': {
        'text': '"Were you aware that my hated enemy, $TITLE1 $NAME2 of the $FACTION3, now spends most of $<2:his:her:x:x> time $DANCINGNAKED9? Let us join forces and put an end to $<2:his:her:x:x> $BADHABITS6!"',
        'responses': [
            {'text': '"Certainly not. $NAME2 is my friend."', 'action': 'diplo'},
            {'text': '"A prudent suggestion--let us begin at once!"', 'action': 'diplo'}
        ]
    },
    'DEMANDATTACK1B': {
        'text': '"My nemesis, $TITLE1 $NAME2 of the $FACTION3, is bent on $IMPLEMENTING_HIS_EVIL_AGENDA8. I propose that you switch allegiances and help me stop $<2:him:her:x:x> before it is too late!"',
        'responses': [
            {'text': '"Certainly not. The $FACTION3 $<3:is my friend:are my friends>."', 'action': 'diplo'},
            {'text': '"A prudent suggestion--let us begin at once!"', 'action': 'diplo'}
        ]
    },
    'DEMANDATTACK2a': {
        'text': '"The $<2:$CHARPEJ8> $TITLE1 $NAME2 and $<2:his:her:x:x> $<M1:$FACTIONPEJ9> minions have ruthlessly attacked my holdings. Will you assist me in repulsing them?"',
        'responses': [
            {'text': '"No. I have pledged Blood Truce with the $FACTION3."', 'action': 'diplo'},
            {'text': '"By all means. Let us rid ourselves of the $<M1:$FACTIONADJ6> nuisance."', 'action': 'diplo'}
        ]
    },
    'DEMANDATTACK2b': {
        'text': '"Your sometime enemy, $TITLE1 $NAME2 of the $FACTION3, who has always irrationally feared my $PET_PROJECTS8, has now brutally attacked my settlements bent on $IMPLEMENTING_HIS_EVIL_AGENDA9. Will you assist me in repulsing $<2:him:her:x:x>?',
        'responses': [
            {'text': '"No.', 'action': 'diplo'},
            {'text': 'I have pledged Blood Truce with the $FACTION3."', 'action': 'diplo'},
            {'text': '"By all means.', 'action': 'diplo'},
            {'text': 'Let us rid ourselves of the $<M1:$FACTIONADJ6> nuisance."', 'action': 'diplo'}
        ]
    },
    'DEMANDATTACK3': {
        'text': '"My mortal enemy, $TITLE1 $NAME2 of the $FACTION3, has brutally attacked my settlements. I\'m afraid I must now insist that you honor our Pact and join my Vendetta against $HIMHER5."',
        'responses': [
            {'text': '"Sorry, I cannot help you right now."', 'action': 'diplo'},
            {'text': '"Very well.', 'action': 'diplo'},
            {'text': 'Let us teach $TITLE1 $NAME2 a lesson."', 'action': 'diplo'}
        ]
    },
    'DEMANDATTACK4': {
        'text': '"My enemy, $TITLE1 $NAME2 of the $FACTION3, has ruthlessly attacked my holdings. Will you assist me in repulsing $HIMHER5?"',
        'responses': [
            {'text': '"No. The $FACTION3 $<3:has:have> done me no wrong."', 'action': 'diplo'},
            {'text': '"By all means.', 'action': 'diplo'},
            {'text': 'Let us rid ourselves of the $<M1:$FACTIONADJ6> nuisance."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE0': {
        'text': '"My $<1:$CHARADJ5> $TITLE0, it has become customary for a minor faction leader such as yourself to remit me a small, ah, let us say \'$FEE8,\' to compensate for the services my forces provide in $PROVIDING_VALUABLE_SERVICES9. In your case I believe {$NUM0 energy credits} would be quite sufficient."',
        'responses': [
            {'text': '"You are a $INSULT6, $NAME3.', 'action': 'diplo'},
            {'text': 'You\'ll get nothing from me."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credit \'$FEE8.\'', 'action': 'diplo'},
            {'text': '"I can pay only $NUM1."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE1': {
        'text': '"Planet is a dangerous world, $TITLE0 $NAME1, and who knows what unforeseen tragedies could befall your fragile $PETPROJECTS8. But if you will provide me with {$NUM0 energy credits,} I shall instruct $MY_ENVIRONMENTAL_POLICE9 to see that no such \'accidents\' occur."',
        'responses': [
            {'text': '"I will not listen to your veiled threats, $NAME3."', 'action': 'diplo'},
            {'text': '"You have a point.', 'action': 'diplo'},
            {'text': 'I shall send $NUM0 credits at once."', 'action': 'diplo'},
            {'text': '"I can afford $NUM1, no more."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE2': {
        'text': '"Let us discuss the situation frankly, $TITLE0 $NAME1. Your $RIGHT_WING_FANTASIES8 $<8:stands:stand> in the way of my plans $TO_CARRY_OUT_MY_MISSION9. I will agree to overlook this state of affairs for the time being, but only in exchange for {$NUM0 energy credits."}',
        'responses': [
            {'text': '"Do not boast of your $BAD_HABITS6 to me, $NAME3."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credits.', 'action': 'diplo'},
            {'text': '"Alas, $NAME3.', 'action': 'diplo'},
            {'text': 'I can pay only $NUM1 credits."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE3': {
        'text': '"$TITLE0, You are in contravention of $THE_ENVIRONMENTAL_CODE9! You must pay the fine of {$NUM0 energy credits} at once or suffer the consequences."',
        'responses': [
            {'text': '"So sue me."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credit \'fine.\'', 'action': 'diplo'},
            {'text': '"Perhaps $NUM1 credits would take care of our little problem?"', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE4': {
        'text': '"Do you tire of our Vendetta so soon, $NAME0? I will call it off for nothing more than your humble apology and {$NUM0 energy credits."}',
        'responses': [
            {'text': '"You deceive yourself, $NAME3.', 'action': 'diplo'},
            {'text': 'Prepare to be crushed."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credits.', 'action': 'diplo'},
            {'text': '"Apology, yes, but only $NUM1 credits."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE5a': {
        'text': '"You have now felt the fist within the $<M1:$FACTIONADJ4> glove, $TITLE0. Pay me {$NUM0 energy credits} at once and I shall spare you further indignity."',
        'responses': [
            {'text': '"Save your petty threats for someone else, $NAME3."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credits.', 'action': 'diplo'},
            {'text': '"I can pay only $NUM1 credits."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE5b': {
        'text': '"Your strength is impressive, $TITLE0, but do not underestimate my ability to cause you harm. Pay me {$NUM0 energy credits} at once and I shall forgive your past offenses."',
        'responses': [
            {'text': '"You are in no position to make demands, $NAME3."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credits.', 'action': 'diplo'},
            {'text': '"I can pay $NUM1 credits, or I can destroy you utterly.', 'action': 'diplo'},
            {'text': 'Your choice."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE6': {
        'text': '"My $PETPROJECTS9 $<9:is:are> in sore need of funding, $NAME5. Will you send me {$NUM0 energy credits} in honor of our longtime friendship?"',
        'responses': [
            {'text': '"No.', 'action': 'diplo'},
            {'text': 'Cease this parasitic snivelling at once!"', 'action': 'diplo'},
            {'text': 'Give $NUM0 credits.', 'action': 'diplo'},
            {'text': '"$NUM1 credits and not a joule more."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE7': {
        'text': '"Your power is formidable, $TITLE0 $NAME1, but my own forces are not insignificant, and if you are to continue to hold this planet in your grip I must insist on a piece of the action, to the tune of {$NUM0 energy credits."}',
        'responses': [
            {'text': '"Begone!', 'action': 'diplo'},
            {'text': 'Your faction is no longer important to my plans."', 'action': 'diplo'},
            {'text': '"Very well.', 'action': 'diplo'},
            {'text': 'Take $NUM0 credits and see that you do not interfere."', 'action': 'diplo'},
            {'text': '"You overestimate my riches.', 'action': 'diplo'},
            {'text': '$NUM1 seems a better number."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE8': {
        'text': '"You are rich, $TITLE0 $NAME1, and I am poor. My teeming masses grow restless at this disparity; can you not spare me {$NUM0 credits} to ease their wretched lives?"',
        'responses': [
            {'text': '"Perhaps you should spend your pennies more wisely, $TITLE3."', 'action': 'diplo'},
            {'text': '"Here are $NUM0 credits.', 'action': 'diplo'},
            {'text': 'Do not waste them."', 'action': 'diplo'},
            {'text': '"You overestimate my wealth. $NUM1 seems a better number."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE9': {
        'text': '"Your past crimes against the $FACTION6 are well remembered, $TITLE0 $NAME1, and my followers itch for revenge. Only reparations of {$NUM0 energy credits} will quell their hatred."',
        'responses': [
            {'text': '"You are the only criminal here, $TITLE3."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credits.', 'action': 'diplo'},
            {'text': '"Sorry.', 'action': 'diplo'},
            {'text': 'I can pay only $NUM1 credits."', 'action': 'diplo'}
        ]
    },
    'DEMANDBRIBE10': {
        'text': '"Your enemies have put a price on your head, $TITLE0 $NAME1, but I have other business to attend to and am willing to call off this Vendetta in exchange for {$NUM0 energy credits."}',
        'responses': [
            {'text': '"You\'ll not get a joule from me, $NAME4."', 'action': 'diplo'},
            {'text': 'Pay $NUM0 credits.', 'action': 'diplo'},
            {'text': '"I can pay only $NUM1 credits."', 'action': 'diplo'}
        ]
    },
    'WEASELOUT': {
        'text': '"I\'m warning you, $NAME1! $NUM0 energy credits or else!"',
        'responses': [
            {'text': '"Shrivel and die, you $NATURE_LOONY6!"', 'action': 'diplo'},
            {'text': '"Oh very well, $NUM0 credits it is."', 'action': 'diplo'}
        ]
    },
    'WEASELEDOUT': {
        'text': '"$NUM2 it is, then, but do not abuse my patience further."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'HALFBRIBE': {
        'text': '"Then keep your worthless gift."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'DEMANDTECH0': {
        'text': '"To be blunt, $TITLE1 $NAME2, your $BADHABITS9 $<9:scares:scare> me and it is time for a reckoning between us. I will have your files on {$TECH0,} and I will have them now."',
        'responses': [
            {'text': '"When you pry them from my cold dead fingers, $TITLE3 $NAME4."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH1': {
        'text': '"$TITLE1 $NAME2, you have been accused of $SPOUTING_TREE_CRAZY_PRATTLE9, and many among my followers itch for a military solution. Will you share your files on {$TECH0} as a sign of good faith, or shall I turn my minions loose to seize them?"',
        'responses': [
            {'text': '"Have you no shame, $TITLE3 $NAME4?', 'action': 'diplo'},
            {'text': 'Do your own research."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH2': {
        'text': '"$NAME2, you may spend your days $DANCING_NAKED_THROUGH_THE_TREES9 for all I care, but I will not allow you to hold out on me when it comes to matters of research. Will you disgorge your files on {$TECH0} at once? I do so hope violence between us will not become necessary."',
        'responses': [
            {'text': '"Silence!', 'action': 'diplo'},
            {'text': 'Enough of your veiled threats."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH3': {
        'text': '"Perhaps you have now learned your lesson, $TITLE1 $NAME2. Will you trade me your data on {$TECH0} for an end to this Vendetta, or will you risk total destruction at my hands?"',
        'responses': [
            {'text': '"Do your worst, $TITLE3 $NAME4."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH4': {
        'text': '"There is yet time to reconsider your earlier arrogance. Will you trade me your data on {$TECH0} for an end to this Vendetta, $TITLE1 $NAME2, or will you risk total destruction at my hands?"',
        'responses': [
            {'text': '"Do your worst, $TITLE3 $NAME4."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH5': {
        'text': '"Your research on {$TECH0} is most fascinating, $TITLE1 $NAME2. Won\'t you share it with your $PACTBROTHERORSISTER5?"',
        'responses': [
            {'text': '"No. Go do your own research."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH6': {
        'text': '"Your bases are at my mercy, $NAME1. If you wish to escape with your skin it will also cost you your data on {$TECH6.}"',
        'responses': [
            {'text': '"You shall pay for this treachery, $TITLE3 $NAME4!"', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH6.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH7': {
        'text': '"Your faction is indeed a mighty one, $TITLE1 $NAME2, but my forces are yet strong and I shall not allow you to plunder the wealth of this planet without cutting me in for a share. My price is your data on {$TECH0.}"',
        'responses': [
            {'text': '"Your faction is no longer significant, $TITLE3 $NAME4."', 'action': 'diplo'},
            {'text': 'Transmit data on $TECH0.', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH8': {
        'text': '"$TITLE1 $NAME2, my followers remain suspicious that you plan to repeat your past crimes against us, and they urge me this time to attack preemptively. Will you help me mollify them by transmitting your data on {$TECH0?}"',
        'responses': [
            {'text': '"You must think me quite stupid, $TITLE3, to fall for such a ploy."', 'action': 'diplo'},
            {'text': '"Very well, I shall transmit at once."', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH9': {
        'text': '"An emergency has arisen at one of my bases, $TITLE1 $NAME2! Lives are at stake and information on {$TECH0} is required immediately! Can you help?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'DEMANDTECH9A': {
        'text': '"Your fabricated tales will get you nowhere, $TITLE3 $NAME4."',
        'responses': [
            {'text': '"By all means!', 'action': 'diplo'},
            {'text': 'I shall transmit data on $TECH0 at once!"', 'action': 'diplo'},
            {'text': '"I will gladly help, if you can spare $NUM0 to cover my expenses."', 'action': 'diplo'},
            {'text': '"In exchange for your own data on $TECH6, perhaps?"', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH10': {
        'text': '"Information on {$TECH0} could prove quite useful to my $PET_PROJECTS9. Can you transmit it to me as a personal favor?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'DEMANDTECH10A': {
        'text': '"Nice try, $TITLE3 $NAME4, but that information is confidential."',
        'responses': [
            {'text': '"Very well, begin transmission."', 'action': 'diplo'},
            {'text': '"I am willing, if you can spare $NUM0 to cover my expenses."', 'action': 'diplo'},
            {'text': '"In exchange for your own data on $TECH6, perhaps?"', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH11': {
        'text': '"$TITLE1 $NAME2, I am concerned that you appear to be withholding scientific data in violation of the UN Charter for this mission. Please release your files on {$TECH0} to me at once!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'DEMANDTECH11A': {
        'text': '"Ha! Perhaps you should ask the UN to invoke \'sanctions\'! Ha ha ha!"',
        'responses': [
            {'text': '"How could that have slipped my mind? I shall transmit at once."', 'action': 'diplo'},
            {'text': '"As you wish, but I\'ll require $NUM0 credits to cover my expenses."', 'action': 'diplo'},
            {'text': '"And you will reciprocate with your own data on $TECH6?"', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH12': {
        'text': '"Your enemies offer great rewards for your destruction, $TITLE1 $NAME2, but I will close my ears to their whisperings in exchange for your knowledge of {$TECH0} and {$TECH6.}"',
        'responses': [
            {'text': '"Take your treacherous mouth elsewhere, $NAME4."', 'action': 'diplo'},
            {'text': '"But of course I shall transmit immediately!"', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH13': {
        'text': '"Your enemies offer great rewards for your destruction, $TITLE1 $NAME2, but I will close my ears to their whisperings in exchange for your knowledge of {$TECH0.}"',
        'responses': [
            {'text': '"Take your ', 'action': 'diplo'},
            {'text': 'treacherous mouth elsewhere, $NAME4."', 'action': 'diplo'},
            {'text': '"But of course I shall transmit immediately!"', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH14': {
        'text': '"Your enemies offer generous rewards for your destruction, $TITLE1 $NAME2, but I will close my ears to their whisperings in exchange for your knowledge of {$TECH0,} {$TECH6,} and {$TECH8.}"',
        'responses': [
            {'text': '"Take your treacherous mouth elsewhere, $NAME4."', 'action': 'diplo'},
            {'text': '"But of course I shall transmit immediately!"', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'DEMANDTECH15': {
        'text': '"Your enemies offer a king\'s ransom for your destruction, $TITLE1 $NAME2, but I will close my ears to their whisperings in exchange for your knowledge of {$TECH0,} {$TECH6,} {$TECH8,} and {$TECH9.}"',
        'responses': [
            {'text': '"Take your treacherous mouth elsewhere, $NAME4."', 'action': 'diplo'},
            {'text': '"But of course I shall transmit immediately!"', 'action': 'diplo'},
            {'text': 'Consult Datalinks.', 'action': 'diplo'}
        ]
    },
    'AGREEDENERGY': {
        'text': 'Agreed. $NUM0 credits it is, then.',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'AGREEDTECH': {
        'text': 'Good enough for me.',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'DEMANDTECHAGAIN1': {
        'text': '"I cannot afford your price, $NAME2. Will you transmit your data on {$TECH0} or not?"',
        'responses': [
            {'text': '"Sorry. No check, no tech."', 'action': 'diplo'},
            {'text': '"Oh, have it your way, then."', 'action': 'diplo'}
        ]
    },
    'DEMANDTECHAGAIN2': {
        'text': '"I cannot trust you with that information, $NAME2. So you are refusing to transmit your files on {$TECH0?}"',
        'responses': [
            {'text': '"That\'s right. Make a trade or stop wasting my time."', 'action': 'diplo'},
            {'text': '"Oh, never mind. I\'ll transmit it."', 'action': 'diplo'}
        ]
    },
    'ASKFORLOAN1': {
        'text': '"$TITLE0 $NAME1, I must confess I am a bit strapped for cash. If you can spare me $NUM0 energy credits, I can make generous payments of $NUM1 credit per year for $NUM2 years."',
        'responses': [
            {'text': '"I am not your personal moneylender, $TITLE2 $NAME3."', 'action': 'diplo'},
            {'text': '"Agreed. But if you rob me you shall feel my wrath."', 'action': 'diplo'},
            {'text': '"I can lend you half of that, and no more."', 'action': 'diplo'}
        ]
    },
    'ASKFORLOAN2': {
        'text': '"$TITLE0 $NAME1, I must confess I am a bit strapped for cash. If you can spare me $NUM0 energy credits, I can make generous payments of $NUM1 credits per year for $NUM2 years."',
        'responses': [
            {'text': '"I am not your personal moneylender, $TITLE2 $NAME3."', 'action': 'diplo'},
            {'text': '"Agreed. But if you rob me you shall feel my wrath."', 'action': 'diplo'},
            {'text': '"I can lend you half of that, and no more."', 'action': 'diplo'}
        ]
    },
    'BREAKPACT': {
        'text': '"Enough of your $BADHABITS3, $TITLE0 $NAME1! From this day we are $PACTBROTHERSORSISTERS2 no more!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SWEARAPACT': {
        'text': '"$TITLE0 $NAME1. Our visions are compatible and our interests convergent. Will you swear a {$PACTOFBROTHERORSISTERHOOD2} with me that we may sweep all before us?"',
        'responses': [
            {'text': '"With great pleasure."', 'action': 'diplo'},
            {'text': '"Sorry, my plans dictate otherwise."', 'action': 'diplo'}
        ]
    },
    'RANSOMDEMAND': {
        'text': '"$TITLE0 $NAME1, my forces are strong and my troops are mobilized. If you do not return {$BASENAME2} to my possession immediately I shall destroy you utterly."',
        'responses': [
            {'text': '"Never! $BASENAME2 shall remain mine for all time!"', 'action': 'diplo'},
            {'text': '"Very well, let us trade land for peace."', 'action': 'diplo'}
        ]
    },
    'RANSOMTREATY': {
        'text': '"This is a Vendetta I never truly wanted, $TITLE0 $NAME1. If you will but call it off and sign a Treaty of Friendship, I shall return {$BASENAME2} to your possession."',
        'responses': [
            {'text': '"Fair enough. Let us put this conflict behind us."', 'action': 'diplo'},
            {'text': '"Hah! I shall soon retake $BASENAME2, your petty bargain notwithstanding."', 'action': 'diplo'}
        ]
    },
    'OFFERTRUCE': {
        'text': '"Most prudent. In that case, I am willing to pledge Blood Truce."',
        'responses': [
            {'text': '"So pledged. I thank you."', 'action': 'diplo'},
            {'text': '"No! I shall see this through to the bitter end."', 'action': 'diplo'}
        ]
    },
    'MUSTTRUCE': {
        'text': '"Only with deepest bitterness do I accept this defeat and offer to pledge Blood Truce with you."',
        'responses': [
            {'text': '"And only with greatest scorn do I accept it!"', 'action': 'diplo'},
            {'text': '"Hah! Defend yourself or be crushed!"', 'action': 'diplo'}
        ]
    },
    'WANTTOTRUCE0': {
        'text': '"This Vendetta wastes life and resources. Shall we pledge Blood Truce and have an end to it?"',
        'responses': [
            {'text': '"Well spoken. Let it be done."', 'action': 'diplo'},
            {'text': '"Never! Prepare to be annihilated!"', 'action': 'diplo'}
        ]
    },
    'WANTTOTRUCE1': {
        'text': '"Fighting between the two of us only allows the others to grow stronger. We should pledge Blood Truce before we destroy one another."',
        'responses': [
            {'text': '"Agreed. Let us so pledge."', 'action': 'diplo'},
            {'text': '"It is you who will be destroyed, $TITLE2 $NAME3!"', 'action': 'diplo'}
        ]
    },
    'WANTTOTRUCE2': {
        'text': '"Your forces are formidable, $NAME1, and I see I was unwise to test your patience. Allow me to pledge Blood Truce and make amends."',
        'responses': [
            {'text': '"Very well. See that it does not happen again."', 'action': 'diplo'},
            {'text': '"Too late, $NAME3. Now I shall destroy you!"', 'action': 'diplo'}
        ]
    },
    'TECHTRUCE': {
        'text': '"To secure a Blood Truce, I offer all of our data on {$TECH0.}"',
        'responses': [
            {'text': '"Accepted."', 'action': 'diplo'},
            {'text': '"Your pathetic research does not impress me."', 'action': 'diplo'},
            {'text': '"I must consult the Datalinks."', 'action': 'diplo'}
        ]
    },
    'ENERGYTRUCE': {
        'text': '"If you will but stay your hand, I shall send you {$NUM0 energy credits} to compensate your losses."',
        'responses': [
            {'text': 'Pledge Blood Truce.', 'action': 'diplo'},
            {'text': '"I have no interest in bribes."', 'action': 'diplo'}
        ]
    },
    'TRUCEPLEASE': {
        'text': '"I surrender, mighty $TITLE0 $NAME1, for my defeat is abject and total. If you will but have mercy upon me, I shall give you all of my energy credits ($NUM0) and share all of my research data ($NUM1 new $<#1:tech:techs>). I shall never trouble you again."',
        'responses': [
            {'text': '"Very well, but you must swear a Pact to serve me."', 'action': 'diplo'},
            {'text': '"No. Destroying you will be a service to humanity."', 'action': 'diplo'}
        ]
    },
    'PROTOPACT': {
        'text': '"I am pleased to report that my engineers have completed the new $UNITTYPE0 prototype ($STATS1)! The first units are entering service now. Would you care to share prototype data?"',
        'responses': [
            {'text': '"No. My prototype data is too sensitive."', 'action': 'diplo'},
            {'text': '"Yes, let us combine our prototyping efforts!"', 'action': 'diplo'}
        ]
    },
    'PROTORIVAL': {
        'text': '"I must caution you that my engineers have completed an advanced $UNITTYPE0 prototype ($STATS1). The first units are entering service now, rendering my forces practically invincible."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'NOTORIETY': {
        'text': '"I am well aware of your reputation for treachery, $TITLE0 $NAME1. I shall merely confine myself to remarking that two can play at that game."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MOREWAR': {
        'text': '"So be it! Vendetta upon you, $NAME1! You and your $FACTIONPEJ2 minions shall be obliterated to the last man."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'OFFERTREATY': {
        'text': '"For the record, I have no quarrel with you, $TITLE0 $NAME1, nor with your $<M1:$FACTIONADJ2> followers. Let us sign a Treaty of Friendship and coexist in peace."',
        'responses': [
            {'text': 'Sign treaty.', 'action': 'diplo'},
            {'text': '"Sorry. I cannot accept such a restrictive arrangement."', 'action': 'diplo'}
        ]
    },
    'OFFERTREATY2': {
        'text': '"Our Blood Truce expires soon, $TITLE0 $NAME1, as I am sure you are aware. Shall we make the peace between us permanent by signing a Treaty of Friendship?"',
        'responses': [
            {'text': 'Sign Treaty.', 'action': 'diplo'},
            {'text': '"No. I cannot be so bound--and perhaps I have other plans."', 'action': 'diplo'}
        ]
    },
    'ENERGYTREATY': {
        'text': '"Would a {$NUM0 credit} contribution towards your $PETPROJECTS2 change your mind?"',
        'responses': [
            {'text': 'Sign treaty.', 'action': 'diplo'},
            {'text': '"My affection cannot be purchased, $TITLE0 $NAME1."', 'action': 'diplo'}
        ]
    },
    'MILDPACT': {
        'text': '"My apologies for presuming upon our friendship, $NAME3. It was most unbecoming of me."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MILDTREATY': {
        'text': '"Have it your way, then, $TITLE0 $NAME1, but bear in mind that friendship is a two way street."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'MILD': {
        'text': '"I find your unwillingness to cooperate disturbing, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REBUFFEDPACT': {
        'text': '"Do not presume to insult me, $TITLE0 $NAME1, $PACTBROTHERSORSISTERS2 though we may be."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REBUFFEDTREATY': {
        'text': '"I\'ll let that pass for now, but you may in time have cause to regret such arrogance."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REBUFFED': {
        'text': '"Perhaps you should look to your defenses, $NAME0, for you tread on dangerous ground."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'LOWPATIENCEPACT': {
        'text': '"I will of course speak with you, $NAME0, but please hurry for I have little time."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'LOWPATIENCE': {
        'text': '"State your case quickly, $NAME0, for I am quite busy."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WHATSUPPACT': {
        'text': '"Always a pleasure to be of service, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WHATSUPTREATY': {
        'text': '"Always a pleasure to be of service, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WHATSUP': {
        'text': '"So, $TITLE0 $NAME1, what do you have to say for yourself?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'HELLOPACT': {
        'text': '"Well met, $TITLE1. May our $NAME0 endure forever!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'HELLOTREATY': {
        'text': '"Our friendship is a strong one, $TITLE1 $NAME2. Long may it remain so."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'HELLO': {
        'text': '"I am pleased that you have refrained from interference in my $PETPROJECTS3, $TITLE1 $NAME2. You are a most prudent leader."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WRONGEDENEMY': {
        'text': '"Word has it you most brutally betrayed $TITLE0 $NAME1 of the $FACTION2. Though I shan\'t shed any tears for $HIMHER3, I suggest you refrain from trying the same with me."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WRONGEDMIGHTY': {
        'text': '"A word of warning, $TITLE4 $NAME5. I am quite aware of the treachery you committed against $TITLE0 $NAME1 of the $FACTION2, and shall show no mercy whatsoever if you are so foolish as to attempt such a deed against me."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'WRONGEDMEEK': {
        'text': '"$TITLE0 $NAME1 of the $FACTION2 was a fool to trust you, $TITLE4. I shall remain on my guard so as not to be proven likewise."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT1GOOD': {
        'text': '"You are most wise, $TITLE0 $NAME1, to keep your subjects under tight control. The common man cannot be trusted to manage his own affairs--democracy is the first cousin of anarchy."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT1BAD2': {
        'text': '"You may speak of order and security, $TITLE0 $NAME1, but your Police State is nothing more than a brutal dictatorship, and a slap in the face to all who truly value human life."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT1BAD3': {
        'text': '"Your police state is godless and wretched, $TITLE0 $NAME1, and your brutal crimes cry out to God for punishment. I pray that you will find the Lord\'s salvation while your soul can yet be saved."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT1WAR2': {
        'text': '"Your brutal Police State is a repudiation of everything this mission originally stood for. I have warned you against this path, $TITLE0 $NAME1, and now I must make it my duty to destroy you before you can reduce this planet to slavery."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT1WAR3': {
        'text': '"You are a wretched unbeliever, $TITLE0 $NAME1, and your sins cry out to God for punishment. In the Lord\'s name I now pronounce Vendetta upon you, that by destroying your abomination of a Police State I may redeem the souls of your followers while there is yet hope for their salvation!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT1PACT2': {
        'text': '"Your brutal Police State is a repudiation of everything this mission originally stood for. I have warned you against this path, $TITLE0 $NAME1, and now I cannot continue our $PACT2 while you reduce this planet to slavery."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT1PACT3': {
        'text': '"You are a brutal tyrant, $TITLE0 $NAME1, and your sins cry out to God for punishment. Having made my utmost effort to save your soul, it is now the Lord\'s will that I renounce our $PACT2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT2GOOD': {
        'text': '"You are a wise and benevolent leader, $TITLE0 $NAME1, to have perceived the lasting benefits of a free society even in these difficult times. My hat is off to you."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT2BAD1': {
        'text': '"$TITLE0 $NAME1, you must surely realize that Democracy is a menace to right-thinking people everywhere. Common citizens cannot be allowed to question the decisions of their rulers! I urge you to impose strict police control at once!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT2BAD3': {
        'text': '"$TITLE0 $NAME1, your so-called \'Democracy\' is godless and wretched. True freedom and happiness are only to be found in God\'s love, and I urge you to repent your sins and open your heart to the Lord."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT2WAR1': {
        'text': '"$TITLE0 $NAME1, your crusade for Democracy constitutes a direct threat to my position as leader of the $FACTIONNOUN3. I have warned you against poisoning the minds of common drones with these seditious slogans, and now I shall take military action to stop you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT2WAR3': {
        'text': '"You are a wretched unbeliever, $TITLE0 $NAME1, and your sins cry out to God for punishment. In the Lord\'s name I now pronounce Vendetta upon you, that by destroying your so-called \'Democracy\' I may redeem the souls of your followers while there is yet hope for their salvation!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT2PACT1': {
        'text': '"$TITLE0 $NAME1, your crusade for \'Democracy\' constitutes a direct threat to my position as leader of the $FACTIONNOUN3. You have persisted against my warnings in poisoning the minds of common drones with these seditious slogans, and now I must renounce our $PACT2!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT2PACT3': {
        'text': '"$TITLE0 $NAME1, your so-called \'Democracy\' is a godless, immoral, garbage heap abuzz with indecent, obscene, and even outright criminal activity. Since you have refused to clean up this cess pool yourself, it becomes my moral duty to renounce our $PACT2!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT3GOOD': {
        'text': '"It is a joy to commune with a fellow believer, $TITLE0 $NAME1. I trust your conscience rests easy in the hands of the good Lord."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT3BAD1': {
        'text': '"Have you no intellectual integrity whatsoever, $TITLE0 $NAME1? It pains me to see an educated person pointlessly cripple $<1:himself:herself::> with the pathetic fantasy of a creator and afterlife. Will you not put aside medieval mythology and join the rest of us in the third millenium?"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT3BAD2': {
        'text': '"$TITLE0 $NAME1, it pains me to see you supporting fundamentalist zealotry at the expense of intellectual progress, human dignity, and virtually any other worthwhile value. Let remind you that we are living in the third millenium, and urge you to put your religion aside as the relic that it is."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT3WAR1': {
        'text': '"Well, $NAME1, I see you continue to spout your sanctimonious religious prattle as usual, but can your faith stand up to my superior military? Vendetta upon you, $TITLE0! Best start saying your prayers."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT3WAR2': {
        'text': '"$TITLE0 $NAME1, your religious extremism seeks to turn back the clock to the brutal ignorance of centuries past. The civilized inhabitants of this world will not stand by while you promote fundamentalist zealotry at the expense of intellectual progress, human dignity, and virtually any other worthwhile value. Vendetta upon you, $NAME1! Your worthless prayers will not help you now!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT3PACT1': {
        'text': '"You have been a useful ally, $TITLE0 $NAME1, but I simply can no longer abide your self-righteous followers and their saccharine religious platitudes. Consider our $PACT2 at an end."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL0CAT3PACT2': {
        'text': '"$TITLE0 $NAME1, your religious extremism seeks to turn back the clock to the brutal ignorance of centuries past. I cannot in good conscience remain in this $PACT2 while you go on promoting fundamentalist zealotry at the expense of intellectual progress, human dignity, and virtually any other worthwhile value."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT1GOOD': {
        'text': '"The health and vitality of your free market economy is to be admired, my good $TITLE0. My congratulations."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT1BAD2': {
        'text': '"It appalls me that you seek to perpetuate the crimes of the unjust capitalist system here on this young world, $TITLE0. I must appeal to your basic sense of justice, $NAME1, and implore you to consider a more equitable distribution of goods."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT1BAD3': {
        'text': '"Your exploitation of Planet\'s delicate environment is entirely unacceptable, $TITLE0 $NAME1. Any market economy must be carefully controlled to prevent permanent damage to the local ecology. I implore you to desist from your free market stance at once."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT1WAR2': {
        'text': '"$TITLE0 $NAME1, I have warned you against these evil capitalist economics you have embraced. It is now my moral duty to eradicate your faction before such an unjust system can take root on this young world!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT1WAR3': {
        'text': '"Your systematic rape of Planet\'s limited resources is unforgiveable, $TITLE0 $NAME1. Since you have failed to heed my warnings on this matter, I see no other choice but to use military force to put an end to the environmental crimes you commit in the name of market economics. Vendetta upon you, $TITLE0 $NAME1, in the name of Planet!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT1PACT2': {
        'text': '"$TITLE0 $NAME1, I have warned you against these evil capitalist economics you have embraced. My warnings have gone unheeded, however, and it is now my moral duty to renounce our $PACT2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT1PACT3': {
        'text': '"Your crimes against the environment appall me, $TITLE0 $NAME1. I have always argued that the stability and preservation of Planet\'s fragile native ecosystem must be our first priority, not market economics. As you have persisted in defying this fundamental principle, I am now forced to renounce our $PACT2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT2GOOD': {
        'text': '"Your society\'s willingness to share its prosperity equally among even its lowliest members sets an example we should all follow, $TITLE0 $NAME1. I commend you."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT2BAD1': {
        'text': '"Your Planned economy is wrongheaded and inefficient, $TITLE0 $NAME1, and stifles the just and proper flow of capital on this planet. I hope you will soon open your markets to a more realistic model."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT2BAD3': {
        'text': '"$TITLE0 $NAME1, your Planned economics are wasteful. More to the point, your ballooning population and inefficient, polluting industry will soon cause permanent damage to Planet\'s fragile environment. I am sure your concerns are humanitarian in nature, but in the long run your people will benefit from a carefully regulated Green economy."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT2WAR1': {
        'text': '"I see my warnings have gone unheeded, $TITLE0 $NAME1. I shall not allow your Planned economics to stifle the just and proper flow of capital on this planet. I shall now use all means at my disposal to rid this world of the evils of communism and nationalized industry! Vendetta upon you, $TITLE0 $NAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT2WAR3': {
        'text': '"$TITLE0 $NAME1, your wasteful Planned economics threaten to bury this planet in human garbage and industrial waste. Since you have failed to heed my warnings on this matter, I see no other choice but to use military force to put an end to your environmental crimes. Vendetta upon you, $TITLE0 $NAME1, in the name of Planet!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT2PACT1': {
        'text': '"I see my warnings have gone unheeded, $TITLE0 $NAME1. I shall not allow your Planned economics to stifle the just and proper flow of capital on this planet. I must now renounce our $PACT2 lest you plunge this world into the abyss of communism and nationalized industry!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT2PACT3': {
        'text': '"I see my warnings have gone unheeded, $TITLE0 $NAME1. Your inefficient collective factories continue to belch industrial waste, and you have made no efforts to contain your rampant population growth. Your lack of concern for Planet\'s ecology compels me to renounce our $PACT2!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT3GOOD': {
        'text': '"$TITLE0 $NAME1, your respect for Planet\'s fragile ecosystems is much appreciated. I can only hope that others will follow your excellent example."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT3BAD1': {
        'text': '"$TITLE0 $NAME1, your impractical Green economics are causing irreparable harm to legitimate business interests. I can only hope you will not completely wreck our economy with this nonsense."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT3BAD2': {
        'text': '"We are the last survivors of the human race, $TITLE0 $NAME1. Surely you must recognize that well-managed population and industrial growth must take precedence over the complaints-du-jour of whining environmental idealists. I urge you to renounce your extremist Green position."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT3WAR1': {
        'text': '"$TITLE0 $NAME1, your whimpering Green idealism has become an unacceptable impediment to legitimate economic progress. Since you show no signs of tempering your extremism with a measure of common sense, I shall now terminate your faction as a matter of simple good business practice."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT3WAR2': {
        'text': '"$TITLE0 $NAME1, your misguided Green extremism can no longer be tolerated. Since you persist in blocking the necessary growth of population and industry, I have no choice but to resort to military force. Vendetta upon you, $TITLE0 $NAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT3PACT1': {
        'text': '"$TITLE0 $NAME1, I can no longer abide your whimpering Green extremism. Since you refuse to balance your radical idealism with the legitimate economic needs of the human race, I now find it necessary to terminate our $PACT2, effective immediately."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL1CAT3PACT2': {
        'text': '"I once thought our interests were compatible, $TITLE0 $NAME1, but your continued insistence on these radical Green economics at the expense of the social development of the human race has convinced me otherwise. I must therefore end our $PACT2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT1GOOD': {
        'text': '"I am pleased that you understand the brutal realities of life on this planet, $TITLE0 $NAME1. Military power is key, for only the strong shall survive here."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT1BAD2': {
        'text': '"$TITLE0 $NAME1, your so-called faction is little more than a summer camp for extremists and malcontents. Be warned that I have heard your rantings about \'power\' and I shall not stand idly by while you build a private army to conquer this planet."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT1BAD3': {
        'text': '"$TITLE0 $NAME1, your so-called faction is little more than a summer camp for extremists and malcontents. Be warned that I have heard your rantings about \'power\' and I shall not stand idly by while you build a private army to conquer this planet."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT1WAR2': {
        'text': '"Your talk of \'power\' is merely a pretext for allowing private citizens to possess military grade weapons. Since even a child can see you are planning an armed takeover of this planet, $TITLE0 $NAME1, I must now take it upon myself to destroy you before you become unstoppable."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT1WAR3': {
        'text': '"Your talk of \'power\' is merely a pretext for allowing private citizens to possess military grade weapons. Since even a child can see you are planning an armed takeover of this planet, $TITLE0 $NAME1, I must now take it upon myself to destroy you before you become unstoppable."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT1PACT2': {
        'text': '"All your talk of \'power\' is merely a pretext for allowing private citizens to possess military grade weapons. I shall not be your accomplice in an armed takeover of this planet, $TITLE0 $NAME1--you may consider our $PACT2 at an end."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT1PACT3': {
        'text': '"All your talk of \'power\' is merely a pretext for allowing private citizens to possess military grade weapons. I shall not be your accomplice in an armed takeover of this planet, $TITLE0 $NAME1--you may consider our $PACT2 at an end."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT2GOOD': {
        'text': '"$TITLE0 $NAME1, your research facilities are the envy of the Planet, and none can surpass the expertise of your scientists. I warmly commend you for tireless pursuit of knowledge."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT2BAD1': {
        'text': '"What evils are you cooking up under the guise of \'research\' and \'knowledge\', $TITLE0 $NAME1? You may be fooling the others, but I know you are up to no good."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT2BAD3': {
        'text': '"$TITLE0 $NAME1, we do not have the time and resources to waste on your endless pursuit of pure \'knowledge\'. We must devote ourselves to industrial expansion and economic growth so that the people of this planet can achieve prosperity."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT2WAR1': {
        'text': '"$TITLE0 $NAME1, I cannot allow your research programs to continue any longer unchecked. You may try to hide it, but your so-called pursuit of \'knowledge\' is nothing but a covert weapons research program. I shall therefore neutralize your faction and place these technologies in responsible hands."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT2WAR3': {
        'text': '"$TITLE0 $NAME1, I cannot allow your research programs to continue any longer unchecked. You may try to hide it, but your so-called pursuit of \'knowledge\' is nothing but a covert weapons research program. I shall therefore neutralize your faction and place these technologies in responsible hands."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT2PACT1': {
        'text': '"I have warned you, $TITLE0 $NAME1, that I cannot abide the covert weapons research that you have undertaken in the name of \'knowledge\'. I must now declare our $PACT2 null and void."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT2PACT3': {
        'text': '"$TITLE0 $NAME1, your pursuit of pure \'knowledge\' no longer squares with my own priorities. I must therefore end our $PACT2."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT3GOOD': {
        'text': '"$TITLE0 $NAME1, your factories are efficient and your wealth is impressive. Surely none can stand against your raw industrial might."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT3BAD1': {
        'text': '"$TITLE0 $NAME1, your shameless pursuit of \'wealth\' is shocking. Pray do not grow too fat and weak, lest someone decide to carve you up."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT3BAD2': {
        'text': '"$TITLE0 $NAME1, your open and shameless pursuit of \'wealth\' is offensive to thinkers such as myself. Perhaps you would be wise to better conceal your greed."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT3WAR1': {
        'text': '"Your greedy pursuit of \'wealth\' disgusts me, $TITLE0 $NAME1. You have grown fat and weak, and now I shall destroy you."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT3WAR2': {
        'text': '"Your open and shameless pursuit of \'wealth\' is no longer acceptable, $TITLE0 $NAME1. Vendetta upon you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT3PACT1': {
        'text': '"I shall not continue to associate a faction grown fat and weak in the shameless pursuit of \'wealth\'. Consider our $PACT2 at an end, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL2CAT3PACT2': {
        'text': '"I shall not continue to associate a faction grown fat and weak in the shameless pursuit of \'wealth\'. Consider our $PACT2 at an end, $TITLE0 $NAME1."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT1GOOD': {
        'text': '"I salute you, $TITLE0 $NAME1, in your wise recognition of the benefits of a cybernetic society. Only through a marriage of man and machine can biological life truly achieve greatness."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT1BAD2': {
        'text': '"You may think that machines will make you better, $TITLE0 $NAME1, but the fallacy is obvious: only by celebrating the very essences of our biology--frail or not, imperfect or not--can we truly achieve our full potential."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT1BAD3': {
        'text': '"Your aims are perhaps worthy ones, $TITLE0 $NAME1, but now that you have granted your people such power, you would be a fool not to use the power yourself to increase your control over the masses. Otherwise, one day they will rise up and destroy you."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT1WAR2': {
        'text': '"Your faction has become one of true robots, $TITLE0 $NAME1. I have waited for you to veer from this path, and I can wait no longer. You must be destroyed before you forget everything that ever made you kin to other living things."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT1WAR3': {
        'text': '"The powers you have unleashed have not been properly harnessed, $TITLE0 $NAME1, and soon your people will rise up and destroy not only you but all of us. I have no choice but to declare a preemptive vendetta, to shatter this power before it becomes unstoppable!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT1PACT2': {
        'text': '"I fear you and your robotic minions will contaminate my own efforts at achieving utopia, $TITLE0 $NAME1. Though you are a worthy ally in some ways, I cannot continue our $PACT2 so long as your people resemble machines more than living things."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT1PACT3': {
        'text': '"Your aims are worthy, $TITLE0 $NAME1, but I continue to fear that the powers you have granted your populace will one day overwhelm us all if you do not exercise greater control. I do not dare continue our $PACT2 as long as you continue your policies."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT2GOOD': {
        'text': '"You are a wise and benevolent leader, $TITLE0 $NAME1. Your ability to bring absolute freedom to your people is a shining example for us all. I bow to you."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT2BAD1': {
        'text': '"$TITLE0 $NAME1, such an idealistic society is commendable, but hardly achievable by a living creature. You need the suspension of biological imperatives before you can achieve true enlightenment. You should abandon your \'utopia\' and seek a more practical solution!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT2BAD3': {
        'text': '"$TITLE0 $NAME1, allowing this free-thinking society in the name of \'fulfilling your potential\' is truly wrong-headed. The only way a drone can \'fulfill its potential\' is by a wise and benevolent ruler telling it exactly what to do. I pray you will see the wisdom of this path soon."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT2WAR1': {
        'text': '"$TITLE0 $NAME1, your feeble attempts to provide a paradise are undermining my efforts to bring my people to a greater power through the use of cybernetics. As long as your policies continue you are a threat to my plans...therefore, you must be eliminated. Vendetta upon you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT2WAR3': {
        'text': '"Your policies urging your people to a \'utopia\' are not only foolish, they stir my own people\'s sentiments like a nest of angry bees. I cannot control them for the greater good so long as your seditious talk is spread over the airwaves, and now I see I must stop you by force. Vendetta upon you, $TITLE0 $NAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT2PACT1': {
        'text': '"$TITLE0 $NAME1, I cannot continue our $PACT2, as continued contact with your so-called "worker\'s paradise" is painful to the smooth-flowing emotions of my cybernetic citizens. I express sorrow at this, but it is the most efficient action."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT2PACT3': {
        'text': '"$TITLE0 $NAME1, your so-called "worker\'s paradise" is in direct counter to my wishes, and the wishes of my own people, who desire only a benevolent and wise dictator to provide for them their every need. Therefore I must renounce our $PACT2!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT3GOOD': {
        'text': '"I see you have discovered how truly effective a living society can be when controlled by one brilliant individual, $TITLE0 $NAME1. I salute your far-sighted vision."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT3BAD1': {
        'text': '"$TITLE0 $NAME1, your policies of thought control allow for only one pattern of thought--and an inefficient one, at that! I trust you will realize that you can achieve the same ends by better means by providing your citizens with cybernetic enhancements that, while not providing you the same measure of petty power, make your society far more mighty."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT3BAD2': {
        'text': '"$TITLE0 $NAME1, it is a terrible waste of human potential for you to be the sole controller of your populace. Think of the brilliant researchers and mighty warriors you will never discover due to the quelling of all creative thinking. Please re-think these policies before it is too late."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT3WAR1': {
        'text': '"I see you continue to run an entire society with inefficient human thoughts, $TITLE0 $NAME1. No living being should be given complete control over an entire society...you are too much of a wild card, and I\'m afraid I must destroy you now. Vendetta upon you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT3WAR2': {
        'text': '"$TITLE0 $NAME1, your policies of complete control over your populace are the worst kind of despotism. I can no longer bear to think of the waste of human potential that exists in your nation--therefore, I take it upon myself to liberate them. Vendetta upon you!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT3PACT1': {
        'text': '"You have been a useful ally, $TITLE0 $NAME1, but the absolute power you wield has begun to corrupt you. Therefore, I can no longer trust your all-too-biological decisions. Consider our $PACT2 at an end."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SOCIAL3CAT3PACT2': {
        'text': '"$TITLE0 $NAME1, your oppression of your own people is a grievous waste of human potential. I cannot in good conscience continue our $PACT2 while my own people are begging me to end this slavery of their brethren under the skin."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'COMMITTEDATROCITY': {
        'text': '"$TITLE0 $NAME1, I cannot condone the atrocities you have committed against the $FACTION2. I must warn you to refrain from chemical, biological, and nuclear warfare in the future."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'SELFATROCITY': {
        'text': '"$TITLE0 $NAME1, I cannot condone the atrocities you have committed against your own colonists. I must warn you to refrain from mass genocide in the future."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REPORTWINNING': {
        'text': '"You will be pleased to learn that I have broken the back of the $<M1:$FACTIONADJ0> resistance. I look forward to my personal interrogation of $TITLE1 $NAME2. $<2:His:Her:x:x> days of $DANCINGNAKED3 are numbered."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REPORTLOSING': {
        'text': '"$TITLE1 $NAME2 of the $FACTION3 and $<2:his:her:x:x> $<M1:$FACTIONPEJ5> minions have pressed Vendetta against me most brutally. I implore you to send assistance, as my back is to the wall!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'REPORTEVEN': {
        'text': '"My struggle against $TITLE1 $NAME2 of the $FACTION3 continues apace. If you can provide modest assistance we can together rid ourselves of $<2:his:her:x:x> $BADHABITS5!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TERRITORY': {
        'text': '"Your forces have been sighted in $<M1:$FACTIONADJ1> territory. Tensions between us would be greatly eased by their withdrawal."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'QUISLING': {
        'text': '"Be warned that I shall not long tolerate collaboration with my mortal enemy, the $<1:$CHARPEJ2> $TITLE0 $NAME1!"',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TIMESUPALLY': {
        'text': '"What a pleasant chat we\'ve had, $TITLE0 $NAME1. I\'m afraid, however, that I must now attend to other matters. $NAME2 out."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
    'TIMESUP': {
        'text': '"My apologies, $TITLE0, but I simply haven\'t all day to talk. $NAME2 out."',
        'responses': [{'text': 'Continue', 'action': 'diplo'}]
    },
}