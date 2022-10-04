import pygame as pg

import spells
import globe
import pathfinding


class Wizard:

    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.sprite = pg.image.load('../sprites/wizard.png')
        self.stock_list = []
        self.stock_list_limit = 4
        self.spell_list = []

        self.time_last = globe.time.now()

        self.stat_dict = {"u_health_max": 100,
                          "u_health_current": 100,
                          "u_mana_max": 100,
                          "u_mana_current": 100}

        self.spell_dict = {"s_harvest": {"class": spells.SpellHarvest, "cost": 20, "combo": ["down", "down"], "unlocked": True},
                           "s_give_item": {"class": spells.SpellGiveItem, "cost": 10, "combo": ["up"], "unlocked": True},
                           "s_pickup_item": {"class": spells.SpellPickupItem, "cost": 10, "combo": ["down"], "unlocked": True},
                           "s_consume": {"class": spells.SpellConsume, "cost": 20, "combo": ["right", "down", "left"], "unlocked": True},
                           "s_fireball": {"class": spells.SpellFireball, "cost": 40, "combo": ["up", "left"], "unlocked": True},
                           "s_storm": {"class": spells.SpellStorm, "cost": 100, "combo": ["left", "up", "right", "down"], "unlocked": False},
                           "s_heal": {"class": spells.SpellHeal, "cost": 40, "combo": ["up", "down", "up"], "unlocked": True}}

    def update(self, map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt):

        if move_character_attempt:
            self.move(move_character_attempt, map_entities, map_topology)

        if cast_attempt:
            if temp_spell := self.create_spell(cast_attempt):
                self.spell_list.append(temp_spell)

        for spell in self.spell_list:
            spell.update(map_entities, map_resource, map_item, move_spell_attempt)

        if self.stat_dict["u_mana_current"] < self.stat_dict["u_mana_max"]:
            self.stat_dict["u_mana_current"] += 1

        # TODO Assuming this works, unable to test
        if self.stat_dict["u_health_current"] <= 0:
            pathfinding.drop_items(self.location, self.stock_list, map_topology, map_item)
            del self.spell_list
            del self.ruler_state.wizard

    def move(self, move_attempt, map_entities, map_topology):

        if globe.time.check(self.time_last, self.ruler_state.time_dur_move):
            location_attempt = (self.location[0]+move_attempt[0], self.location[1]+move_attempt[1])
            
            if pathfinding.find_free([location_attempt], map_entities, map_topology):
                self.location = location_attempt
                self.time_last = globe.time.now()

    def create_spell(self, kind):

        if self.stat_dict["u_mana_current"] >= self.spell_dict[kind]["cost"]:
            self.stat_dict["u_mana_current"] -= self.spell_dict[kind]["cost"]
            return self.spell_dict[kind]["class"](self)

        return None