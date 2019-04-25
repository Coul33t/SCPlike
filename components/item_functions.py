import tcod as libtcod

from tools import Point

from components.ai import *

from game_messages import Message

def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You already are at full health.', libtcod.yellow)})

    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds feel better.', libtcod.green)})

    return results

def auto_aim_zap(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    max_range = kwargs.get('max_range')

    results = []

    target = None
    closest_distance = max_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            if caster.distance_to(entity) < closest_distance:
                target = entity
                closest_distance = caster.distance_to(entity)

    if target:
        results.append({'consumed': True,
                        'target': target,
                        'message': Message(f'The Zap Automatic Processor hits the {target.name} for {damage} damage!')})
        results.extend(target.fighter.take_damage(damage))

    else:
        results.append({'consumed': False,
                        'target': None,
                        'message': Message(f'No valid target in range.', libtcod.red)})

    return results


def guided_rocket(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    damage_radius = kwargs.get('damage_radius')
    target_coor = Point(kwargs.get('target_coordinates'))

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_coor.x, target_coor.y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    results.append({'consumed': True,
                    'message': Message(f'The guided rocket explodes in a radius of {damage_radius} tiles!', libtcod.orange)})


    for entity in [x for x in entities if x.fighter]:
        distance = target_coor.distance_to(entity.get_coordinates())
        if distance <= damage_radius:
            # 4 : decay constant
            # TODO: put into a constant file OR pass it as an argument
            final_damage = int(round(damage / (1 + (distance * 4 / damage_radius))))
            if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
                results.append({'message': Message(f'The {entity.name} gets burned for {final_damage} hit points.', libtcod.orange)})
            results.extend(entity.fighter.take_damage(final_damage))

    return results

def teleporting_bomb(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    damage_radius = kwargs.get('damage_radius')
    target_coord = Point(kwargs.get('target_coordinates'))
    target_tile = kwargs.get('target_tile')

    results = []

    if not target_tile.explored:
        results.append({'consumed': False,
                        'message': Message("You cannot target a tile you haven't explored yet.", libtcod.yellow)})
        return results

    if libtcod.map_is_in_fov(fov_map, target_coord.x, target_coord.y):
        results.append({'consumed': True,
                        'message': Message(f'The teleporting bomb explodes in a radius of {damage_radius} tiles!', libtcod.orange)})

    else:
        results.append({'consumed': True,
                        'message': Message(f'You hear a distant explosion!', libtcod.orange)})

    for entity in [x for x in entities if x.fighter]:
        distance = target_coord.distance_to(entity.get_coordinates())
        if distance <= damage_radius:
            # 4 : decay constant
            # TODO: put into a constant file OR pass it as an argument
            final_damage = int(round(damage / (1 + (distance * 4 / damage_radius))))
            if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
                results.append({'message': Message(f'The {entity.name} gets burned for {final_damage} hit points.', libtcod.orange)})
            results.extend(entity.fighter.take_damage(final_damage))

    return results

def confuse(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_coord = Point(kwargs.get('target_coordinates'))

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_coord.x, target_coord.y):
        results.append({'consumed': False,
                        'message': Message(f"You cannot target a tile you haven't explored yet.", libtcod.orange)})
        return results

    for entity in entities:
        if entity.ai and entity.x == target_coord.x and entity.y == target_coord.y:
            confused_ai = ConfusedAI(entity.ai, 10)
            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({'consumed': True, 'message': Message(f"The {entity.name} starts behaving weirdly...", libtcod.violet)})
            break

    else:
        results.append({'consumed': False, 'message': Message(f"There's no targetable entity at this location.", libtcod.orange)})


    return results