import pygame as pg


def item_add(list, item, number):

    count = 0
    while count < number:
        list.append(item)
        count += 1
    return count


def item_remove(list, item, number):

    count = 0
    while count < number and item in list:
        list.remove(item)
        count +=1
    return count


def item_transfer(list_from, list_to, item, number):

    count = 0
    while count < number and item in list_from:
        list_from.remove(item)
        list_to.append(item)
        count += 1
    return count


def item_count(list, item):

    count = 0
    for i in list:
        if i == item:
            count += 1
    return count


def item_summary(list):

    dict = {}
    for item in list:
        if item in dict:
            dict[item] += 1
        else:
            dict[item] = 1
    return dict


def colour_image(image, colour):
    """Replace the file colour values with the given input colour."""

    image = image.copy()
    image.fill((0, 0, 0, 255), None, pg.BLEND_RGBA_MULT)
    image.fill(colour[0:3] + (0,), None, pg.BLEND_RGBA_ADD)
    return image
