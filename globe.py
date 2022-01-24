import pygame as pg


class Time:

    def __init__(self):

        self.clock = pg.time.Clock()
        self.time_now = 0
        self.frame_now = 0

        self.frame_last = 0

    def update(self, game_state):
        """Update display frame, global time in milliseconds and global animation frame."""
        
        self.clock.tick(20)

        if game_state == "play":
            self.time_now += self.clock.get_time()

        if self.check(self.frame_last, TIME_FRAME):
            if self.frame_now < 2:
                self.frame_now += 1
            else:
                self.frame_now = 0

            self.frame_last = self.now()

    def frame(self):
        """Returns the current global animation frame."""

        return self.frame_now

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

CODE_FOOD = 1
CODE_WOOD = 2
CODE_METAL = 3

COST_HOUSE = 5
COST_SHRINE = 3

TIME_CAMERA = 100
TIME_FRAME = 1200
