"""Planetary Council proposal definitions."""

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
