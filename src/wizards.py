import pygame as pg

import spells
import globe
import pathfinding


class Wizard:

    def __init__(self, ruler_state, location):

        self.stat_dict = {"stock_max": 4,
                          "health_max": 100,
                          "health_current": 100,
                          "mana_max": 100,
                          "mana_current": 100,
                          "move_duration": 300}

        self.spell_dict = {"harvest": {"class": spells.Harvest, "cost": 20, "combo": ["down", "down"], "unlocked": True},
                           "give_item": {"class": spells.GiveItem, "cost": 10, "combo": ["up"], "unlocked": True},
                           "pickup_item": {"class": spells.PickupItem, "cost": 10, "combo": ["down"], "unlocked": True},
                           "consume": {"class": spells.Consume, "cost": 20, "combo": ["right", "down", "left"], "unlocked": True},
                           "fireball": {"class": spells.Fireball, "cost": 40, "combo": ["up", "left"], "unlocked": False},
                           "paralyse": {"class": spells.Paralyse, "cost": 100, "combo": ["up", "right", "up", "down"], "unlocked": True},
                           "storm": {"class": spells.Storm, "cost": 100, "combo": ["left", "up", "right", "down"], "unlocked": False},
                           "heal": {"class": spells.Heal, "cost": 40, "combo": ["up", "down", "up"], "unlocked": False}}

        self.sprite = pg.image.load('../sprites/wizard.png')
        self.ruler_state = ruler_state
        self.location = location
        self.stock_list = []
        self.spell_list = []

        self.time_last = globe.time.now()

    def update(self, map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt):

        if move_character_attempt:
            self.move(move_character_attempt, map_entities, map_topology)

        if cast_attempt:
            if temp_spell := self.create_spell(cast_attempt):
                self.spell_list.append(temp_spell)

        for spell in self.spell_list:
            spell.update(map_entities, map_resource, map_item, move_spell_attempt)

        if self.stat_dict["mana_current"] < self.stat_dict["mana_max"]:
            self.stat_dict["mana_current"] += 1

        # TODO Assuming this works, unable to test
        if self.stat_dict["health_current"] <= 0:
            pathfinding.drop_items(self.location, self.stock_list, map_topology, map_item)
            del self.spell_list
            del self.ruler_state.wizard

    def move(self, move_attempt, map_entities, map_topology):

        if globe.time.check(self.time_last, self.stat_dict["move_duration"]):
            location_attempt = (self.location[0]+move_attempt[0], self.location[1]+move_attempt[1])
            
            if pathfinding.find_free([location_attempt], map_entities, map_topology):
                self.location = location_attempt
                self.time_last = globe.time.now()

    def create_spell(self, kind):

        if self.stat_dict["mana_current"] >= self.spell_dict[kind]["cost"]:
            self.stat_dict["mana_current"] -= self.spell_dict[kind]["cost"]
            return self.spell_dict[kind]["class"](self)

        return None
