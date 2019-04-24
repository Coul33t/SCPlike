from random import randint

from map_objects.tile import Tile
from map_objects.rectangle import Rect

from map_objects.monsters_def import get_monster
from map_objects.items_def import get_item

from rendering import RenderOrder

MONSTER_PROB = {'maintenance': [0, 80], 'guard': [80,100]}

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.rooms = []

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


    def select_entity(self, prob, x, y):
        rand = randint(0, 100)

        for k, v in prob.items():
            if v[0] <= rand <= v[1]:
                return get_monster(k, x, y)


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


    def populate_room(self, room, entities, max_monsters):
        nb_monsters = randint(0, max_monsters)

        if nb_monsters == 0:
            return

        succesful = 0

        # 100 try in total
        for _ in range(1000):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            entity = self.select_entity(MONSTER_PROB, x, y)

            if self.place_entity(x, y, entity, entities):
                succesful += 1

            if succesful == nb_monsters:
                break

    def place_items(self, room, entities, max_items):
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

            item_type = randint(0, 100)

            if item_type < 1:
                entity = get_item('Healing Potion', x, y)
            elif item_type < 2:
                entity = get_item('ZAP', x, y)
            elif item_type < 3:
                entity = get_item('Wrist-mounted rocket launcher', x, y)
            else:
                entity = get_item('Teleporting bomb', x, y)

            self.place_entity(x, y, entity, entities)




    def populate_dungeon(self, entities):
        for room in self.rooms:
            self.populate_room(room, entities, 4)
            self.place_items(room, entities, 2)


    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player):
        self.rooms = []
        num_rooms = 0

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


    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False