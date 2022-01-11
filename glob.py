import pygame as pg


class Time:

    def __init__(self):

        self.clock = pg.time.Clock()
        self.time_now = 0

    def update(self):
        
        self.clock.tick(20)
        self.time_now = pg.time.get_ticks()

    def now(self):
        """Returns the current time in milliseconds."""
        
        return self.time_now

    def check(self, time_last, time_duration):
        """Returns true if the duration has been exceeded, returns false if not."""

        if self.time_now - time_last >= time_duration:
            return True
        else:
            return False


time = Time()

WORLD_SIZE = (60, 60)
TILE_SIZE = 20
STATE_NUMBER = 2

FOOD = 1
WOOD = 2
METAL = 3

HOUSE_COST = 5

TIME_CAMERA = 100
