import pygame as pg
import sys

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
        self.player = player.Player(self.world.state_list[0].wizard)
        self.graphics = graphics.Graphics()
        self.game_state = "start"

    def update(self):

        events = event_loop()
        if self.game_state == "start":
            self.start(events)
        elif self.game_state == "pause":
            self.pause(events)
        elif self.game_state == "play":
            self.play(events)
        globe.time.update(self.game_state)
        pg.display.update()

    def start(self, events):

        self.game_state = menus.start(events, self.graphics.set_window_scale)
        self.graphics.draw_start()

    def pause(self, events):

        self.game_state = menus.pause(events)
        self.graphics.draw_pause()

    def play(self, events):

        self.game_state = menus.play(events)
        self.world.update()
        self.player.update(self.world.map_topology, self.world.map_resource, self.world.map_entities, events)
        self.graphics.update_terrain(self.player.camera.location, self.player.camera.inspector_location, self.player.camera.inspector_mode, self.player.character.wizard.location, self.world.map_topology, self.world.map_resource, self.world.state_list)
        self.graphics.update_ui_panel(self.world.state_list[0], self.player.camera.inspector_dict, self.player.interface)
        self.graphics.update_ui_wizard(self.player.camera, self.player.character, spells.spell_info)
        self.graphics.update_window()


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
