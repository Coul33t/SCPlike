import libtcodpy as libtcod

from game_states import GameStates
from rendering import RenderOrder

def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red

    return 'You died!', GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = f'{monster.name.capitalize()} is dead!'

    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.render_order = RenderOrder.CORPSE
    monster.name = 'remains of ' + monster.name

    return death_message