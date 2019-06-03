import tcod as libtcod

from tools import dst_entities

from rendering import RenderOrder


class Entity:

    def __init__(self, name, x, y, char, colour, blocks=True, render_order=RenderOrder.ACTOR, is_player=False,
                 fighter=None, ai=None, item=None, inventory=None, stairs=None, level=None):
        self.name = name
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour
        self.blocks = blocks

        self.is_player = is_player

        self.render_order = render_order

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

        self.inventory = inventory
        if self.inventory:
            self.inventory.owner = self

        self.stairs = stairs
        if self.stairs:
            self.stairs.owner = self

        self.level = level
        if self.level:
            self.level.owner = self

    def get_coordinates(self):
        return (self.x, self.y)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def distance_to(self, en):
        return dst_entities(self, en)

    def move_towards(self, target, game_map, entities):
        dx = (target.x - self.x)
        dy = (target.y - self.y)

        if dx != 0:
            dx = int(dx / abs(target.x - self.x))
        if dy != 0:
            dy = int(dy / abs(target.y - self.y))

        # In order to avoid static monsters when no direct path is available
        # (blocked by another monster for example), we check the movement in
        # dx and dy first, then only one of them
        # Example:
        #              #
        #       ########m <- this monster would stay blocked
        #           @ m
        #       ########
        #              #
        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                is_blocked_by_entity(self.x + dx, self.y + dy, entities)):
            self.move(dx, dy)

        elif dx != 0 and not (game_map.is_blocked(self.x + dx, self.y) or
                              is_blocked_by_entity(self.x + dx, self.y, entities)):
            self.move(dx, 0)

        elif dy != 0 and not (game_map.is_blocked(self.x, self.y + dy) or
                              is_blocked_by_entity(self.x, self.y + dy, entities)):
            self.move(0, dy)

    def move_astar(self, target, fov_map, game_map, entities):
        fov_map_astar = fov_map

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov_map_astar, entity.x, entity.y, True, False)

        # Allocate a A* path
        my_path = libtcod.path_new_using_map(fov_map_astar, 1.4)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths
        # (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running
        # around the map if there's an alternative path really far away
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 10:
            # Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)

            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths
            # (for example another monster blocks a corridor). It will still try
            # to move towards the player (closer to the corridor opening)
            self.move_towards(target, game_map, entities)

        # Delete the path to free memory
        libtcod.path_delete(my_path)

def is_blocked_by_entity(x, y, entities):
    for en in entities:
        if en.x == x and en.y == y and en.blocks:
            return en

    return None
