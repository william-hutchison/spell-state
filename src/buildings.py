import pygame as pg
import random

import pathfinding
import globe


class Building:
    """Parent building class for various building objects."""
    
    def __init__(self, ruler_state, location):

        self.stat_dict = {"stock_max":0,
                          "health_max": 100,
                          "health_current": 100}

        self.sprite = pg.image.load('../sprites/house.png')
        self.ruler_state = ruler_state
        self.location = location
        self.stock_list = []
        self.stock_list_needed = []

        self.time_last = globe.time.now()
        self.under_construction = 0
        self.under_work = 0

    def update(self, map_topology, map_item):

        if self.stat_dict["health_current"] <= 0:
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
        self.sprite = pg.image.load('../sprites/construction.png')
        self.constructing(0)

    def constructed(self):
        
        self.sprite = pg.image.load('../sprites/tower.png')
        self.stat_dict["stock_max"] = 100
        self.ruler_state.stat_dict["person_max"] += 3


class House(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('../sprites/construction.png')
        self.stock_list_needed = ruler_state.building_dict["house"]["cost"]
        self.stat_dict["stock_max"] = len(self.stock_list_needed)
        self.under_construction = 4000

    def constructed(self):

        self.sprite = pg.image.load('../sprites/house.png')
        self.stock_list_needed = []
        self.stat_dict["stock_max"] = 0
        self.ruler_state.stat_dict["person_max"] += 1


class Shrine(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('../sprites/construction.png')
        self.under_construction = 6000
        self.max_work = 3000
        self.under_work = self.max_work

    def constructed(self):

        self.sprite = pg.image.load('../sprites/house.png')
        pass

    def work(self):

        print("work complete")


class WellOfCurses(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('../sprites/construction.png')
        self.stock_list_needed = ruler_state.building_dict["well_of_curses"]["cost"]
        self.stat_dict["stock_max"] = len(self.stock_list_needed)
        self.under_construction = 6000
        self.max_work = 2000
        self.under_work = self.max_work

    def constructed(self):

        self.sprite = pg.image.load('../sprites/house.png')
        self.stock_list_needed = []
        self.stat_dict["stock_max"] = 0

    def work(self):

        temp_list = []
        for i in ["fireball", "paralyse", "storm"]:
            if not self.ruler_state.wizard.spell_dict[i]["unlocked"]:
                temp_list.append(i)
        if temp_list:
            choice = random.choice(temp_list)
            self.ruler_state.wizard.spell_dict[choice]["unlocked"] = True


class WellOfBlessings(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('../sprites/construction.png')
        self.stock_list_needed = ruler_state.building_dict["well_of_blessings"]["cost"]
        self.stat_dict["stock_max"] = len(self.stock_list_needed)
        self.under_construction = 6000
        self.max_work = 2000
        self.under_work = self.max_work

    def constructed(self):

        self.sprite = pg.image.load('../sprites/house.png')
        self.stock_list_needed = []
        self.stat_dict["stock_max"] = 0

    def work(self):

        temp_list = []
        for i in ["heal"]:
            if not self.ruler_state.wizard.spell_dict[i]["unlocked"]:
                temp_list.append(i)
        if temp_list:
            choice = random.choice(temp_list)
            self.ruler_state.wizard.spell_dict[choice]["unlocked"] = True
