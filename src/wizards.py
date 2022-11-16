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
                          "move_duration": 280}

        self.spell_dict = {"harvest": {"class": spells.Harvest, "cost": 20, "combo": ["down", "down"], "unlocked": True},
                           "consume": {"class": spells.Consume, "cost": 20, "combo": ["right", "down", "left"], "unlocked": True},
                           "fireball": {"class": spells.Fireball, "cost": 40, "combo": ["up", "left"], "unlocked": True},
                           "paralyse": {"class": spells.Paralyse, "cost": 100, "combo": ["up", "right", "up", "down"], "unlocked": True},
                           "storm": {"class": spells.Storm, "cost": 100, "combo": ["left", "up", "right", "down"], "unlocked": True},
                           "heal": {"class": spells.Heal, "cost": 40, "combo": ["up", "down", "up"], "unlocked": True}}

        self.sprite = pg.image.load('../sprites/wizard.png')
        self.ruler_state = ruler_state
        self.location = location
        self.stock_list = []
        self.spell_list = []

        self.time_last = globe.time.now()

    def update(self, map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt):

        # TODO Control these attempts through dedicated functions instead passed variables
        if move_character_attempt:
            self.move(move_character_attempt, map_entities, map_topology)

        if cast_attempt:
            if temp_spell := self.create_spell(cast_attempt):
                self.spell_list.append(temp_spell)

        for spell in self.spell_list:
            spell.update(map_entities, map_resource, map_item, move_spell_attempt)

        if self.stat_dict["mana_current"] < self.stat_dict["mana_max"]:
            self.stat_dict["mana_current"] += 1

        # Check for wizard destruction
        if self.stat_dict["health_current"] <= 0:
            pathfinding.drop_items(self.location, self.stock_list, map_topology, map_item)
            self.spell_list = []
            self.ruler_state.wizard.location = (-1, -1) # TODO Replace with win / lose game state

    def move(self, move_attempt, map_entities, map_topology):
        """Attempt to move wizard in direction move_attempt, check for collision with map_entities or impassable terrain
        with map_topology."""

        if globe.time.check(self.time_last, self.stat_dict["move_duration"]):
            location_attempt = (self.location[0]+move_attempt[0], self.location[1]+move_attempt[1])
            
            if pathfinding.find_free([location_attempt], map_entities, map_topology):
                self.location = location_attempt
                self.time_last = globe.time.now()

    def create_spell(self, kind):
        """Attempt to create spell kind. Returns the new spell object if successful, otherwise returns none."""

        # Prevent new spell creation if a spell is currently being held
        if self.spell_list:
            if self.spell_list[0].status != "hold":
                return None

        # Prevent new spell creation if insufficient mana
        if self.stat_dict["mana_current"] < self.spell_dict[kind]["cost"]:
            return None

        # Create spell
        self.stat_dict["mana_current"] -= self.spell_dict[kind]["cost"]
        return self.spell_dict[kind]["class"](self)

