import pygame as pg
import random

import globe


class Building:
    
    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.sprite = pg.image.load('sprites/house.png')
        self.time_last = globe.time.now()
        self.under_construction = 0
        self.under_work = 0

        self.stat_dict = {"health max": 100, "health current": 100}

    def update(self):

        if self.stat_dict["health current"] <= 0:
            self.ruler_state.building_list.remove(self)

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
        self.sprite = pg.image.load('sprites/tower.png')


class House(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('sprites/construction.png')
        self.under_construction = 4000

    def constructed(self):

        self.ruler_state.increase_pop_limit(self.ruler_state, 1)
        self.sprite = pg.image.load('sprites/house.png')


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
        self.under_construction = 6000
        self.max_work = 2000
        self.under_work = self.max_work

    def constructed(self):

        self.sprite = pg.image.load('sprites/house.png')
        pass

    def work(self):

        print("work complete")


class Tavern(Building):

    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.sprite = pg.image.load('sprites/construction.png')
        self.under_construction = 6000

    def constructed(self):

        self.sprite = pg.image.load('sprites/house.png')
        pass


building_info = {"tower": {"obj": Tower, "cost": []},
                 "house": {"obj": House, "cost": [(globe.CODE_WOOD, 3)]},
                 "shrine": {"obj": Shrine, "cost": [(globe.CODE_WOOD, 1)]},
                 "tavern": {"obj": Tavern, "cost": [(globe.CODE_METAL, 3)]},
                 "lab_offence": {"obj": LabOffence, "cost": [(globe.CODE_WOOD, 1)]}}