import pygame as pg
import sys
import pickle

import player
import world
import graphics
import menus
import spells  # TODO A bit awkward to import lower file in main.
import globe


class Game:

    def __init__(self):

        pg.init()
        self.world = world.World()
        self.menu = menus.Menu()
        self.player = player.Player(self.world.state_list[0].wizard)
        self.graphics = graphics.Graphics()
        self.game_state = "start"

    def update(self):

        events = event_loop()

        if self.game_state == "play":
            self.game_state = self.play(events)
        elif self.game_state == "start":
            self.game_state = self.menu.start(events)
            self.graphics.draw_menu(self.menu.options, self.menu.current_option)
        elif self.game_state == "settings":
            self.game_state = self.menu.settings(events, self.graphics.set_window_scale)
            self.graphics.draw_menu(self.menu.options, self.menu.current_option)
        elif self.game_state == "pause":
            self.game_state = self.menu.pause(events)
            self.graphics.draw_menu(self.menu.options, self.menu.current_option)
        elif self.game_state == "load":
            self.game_state = self.menu.load(events, self.load_file)
            self.graphics.draw_menu(self.menu.options, self.menu.current_option)
        elif self.game_state == "save":
            self.game_state = self.menu.save(events, self.save_file)
            self.graphics.draw_menu(self.menu.options, self.menu.current_option)
        elif self.game_state == "quit":
            self.quit()

        globe.time.update(self.game_state)
        pg.display.update()

    def save_file(self, file_name):

        self.world.save_time = globe.time.now()
        self.world.save_player = player.Player(self.world.state_list[0].wizard)
        
        with open('saves/'+file_name, 'wb') as f:
            pickle.dump(self.world, f)

    def load_file(self, file_name):

        with open('saves/'+file_name, 'rb') as f:
            self.world = pickle.load(f)

        globe.time.set_time(self.world.save_time)  
        self.player = self.world.save_player

    def quit(self):
        
        pg.quit()
        sys.exit()

    def play(self, events):

        self.world.update()
        self.player.update(self.world.map_topology, self.world.map_resource, self.world.map_entities, events)
        self.graphics.update_terrain(self.player.camera.location, self.player.camera.inspector_location, self.player.camera.inspector_mode, self.player.character.wizard.location, self.world.map_topology, self.world.map_resource, self.world.state_list)
        self.graphics.update_ui_panel(self.world.state_list[0], self.player.camera.inspector_dict, self.player.interface)
        self.graphics.update_ui_wizard(self.player.camera, self.player.character, spells.spell_info)
        self.graphics.update_window()

        if events[0] and events[1][pg.K_ESCAPE]:
            return "pause"
        else:
            return "play"

def event_loop():

    key_press = False
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            key_press = True

    return key_press, pg.key.get_pressed()


game = Game()
while True:
    game.update()
