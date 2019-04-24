from math import hypot
from dataclasses import dataclass

@dataclass
class Point:
    def __init__(self, *args) -> None:
        if len(args) == 2:
            self.x = args[0]
            self.y = args[1]

        elif (len(args) == 1
              and (isinstance(args[0], tuple)
              or isinstance(args[0], list))):
            self.x = args[0][0]
            self.y = args[0][1]

    def distance_to(self, *args):
        if len(args) == 2:
            return hypot(self.x - args[0], self.y - args[1])

        elif len(args) == 1:
            if isinstance(args[0], Point):
                return hypot(self.x - args[0].x, self.y - args[0].y)

            elif isinstance(args[0], tuple) or isinstance(args[0], list):
                return hypot(self.x - args[0][0], self.y - args[0][1])

def dst_entities(en1, en2):
    return hypot(en1.x - en2.x, en1.y - en2.y)

def dst_coordinates(x, y):
    return abs(y - x)