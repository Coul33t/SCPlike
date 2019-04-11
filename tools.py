from math import hypot

def dst_entities(en1, en2):
    return hypot(en1.x - en2.x, en1.y - en2.y)

def dst_coordinates(x, y):
    return abs(y - x)