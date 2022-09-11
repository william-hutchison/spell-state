import globe


class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(map_entities, map_topology, start, end, adjacent=False, max_children=400):
    """Returns a list of tuples as a path from the given start to the given end in the given maze.
    Returns an empty list if no path is found."""
    
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
    """Returns list of all tile coordinates in map matching target kind."""

    matches = []
    for y, row in enumerate(map):
        for x, tile_kind in enumerate(row):
            if tile_kind == target_kind:
                matches.append((x, y))

    return matches


def find_closest(location, target_list):
    """Returns tile coordinate of the closest target to start as the crow flies."""

    distances = []
    for target in target_list:
        distances.append(abs(location[0] - target[0]) + abs(location[1] - target[1]))
    min_distance = min(distances)

    return target_list[distances.index(min_distance)]


def find_edges(location):
    """Returns list of coordinates adjacent to a location."""

    adjacent_list = [(location[0], location[1] - 1), (location[0] - 1, location[1]), (location[0], location[1] + 1), (location[0] + 1, location[1])]

    return adjacent_list


def find_free(locations, map_entities, map_topology):
    """Returns list of coordinates not overlapped by collision and within the bounds of the map."""

    free_locations = [] 
    for location in locations:
        if (0 <= location[0] < globe.WORLD_SIZE[0]) and (0 <= location[1] < globe.WORLD_SIZE[0]):
            if not map_entities[location[1]][location[0]] and map_topology[location[1]][location[0]] != 0:
                free_locations.append(location)

    return free_locations


def find_within_radius(location, radius):
    """Returns list of coordinates within a given radius of a location."""

    possible_locations = [] 
    for x in range(-radius, radius):
        for y in range(-radius, radius):
            possible_locations.append((location[0]+x, location[1]+y))

    return possible_locations
