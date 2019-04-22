import tcod as libtcod

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

def cast_lightning(*args, **kwargs):
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
        results.append({'consumed': True, 'target': target, 'message': Message(f'The Zap Automatic Processor hits the {target.name} for {damage} damage!')})
        results.extend(target.fighter.take_damage(damage))

    else:
        results.append({'consumed': False, 'target': None, 'message': Message(f'No valid target in range.', libtcod.red)})

    return results