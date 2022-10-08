import globe
import pathfinding


class Spell:

    def __init__(self, wizard):

        self.ruler_wizard = wizard
        self.location = wizard.location
        self.status = "hold"

        self.effect_target = None
        self.effect_start_time = None


class SpellKindSelf(Spell):

    def __init__(self, wizard):

        super().__init__(wizard)

    def update(self, map_entities, map_resource, map_item, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
        if move_attempt:
            self.impact(map_entities)
            self.ruler_wizard.spell_list.remove(self)


class SpellKindDirectional(Spell):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.move_direction = (0, 0)
        self.travel_current = 0
        self.time_dur_move = 100
        self.time_last = 0  # to allow immediate cast IS THIS DESIRABLE?

    def update(self, map_entities, map_resource, map_item, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
        elif self.status == "effect":
            print("try")
            self.effect(self.effect_target)

        if type(move_attempt) == tuple:
            self.status = "moving"
            self.move_direction = move_attempt

        if self.status == "moving":

            # check for spell movement
            if self.travel_current <= self.travel_max+1:
                self.move(self.move_direction)
            if self.travel_current >= self.travel_max+1 or not 0 <= self.location[0] < globe.WORLD_SIZE[0] or not 0 <= self.location[1] < globe.WORLD_SIZE[1]:
                self.ruler_wizard.spell_list.remove(self)

            # check for spell impact
            else:

                # special case for harvesting
                if type(self).__name__ == "SpellHarvest":
                    if target := map_resource[self.location[1]][self.location[0]]:
                        self.impact(target)
                        self.ruler_wizard.spell_list.remove(self)

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

        if globe.time.check(self.time_last, self.time_dur_move):
            self.location = (self.location[0] + move_attempt[0], self.location[1] + move_attempt[1])
            self.travel_current += 1
            self.time_last = globe.time.now()


class SpellKindSelect(Spell):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.location_select = self.ruler_wizard.location
        self.status = "select"

    def update(self, map_entities, map_resource, map_item, map_move_attempt):

        self.location = self.ruler_wizard.location

    def select(self, map_entities):

        if target := map_entities[self.location_select[1]][self.location_select[0]]:
            self.impact(target)


class SpellHarvest(SpellKindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 1

    def impact(self, target):

        if target:
            if len(self.ruler_wizard.stock_list) < self.ruler_wizard.stock_list_limit:
                self.ruler_wizard.stock_list.append(target)

        self.ruler_wizard.spell_list.remove(self)


class SpellGiveItem(SpellKindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 1

    def impact(self, target):

        # TODO Select item from item list with arrow keys and enter (matching location selection spells)
        if self.ruler_wizard.stock_list:
            if len(target.stock_list) < target.stock_list_limit:
                target.stock_list.append(self.ruler_wizard.stock_list.pop(0))

        self.ruler_wizard.spell_list.remove(self)

    def map_item_impact(self, map_item):

        if self.ruler_wizard.stock_list:
            if map_item[self.location[1]][self.location[0]] == "":
                map_item[self.location[1]][self.location[0]] = self.ruler_wizard.stock_list.pop(0)

        self.ruler_wizard.spell_list.remove(self)


class SpellPickupItem(SpellKindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 1

    def impact(self, target):

        # TODO Select item from item list with arrow keys and enter (matching location selection spells)
        if len(self.ruler_wizard.stock_list) < self.ruler_wizard.stock_list_limit:
            if target.stock_list:
                self.ruler_wizard.stock_list.append(target.stock_list.pop(0))

        self.ruler_wizard.spell_list.remove(self)

    def map_item_impact(self, map_item):

        if len(self.ruler_wizard.stock_list) < self.ruler_wizard.stock_list_limit:
            if map_item[self.location[1]][self.location[0]]:
                self.ruler_wizard.stock_list.append(map_item[self.location[1]][self.location[0]])
                map_item[self.location[1]][self.location[0]] = ""

        self.ruler_wizard.spell_list.remove(self)


class SpellConsume(SpellKindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 1
        self.health_damage = 1000
        self.mana_gain = 60
        self.action_weight_change = -5

    def impact(self, target):

        if type(target).__name__ == "Person":
            target.stat_dict["u_health_current"] -= self.health_damage
            self.ruler_wizard.stat_dict["u_mana_current"] += self.mana_gain

            # TODO Create function for this in Spell class
            if target.ruler_state == self.ruler_wizard.ruler_state:
                target.ruler_state.action_dict[target.action_super]["weight"] += self.action_weight_change

        self.ruler_wizard.spell_list.remove(self)


class SpellFireball(SpellKindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 10
        self.health_damage = 50
        self.action_weight_change = -5

    def impact(self, target):

        target.stat_dict["u_health_current"] -= self.health_damage

        if type(target).__name__ == "Person":
            if target.ruler_state == self.ruler_wizard.ruler_state:
                target.ruler_state.action_dict[target.action_super]["weight"] += self.action_weight_change

        self.ruler_wizard.spell_list.remove(self)


class SpellParalyse(SpellKindDirectional):

    # TODO Allow multiple spells to exist simultaneously
    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 3
        self.move_duration_change = 10000
        self.effect_duration = 50000
        self.action_weight_change = -5

    def impact(self, target):

        if type(target).__name__ in ["Person", "Wizard"]:
            target.stat_dict["u_move_duration"] += self.move_duration_change
            self.status = "effect"
            self.effect_target = target
            self.effect_start_time = globe.time.now()
        else:
            self.ruler_wizard.spell_list.remove(self)

        if type(target).__name__ == "Person":
            if target.ruler_state == self.ruler_wizard.ruler_state:
                target.ruler_state.action_dict[target.action_super]["weight"] += self.action_weight_change

    def effect(self, target):

        if globe.time.check(self.effect_start_time, self.effect_duration):
            target.stat_dict["u_move_duration"] -= self.move_duration_change
            self.ruler_wizard.spell_list.remove(self)

        print("paralysing")


class SpellStorm(SpellKindSelf):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.health_damage = 100
        self.radius = 4
        self.action_weight_change = -5

    def impact(self, map_entities):

        radius_list = pathfinding.find_within_radius(self.ruler_wizard.location, self.radius)
        radius_list.remove(self.ruler_wizard.location)

        # TODO Move logic to within area of effect class and inherit
        for i in radius_list:
            target = map_entities[i[1]][i[0]]
            if target:
                map_entities[i[1]][i[0]].stat_dict["u_health_current"] -= self.health_damage

                if type(target).__name__ == "Person":
                    if target.ruler_state == self.ruler_wizard.ruler_state:
                        target.ruler_state.action_dict[target.action_super]["weight"] += self.action_weight_change

        self.ruler_wizard.spell_list.remove(self)


class SpellHeal(SpellKindSelect):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.health_heal = 50
        self.action_weight_change = 10

    def impact(self, target):

        target.stat_dict["u_health_current"] += self.health_heal

        if type(target).__name__ == "Person":
            if target.ruler_state == self.ruler_wizard.ruler_state:
                target.ruler_state.action_dict[target.action_super]["weight"] += self.action_weight_change

        self.ruler_wizard.spell_list.remove(self)
