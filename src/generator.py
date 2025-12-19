from math import floor
from typing import List, Literal, Tuple
from random import randint, choice

from puzzle import Bridge, Island, Puzzle
from direction import Direction
from grid import Grid, Node


Difficulty = Literal["easy", "medium", "hard", "extreme"]


def generate_candidate(
    width: int,
    height: int,
    max_degree: int,
    single_bridge_odds: float,
    shorter_bridges: bool,
    min_island_count: int,
    max_cycles: int = 100,
) -> Tuple[Grid, int, List[Bridge]]:
    grid = Grid(width, height)

    island_count = 0
    solution: List[Bridge] = []
    to_expand: List[Node] = [grid.grid[randint(0, width - 1)][randint(0, height - 1)]]
    to_expand[0].to_island(0)

    for _ in range(max_cycles):
        if len(to_expand) == 0:
            break

        if island_count >= min_island_count:
            break

        # Create random bridge from random node
        start_node = choice(to_expand)
        bridge_direction = grid.get_random_direction(start_node.x, start_node.y)
        if bridge_direction is None:
            to_expand.remove(start_node)
            continue
        if start_node.degree >= max_degree:
            to_expand.remove(start_node)
            continue
        thickness = grid.get_random_bridge_thickness(
            start_node.x, start_node.y, max_degree, single_bridge_odds
        )
        length = grid.get_random_bridge_length(
            start_node.x, start_node.y, bridge_direction, shorter_bridges
        )
        bridge_vector = bridge_direction.get_vector()
        end_node_x = start_node.x + bridge_vector[0] * (length + 1)
        end_node_y = start_node.y + bridge_vector[1] * (length + 1)
        end_node = grid.grid[end_node_x][end_node_y]

        # Check if end node has adjacent neighbour
        adjacent_island_found = False
        for check_direction in Direction:
            check_vector = check_direction.get_vector()
            check_node_x = end_node.x + check_vector[0]
            check_node_y = end_node.y + check_vector[1]
            if (
                grid.within_bounds(check_node_x, check_node_y)
                and grid.grid[check_node_x][check_node_y].type == "island"
            ):
                adjacent_island_found = True
        if adjacent_island_found:
            continue

        start_node.degree += thickness
        end_node.to_island(thickness)
        to_expand.append(end_node)
        island_count += 1

        grid.add_bridge(start_node.x, start_node.y, length, bridge_direction)
        solution.append(
            Bridge(
                Island(start_node.x, start_node.y, 0),
                Island(end_node.x, end_node.y, 0),
                thickness == 1,
            )
        )
    return grid, island_count, solution


def is_candidate_full(grid: Grid) -> bool:
    # Check if there is no empty outer row / column
    if all([grid.grid[i][0].type == "empty" for i in range(grid.width)]):
        return False
    if all([grid.grid[i][-1].type == "empty" for i in range(grid.width)]):
        return False
    if all([grid.grid[0][i].type == "empty" for i in range(grid.height)]):
        return False
    if all([grid.grid[-1][i].type == "empty" for i in range(grid.height)]):
        return False

    return True


def generate(width: int, height: int, difficulty: Difficulty) -> Puzzle:
    settings = {
        "easy": {
            "max_degree": 8,
            "single_bridge_odds": 0.45,
            "max_island_density": 5.5,
            "shorter_bridges": False,
        },
        "medium": {
            "max_degree": 7,
            "single_bridge_odds": 0.5,
            "max_island_density": 4.5,
            "shorter_bridges": False,
        },
        "hard": {
            "max_degree": 6,
            "single_bridge_odds": 0.55,
            "max_island_density": 3.5,
            "shorter_bridges": False,
        },
        "extreme": {
            "max_degree": 5,
            "single_bridge_odds": 0.6,
            "max_island_density": 2.5,
            "shorter_bridges": True,
        },
    }[difficulty]

    decay = 0.01
    min_island_density = settings["max_island_density"]

    while True:
        min_island_count = max(4, floor(width * height / min_island_density))
        estimated_max_cycles = min_island_count * 10

        grid, island_count, solution = generate_candidate(
            width,
            height,
            settings["max_degree"],
            settings["single_bridge_odds"],
            settings["shorter_bridges"],
            min_island_count,
            estimated_max_cycles,
        )

        # Too few islands
        if island_count < min_island_count:
            min_island_density += decay
            continue

        # Entire grid is used up
        if is_candidate_full(grid):
            break

    return grid.to_puzzle().with_solution(tuple(solution))


if __name__ == "__main__":
    puzzle = generate(11, 11, "extreme")
    print(puzzle.without_solution())
    print(puzzle)
