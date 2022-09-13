import pygame as pg
import math

import pathfinding


class Audio:

    def __init__(self, receiver_entity):

        pg.mixer.init()
        self.sound_dict = {"birth": (pg.mixer.Sound("sounds/pure_c.wav"), 0.6), "construction": (pg.mixer.Sound("sounds/pure_c.wav"), 0.6), "move": (pg.mixer.Sound("sounds/pure_d.wav"), 0.2)}
        self.receiver_entity = receiver_entity

    def play_relative_sound(self, sound, location):
        """Play a sound from the sound dictionary base on input sound key, each with its own base volume and audio file.
        Volume relative to distance from player wizard."""

        distance_modifier = 1 / math.sqrt(pathfinding.find_distance(location, self.receiver_entity.location))
        if self.sound_dict[sound][1] * distance_modifier >= 0.05:
            self.sound_dict[sound][0].set_volume(self.sound_dict[sound][1] * distance_modifier)
            self.sound_dict[sound][0].play()


audio = None