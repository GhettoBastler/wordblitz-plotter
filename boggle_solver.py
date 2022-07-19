#! /usr/bin/env python

from random import choice
from itertools import groupby
import json
import time
from string import ascii_letters
import sys


NEIGHBORS = {
    (0, 0): {(0, 1), (1, 0), (1, 1)},
    (0, 1): {(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)},
    (0, 2): {(0, 1), (1, 1), (1, 2), (1, 3), (0, 3)},
    (1, 0): {(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)},
    (2, 0): {(1, 0), (1, 1), (2, 1), (3, 1), (3, 0)},
    (1, 3): {(0, 3), (0, 2), (1, 2), (2, 2), (2, 3)},
    (2, 3): {(1, 3), (1, 2), (2, 2), (3, 2), (3, 3)},
    (3, 1): {(3, 0), (2, 0), (2, 1), (2, 2), (3, 2)},
    (3, 2): {(3, 1), (2, 1), (2, 2), (2, 3), (3, 3)},
    (1, 1): {(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)},
    (1, 2): {(0, 1), (0, 2), (0, 3), (1, 1), (1, 3), (2, 1), (2, 2), (2, 3)},
    (2, 1): {(1, 0), (1, 1), (1, 2), (2, 0), (2, 2), (3, 0), (3, 1), (3, 2)},
    (2, 2): {(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)},
    (0, 3): {(0, 2), (1, 2), (1, 3)},
    (3, 0): {(2, 0), (2, 1), (3, 1)},
    (3, 3): {(3, 2), (2, 2), (2, 3)},
}

def path_to_word(path, grid):
    res = ''
    for coord in path:
        res += grid[coord[0]][coord[1]]

    return res


def search_paths(grid, tree):
    res = []
    found = set()

    queue = [[n] for n in NEIGHBORS]

    while queue:

        curr_path = queue.pop()
        possible_neighbors = [n for n in NEIGHBORS[curr_path[-1]] if n not in curr_path]

        for neighbor in possible_neighbors:

            candidate = curr_path + [neighbor]
            word = path_to_word(candidate, grid)

            if word in tree:
                if '.' in tree[word] and word not in found:
                    # Arrived at a leaf node. This is a valid word.
                    res.append(candidate)
                    found.add(word)

                queue.insert(0, candidate)
                
    res.sort(key=len, reverse=True)
    return res


def get_squares_coordinates(grid_size):
    square_size = grid_size / 4
    offset = square_size/2

    return [[(offset + square_size*i, offset + square_size*j) for i in range(4)] for j in range(4)]


def sort_paths(paths):
    groups_key = [(k, list(g)) for k, g in groupby(paths, len)]
    groups_key.sort(key=lambda t: t[0], reverse=True)
    groups = [g for _, g in groups_key]

    res = []
    for group in groups:
        curr_group = []
        remaining = group.copy()
        curr = choice(remaining)
        while remaining:
            closest = min(remaining, key=lambda t: abs(t[0][0] - curr[-1][0]) + abs(t[0][1] - curr[-1][1]))
            curr_group.append(closest)
            curr = closest
            remaining.remove(curr)
        res += curr_group
    return res

def path_to_coords(path, grid_size):
    res = []

    coordinates = get_squares_coordinates(grid_size)
    for coords in path:
        x, y = coords
        res.append(coordinates[x][y])

    return res


def get_paths(grid, tree, grid_size):
    res = []
    paths = search_paths(grid, tree)
    paths = sort_paths(paths)
    for p in paths:
        res.append(path_to_coords(p, grid_size))
    return res
