import libtcodpy as libtcod
from math import hypot
from random import randint

from entity import Entity

from tools import dst_entities, Point

from game_messages import Message

import pdb

class BasicAi:
    def __init__(self, search_radius=10):
        self.search_radius = search_radius
        self.last_seen_player = (None, None)
        self.owner = None

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.search_radius >= dst_entities(self.owner, target):
            m = self.owner

            if libtcod.map_is_in_fov(fov_map, m.x, m.y):
                if target.is_player:
                    self.last_seen_player = (target.x, target.y)

                if dst_entities(self.owner, target) >= 2:
                    m.move_astar(target, fov_map, game_map, entities)

                else:
                    atk_res = m.fighter.attack(target)
                    results.extend(atk_res)

            else:
                # If the player has been seen as a position in the few last turns,
                # the monster goes there
                if self.last_seen_player != (None, None):
                    new_target = Entity('PLACEHOLDER ENTITY', self.last_seen_player[0], self.last_seen_player[1], '0', libtcod.black)
                    m.move_astar(new_target, fov_map, game_map, entities)

        return results

class ConfusedAI:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        m = self.owner

        if self.number_of_turns > 0:
            random_x = m.x + randint(0,2) - 1
            random_y = m.y + randint(0,2) - 1

            if random_x != m.x and random_y != m.y:
                m.move_towards(Point(random_x, random_y), game_map, entities)

            self.number_of_turns -= 1


        else:
            m.ai = self.previous_ai
            results.append({'message': Message(f'The {m.name} is no longer confused.', libtcod.red)})

        return results