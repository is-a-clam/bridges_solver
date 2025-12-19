from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from io import StringIO
from typing import Tuple, Optional


@dataclass(frozen=True)
class Island:
    x: int
    y: int
    degree: int


@dataclass(frozen=True)
class Bridge:
    node1: Island
    node2: Island
    single: bool


@dataclass(frozen=True)
class Puzzle:
    width: int
    height: int
    islands: Tuple[Island, ...]
    solution: Optional[Tuple[Bridge, ...]]

    def without_solution(self) -> Puzzle:
        return Puzzle(self.width, self.height, self.islands, None)

    def with_solution(self, solution: Tuple[Bridge, ...]) -> Puzzle:
        return Puzzle(self.width, self.height, self.islands, solution)

    def to_grid(self):
        from grid import Grid

        puzzle_grid = Grid(self.width, self.height)
        for island in self.islands:
            puzzle_grid.grid[island.x][island.y].to_island(island.degree)
        return puzzle_grid

    def check_solution(self) -> Tuple[bool, str]:
        assert self.solution is not None

        # Check degrees
        island_degree = {(island.x, island.y): island.degree for island in self.islands}
        for bridge in self.solution:
            island_degree[(bridge.node1.x, bridge.node1.y)] -= 1 if bridge.single else 2
            island_degree[(bridge.node2.x, bridge.node2.y)] -= 1 if bridge.single else 2
        if any(degree != 0 for degree in island_degree.values()):
            return False, "Islands do not match bridges"

        # Check fully connected (BFS)
        neighbours = {(island.x, island.y): [] for island in self.islands}
        for bridge in self.solution:
            neighbours[(bridge.node1.x, bridge.node1.y)].append((bridge.node2.x, bridge.node2.y))
            neighbours[(bridge.node2.x, bridge.node2.y)].append((bridge.node1.x, bridge.node1.y))
        visited_dict = {(island.x, island.y): False for island in self.islands}
        to_visit = deque()
        to_visit.append((self.islands[0].x, self.islands[0].y))
        while len(to_visit) > 0:
            current = to_visit.popleft()
            if visited_dict[current] == True:
                continue
            visited_dict[current] = True
            for neighbour in neighbours[current]:
                to_visit.append(neighbour)
        if any(not visited for visited in visited_dict.values()):
            print(f"Started at node ({self.islands[0].x}, {self.islands[0].y})")
            for (x, y), visited in visited_dict.items():
                if not visited:
                    print(f"Unable to reach ({x}, {y})")
            return False, "Islands are not fully connected"

        return True, "Success"

    def __str__(self):
        board_width = self.width * 3
        symbol_dict = {(island.x, island.y): f" {island.degree} " for island in self.islands}

        # Calculate placement of bridges
        if self.solution is not None:
            for bridge in self.solution:
                if bridge.node1.x == bridge.node2.x:
                    start = min(bridge.node1.y, bridge.node2.y) + 1
                    stop = max(bridge.node1.y, bridge.node2.y)
                    for y in range(start, stop):
                        symbol_dict[(bridge.node1.x, y)] = " │ " if bridge.single else " ║ "
                elif bridge.node1.y == bridge.node2.y:
                    start = min(bridge.node1.x, bridge.node2.x) + 1
                    stop = max(bridge.node1.x, bridge.node2.x)
                    for x in range(start, stop):
                        symbol_dict[(x, bridge.node1.y)] = "───" if bridge.single else "═══"
                else:
                    raise ValueError("Solution is invalid")

        # Uses box drawing characters to print Hashi board
        with StringIO() as output:
            output.write("┌" + "─" * board_width + "┐\n")
            for y in range(self.height):
                output.write(f"│")
                for x in range(self.width):
                    output.write(symbol_dict.get((x, y), "   "))
                output.write("│\n")
                # Print spacing rows
                if y != self.height - 1:
                    output.write(f"│")
                    for x in range(self.width):
                        # Allow bridges to be continuous through spacing
                        if symbol_dict.get((x, y)) == symbol_dict.get((x, y + 1)) and (
                            symbol_dict.get((x, y)) == " │ " or symbol_dict.get((x, y)) == " ║ "
                        ):
                            output.write(symbol_dict.get((x, y), "   "))
                        else:
                            output.write("   ")
                    output.write("│\n")
            output.write("└" + "─" * board_width + "┘")
            return output.getvalue()


if __name__ == "__main__":
    test_puzzle = Puzzle(4, 4, (Island(0, 0, 3), Island(0, 3, 2), Island(3, 0, 1)), None)
    test_solved_puzzle_1 = test_puzzle.with_solution(
        (
            Bridge(Island(0, 0, 3), Island(0, 3, 2), False),
            Bridge(Island(0, 0, 3), Island(3, 0, 1), True),
        )
    )
    test_solved_puzzle_2 = Puzzle(
        4,
        4,
        (Island(0, 0, 3), Island(0, 3, 1), Island(3, 0, 2)),
        (
            Bridge(Island(0, 0, 3), Island(0, 3, 1), True),
            Bridge(Island(0, 0, 3), Island(3, 0, 2), False),
        ),
    )
    test_solved_puzzle_3 = Puzzle(
        4,
        4,
        (Island(0, 0, 3), Island(0, 3, 2), Island(3, 0, 1)),
        (
            Bridge(Island(0, 0, 3), Island(0, 3, 2), False),
            Bridge(Island(0, 0, 3), Island(3, 0, 1), False),
        ),
    )
    test_solved_puzzle_4 = Puzzle(
        4,
        4,
        (Island(0, 0, 2), Island(0, 3, 1), Island(3, 0, 2), Island(3, 3, 1)),
        (
            Bridge(Island(0, 0, 2), Island(3, 0, 2), False),
            Bridge(Island(0, 3, 1), Island(3, 3, 1), True),
        ),
    )
    print(test_puzzle)
    print(test_solved_puzzle_1)
    print(test_solved_puzzle_1.check_solution())
    print(test_solved_puzzle_2)
    print(test_solved_puzzle_2.check_solution())
    print(test_solved_puzzle_3)
    print(test_solved_puzzle_3.check_solution())
    print(test_solved_puzzle_4)
    print(test_solved_puzzle_4.check_solution())
