import pygame as pg


class Time:
    """Class to store time information and handle time information requests from other parts of
    the program."""

    def __init__(self):

        self.clock = pg.time.Clock()
        self.time_now = 0
        self.frame_now = 0
        self.frame_last = 0

    def update(self):
        """Update display frame, global time in milliseconds and global animation frame."""
        
        self.clock.tick(20)

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

    def set_time(self, new_time):
        """Set time_now to equaly tht input new_time."""

        self.time_now = new_time


# Time object stored within this file for easy access elsewhere in the program
time = None

# TODO This can probably all go somewhere else, turn globe into a file for time only
WORLD_SIZE = (60, 60)
TILE_SIZE = 20
STATE_NUMBER = 2

TIME_CAMERA = 100
TIME_FRAME = 1200
