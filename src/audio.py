import pygame as pg
import math

import pathfinding


class Audio:

    def __init__(self, receiver_entity):

        pg.mixer.init()
        self.receiver_entity = receiver_entity
        self.music_current = None
        self.sound_volume = 0
        self.music_volume = 0
        self.sound_dict = {"n_birth": (pg.mixer.Sound("../sounds/pure_c.wav"), 0.8),
                           "n_construction": (pg.mixer.Sound("../sounds/pure_c.wav"), 0.8),
                           "n_move": (pg.mixer.Sound("../sounds/pure_d.wav"), 0.4)}
        self.music_dict = {"n_theme": "../sounds/theme.mp3"}


    def play_relative_sound(self, sound, location):
        """Play a sound from the sound dictionary base on input sound key, each with its own base volume and audio file.
        Volume relative to distance from player wizard."""

        distance_modifier = 1 / math.sqrt(pathfinding.find_distance(location, self.receiver_entity.location) + 0.01)
        if self.sound_dict[sound][1] * distance_modifier >= 0.05:
            self.sound_dict[sound][0].set_volume(self.sound_dict[sound][1]*distance_modifier*self.sound_volume)
            self.sound_dict[sound][0].play()

    def play_music(self, music):

        if self.music_current != music:
            pg.mixer.music.load(self.music_dict[music])
            pg.mixer.music.set_volume(self.music_volume)
            pg.mixer.music.play()
            self.music_current = music

    def stop_music(self):

        pg.mixer.music.stop()
        self.music_current = None


audio = None