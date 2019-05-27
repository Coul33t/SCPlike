import tcod as libtcod
from input_handler import handle_keys, handle_mouse, handle_main_menu
from entity import is_blocked_by_entity
from fov_functions import initiliase_fov, recompute_fov
from rendering import render_all, clear_all
from game_states import GameStates
from menus import main_menu, message_box
from colours import colours

from death_functions import kill_monster, kill_player
from game_messages import Message

from tools import dst_entities

from loader_functions.initialise_new_game import (get_constants,
                                                  get_game_variables)

from loader_functions.data_loaders import (save_game,
                                           load_game)


def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    fov_map = initiliase_fov(game_map)
    fov_recompute = True

    previous_game_state = game_state

    targeting_item = None

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'],
                          constants['fov_light_walls'], constants['fov_algorithm'])

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], mouse, colours, game_state)

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

        if game_state == GameStates.TARGETING:
            mouse_action = handle_mouse(mouse)

            l_click = mouse_action.get('left_click')
            r_click = mouse_action.get('right_click')

            if l_click:
                target_x, target_y = l_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_coordinates=(target_x, target_y),
                                                        target_tile=game_map.tiles[target_x][target_y])

                player_turn_results.extend(item_use_results)

            elif r_click:
                player_turn_results.append({'targeting_cancelled': True})

        if action.get('take_stairs') and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constants)
                    fov_map = initiliase_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(con)
                    break
            else:
                message_log.add_message(Message("There are no stairs here.", libtcod.yellow))

        if action.get('exit'):
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        if action.get('fullscreen'):
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for p_turn_res in player_turn_results:
            message = p_turn_res.get('message')
            dead_entity = p_turn_res.get('dead')
            item_added = p_turn_res.get('item_added')
            item_consumed = p_turn_res.get('consumed')
            item_droppred = p_turn_res.get('item_dropped')
            targeting = p_turn_res.get('targeting')
            targeting_cancelled = p_turn_res.get('targeting_cancelled')

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

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled.'))

            if targeting:
                previous_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

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


def main():
    # How cute is a program that says "Hello World!" at the beginning?
    # I'll tell ya, it's 100% cute.
    print('Hello world!')

    constants = get_constants()

    libtcod.console_set_custom_font('Bedstead_12x20.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)

    libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)

    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, constants['screen_width'], constants['screen_height'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False

            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYER_TURN
                show_main_menu = False

            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True

            elif exit_game:
                break

        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants)
            show_main_menu = True


if __name__ == '__main__':
    main()