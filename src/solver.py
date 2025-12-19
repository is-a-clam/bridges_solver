from typing import List, Tuple

from grid import Grid
from puzzle import Bridge, Island, Puzzle
from pulp import PULP_CBC_CMD, LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value

# Integer Linear Programming
#
# N:   set of all islands
# E:   set of all potential bridges
# C:   set of all potential crossing bridges
# r_i: degree of node i
#
# b_i_j \in {0, 1, 2}: bridge count
# y_i_j \in {0, 1}: bridge existence indicator
# f_i_j >= 0: flow from node i to j
#
# minimise \sum_{i,j} b_i_j
# island degree:     for all i \in N: \sum_{j \in N: (i,j) \in E} b_i_j = r_i
# bridge existence:  for all (i,j) \in E: y_i_j <= b_i_j <= 2 * y_i_j
# no crossing:       for all ((i,j), (k,l)) \in C: y_i_j + y_k_l <= 1
# flow conservation: for all i \in N: \sum_{j} f_i_j - \sum_{j} f_j_i = |N| - 1 if i == 0 else -1
# flow capacity:     for all (i,j) \in E: f_i_j + f_j_i <= (|N| - 1) * y_i_j


def get_possible_bridges(puzzle: Puzzle, grid: Grid):
    bridges = []

    for i, island_i in enumerate(puzzle.islands):
        for j, island_j in enumerate(puzzle.islands):
            if i >= j:
                continue

            # Vertical Bridge
            if island_i.x == island_j.x:
                # Check for in between nodes
                valid_bridge = True
                start_y = min(island_i.y, island_j.y)
                end_y = max(island_i.y, island_j.y)
                for y in range(start_y + 1, end_y):
                    if grid.grid[island_i.x][y].type == "island":
                        valid_bridge = False
                        break
                if valid_bridge:
                    bridges.append((i, j))

            # Horizontal bridge
            elif island_i.y == island_j.y:
                # Check for in between nodes
                valid_bridge = True
                start_x = min(island_i.x, island_j.x)
                end_x = max(island_i.x, island_j.x)
                for x in range(start_x + 1, end_x):
                    if grid.grid[x][island_i.y].type == "island":
                        valid_bridge = False
                        break
                if valid_bridge:
                    bridges.append((i, j))

    return bridges


def get_crossing_bridges(puzzle: Puzzle, potential_bridges: List[Tuple[int, int]]):
    crossing = []

    for index_1, (i1, j1) in enumerate(potential_bridges):
        for index_2, (i2, j2) in enumerate(potential_bridges):
            if index_1 >= index_2:
                continue

            i1_island = puzzle.islands[i1]
            j1_island = puzzle.islands[j1]
            i2_island = puzzle.islands[i2]
            j2_island = puzzle.islands[j2]

            is_1_horizontal = i1_island.y == j1_island.y
            is_2_horizontal = i2_island.y == j2_island.y

            # if bridges are parallel, definitely not crossing
            if is_1_horizontal == is_2_horizontal:
                continue

            horizontal, vertical = (
                ((i1_island, j1_island), (i2_island, j2_island))
                if is_1_horizontal
                else ((i2_island, j2_island), (i1_island, j1_island))
            )

            horizontal_min = min(horizontal[0].x, horizontal[1].x)
            horizontal_max = max(horizontal[0].x, horizontal[1].x)
            vertical_min = min(vertical[0].y, vertical[1].y)
            vertical_max = max(vertical[0].y, vertical[1].y)

            if (
                vertical_min < horizontal[0].y < vertical_max
                and horizontal_min < vertical[0].x < horizontal_max
            ):
                crossing.append(((i1, j1), (i2, j2)))

    return crossing


def solve(puzzle: Puzzle):
    grid = puzzle.to_grid()
    island_count = len(puzzle.islands)
    possible_bridges = get_possible_bridges(puzzle, grid)
    crossing_bridges = get_crossing_bridges(puzzle, possible_bridges)

    b = {}
    y = {}
    f = {}

    problem = LpProblem("puzzle", LpMinimize)
    for i, j in possible_bridges:
        b[(i, j)] = LpVariable(f"b_{i}_{j}", lowBound=0, upBound=2, cat="Integer")
        y[(i, j)] = LpVariable(f"y_{i}_{j}", cat="Binary")
        f[(i, j)] = LpVariable(f"f_{i}_{j}", lowBound=0, upBound=island_count - 1)
        f[(j, i)] = LpVariable(f"f_{j}_{i}", lowBound=0, upBound=island_count - 1)

    # Objective Function
    problem += lpSum([b[(i, j)] for (i, j) in possible_bridges])

    # Island degree
    for i, island in enumerate(puzzle.islands):
        island_bridges = []
        for u, v in possible_bridges:
            if u == i or v == i:
                island_bridges.append(b[(u, v)])

        problem += lpSum(island_bridges) == island.degree

    # bridge existence
    for bridge in possible_bridges:
        problem += y[bridge] <= b[bridge]
        problem += b[bridge] <= 2 * y[bridge]

    # no crossing
    for bridge1, bridge2 in crossing_bridges:
        problem += y[bridge1] + y[bridge2] <= 1

    # flow conservation
    root_node = 0
    for i, island in enumerate(puzzle.islands):
        outflow = []
        inflow = []
        for u, v in possible_bridges:
            if u == i:
                outflow.append(f[(i, v)])
                inflow.append(f[(v, i)])
            elif v == i:
                outflow.append(f[(i, u)])
                inflow.append(f[(u, i)])

        if i == root_node:
            problem += lpSum(outflow) - lpSum(inflow) == island_count - 1
        else:
            problem += lpSum(outflow) - lpSum(inflow) == -1

    # flow capacity
    for i, j in possible_bridges:
        problem += f[(i, j)] + f[(j, i)] <= (island_count - 1) * y[(i, j)]

    status = problem.solve(PULP_CBC_CMD(msg=False))
    print(f"Solution status: {LpStatus[status]}")

    if LpStatus[status] in ["Optimal", "Feasible"]:
        solution = []

        for i, j in possible_bridges:
            bridge_count = value(b[(i, j)])
            if bridge_count is not None and bridge_count > 0.5:
                solution.append(
                    Bridge(puzzle.islands[i], puzzle.islands[j], int(round(bridge_count)) == 1)
                )

        return tuple(solution)
    else:
        print("No solution found")
        return None


if __name__ == "__main__":
    width = int(input("Enter puzzle width: ").strip())
    height = int(input("Enter puzzle height: ").strip())
    islands = []
    while True:
        islands_position = input("Enter island coordinate (i.e. x,y or none): ").strip().lower()
        if islands_position == "none":
            break
        island_x, island_y = islands_position.split(",")
        island_x, island_y = int(island_x.strip()), int(island_y.strip())
        degree = int(input("Enter island degree: ").strip())
        islands.append(Island(island_x, island_y, degree))
    puzzle = Puzzle(width, height, tuple(islands), None)
    print(puzzle)
    solution = solve(puzzle)
    if solution is not None:
        puzzle = puzzle.with_solution(solution)
        verify, reason = puzzle.check_solution()
        if verify:
            print(puzzle)
        else:
            print(reason)
