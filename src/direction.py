from enum import Enum
from typing import Tuple


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def get_vector(self) -> Tuple[int, int]:
        match self:
            case Direction.UP:
                return (0, -1)
            case Direction.DOWN:
                return (0, 1)
            case Direction.LEFT:
                return (-1, 0)
            case Direction.RIGHT:
                return (1, 0)
