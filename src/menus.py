import pygame as pg
import os
import random


class MenuManager:
    """Stores and updates the current menu object. Creates a new menu object when required."""

    def __init__(self):

        self.menu_dict = {"Play": None, "Start": Start, "Pause": Pause, "Settings": Settings, "Load": Load, "Save": Save}
        self.current_menu = self.menu_dict["Start"]()

    def update(self, events, set_window_scale, save_file, load_file, exit_game):

        self.current_menu.navigate(events)
        selection = self.current_menu.select(events, set_window_scale, save_file, load_file, exit_game)

        if type(self.current_menu).__name__ != selection:
            if selection == "Play":
                self.current_menu = self.menu_dict[selection]
            else:
                self.current_menu = self.menu_dict[selection]()


class Menu:
    """Parent class for various menu objects."""

    def __init__(self):

        self.options = []
        self.current_option = 0

    def navigate(self, events):
        """Change current menu option based on events."""

        key_press = events[0]
        keys = events[1]
        if key_press:
            if keys[pg.K_DOWN]:
                if self.current_option < len(self.options) - 1:
                    self.current_option += 1
            elif keys[pg.K_UP]:
                if self.current_option > 0:
                    self.current_option -= 1


class Start(Menu):

    def __init__(self):

        super().__init__()
        self.options = ["Play", "Load", "Settings", "Quit"]

    def select(self, events, set_window_scale, save_file, load_file, exit_game):

        key_press = events[0]
        keys = events[1]

        if key_press:
            if keys[pg.K_RETURN]:
                if self.options[self.current_option] == "Quit":
                    exit_game()
                else:
                    return self.options[self.current_option]
        return type(self).__name__


class Pause(Menu):

    def __init__(self):

        super().__init__()
        self.options = ["Play", "Save", "Quit"]

    def select(self, events, set_window_scale, save_file, load_file, exit_game):

        key_press = events[0]
        keys = events[1]

        if key_press:
            if keys[pg.K_RETURN]:
                if self.options[self.current_option] == "Quit":
                    exit_game()
                else:
                    return self.options[self.current_option]
        return type(self).__name__


class Settings(Menu):

    def __init__(self):

        super().__init__()
        self.options = ["1200 x 800", "2400 x 1600", "Start"]

    def select(self, events, set_window_scale, save_file, load_file, exit_game):

        key_press = events[0]
        keys = events[1]

        if key_press:
            if keys[pg.K_RETURN]:
                if self.options[self.current_option] == "1200 x 800":
                    set_window_scale(0)
                elif self.options[self.current_option] == "2400 x 1600":
                    set_window_scale(1)
                else:
                    return self.options[self.current_option]
        return type(self).__name__


# TODO Fix saving and loading
class Load(Menu):

    def __init__(self):

        super().__init__()
        file_names = os.listdir("../saves")
        self.options = file_names + ["Start"]

    def select(self, events, set_window_scale, save_file, load_file, exit_game):

        key_press = events[0]
        keys = events[1]

        if key_press:
            if keys[pg.K_RETURN]:
                if self.options[self.current_option] != "Start":
                    load_file(self.options[self.current_option])
                else:
                    return self.options[self.current_option]
        return type(self).__name__


class Save(Menu):

    def __init__(self):

        super().__init__()
        file_name = [str(random.randint(0000, 9999))]
        self.options = file_name + ["Pause"]

    def select(self, events, set_window_scale, save_file, load_file, exit_game):

        key_press = events[0]
        keys = events[1]

        if key_press:
            if keys[pg.K_RETURN]:
                if self.options[self.current_option] != "Pause":
                    save_file(self.options[self.current_option])
                else:
                    return self.options[self.current_option]
        return type(self).__name__
