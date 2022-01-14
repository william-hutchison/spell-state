import glob


class Spell:

    def __init__(self, wizard):

        self.ruler_wizard = wizard
        self.location = wizard.location
        self.status = "hold"


class SpellDirectional(Spell):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.move_direction = (0, 0)
        self.travel_current = 0
        self.time_dur_move = 100
        self.time_last = 0  # to allow immediate cast IS THIS DESIRABLE?

    def update(self, map_entities, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
        if move_attempt:
            self.status = "moving"
            self.move_direction = move_attempt

        if self.status == "moving":

            if self.travel_current <= self.travel_max+1:
                self.move(self.move_direction)
            if self.travel_current >= self.travel_max+1:
                self.ruler_wizard.spell_list.remove(self)
            else:
                self.impact(map_entities)

    def move(self, move_attempt):

        if glob.time.check(self.time_last, self.time_dur_move):
            self.location = (self.location[0] + move_attempt[0], self.location[1] + move_attempt[1])
            self.travel_current += 1
            self.time_last = glob.time.now()


class SpellConsume(SpellDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 1
        self.health_damage = 1000
        self.mana_gain = 60

    def impact(self, map_entities):

        if target := map_entities[self.location[1]][self.location[0]]:
            if type(target).__name__ == "Person":
                target.stat_dict["health current"] -= self.health_damage
                self.ruler_wizard.stat_dict["mana current"] += self.mana_gain
            self.ruler_wizard.spell_list.remove(self)


class SpellFireball(SpellDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 10
        self.health_damage = 50

    def impact(self, map_entities):

        if target := map_entities[self.location[1]][self.location[0]]:
            target.stat_dict["health current"] -= self.health_damage
            self.ruler_wizard.spell_list.remove(self)


spell_info = [("consume", SpellConsume, 20), ("fireball", SpellFireball, 40)]

