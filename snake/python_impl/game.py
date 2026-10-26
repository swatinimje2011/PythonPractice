"""Framework-independent state and rules for the Snake game."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import random


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def opposite(self) -> Direction:
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[self]


Position = tuple[int, int]


@dataclass
class SnakeGame:
    """A grid-based Snake game whose methods do not depend on Qt."""

    columns: int = 20
    rows: int = 20
    rng: random.Random = field(default_factory=random.Random, repr=False)
    snake: list[Position] = field(init=False)
    direction: Direction = field(init=False, default=Direction.RIGHT)
    food: Position = field(init=False)
    score: int = field(init=False, default=0)
    game_over: bool = field(init=False, default=False)
    paused: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if self.columns < 4 or self.rows < 4:
            raise ValueError("The board must be at least 4 by 4.")
        self.reset()

    def reset(self) -> None:
        center = (self.columns // 2, self.rows // 2)
        self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
        self.paused = False
        self.food = self._new_food()

    def change_direction(self, direction: Direction) -> bool:
        """Change heading unless it would reverse directly into the body."""
        if direction is self.direction.opposite:
            return False
        self.direction = direction
        return True

    def toggle_pause(self) -> None:
        if not self.game_over:
            self.paused = not self.paused

    def step(self) -> None:
        if self.game_over or self.paused:
            return

        dx, dy = self.direction.value
        head = self.snake[0]
        next_head = (head[0] + dx, head[1] + dy)
        eating = next_head == self.food
        body_to_check = self.snake if eating else self.snake[:-1]

        if (
            next_head[0] < 0
            or next_head[0] >= self.columns
            or next_head[1] < 0
            or next_head[1] >= self.rows
            or next_head in body_to_check
        ):
            self.game_over = True
            return

        self.snake.insert(0, next_head)
        if eating:
            self.score += 10
            self.food = self._new_food()
        else:
            self.snake.pop()

    def _new_food(self) -> Position:
        occupied = set(self.snake)
        available = [
            (x, y)
            for y in range(self.rows)
            for x in range(self.columns)
            if (x, y) not in occupied
        ]
        if not available:
            self.game_over = True
            return self.snake[0]
        return self.rng.choice(available)
