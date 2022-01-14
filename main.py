import pygame as pg

import player
import world
import graphics
import menu
import glob


class Game:

    def __init__(self):

        pg.init()
        self.world = world.World()
        self.player = player.Player(self.world.state_list[0].wizard)
        self.graphics = graphics.Graphics()

        self.game_state = "start"

    def update(self):

        if self.game_state == "start":
            self.start()
        elif self.game_state == "play":
            self.play()

        pg.display.update()

    def start(self):

        self.game_state = menu.start(self.player.event_loop(), self.graphics.set_window_scale)
        self.graphics.draw_start()

    def play(self):

        self.world.update()
        self.player.update(self.world.map_topology, self.world.map_resource, self.world.map_entities)
        self.graphics.update_terrain(self.player.camera.location, self.player.camera.inspector_location,
                                     self.player.character.wizard.location, self.world.map_topology,
                                     self.world.map_resource, self.world.state_list)
        self.graphics.update_ui_panel(self.world.state_list[0], self.player.camera, self.player.character,
                                self.player.camera.inspector_dict)
        self.graphics.update_ui_wizard(player.spell_dict) # TODO MOVE THIS DICT SOMEWHERE BETTER
        self.graphics.update_window()
        glob.time.update()


game = Game()
while True:
    game.update()





