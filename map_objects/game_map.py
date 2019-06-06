import tcod as libtcod

from random import randint

from map_objects.tile import Tile
from map_objects.rectangle import Rect

from map_objects.monsters_def import get_monster
from map_objects.items_def import get_item

from entity import Entity
from rendering import RenderOrder
from tools import Point

from components.stairs import Stairs

from game_messages import Message
from random_utils import (random_choice_from_dict,
                          from_dungeon_level)

# TODO: use from_dungeon_level
MONSTER_PROB = {'maintenance': 80, 'guard': 20}
ITEM_PROB = {'Healing Potion': 50,
             'ZAP': 10,
             'Wrist-mounted rocket launcher': 5,
             'Teleporting bomb': 3,
             'Confuser': 10,
             'Parabola': 5,
             'Crowbar': 5,
             'Hammer': 5}


class GameMap:
    def __init__(self, width, height, current_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.rooms = []
        self.current_level = current_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def valid_position(self, x, y, entities):
        if entities:
            if not any([en for en in entities if x == en.x and y == en.y]):
                return True

            return False

        return True


    def place_entity(self, x, y, entity, entities):
        if entities:
            if not any([en for en in entities if x == en.x and y == en.y]):
                entities.append(entity)
                return True

            return False

        entities.append(entity)
        return True


    def populate_room(self, room, entities):
        max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.current_level)
        nb_monsters = randint(0, max_monsters)

        if nb_monsters == 0:
            return

        succesful = 0

        # 100 try in total
        for _ in range(1000):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)


            monster_choice = random_choice_from_dict(MONSTER_PROB)
            entity = get_monster(monster_choice, x, y)

            if self.place_entity(x, y, entity, entities):
                succesful += 1

            if succesful == nb_monsters:
                break

    def place_items(self, room, entities):
        max_items = from_dungeon_level([[1, 1], [2, 4]], self.current_level)
        nb_items = randint(0, max_items)

        if nb_items == 0:
            return

        for _ in range(nb_items):
            # 100 try for each object
            for _ in range(100):
                x = randint(room.x1 + 1, room.x2 - 1)
                y = randint(room.y1 + 1, room.y2 - 1)
                if self.valid_position(x, y, entities):
                    break

            # We couldn't place the object
            else:
                continue

            item_choice = random_choice_from_dict(ITEM_PROB)
            entity = get_item(item_choice, x, y)

            self.place_entity(x, y, entity, entities)




    def populate_dungeon(self, entities):
        for room in self.rooms:
            self.populate_room(room, entities)
            self.place_items(room, entities)


    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):
        self.rooms = []
        num_rooms = 0

        center_last_room = Point()

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    break

            else:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                center_last_room = Point(new_x, new_y)

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y

                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = self.rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                # finally, append the new room to the list
                self.rooms.append(new_room)
                num_rooms += 1

        stairs_comp = Stairs(self.current_level + 1)
        down_stairs = Entity('Stairs', center_last_room.x, center_last_room.y,
                             '>', libtcod.white, render_order=RenderOrder.STAIRS,
                             stairs=stairs_comp)
        entities.append(down_stairs)


    def next_floor(self, player, message_log, constants):
        self.current_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'],
                      constants['room_max_size'], constants['map_width'],
                      constants['map_height'], player, entities)
        self.populate_dungeon(entities)

        message_log.add_message(Message('You feel DETERMINED.', libtcod.red))

        return entities

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
