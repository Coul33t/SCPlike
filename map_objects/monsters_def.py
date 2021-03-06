import libtcodpy as libtcod

from entity import Entity
from components.fighter import Fighter
from components.ai import BasicAi

def get_monster(name, x, y):
    if name == 'maintenance':
        fighter_comp = Fighter(5, 2, 0, xp_given=50)
        ai_comp = BasicAi()
        return Entity('Maintenance robot', x, y, 'm', libtcod.sepia, fighter=fighter_comp, ai=ai_comp)
    elif name == 'guard':
        fighter_comp = Fighter(10, 4, 3, xp_given=200)
        ai_comp = BasicAi()
        return Entity('Guardian robot', x, y, 'g', libtcod.darker_green, fighter=fighter_comp, ai=ai_comp)

    return None
