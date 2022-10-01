import pygame as pg
import random

import pathfinding
import globe


class Building:
    
    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.sprite = pg.image.load('sprites/house.png')
        self.stock_list = []
        self.stock_list_needed = []
        self.stock_list_limit = 0
        self.time_last = globe.time.now()
        self.under_construction = 0
        self.under_work = 0

        self.stat_dict = {"u_health_max": 100, "u_health_current": 100}

    def update(self, map_topology, map_item):

        if self.stat_dict["u_health_current"] <= 0:
            pathfinding.drop_items(self.location, self.stock_list, map_topology, map_item)
            self.ruler_state.building_list.remove(self)

        for item in self.stock_list_needed:
            if item in self.stock_list:
                self.stock_list_needed.remove(item)
                self.stock_list.remove(item)

    def constructing(self, build_amount):
        """Subtract build_amount from under_construction until 0 is reached, then return 0."""

        self.under_construction -= build_amount
        if self.under_construction <= 0:
            self.under_construction = 0
            self.constructed()

        return self.under_construction

    def working(self, work_amount):
        """Subtract work_amount from under_work until 0 is reached, then return 0."""

        self.under_work -= work_amount
        if self.under_work <= 0:
            self.under_work = self.max_work
            self.work()

            return 0
        return self.under_work


class Tower(Building):
    
    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('sprites/construction.png')
        self.constructing(0)

    def constructed(self):

        self.ruler_state.increase_pop_limit(self.ruler_state, 1)
        self.stock_list_limit = 100
        self.sprite = pg.image.load('sprites/tower.png')


class House(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('sprites/construction.png')
        self.stock_list_needed = building_info["b_house"]["cost"]
        self.stock_list_limit = len(self.stock_list_needed)
        self.under_construction = 4000

    def constructed(self):

        self.ruler_state.increase_pop_limit(self.ruler_state, 1)
        self.sprite = pg.image.load('sprites/house.png')
        self.stock_list_needed = []
        self.stock_list_limit = 0


class Shrine(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('sprites/construction.png')
        self.under_construction = 6000
        self.max_work = 3000
        self.under_work = self.max_work

    def constructed(self):

        self.sprite = pg.image.load('sprites/house.png')
        pass

    def work(self):

        print("work complete")

class LabOffence(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('sprites/construction.png')
        self.stock_list_needed = building_info["b_lab_offence"]["cost"]
        self.stock_list_limit = len(self.stock_list_needed)
        self.under_construction = 6000
        self.max_work = 2000
        self.under_work = self.max_work

    def constructed(self):

        self.sprite = pg.image.load('sprites/house.png')
        self.stock_list_needed = []
        self.stock_list_limit = 0

    def work(self):

        temp_list = []
        for i in ["s_storm", "s_fireball"]:
            if not self.ruler_state.wizard.spell_dict[i]["unlocked"]:
                temp_list.append(i)
        if temp_list:
            choice = random.choice(temp_list)
            self.ruler_state.wizard.spell_dict[choice]["unlocked"] = True


class Tavern(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('sprites/construction.png')
        self.under_construction = 6000

    def constructed(self):

        self.sprite = pg.image.load('sprites/house.png')
        pass


building_info = {"b_tower": {"obj": Tower, "cost": []},
                 "b_house": {"obj": House, "cost": ["i_wood", "i_wood"]},
                 "b_shrine": {"obj": Shrine, "cost": ["i_metal"]},
                 "b_tavern": {"obj": Tavern, "cost": ["i_wood", "i_food"]},
                 "b_lab_offence": {"obj": LabOffence, "cost": ["i_wood", "i_metal"]}}