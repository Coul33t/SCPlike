class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, dmg):
        self.hp -= dmg

    def attack(self, target):
        dmg = self.power - target.fighter.defense

        if dmg > 0:
            target.fighter.take_damage(dmg)
            print(f' The {self.owner.name} attacks the {target.name} for {dmg} damage!')
        else:
            print(f'The {self.owner.name} attacks does no damage to the {target.name}.')