import libtcodpy as libtcod
from input_handler import handle_keys
from entity import Entity, is_blocked_by_entity
from map_objects.game_map import GameMap
from fov_functions import initiliase_fov, recompute_fov
from rendering import render_all, clear_all
from game_states import GameStates
from colours import *
from components.fighter import Fighter
import pdb

def main():
    print('Hello world!')

    screen_width = 80
    screen_height = 40

    map_width = 70
    map_height = 35

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    fighter_comp = Fighter(20, 1, 1)
    player = Entity('Player', int(screen_width / 2), int(screen_height / 2), '@', libtcod.white, is_player=True, fighter=fighter_comp)
    entities = [player]

    libtcod.console_set_custom_font('Bedstead_12x20.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)

    libtcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    con = libtcod.console_new(screen_width, screen_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)
    game_map.populate_dungeon(entities)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    fov_map = initiliase_fov(game_map)
    fov_recompute = True

    game_state = GameStates.PLAYER_TURN

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colours)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        if action.get('move') and game_state == GameStates.PLAYER_TURN:
            dx, dy = action.get('move')
            if not game_map.is_blocked(player.x + dx, player.y + dy):

                target = is_blocked_by_entity(player.x + dx, player.y + dy, entities)
                if target:
                    player.fighter.attack(target)
                else:
                    player.move(dx, dy)
                    fov_recompute = True
            
                game_state = GameStates.ENEMY_TURN

        if action.get('exit'):
            return True

        if action.get('fullscreen'):
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity != player:
                    entity.ai.take_turn(player, fov_map, game_map, entities)
            game_state = GameStates.PLAYER_TURN


if __name__ == '__main__':
    main()