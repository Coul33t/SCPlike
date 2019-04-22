import libtcodpy as libtcod
from input_handler import handle_keys
from entity import Entity, is_blocked_by_entity
from map_objects.game_map import GameMap
from fov_functions import initiliase_fov, recompute_fov
from rendering import render_all, clear_all, RenderOrder
from game_states import GameStates
from colours import *

from death_functions import kill_monster, kill_player
from game_messages import MessageLog, Message

from components.fighter import Fighter
from components.inventory import Inventory

from tools import dst_entities

import pdb

def main():
    print('Hello world!')

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

    fighter_comp = Fighter(20, 5, 5)
    inventory_comp = Inventory(10)
    player = Entity('Player', int(screen_width / 2), int(screen_height / 2), '@', libtcod.white,
                    is_player=True, fighter=fighter_comp, inventory=inventory_comp)

    entities = [player]

    libtcod.console_set_custom_font('Bedstead_12x20.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)

    libtcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    con = libtcod.console_new(screen_width, screen_height)
    panel = libtcod.console_new(screen_width, panel_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)
    game_map.populate_dungeon(entities)

    message_log = MessageLog(message_x, message_width, message_height)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    fov_map = initiliase_fov(game_map)
    fov_recompute = True

    game_state = GameStates.PLAYER_TURN
    previous_game_state = game_state

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                   screen_width, screen_height, bar_width, panel_height, panel_y, mouse, colours,
                   game_state)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key, game_state)

        player_turn_results = []

        if action.get('move') and game_state == GameStates.PLAYER_TURN:
            dx, dy = action.get('move')
            if not game_map.is_blocked(player.x + dx, player.y + dy):

                target = is_blocked_by_entity(player.x + dx, player.y + dy, entities)
                if target and target.fighter:
                    atk_res = player.fighter.attack(target)
                    player_turn_results.extend(atk_res)
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if action.get('wait'):
            game_state = GameStates.ENEMY_TURN

        if action.get('pickup') and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and dst_entities(entity, player) < 2:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))

        if action.get('show_inventory'):
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if (action.get('inventory_index') is not None
            and previous_game_state != game_state.PLAYER_DEAD
            and player.inventory.items
            and action.get('inventory_index') < len(player.inventory.items)):

            item = player.inventory.items[action.get('inventory_index')]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))

            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if action.get('drop_inventory'):
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if action.get('exit'):
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            else:
                return True

        if action.get('fullscreen'):
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for p_turn_res in player_turn_results:
            message = p_turn_res.get('message')
            dead_entity = p_turn_res.get('dead')
            item_added  = p_turn_res.get('item_added')
            item_consumed = p_turn_res.get('consumed')
            item_droppred = p_turn_res.get('item_dropped')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_droppred:
                entities.append(item_droppred)
                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_res = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for en_turn_res in enemy_turn_res:
                        message = en_turn_res.get('message')
                        dead_entity = en_turn_res.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYER_TURN


if __name__ == '__main__':
    main()