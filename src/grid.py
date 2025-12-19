from dataclasses import dataclass
from random import random, randint, choice
from typing import List, Literal, Optional

from direction import Direction


@dataclass
class Node:
    x: int
    y: int
    type: Literal["empty", "island", "bridge"] = "empty"
    degree: int = -1

    def to_empty(self) -> None:
        self.type = "empty"
        self.degree = -1

    def to_island(self, degree: int) -> None:
        self.type = "island"
        self.degree = degree

    def to_bridge(self) -> None:
        self.type = "bridge"
        self.degree = -1


@dataclass(init=False)
class Grid:
    width: int
    height: int
    grid: List[List[Node]]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Node(i, j) for j in range(height)] for i in range(width)]

    def to_puzzle(self):
        from puzzle import Puzzle, Island

        islands = []
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y].type == "island":
                    islands.append(Island(x, y, self.grid[x][y].degree))
        return Puzzle(self.width, self.height, tuple(islands), None)

    def within_bounds(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_random_direction(self, x: int, y: int) -> Optional[Direction]:
        available_directions: List[Direction] = []
        if y >= 2 and self.grid[x][y - 1].type == "empty" and self.grid[x][y - 2].type == "empty":
            available_directions.append(Direction.UP)
        if (
            y < self.height - 2
            and self.grid[x][y + 1].type == "empty"
            and self.grid[x][y + 2].type == "empty"
        ):
            available_directions.append(Direction.DOWN)
        if x >= 2 and self.grid[x - 1][y].type == "empty" and self.grid[x - 2][y].type == "empty":
            available_directions.append(Direction.LEFT)
        if (
            x < self.width - 2
            and self.grid[x + 1][y].type == "empty"
            and self.grid[x + 2][y].type == "empty"
        ):
            available_directions.append(Direction.RIGHT)

        if len(available_directions) == 0:
            return None
        return choice(available_directions)

    def get_random_bridge_thickness(
        self, x: int, y: int, max_degree: int, single_bridge_odds: float
    ) -> int:
        if max_degree - self.grid[x][y].degree >= 2:
            return 1 if random() < single_bridge_odds else 2
        return 1

    def get_random_bridge_length(
        self, x: int, y: int, direction: Direction, shorter_bridges: bool = False
    ) -> int:
        vector = direction.get_vector()
        check_x = x + vector[0] * 3
        check_y = y + vector[1] * 3
        max_length = 1
        while True:
            if not self.within_bounds(check_x, check_y):
                break
            if self.grid[check_x][check_y].type != "empty":
                break
            max_length += 1
            check_x += vector[0]
            check_y += vector[1]

        # Bias towards shorter bridges
        if shorter_bridges:
            return min(randint(1, max_length), randint(1, max_length))
        return randint(1, max_length)

    def add_bridge(self, x: int, y: int, length: int, direction: Direction) -> None:
        bridge_vector = direction.get_vector()
        for i in range(length):
            bridge_node_x = x + bridge_vector[0] * (i + 1)
            bridge_node_y = y + bridge_vector[1] * (i + 1)
            self.grid[bridge_node_x][bridge_node_y].to_bridge()
