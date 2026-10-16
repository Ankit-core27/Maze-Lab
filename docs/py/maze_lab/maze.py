"""Maze data structure and generation.

The maze is a grid of tiles (not cells-with-walls). Odd rows/cols are "rooms",
even rows/cols are wall slots between them. Carving a passage = opening the
wall tile between two rooms.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterator

Point = tuple[int, int]  # (row, col)

WALL, OPEN = 1, 0
STEPS = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up, down, left, right


@dataclass
class Maze:
    grid: list[list[int]]
    start: Point
    end: Point

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0])

    def is_open(self, p: Point) -> bool:
        r, c = p
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == OPEN

    def neighbors(self, p: Point) -> Iterator[Point]:
        """Yield the open tiles directly above/below/left/right of p."""
        r, c = p
        for dr, dc in STEPS:
            q = (r + dr, c + dc)
            if self.is_open(q):
                yield q

    # ---- construction -------------------------------------------------

    @classmethod
    def blank(cls, rows: int, cols: int) -> "Maze":
        """A maze that is all wall. Sizes are forced odd so rooms line up."""
        rows, cols = max(5, rows) | 1, max(5, cols) | 1
        grid = [[WALL] * cols for _ in range(rows)]
        return cls(grid, start=(1, 1), end=(rows - 2, cols - 2))

    def carve(self, rng: random.Random) -> Iterator[Point]:
        """Randomised depth-first search ("recursive backtracker").

        A generator: it carves one room, yields it, and pauses. That lets the
        caller animate the carving, or just exhaust it to get the final maze.
        Uses an explicit stack instead of recursion so big mazes can't hit
        Python's recursion limit.
        """
        g = self.grid
        g[1][1] = OPEN
        stack: list[Point] = [(1, 1)]
        yield (1, 1)
        while stack:
            r, c = stack[-1]
            options = [
                (dr, dc)
                for dr, dc in STEPS
                if 0 < r + 2 * dr < self.rows - 1
                and 0 < c + 2 * dc < self.cols - 1
                and g[r + 2 * dr][c + 2 * dc] == WALL
            ]
            if not options:
                stack.pop()  # dead end: backtrack
                continue
            dr, dc = rng.choice(options)
            g[r + dr][c + dc] = OPEN  # knock down the wall between rooms
            g[r + 2 * dr][c + 2 * dc] = OPEN
            stack.append((r + 2 * dr, c + 2 * dc))
            yield (r + 2 * dr, c + 2 * dc)

    def add_loops(self, rng: random.Random, fraction: float) -> None:
        """Knock out some extra walls so there are several routes.

        A plain DFS maze has exactly one route between any two points, which
        makes every solver return the same path. Loops make the algorithms
        actually differ (DFS finds *a* path, BFS/A* find the *shortest*).
        """
        candidates = [
            (r, c)
            for r in range(1, self.rows - 1)
            for c in range(1, self.cols - 1)
            if self.grid[r][c] == WALL
            and (
                (self.grid[r - 1][c] == OPEN and self.grid[r + 1][c] == OPEN)
                or (self.grid[r][c - 1] == OPEN and self.grid[r][c + 1] == OPEN)
            )
        ]
        rng.shuffle(candidates)
        for r, c in candidates[: int(len(candidates) * fraction)]:
            self.grid[r][c] = OPEN

    @classmethod
    def generate(
        cls, rows: int, cols: int, seed: int | None = None, loops: float = 0.0
    ) -> "Maze":
        rng = random.Random(seed)  # own RNG => same seed, same maze
        maze = cls.blank(rows, cols)
        for _ in maze.carve(rng):
            pass
        if loops:
            maze.add_loops(rng, loops)
        return maze
