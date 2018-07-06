import libtcodpy as libtcod
from input_handler import handle_keys
from entity import Entity
from map_objects.game_map import GameMap
from rendering import render_all, clear_all
from colours import *

def main():
    print('Hello world!')

    screen_width = 80
    screen_height = 40

    map_width = 70
    map_height = 35

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', libtcod.white)
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), 'O', libtcod.yellow)
    entities = [player, npc]

    libtcod.console_set_custom_font('Bedstead_12x20.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)

    libtcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    con = libtcod.console_new(screen_width, screen_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        render_all(con, entities, game_map, screen_width, screen_height, colours)

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        if action.get('move'):
            dx, dy = action.get('move')
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)

        if action.get('exit'):
            return True

        if action.get('fullscreen'):
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
    main()