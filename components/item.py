import libtcodpy as libtcod

from entity import Entity
from rendering import RenderOrder

class Item:
    def __init__(self, use_function=None, **kwargs):
        self.use_function = use_function
        self.function_kwargs = kwargs