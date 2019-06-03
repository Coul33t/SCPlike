from game_messages import Message

class Fighter:
    def __init__(self, hp, defense, power, xp_given=0):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.xp_given = xp_given
        self.owner = None

    def take_damage(self, dmg):
        results = []

        self.hp -= dmg

        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp_given': self.xp_given})

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

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
