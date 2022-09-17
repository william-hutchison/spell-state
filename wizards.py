import pygame as pg

import spells
import globe
import pathfinding


class Wizard:

    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.sprite = pg.image.load('sprites/wizard.png')
        self.spell_dict = spells.spell_info
        self.stock_list = []
        self.stock_list_limit = 2
        self.spell_list = []

        self.time_last = globe.time.now()

        self.stat_dict = {"health max": 100, "health current": 100, "mana max": 100, "mana current": 100}

    def update(self, map_entities, map_topology, cast_attempt, move_character_attempt, move_spell_attempt):

        if move_character_attempt:
            self.move(move_character_attempt, map_entities, map_topology)

        if cast_attempt:
            if temp_spell := self.create_spell(cast_attempt):
                self.spell_list.append(temp_spell)

        for spell in self.spell_list:
            spell.update(map_entities, move_spell_attempt)

        if self.stat_dict["mana current"] < self.stat_dict["mana max"]:
            self.stat_dict["mana current"] += 1

        # ASSUMING THIS WORKS, CURRENTLY UNABLE TO TEST
        if self.stat_dict["health current"] <= 0:
            del self.spell_list
            del self.ruler_state.wizard

    def move(self, move_attempt, map_entities, map_topology):

        if globe.time.check(self.time_last, self.ruler_state.time_dur_move):
            location_attempt = (self.location[0]+move_attempt[0], self.location[1]+move_attempt[1])
            
            if pathfinding.find_free([location_attempt], map_entities, map_topology):
                self.location = location_attempt
                self.time_last = globe.time.now()

    def create_spell(self, kind):

        if self.stat_dict["mana current"] >= self.spell_dict[kind][1]:
            self.stat_dict["mana current"] -= self.spell_dict[kind][1]
            return self.spell_dict[kind][0](self)

        return None
