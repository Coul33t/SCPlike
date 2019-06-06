class Level:
    def __init__(self, current_level=1, current_xp=0, level_up_base=200, level_up_factor=150):
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor

    @property
    def xp_to_next_level(self):
        return self.level_up_base + (self.level_up_factor * (self.current_level - 1))

    def add_xp(self, xp_amount):
        has_level_up = False
        self.current_xp += xp_amount

        while self.current_xp > self.xp_to_next_level:
            self.current_xp -= self.xp_to_next_level
            self.current_level += 1
            has_level_up = True

        return has_level_up
