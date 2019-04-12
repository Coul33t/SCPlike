import libtcodpy as libtcod

from entity import Entity
from rendering import RenderOrder

from components.item import Item

from components.item_functions import *

def get_item(name, x, y):
    if name == 'Healing Potion':
        item_comp = Item(use_function=heal, amount=4)
        return Entity('Healing Potion', x, y, '!', libtcod.violet, blocks=False,
                      render_order=RenderOrder.ITEM, item=item_comp)

    return None