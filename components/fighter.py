from game_messages import Message

class Fighter:
    def __init__(self, hp, defense, power, xp_given=0):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp_given = xp_given
        self.owner = None

    @property
    def max_hp(self):
        bonus = 0

        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus

        return self.base_max_hp + bonus

    @property
    def power(self):
        bonus = 0

        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus

        return self.base_power + bonus

    @property
    def defense(self):
        bonus = 0

        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus

        return self.base_defense + bonus

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
