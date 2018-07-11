import libtcodpy as libtcod

MOVEMENT_KEYS = {libtcod.KEY_KP8: (0, -1), 
                 libtcod.KEY_KP9: (1, -1),
                 libtcod.KEY_KP6: (1, 0),
                 libtcod.KEY_KP3: (1, 1),
                 libtcod.KEY_KP2: (0, 1),
                 libtcod.KEY_KP1: (-1, 1),
                 libtcod.KEY_KP4: (-1, 0),
                 libtcod.KEY_KP7: (-1, -1),
                 libtcod.KEY_KP5: (0, 0)}
                 
def handle_keys(key):
    # Movement keys
    if key.vk in MOVEMENT_KEYS:
        return {'move': MOVEMENT_KEYS[key.vk]}


    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}