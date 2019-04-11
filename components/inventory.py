import libtcodpy as libtcod

from game_messages import Message

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []
        self.owner = None

    def add_item(self, item):
        results = []

        if len(self.items) < self.capacity:
            results.append({'item_added': item,
                           'message': Message(f'You pick up the {item.name}', libtcod.blue)})
            self.items.append(item)

        else:
            results.append({'item_added': None,
                           'message': Message(f'Your inventory is full', libtcod.yellow)})

        return results
        