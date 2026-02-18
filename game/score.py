"""Alpha Centauri score computation.

Score breakdown:
  (1) 1 pt per citizen in each player base
  (2) Diplo/Economic victory: +1 pt per citizen in Pact Brother bases,
      +0.5 pt per citizen in any other faction's bases
  (3) 1 pt per citizen in a surrendered base (extra on top of (1))
  (4) 1 pt per unit of commerce income across player bases
  (5) 1 pt per technology discovered
  (6) 10 pts per Transcendent Thought advance
  (7) 25 pts per Secret Project owned
  (8) Victory bonus (varies by victory type, minus 2 per turn elapsed)
  (9) Native Life multiplier: rare −25%, abundant +25%
 (10) Iron Man +100% — not yet implemented
"""

from game.data.facility_data import SECRET_PROJECTS

_SECRET_PROJECT_IDS = {sp['id'] for sp in SECRET_PROJECTS}

# Victory base bonuses (before turn deduction)
_VICTORY_BASE = {
    'transcendence': 2000,
    'diplomatic': 1200,
    'economic': 1200,
    'conquest': 1000,
}


def calculate_score(game):
    """Compute the player's Alpha Centauri score.

    Args:
        game: Game instance

    Returns:
        dict with 'total' and individual component keys for display.
    """
    player_id = game.player_faction_id
    player_tech_tree = game.factions[player_id].tech_tree
    player_bases = [b for b in game.bases if b.owner == player_id]

    # (1) Citizens in player bases
    citizens = sum(b.population for b in player_bases)

    # (2) Diplomatic / Economic victory: allied and neutral faction citizens
    diplo_bonus = 0
    victory_type = getattr(game, 'victory_type', None)
    if victory_type in ('diplomatic', 'economic'):
        diplo = None
        if hasattr(game, 'ui_manager') and game.ui_manager:
            diplo = getattr(game.ui_manager, 'diplomacy', None)
        for fid in game.factions:
            if fid == player_id:
                continue
            faction_pop = sum(b.population for b in game.bases if b.owner == fid)
            if faction_pop == 0:
                continue
            relation = diplo.diplo_relations.get(fid, 'Uncommitted') if diplo else 'Uncommitted'
            if relation == 'Pact':
                diplo_bonus += faction_pop
            else:
                diplo_bonus += faction_pop // 2  # floor of 0.5 per citizen

    # (3) Surrendered bases (bases with base.surrendered == True get an extra point per citizen)
    surrendered_pts = sum(
        b.population for b in player_bases if getattr(b, 'surrendered', False)
    )

    # (4) Commerce income across player bases
    commerce = sum(int(getattr(b, 'commerce_income', 0)) for b in player_bases)

    # (5) Technologies discovered
    techs = len(player_tech_tree.discovered_techs)

    # (6) Transcendent Thought: 10 pts per advance (single tech in our tree)
    transcendent = 10 if 'TranT' in player_tech_tree.discovered_techs else 0

    # (7) Secret Projects owned (25 pts each)
    secret_count = sum(
        1 for b in player_bases for fac in b.facilities if fac in _SECRET_PROJECT_IDS
    )
    secret_pts = secret_count * 25

    # (8) Victory bonus
    turn = getattr(game, 'turn', 0)
    base_bonus = _VICTORY_BASE.get(victory_type, 0)
    victory_bonus = max(0, base_bonus - 2 * turn) if victory_type else 0

    subtotal = (citizens + diplo_bonus + surrendered_pts + commerce
                + techs + transcendent + secret_pts + victory_bonus)

    # (9) Native Life multiplier
    native_life = getattr(game.game_map, 'native_life', 'average')
    if native_life == 'rare':
        native_mult = 0.75
    elif native_life == 'abundant':
        native_mult = 1.25
    else:
        native_mult = 1.0

    # (10) Iron Man — not yet implemented
    # iron_man_mult = 2.0 if getattr(game, 'iron_man', False) else 1.0
    iron_man_mult = 1.0

    total = int(subtotal * native_mult * iron_man_mult)

    return {
        'total': total,
        'citizens': citizens,
        'diplo_bonus': diplo_bonus,
        'surrendered': surrendered_pts,
        'commerce': commerce,
        'techs': techs,
        'transcendent': transcendent,
        'secret_projects': secret_pts,
        'secret_count': secret_count,
        'victory_bonus': victory_bonus,
        'victory_type': victory_type,
        'native_life': native_life,
        'native_mult': native_mult,
        'subtotal': subtotal,
    }
