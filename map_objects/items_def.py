import tcod as libtcod

from entity import Entity
from rendering import RenderOrder

from components.item import Item

from game_messages import Message

from components.item_functions import *

def get_item(name, x, y):
    if name == 'Healing Potion':
        item_comp = Item(use_function=heal, amount=4)
        return Entity('Healing Potion', x, y, '!', libtcod.violet, blocks=False,
                      render_order=RenderOrder.ITEM, item=item_comp)

    if name == 'ZAP':
        item_comp = Item(use_function=auto_aim_zap, damage=4, max_range=5)
        return Entity('ZAP', x, y, 'z', libtcod.yellow, blocks=False,
                      render_order=RenderOrder.ITEM, item=item_comp)

    if name == 'Wrist-mounted rocket launcher':
        item_comp = Item(use_function=guided_rocket, targeting=True,
                        targeting_message=Message('Left-click a target to fire, right-click to cancel', libtcod.light_cyan),
                        damage=20, damage_radius=2)
        return Entity('Wrist-mounted rocket launcher', x, y, 'w',
                      libtcod.orange, blocks=False, render_order=RenderOrder.ITEM,
                      item=item_comp)

    if name == 'Teleporting bomb':
        item_comp = Item(use_function=teleporting_bomb, targeting=True,
                        targeting_message=Message('Left-click a target to fire, right-click to cancel', libtcod.light_cyan),
                        damage=10, damage_radius=2)
        return Entity('Teleporting bomb', x, y, 't',
                      libtcod.light_blue, blocks=False, render_order=RenderOrder.ITEM,
                      item=item_comp)

    return None