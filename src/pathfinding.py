import random
import math

import globe


class Node:
    """A node class for A* Pathfinding."""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(map_entities, map_topology, start, end, adjacent=False, max_children=400):
    """Returns a list of tuples as a path from the given start to the given end in the given maze. Returns an empty list
    if no path is found."""
    
    if adjacent:
        end_list = find_edges(end)
    else:
        end_list = [end]
    count = 0

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node.position in end_list:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            # Return reversed path
            return path[::-1]

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(map_entities) - 1) or node_position[0] < 0 or node_position[1] > (len(map_entities[len(map_entities)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if map_entities[node_position[1]][node_position[0]] != None or map_topology[node_position[1]][node_position[0]] == 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)
            count += 1

        if count > max_children:
            return []


def find_targets(map, target_kind):
    """Returns list of all tile coordinates in map matching target_kind."""

    matches = []
    for y, row in enumerate(map):
        for x, tile_kind in enumerate(row):
            if tile_kind == target_kind:
                matches.append((x, y))

    return matches


def find_closest(location, target_list):
    """Returns coordinate of the closest tile in target_list to location as the crow flies."""

    distances = []
    for target in target_list:
        distances.append(math.sqrt(abs(target[0] - location[0]) ** 2 + abs(target[1] - location[1]) ** 2)) #abs(location[0] - target[0]) + abs(location[1] - target[1]))
    min_distance = min(distances)

    return target_list[distances.index(min_distance)]


def find_distance(start, end):
    """Returns float distance between start and end points as the crow flies."""

    return math.sqrt(abs(start[0] - end[0]) ** 2 + abs(start[1] - end[1]) ** 2)


def find_edges(location):
    """Returns list of coordinates adjacent to location."""

    adjacent_list = [(location[0], location[1] - 1), (location[0] - 1, location[1]), (location[0], location[1] + 1), (location[0] + 1, location[1])]

    return adjacent_list


def find_free(locations, map_entities, map_topology):
    """Returns list of coordinates not overlapped by collision and within the bounds of the map, out of the input list
    locations."""

    free_locations = [] 
    for location in locations:
        if (0 <= location[0] < globe.WORLD_SIZE[0]) and (0 <= location[1] < globe.WORLD_SIZE[0]):
            if not map_entities[location[1]][location[0]] and map_topology[location[1]][location[0]] != 0:
                free_locations.append(location)

    return free_locations


def drop_items(location, items, map_topology, map_item):
    """Finds free locations and adds items to map_item at those locations."""

    possible_locations = find_within_radius(location, round(2+len(items)/4))
    for item in items:

        # Check if location is empty on item map and not water on topology map
        searching_locations = True
        while searching_locations:
            try_location = random.choice(possible_locations)
            if not map_item[try_location[1]][try_location[0]] and map_topology[try_location[1]][try_location[0]]:
                map_item[try_location[1]][try_location[0]] = item
                possible_locations.remove(try_location)
                searching_locations = False

            # TODO Do something to avoid infinite loop in case of no locations found


def find_within_radius(location, radius):
    """Returns list of coordinates within the given radius of location and within the bounds of the map."""

    possible_locations = []
    for x in range(-radius, radius+1):
        for y in range(-radius, radius+1):
            if (0 <= location[0]+x < globe.WORLD_SIZE[0]) and (0 <= location[1]+y < globe.WORLD_SIZE[0]):
                possible_locations.append((location[0]+x, location[1]+y))

    return possible_locations


def find_within_ring(location, radius):
    """Returns list of coordinates within a one tile thick ring at the given radius of location and within the bounds
    of the map."""

    inner_tiles = find_within_radius(location, radius-1)
    all_tiles = find_within_radius(location, radius)

    for tile in inner_tiles:
        all_tiles.remove(tile)

    return all_tiles


def find_within_cross(location, radius):
    """Returns list of tiles in straight lines of length radius emanating from location and within the bounds of the
    map."""

    possible_locations = []
    for x in range(-radius, radius+1):
        if (0 <= location[0] + x < globe.WORLD_SIZE[0]):
            possible_locations.append((location[0] + x, location[1]))

    for y in range(-radius, radius+1):
        if (0 <= location[1] + y < globe.WORLD_SIZE[1]):
            possible_locations.append((location[0], location[1] + y))

    return possible_locations


def find_direction(location_from, location_to):
    """Returns a tuple of x and y coordinates with direction for each dimension represented as -1, 0 or 1."""

    difference = (location_to[0] - location_from[0], location_to[1] - location_from[1])

    if difference[0] > 0:
        x_direction = 1
    elif difference[0] < 0:
        x_direction = -1
    else:
        x_direction = 0

    if difference[1] > 0:
        y_direction = 1
    elif difference[1] < 0:
        y_direction = -1
    else:
        y_direction = 0

    return (x_direction, y_direction)
