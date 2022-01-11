import pygame as pg


def start(event_loop, set_window_scale):

    keys = event_loop[1]

    if keys[pg.K_1]:
        set_window_scale(0)
        return "play"
    elif keys[pg.K_2]:
        set_window_scale(1)
        return "play"

    return "start"
