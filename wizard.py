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

    def ai_update(self, map_entities):
        # TODO IN FUTURE CONTROL FROM AI FILE
        pass

    def player_update(self, map_entities, cast_attempt, move_character_attempt, move_spell_attempt):

        if move_character_attempt:
            self.move(move_character_attempt, map_entities)

        if move_spell_attempt:
            holding_spell = [i for i in self.spell_list if i.status == "hold"]
            if holding_spell:
                holding_spell.pop().move(move_spell_attempt)

        if cast_attempt:
            self.create_spell(cast_attempt)

        for spell in self.spell_list:
            spell.update(map_entities)

        print(self.spell_list)

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

        self.wizard = wizard
        self.location = wizard.location
        self.kind = kind
        self.status = "hold"

    def update(self, map_entities):

        if self.status == "hold":
            self.location = self.wizard.location

    def move(self, move_attempt):

        self.location = (self.location[0] + move_attempt[0], self.location[1] + move_attempt[1])
        self.status = "moved"



