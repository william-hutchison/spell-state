import pygame as pg


def item_add(list, item, number):
    """Add the input number of item to list. Returns the number of items added."""

    count = 0
    while count < number:
        list.append(item)
        count += 1
    return count


def item_remove(list, item, number):
    """Remove the input number of item from list. Returns the number of items removed"""

    count = 0
    while count < number and item in list:
        list.remove(item)
        count +=1
    return count


def item_transfer(list_from, list_to, item, number):
    """Move up to the input number of item from list_from to list_to. Returns the number of items
    moved."""

    count = 0
    while count < number and item in list_from:
        list_from.remove(item)
        list_to.append(item)
        count += 1
    return count


def item_count(list, item):
    """Returns the amount of item in the list."""

    count = 0
    for i in list:
        if i == item:
            count += 1
    return count


def colour_image(image, colour):
    """Replace the image colour values with the given input colour."""

    image = image.copy()
    image.fill((0, 0, 0, 255), None, pg.BLEND_RGBA_MULT)
    image.fill(colour[0:3] + (0,), None, pg.BLEND_RGBA_ADD)
    return image
