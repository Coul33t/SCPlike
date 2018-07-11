import libtcodpy as libtcod
from math import hypot
from entity import Entity

import pdb

class BasicAi:
    def __init__(self, detection_radius=20):
        self.detection_radius = detection_radius
        self.last_seen_player = (None, None)

    def dst(self, p):
        return hypot(p.x - self.owner.x, p.y - self.owner.y)

    def take_turn(self, target, fov_map, game_map, entities):
        if self.detection_radius >= self.dst(target):
            m = self.owner

            if libtcod.map_is_in_fov(fov_map, m.x, m.y):
                if target.is_player:
                    self.last_seen_player = (target.x, target.y)

                if self.dst(target) >= 2:
                    m.move_astar(target, fov_map, game_map, entities)

                else:
                    m.fighter.attack(target)

            else:
                if self.last_seen_player != (None, None):
                    new_target = Entity('PLACEHOLDER ENTITY', self.last_seen_player[0], self.last_seen_player[1], '0', libtcod.black)
                    m.move_astar(new_target, fov_map, game_map, entities)
