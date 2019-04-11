from game_messages import Message

class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.owner = None

    def take_damage(self, dmg):
        results = []

        self.hp -= dmg

        if self.hp <= 0:
            results.append({'dead': self.owner})

        return results


    def attack(self, target):
        results = []

        dmg = self.power - target.fighter.defense

        if dmg > 0:
            results.append({'message': Message(f'The {self.owner.name} attacks the {target.name} for {dmg} damage!')})
            results.extend(target.fighter.take_damage(dmg))
        else:
           results.append({'message': Message(f'The {self.owner.name} attacks does no damage to the {target.name}.')})

        return results