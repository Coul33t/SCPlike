import libtcodpy as libtcod

from game_states import GameStates

MOVEMENT_KEYS = {libtcod.KEY_KP8: (0, -1),
                 libtcod.KEY_KP9: (1, -1),
                 libtcod.KEY_KP6: (1, 0),
                 libtcod.KEY_KP3: (1, 1),
                 libtcod.KEY_KP2: (0, 1),
                 libtcod.KEY_KP1: (-1, 1),
                 libtcod.KEY_KP4: (-1, 0),
                 libtcod.KEY_KP7: (-1, -1)}

def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.SHOW_INVENTORY:
        return handle_player_inventory_keys(key)
    return {}

def handle_player_turn_keys(key):
    # Movement keys
    key_char = chr(key.c)

    if key.vk in MOVEMENT_KEYS:
        return {'move': MOVEMENT_KEYS[key.vk]}

    elif key.vk == libtcod.KEY_KP5:
        return {'wait': True}

    elif key_char == 'g':
        return {'pickup': True}

    elif key_char == 'i':
        return {'show_inventory': True}

    elif key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}

def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}

    elif key.vk == libtcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    elif key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_player_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    elif key.vk == libtcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    elif key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    return {}