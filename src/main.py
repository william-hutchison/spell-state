import pygame as pg
import sys
import pickle

import player
import world
import graphics
import menus
import globe
import audio


class Game:

    def __init__(self):

        pg.init()
        globe.time = globe.Time()
        self.world = world.World()
        self.player = player.Player(self.world.state_list[0].wizard)
        self.graphics = graphics.Graphics()
        self.menu_manager = menus.MenuManager()
        audio.audio = audio.Audio(self.world.state_list[0].wizard)

    def update(self):

        events = event_loop()
        if not self.menu_manager.current_menu:
            self.play(events)
            audio.audio.stop_music()
            # TODO Stop time from increasing while the game is paused
            globe.time.update()
        else:
            self.graphics.draw_menu(self.menu_manager.current_menu.options, self.menu_manager.current_menu.current_option)
            self.menu_manager.update(events, self.graphics.set_window_scale, self.save_file, self.load_file, self.exit_game)
        pg.display.update()

    # TODO Move these functions somewhere else
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

    def exit_game(self):
        
        pg.quit()
        sys.exit()

    def play(self, events):

        self.player.update(self.world.map_topology, self.world.map_resource, self.world.map_item, self.world.map_entities, events)
        self.world.update()
        self.graphics.update_world(self.player.camera.location, self.world.map_topology, self.world.map_resource, self.world.map_item, self.world.map_entities)
        self.graphics.update_overlay(self.player.camera.location, self.player.camera.inspector_location, self.player.camera.inspector_mode, self.player.character.wizard.location, self.world.state_list)
        self.graphics.update_interface(self.world.state_list[0], self.player.character, self.player.camera, self.player.camera.inspector_dict)

        if events[0] and events[1][pg.K_ESCAPE]:
            self.menu_manager.current_menu = self.menu_manager.menu_dict["Pause"]()


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
