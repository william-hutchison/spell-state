import globe
import pathfinding


class Spell:

    def __init__(self, wizard):

        self.ruler_wizard = wizard
        self.location = wizard.location
        self.status = "hold"


class SpellKindSelf(Spell):

    def __init__(self, wizard):

        super().__init__(wizard)

    def update(self, map_entities, move_attempt):

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

    def update(self, map_entities, move_attempt):

        if self.status == "hold":
            self.location = self.ruler_wizard.location
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
                if target := map_entities[self.location[1]][self.location[0]]:
                    self.impact(target)
                    self.ruler_wizard.spell_list.remove(self)

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

    def update(self, map_entities, move_attempt):

        self.location = self.ruler_wizard.location

    def select(self, map_entities):

        if target := map_entities[self.location_select[1]][self.location_select[0]]:
            self.impact(target)
        self.ruler_wizard.spell_list.remove(self)


class SpellConsume(SpellKindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 1
        self.health_damage = 1000
        self.mana_gain = 60

    def impact(self, target):

        if type(target).__name__ == "Person":
            target.stat_dict["health current"] -= self.health_damage
            self.ruler_wizard.stat_dict["mana current"] += self.mana_gain

            if target.ruler_state == self.ruler_wizard.ruler_state:
                self.ruler_wizard.ruler_state.stat_dict["fear"] += 2
                self.ruler_wizard.ruler_state.stat_dict["loyalty"] -= 1


class SpellFireball(SpellKindDirectional):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.travel_max = 10
        self.health_damage = 50

    def impact(self, target):

        target.stat_dict["health current"] -= self.health_damage


class SpellStorm(SpellKindSelf):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.health_damage = 100
        self.radius = 4

    def impact(self, map_entities):

        radius_list = pathfinding.find_within_radius(self.ruler_wizard.location, self.radius)
        radius_list.remove(self.ruler_wizard.location)

        for i in radius_list:
            if map_entities[i[1]][i[0]]:
                map_entities[i[1]][i[0]].stat_dict["health current"] -= self.health_damage


class SpellHeal(SpellKindSelect):

    def __init__(self, wizard):

        super().__init__(wizard)
        self.health_heal = 50

    def impact(self, target):

        target.stat_dict["health current"] += self.health_heal


spell_info = {"s_consume": {"obj": SpellConsume, "cost": 20, "combo": ["down", "down"], "unlocked": True},
              "s_fireball": {"obj": SpellFireball, "cost": 40, "combo": ["up", "left"], "unlocked": False},
              "s_storm": {"obj": SpellStorm, "cost": 100, "combo": ["left", "up", "right", "down"], "unlocked": False},
              "s_heal": {"obj": SpellHeal, "cost": 40, "combo": ["up", "down", "up"], "unlocked": True}}

