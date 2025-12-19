from generator import generate
from solver import solve


if __name__ == "__main__":
    puzzle = generate(11, 11, "extreme").without_solution()
    print(puzzle)
    solution = solve(puzzle)
    if solution is not None:
        puzzle = puzzle.with_solution(solution)
        verify, reason = puzzle.check_solution()
        if verify:
            print(puzzle)
        else:
            print(reason)
