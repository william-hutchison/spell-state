import pygame as pg


class Timer:
    """Class to store time information and handle time information requests from other parts of
    the program."""

    def __init__(self):

        self.FRAME_DURATION = 800
        self.FRAME_NUMBER = 4

        self.clock = pg.time.Clock()

        self.game_time = 0
        self.world_time = 0

        self.current_frame = 0
        self.last_frame_time = 0

    def update(self):
        """Update game_time, world_time, display frame and global animation frame."""
        
        self.clock.tick(20)

        self.game_time += self.clock.get_time()
        self.world_time += self.clock.get_time()
        
        # Cycle current animation frame when approriate
        if self.game_time - self.last_frame_time >= self.FRAME_DURATION:
            if self.current_frame < self.FRAME_NUMBER - 1:
                self.current_frame += 1
            else:
                self.current_frame = 0

            self.last_frame_time = self.game_time

    def pause(self):
        """Deducts time elapsed this step from world_time to prevent world_time progression."""

        self.world_time -= self.clock.get_time()

    def frame(self):
        """Returns the current global animation frame."""

        return self.current_frame

    def now(self):
        """Returns world_time in milliseconds."""
        
        return self.world_time

    def check(self, time_last, time_duration):
        """Returns True if the time_duration has been exceeded, otherwise returns False."""

        if self.world_time - time_last >= time_duration:
            return True
        else:
            return False

    def set_time(self, new_time):
        """Set world_time to equal the input new_time."""

        self.world_time = new_time


# Time object stored within this file for easy access elsewhere in the program
timer = None
