import pygame as pg

import timer
import pathfinding


class Spell:
    """Parent class for spell kinds."""

    def __init__(self, wizard):

        self.stat_dict = {}

        self.ruler_wizard = wizard
        self.location = wizard.location
        self.status = "hold"

        self.effect_target = None
        self.effect_start_time = None

        self.sprite = pg.image.load('../sprites/spells/hold.png')

    def change_action_weight(self, target, action_weight_change):
        """Change the action weight of the ruler_state of the target person based on the input
        action_weight_change."""

        if type(target).__name__ == "Person":
            if target.ruler_state == self.ruler_wizard.ruler_state:
                target.ruler_state.action_dict[target.action_super]["weight"] += action_weight_change

    def change_relation_weight(self, target, relation_weight_change):
        """Change the relation weight of the ruler_state of the target entity based on the input
        relation_weight_change."""

        if target.ruler_state != self.ruler_wizard.ruler_state:
            target.ruler_state.relation_dict[self.ruler_wizard.ruler_state] += relation_weight_change


class KindSelf(Spell):
    """Parent class for spells cast on the wizard entity itself."""

    def __init__(self, wizard):

        super().__init__(wizard)

    def update(self, map_entities, map_resource, map_item, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
        if move_attempt:
            self.impact(map_entities)

        if self.status == "effect":
            self.effect(map_entities, self.effect_target)


class KindDirectional(Spell):
    """Parent class for spells with directional movement."""

    def __init__(self, wizard):

        super().__init__(wizard)
        self.move_direction = (0, 0)
        self.travel_current = 0
        self.time_last = 0

    def update(self, map_entities, map_resource, map_item, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
        elif self.status == "effect":
            self.effect(map_entities, self.effect_target)

        if type(move_attempt) == tuple:
            self.status = "moving"
            self.move_direction = move_attempt

        if self.status == "moving":

            # Check for spell movement
            if self.travel_current <= self.stat_dict["move_max"]+1:
                self.move(self.move_direction)
            if self.travel_current >= self.stat_dict["move_max"]+1 or not 0 <= self.location[0] < len(map_entities[0]) or not 0 <= self.location[1] < len(map_entities[1]):
                self.ruler_wizard.spell_list.remove(self)

            # Check for spell impact
            else:
                # Special case for harvesting
                if type(self).__name__ == "Harvest":
                    if target := map_resource[self.location[1]][self.location[0]]:
                        self.impact(target)

                # All other spells
                else:
                    if target := map_entities[self.location[1]][self.location[0]]:
                        self.impact(target)

    def move(self, move_attempt):

        if timer.timer.check(self.time_last, self.stat_dict["move_duration"]):
            self.location = (self.location[0] + move_attempt[0], self.location[1] + move_attempt[1])
            self.travel_current += 1
            self.time_last = timer.timer.now()


class KindSelect(Spell):
    """Parent class for spells with target selection."""

    def __init__(self, wizard):

        super().__init__(wizard)
        self.location_select = self.ruler_wizard.location
        self.status = "select"

    def update(self, map_entities, map_resource, map_item, map_move_attempt):

        self.location = self.ruler_wizard.location

    def select(self, map_entities):

        if target := map_entities[self.location_select[1]][self.location_select[0]]:
            self.impact(target)


class Harvest(KindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 1

    def impact(self, target):

        if target:
            if len(self.ruler_wizard.stock_list) < self.ruler_wizard.stat_dict["stock_max"]:
                self.ruler_wizard.stock_list.append(target)

        self.ruler_wizard.spell_list.remove(self)


class Consume(KindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = -10
        self.stat_dict["relation_weight_change"] = -10
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 1
        self.stat_dict["health_change"] = -1000
        self.stat_dict["mana_change"] = 60

    def impact(self, target):

        if type(target).__name__ == "Person":
            target.stat_dict["health_current"] += self.stat_dict["health_change"]
            self.ruler_wizard.stat_dict["mana_current"] += self.stat_dict["mana_change"]

        self.change_action_weight(target, self.stat_dict["action_weight_change"])
        self.change_relation_weight(target, self.stat_dict["relation_weight_change"])
        self.ruler_wizard.spell_list.remove(self)


class Fireball(KindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["relation_weight_change"] = -5
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 10
        self.stat_dict["health_change"] = -50
        self.sprite = pg.image.load("../sprites/spells/fireball.png")

    def impact(self, target):

        target.stat_dict["health_current"] += self.stat_dict["health_change"]
        self.change_action_weight(target, self.stat_dict["action_weight_change"])
        self.change_relation_weight(target, self.stat_dict["relation_weight_change"])
        self.ruler_wizard.spell_list.remove(self)


class Paralyse(KindDirectional):

    # TODO Allow multiple spells to exist simultaneously
    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["relation_weight_change"] = -5
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 3
        self.stat_dict["move_duration_change"] = 10000
        self.stat_dict["effect_duration"] = 5000

    def impact(self, target):

        if type(target).__name__ in ["Person", "Wizard"]:
            target.stat_dict["move_duration"] += self.stat_dict["move_duration_change"]
            self.status = "effect"
            self.effect_target = target
            self.effect_start_time = timer.timer.now()
        else:
            self.ruler_wizard.spell_list.remove(self)

        self.change_action_weight(target, self.stat_dict["action_weight_change"])
        self.change_action_weight(target, self.stat_dict["relation_weight_change"])

    def effect(self, map_entities, target):
        """Remove spell effect after effect duration reached."""

        if timer.timer.check(self.effect_start_time, self.stat_dict["effect_duration"]):
            target.stat_dict["move_duration"] -= self.stat_dict["move_duration_change"]
            self.ruler_wizard.spell_list.remove(self)


class Storm(KindSelf):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["relation_weight_change"] = -5
        self.stat_dict["health_change"] = -100
        self.stat_dict["radius"] = 4
        self.stat_dict["ring_duration"] = 200
        self.stat_dict["effect_duration"] = 300
        self.sprite = pg.image.load("../sprites/spells/storm.png")

    def impact(self, map_entities):

        self.status = "effect"
        self.effect_target = self.ruler_wizard
        self.effect_start_time = timer.timer.now()
        self.current_ring = 1

    def effect(self, map_entities, target):
        """Remove spell effect after effect duration reached."""

        if timer.timer.check(self.effect_start_time, self.stat_dict["ring_duration"]):
            self.effect_start_time = timer.timer.now()

            # Create dummy spell and apply effect for each tile in radius ring
            ring_tiles = pathfinding.find_within_ring(self.ruler_wizard.location, self.current_ring)
            for tile in ring_tiles:
                self.ruler_wizard.spell_list.append(DummySpell(self.ruler_wizard, tile, self.stat_dict["effect_duration"], self.sprite))
                if target := map_entities[tile[1]][tile[0]]:
                    target.stat_dict["health_current"] += self.stat_dict["health_change"]
                    self.change_action_weight(target, self.stat_dict["action_weight_change"])
                    self.change_relation_weight(target, self.stat_dict["relation_weight_change"])

            self.current_ring += 1
            if self.current_ring > self.stat_dict["radius"]:
                self.ruler_wizard.spell_list.remove(self)

class Heal(KindSelect):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = 10
        self.stat_dict["relation_weight_change"] = 10
        self.stat_dict["health_change"] = 50

    def impact(self, target):

        target.stat_dict["health_current"] += self.stat_dict["health_change"]
        self.change_action_weight(target, self.stat_dict["action_weight_change"])
        self.change_relation_weight(target, self.stat_dict["relation_weight_change"])
        self.ruler_wizard.spell_list.remove(self)


class DummySpell:
    """Superficial dummy spell, exists at a given tile for a given duration then vanishes."""

    def __init__(self, ruler_wizard, location, duration, sprite):

        self.ruler_wizard = ruler_wizard
        self.location = location
        self.duration = duration
        self.sprite = sprite

        self.dummy_start_time = timer.timer.now()
        self.status = None

    def update(self, map_entities, map_resource, map_item, move_attempt):

        if timer.timer.check(self.dummy_start_time, self.duration):
            self.ruler_wizard.spell_list.remove(self)