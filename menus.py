import pygame as pg
import os
import random


class Menu:

    def __init__(self):

        self.options = []        
        self.current_option = 0

    def start(self, events):
        
        self.options = ["play", "load", "settings", "quit"]
        return self.option_select(events, "start")

    def pause(self, events):

        self.options = ["play", "save", "quit"]
        return self.option_select(events, "pause")

    def settings(self, events, set_window_scale):
        
        self.options = ["1200 x 800", "2400 x 1600", "back"]
        option_selected = self.option_select(events, "settings")

        if option_selected == "1200 x 800":
            set_window_scale(0)
            return "settings"
        elif option_selected == "2400 x 1600":
            set_window_scale(1)
            return "settings"
        elif option_selected == "back": 
            return "start"

        return "settings"

    def load(self, events, load_file):

        file_names = os.listdir("saves")
        self.options = file_names + ["back"]
        option_selected = self.option_select(events, "load")

        if option_selected not in ["back", "load"]:
            load_file(option_selected)
            return "play"
        if option_selected == "back":
            return "start"

        return "load"

    def save(self, events, save_file):

        file_name = str(random.randint(0000, 9999))
        self.options = [file_name] + ["back"]     
        option_selected = self.option_select(events, "save")

        if option_selected not in ["back", "save"]:
            save_file(option_selected)
            return "pause"
        if option_selected == "back":
            return "pause"

        return "save"

    def option_select(self, events, game_state):

        key_press = events[0]
        keys = events[1]

        if key_press:
            if keys[pg.K_DOWN]:
                if self.current_option < len(self.options) - 1:
                    self.current_option += 1
            elif keys[pg.K_UP]:
                if self.current_option > 0:
                    self.current_option -= 1
            elif keys[pg.K_RETURN]:
                temp_selection = self.options[self.current_option]
                self.current_option = 0
                return(temp_selection)
        
        return game_state