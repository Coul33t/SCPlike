import tcod as libtcod

from entity import Entity
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from map_objects.game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates


def get_constants():
    window_title = 'When Did It Go Wrong?'
    screen_width = 80
    screen_height = 40

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 70
    map_height = 33

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius
    }

    return constants


def get_game_variables(constants):
    fighter_comp = Fighter(20, 5, 5)
    inventory_comp = Inventory(10)
    level_comp = Level()
    player = Entity('Player', int(constants['screen_width'] / 2),
                    int(constants['screen_height'] / 2), '@', libtcod.white,
                    is_player=True, fighter=fighter_comp, inventory=inventory_comp,
                    level=level_comp)

    entities = [player]

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'],
                      constants['room_max_size'], constants['map_width'],
                      constants['map_height'], player, entities)

    game_map.populate_dungeon(entities)

    message_log = MessageLog(constants['message_x'],
                             constants['message_width'],
                             constants['message_height'])

    game_state = GameStates.PLAYER_TURN

    return player, entities, game_map, message_log, game_state
