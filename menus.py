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


def pause(event_loop):

    key_press = event_loop[0]
    keys = event_loop[1]

    if key_press and keys[pg.K_ESCAPE]:
        return "play"

    return "pause"


def play(event_loop):

    key_press = event_loop[0]
    keys = event_loop[1]

    if key_press and keys[pg.K_ESCAPE]:
        return "pause"

    return "play"
