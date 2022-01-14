import spells
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

        self.stat_dict = {"health max": 100, "health current": 100, "mana max": 100, "mana current": 100}

    def update(self, map_entities, cast_attempt, move_character_attempt, move_spell_attempt):

        if move_character_attempt:
            self.move(move_character_attempt, map_entities)

        if cast_attempt:
            self.create_spell(cast_attempt)

        for spell in self.spell_list:
            spell.update(map_entities, move_spell_attempt)

        if self.stat_dict["mana current"] < self.stat_dict["mana max"]:
            self.stat_dict["mana current"] += 1

        # ASSUMING THIS WORKS, CURRENTLY UNABLE TO TEST
        if self.stat_dict["health current"] <= 0:
            del self.spell_list
            del self.ruler_state.wizard

    def move(self, move_attempt, map_entities):

        if glob.time.check(self.time_last, self.ruler_state.time_dur_move):
            location_attempt = (self.location[0]+move_attempt[0], self.location[1]+move_attempt[1])
            
            if pathfinding.find_free([location_attempt], map_entities):
                self.location = location_attempt
                self.time_last = glob.time.now()

    def create_spell(self, kind):

        for spell in spells.spell_info:
            if spell[0] == kind:
                if self.stat_dict["mana current"] >= spell[2]:
                    self.stat_dict["mana current"] -= spell[2]
                    self.spell_list.append(spell[1](self))
