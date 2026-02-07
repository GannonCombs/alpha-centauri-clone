"""Save/Load system for game state persistence.

This module handles serialization and deserialization of the entire game state
to/from JSON files with .sav extension.
"""

import json
import os


def save_game(game, filepath: str) -> tuple[bool, str]:
    """Save the current game state to a file.

    Args:
        game: Game instance to save
        filepath: Full path to save file (should end in .sav)

    Returns:
        tuple: (success: bool, message: str)
    """
    # Validation checks
    if game.combat.active_battle:
        return False, "Cannot save during combat"

    if game.processing_ai:
        return False, "Cannot save during AI turn"

    try:
        # Serialize game state
        save_data = game.to_dict()

        # Ensure saves directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Write JSON to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)

        return True, f"Game saved to {os.path.basename(filepath)}"

    except Exception as e:
        return False, f"Failed to save game: {str(e)}"


def load_game(filepath: str):
    """Load a game state from a file.

    Args:
        filepath: Full path to save file

    Returns:
        Game: Reconstructed game instance

    Raises:
        FileNotFoundError: If save file doesn't exist
        ValueError: If save file is corrupted or incompatible
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Save file not found: {filepath}")

    try:
        # Read JSON from file
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        # Validate version
        if 'version' not in save_data:
            raise ValueError("Invalid save file: missing version")

        # For now, we only support version 1.0
        if save_data['version'] != "1.0":
            raise ValueError(f"Incompatible save version: {save_data['version']}")

        # Import here to avoid circular dependency
        from game.game import Game

        # Reconstruct game state
        game = Game.from_dict(save_data)

        return game

    except json.JSONDecodeError as e:
        raise ValueError(f"Save file is corrupted: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to load game: {str(e)}")


def list_save_files(saves_dir: str = "game/saves") -> list[dict]:
    """List all save files in the saves directory.

    Args:
        saves_dir: Path to saves directory

    Returns:
        list: List of dicts with 'filename', 'filepath', 'mission_year', 'timestamp'
    """
    if not os.path.exists(saves_dir):
        return []

    save_files = []

    for filename in os.listdir(saves_dir):
        if not filename.endswith('.sav'):
            continue

        filepath = os.path.join(saves_dir, filename)

        try:
            # Read basic metadata without fully loading the game
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            save_files.append({
                'filename': filename,
                'filepath': filepath,
                'mission_year': data.get('game_state', {}).get('mission_year', 0),
                'timestamp': data.get('save_timestamp', 'Unknown')
            })
        except Exception:
            # Skip corrupted files
            continue

    # Sort by timestamp (newest first)
    save_files.sort(key=lambda x: x['timestamp'], reverse=True)

    return save_files


def generate_save_filename(game) -> str:
    """Generate a suggested filename for the current game state.

    Format: <player_name>_of_the_<faction_name>,_<mission_year>.sav
    Example: Lady_Deirdre_Skye_of_the_Gaians,_2101.sav

    Args:
        game: Game instance

    Returns:
        str: Suggested filename (sanitized for filesystem)
    """
    from game.data.data import FACTIONS

    # Get player's chosen faction
    player_faction_id = getattr(game, 'player_faction_id', 0)
    player_faction = FACTIONS[player_faction_id]

    # Use custom player name if set, otherwise use faction leader name
    player_name = getattr(game, 'player_name', None) or player_faction['leader']
    faction_name = player_faction['name']
    mission_year = game.mission_year

    # Sanitize for filesystem (replace spaces with underscores, remove special chars)
    player_name_clean = player_name.replace(' ', '_')
    faction_name_clean = faction_name.replace(' ', '_')

    # Remove any problematic characters
    import re
    player_name_clean = re.sub(r'[^\w\-]', '', player_name_clean)
    faction_name_clean = re.sub(r'[^\w\-]', '', faction_name_clean)

    filename = f"{player_name_clean}_of_the_{faction_name_clean},_{mission_year}.sav"

    return filename
