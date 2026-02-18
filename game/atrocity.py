"""Atrocity system — simple and major atrocities committed by the player.

Simple atrocities (nerve_staple, nerve_gas, genetic_warfare, obliterate_base):
  - Commerce sanctions for 10 × cumulative-count turns
  - Target faction permanently refuses truce/treaty
  - Integrity drops one level

Major atrocities (planet_buster):
  - All of the above
  - Every faction immediately declares Vendetta (permanent)
  - Player vote count is permanently 0 for governor/supreme leader
"""

INTEGRITY_LEVELS = ['Noble', 'Faithful', 'Scrupulous', 'Dependable', 'Ruthless', 'Treacherous']


def get_integrity_label(game):
    """Return the current integrity level name for the player."""
    level = getattr(game, 'integrity_level', 0)
    level = max(0, min(level, len(INTEGRITY_LEVELS) - 1))
    return INTEGRITY_LEVELS[level]


def drop_integrity(game):
    """Drop player integrity one level (floor at Treacherous)."""
    current = getattr(game, 'integrity_level', 0)
    game.integrity_level = min(current + 1, len(INTEGRITY_LEVELS) - 1)


def commit_atrocity(game, atrocity_type, target_faction_id=None):
    """Process an atrocity committed by the player.

    Args:
        game: Game instance
        atrocity_type: One of 'nerve_staple' | 'nerve_gas' | 'genetic_warfare' |
                       'obliterate_base' | 'planet_buster'
        target_faction_id: Faction directly victimized (None if not applicable)

    Returns:
        bool: True if major atrocity (planet buster), False otherwise
    """
    MAJOR_ATROCITIES = {'planet_buster'}
    is_major = atrocity_type in MAJOR_ATROCITIES

    # --- Commerce sanctions ---
    game.atrocity_count += 1
    sanction_turns = 10 * game.atrocity_count
    game.sanctions_turns_remaining = max(
        getattr(game, 'sanctions_turns_remaining', 0), sanction_turns
    )

    # --- Integrity drops one level per atrocity ---
    drop_integrity(game)

    # --- Target faction permanently hostile (all atrocities) ---
    if target_faction_id is not None and target_faction_id != game.player_faction_id:
        pv = getattr(game, 'permanent_vendetta_factions', set())
        pv.add(target_faction_id)
        game.permanent_vendetta_factions = pv
        _force_vendetta(game, target_faction_id)

    # --- Major atrocity: everyone declares vendetta ---
    if is_major:
        game.major_atrocity_committed = True
        new_vendettas = []
        for fid in getattr(game, 'ai_faction_ids', []):
            if fid in getattr(game, 'eliminated_factions', set()):
                continue
            pv = getattr(game, 'permanent_vendetta_factions', set())
            pv.add(fid)
            game.permanent_vendetta_factions = pv
            if _force_vendetta(game, fid):
                new_vendettas.append(fid)

        if new_vendettas:
            game.pending_major_atrocity_popup = True

    return is_major


def _force_vendetta(game, faction_id):
    """Set relation to Vendetta for faction_id against the player.

    Returns True if the relation actually changed (was not already Vendetta).
    """
    if not (hasattr(game, 'ui_manager') and game.ui_manager):
        return False
    diplo = getattr(game.ui_manager, 'diplomacy', None)
    if not diplo:
        return False
    current = diplo.diplo_relations.get(faction_id, 'Uncommitted')
    if current != 'Vendetta':
        diplo.diplo_relations[faction_id] = 'Vendetta'
        return True
    return False
