import globe
import pathfinding


class Spell:

    def __init__(self, wizard):

        self.stat_dict = {}

        self.ruler_wizard = wizard
        self.location = wizard.location
        self.status = "hold"

        self.effect_target = None
        self.effect_start_time = None

    def change_action_weight(self, target, action_weight_change):

        if type(target).__name__ == "Person":
            if target.ruler_state == self.ruler_wizard.ruler_state:
                target.ruler_state.action_dict[target.action_super]["weight"] += action_weight_change


class KindSelf(Spell):

    def __init__(self, wizard):

        super().__init__(wizard)

    def update(self, map_entities, map_resource, map_item, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
        if move_attempt:
            self.impact(map_entities)
            self.ruler_wizard.spell_list.remove(self)


class KindDirectional(Spell):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.move_direction = (0, 0)
        self.travel_current = 0
        self.time_last = 0

    def update(self, map_entities, map_resource, map_item, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
        elif self.status == "effect":
            self.effect(self.effect_target)

        if type(move_attempt) == tuple:
            self.status = "moving"
            self.move_direction = move_attempt

        if self.status == "moving":

            # check for spell movement
            if self.travel_current <= self.stat_dict["move_max"]+1:
                self.move(self.move_direction)
            if self.travel_current >= self.stat_dict["move_max"]+1 or not 0 <= self.location[0] < globe.WORLD_SIZE[0] or not 0 <= self.location[1] < globe.WORLD_SIZE[1]:
                self.ruler_wizard.spell_list.remove(self)

            # check for spell impact
            else:

                # special case for harvesting
                if type(self).__name__ == "SpellHarvest":
                    if target := map_resource[self.location[1]][self.location[0]]:
                        self.impact(target)

                # special case for accessing items
                elif type(self).__name__ in ["SpellGiveItem", "SpellPickupItem"]:
                    if target := map_entities[self.location[1]][self.location[0]]:
                        self.impact(target)
                    else:
                        self.map_item_impact(map_item)

                # all other spells
                else:
                    if target := map_entities[self.location[1]][self.location[0]]:
                        self.impact(target)

    def move(self, move_attempt):

        if globe.time.check(self.time_last, self.stat_dict["move_duration"]):
            self.location = (self.location[0] + move_attempt[0], self.location[1] + move_attempt[1])
            self.travel_current += 1
            self.time_last = globe.time.now()


class KindSelect(Spell):

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


class GiveItem(KindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 1

    def impact(self, target):

        # TODO Select item from item list with arrow keys and enter (matching location selection spells)
        if self.ruler_wizard.stock_list:
            if len(target.stock_list) < target.stat_dict["stock_max"]:
                target.stock_list.append(self.ruler_wizard.stock_list.pop(0))

        self.ruler_wizard.spell_list.remove(self)

    def map_item_impact(self, map_item):

        if self.ruler_wizard.stock_list:
            if map_item[self.location[1]][self.location[0]] == "":
                map_item[self.location[1]][self.location[0]] = self.ruler_wizard.stock_list.pop(0)

        self.ruler_wizard.spell_list.remove(self)


class PickupItem(KindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 1

    def impact(self, target):

        # TODO Select item from item list with arrow keys and enter (matching location selection spells)
        if len(self.ruler_wizard.stock_list) < self.ruler_wizard.stat_dict["stock_max"]:
            if target.stock_list:
                self.ruler_wizard.stock_list.append(target.stock_list.pop(0))

        self.ruler_wizard.spell_list.remove(self)

    def map_item_impact(self, map_item):

        if len(self.ruler_wizard.stock_list) < self.ruler_wizard.stat_dict["stock_max"]:
            if map_item[self.location[1]][self.location[0]]:
                self.ruler_wizard.stock_list.append(map_item[self.location[1]][self.location[0]])
                map_item[self.location[1]][self.location[0]] = ""

        self.ruler_wizard.spell_list.remove(self)


class Consume(KindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 1
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["health_change"] = -1000
        self.stat_dict["mana_change"] = 60

    def impact(self, target):

        if type(target).__name__ == "Person":
            target.stat_dict["health_current"] += self.stat_dict["health_change"]
            self.ruler_wizard.stat_dict["mana_current"] += self.stat_dict["mana_change"]

        self.change_action_weight(target, self.stat_dict["action_weight_change"])
        self.ruler_wizard.spell_list.remove(self)


class Fireball(KindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 10
        self.stat_dict["health_change"] = -50

    def impact(self, target):

        target.stat_dict["health_current"] -= self.stat_dict["health_change"]
        self.change_action_weight(target, self.stat_dict["action_weight_change"])
        self.ruler_wizard.spell_list.remove(self)


class Paralyse(KindDirectional):

    # TODO Allow multiple spells to exist simultaneously
    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["move_duration"] = 100
        self.stat_dict["move_max"] = 3
        self.stat_dict["move_duration_change"] = 10000
        self.stat_dict["effect_duration"] = 5000

    def impact(self, target):

        if type(target).__name__ in ["Person", "Wizard"]:
            target.stat_dict["move_duration"] += self.stat_dict["move_duration_change"]
            self.status = "effect"
            self.effect_target = target
            self.effect_start_time = globe.time.now()
        else:
            self.ruler_wizard.spell_list.remove(self)

        self.change_action_weight(target, self.stat_dict["action_weight_change"])

    def effect(self, target):

        if globe.time.check(self.effect_start_time, self.stat_dict["effect_duration"]):
            target.stat_dict["move_duration"] -= self.stat_dict["move_duration_change"]
            self.ruler_wizard.spell_list.remove(self)


class Storm(KindSelf):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = -5
        self.stat_dict["health_change"] = -100
        self.stat_dict["radius"] = 4

    def impact(self, map_entities):

        radius_list = pathfinding.find_within_radius(self.ruler_wizard.location, self.stat_dict["radius"])
        radius_list.remove(self.ruler_wizard.location)

        # TODO Move logic to within area of effect class and inherit
        for i in radius_list:
            target = map_entities[i[1]][i[0]]
            if target:
                map_entities[i[1]][i[0]].stat_dict["health_current"] += self.stat_dict["health_change"]
                self.change_action_weight(target, self.stat_dict["action_weight_change"])

        self.ruler_wizard.spell_list.remove(self)


class Heal(KindSelect):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.stat_dict["action_weight_change"] = 10
        self.stat_dict["health_change"] = 50

    def impact(self, target):

        target.stat_dict["health_current"] += self.stat_dict["health_change"]
        self.change_action_weight(target, self.stat_dict["action_weight_change"])
        self.ruler_wizard.spell_list.remove(self)
