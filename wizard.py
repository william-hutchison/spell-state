import glob
import pathfinding


class Wizard:

    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.stock_list = []
        self.stock_list_limit = 2
        self.spell_list = []

        self.time_last = glob.time.now()

        self.health = 100

    def update(self, map_entities, cast_attempt, move_character_attempt, move_spell_attempt):

        if move_character_attempt:
            self.move(move_character_attempt, map_entities)

        if cast_attempt:
            self.create_spell(cast_attempt)

        for spell in self.spell_list:
            spell.update(map_entities, move_spell_attempt)

        # ASSUMING THIS WORKS, CURRENTLY UNABLE TO TEST
        if self.health <= 0:
            del self.spell_list
            del self.ruler_state.wizard

    def move(self, move_attempt, map_entities):

        if glob.time.check(self.time_last, self.ruler_state.time_dur_move):
            location_attempt = (self.location[0]+move_attempt[0], self.location[1]+move_attempt[1])
            
            if pathfinding.find_free([location_attempt], map_entities):
                self.location = location_attempt
                self.time_last = glob.time.now()

    def create_spell(self, kind):

        self.spell_list.append(Spell(self, kind))


class Spell:

    def __init__(self, wizard, kind):

        self.ruler_wizard = wizard
        self.location = wizard.location

        self.status = "hold"
        self.move_direction = (0, 0)

        self.time_dur_move = 100
        self.time_last = 0  # to allow immediate cast IS THIS DESIRABLE?

        self.kind = kind
        self.travel_current = 0
        self.travel_max = 10

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

    def impact(self, map_entities):

        if target := map_entities[self.location[1]][self.location[0]]:

            if self.kind == "consume":
                if type(target).__name__ in ["Wizard", "Person"]:
                    target.health -= 1000
                    self.ruler_wizard.health += 10
                self.ruler_wizard.spell_list.remove(self)




