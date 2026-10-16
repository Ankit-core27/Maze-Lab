"""Path-finding algorithms.

Every solver is a *generator*: it yields each tile as it explores it, and
`return`s the final path (or None). The yielded tiles drive the animation;
the return value arrives on `StopIteration.value` (see `run`).

All three share the same skeleton, only the "frontier" data structure differs:
    BFS   -> queue          (deque)      -> shortest path
    DFS   -> stack          (list)       -> any path, often long
    A*    -> priority queue (heapq)      -> shortest path, explores less
"""
from __future__ import annotations

import heapq
from collections import deque
from typing import Callable, Generator, Optional

from .maze import Maze, Point

Path = Optional[list[Point]]
Solver = Callable[[Maze], Generator[Point, None, Path]]


def _rebuild(parents: dict[Point, Optional[Point]], end: Point) -> list[Point]:
    """Walk the parent links backwards from end to start, then reverse."""
    path: list[Point] = []
    node: Optional[Point] = end
    while node is not None:
        path.append(node)
        node = parents[node]
    return path[::-1]


def bfs(maze: Maze) -> Generator[Point, None, Path]:
    parents: dict[Point, Optional[Point]] = {maze.start: None}
    queue = deque([maze.start])
    while queue:
        cur = queue.popleft()  # oldest first => explores in widening rings
        yield cur
        if cur == maze.end:
            return _rebuild(parents, cur)
        for nxt in maze.neighbors(cur):
            if nxt not in parents:
                parents[nxt] = cur
                queue.append(nxt)
    return None


def dfs(maze: Maze) -> Generator[Point, None, Path]:
    parents: dict[Point, Optional[Point]] = {maze.start: None}
    stack = [maze.start]
    while stack:
        cur = stack.pop()  # newest first => dives deep before backtracking
        yield cur
        if cur == maze.end:
            return _rebuild(parents, cur)
        for nxt in maze.neighbors(cur):
            if nxt not in parents:
                parents[nxt] = cur
                stack.append(nxt)
    return None


def _manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze: Maze) -> Generator[Point, None, Path]:
    """f(n) = g(n) + h(n): steps taken so far + optimistic guess to the goal.

    Manhattan distance never overestimates on a 4-direction grid (it's
    "admissible"), which is what guarantees the path found is shortest.
    """
    parents: dict[Point, Optional[Point]] = {maze.start: None}
    best_g = {maze.start: 0}
    # heap entries: (f, tie_breaker, g, point). The counter stops Python from
    # ever comparing two tuples-as-points when f values tie.
    counter = 0
    heap = [(_manhattan(maze.start, maze.end), counter, 0, maze.start)]
    closed: set[Point] = set()
    while heap:
        _, _, g, cur = heapq.heappop(heap)
        if cur in closed:
            continue  # stale entry: we found a better route to cur earlier
        closed.add(cur)
        yield cur
        if cur == maze.end:
            return _rebuild(parents, cur)
        for nxt in maze.neighbors(cur):
            ng = g + 1
            if ng < best_g.get(nxt, float("inf")):
                best_g[nxt] = ng
                parents[nxt] = cur
                counter += 1
                heapq.heappush(heap, (ng + _manhattan(nxt, maze.end), counter, ng, nxt))
    return None


SOLVERS: dict[str, Solver] = {"bfs": bfs, "dfs": dfs, "astar": astar}


def run(solver: Solver, maze: Maze) -> tuple[Path, int]:
    """Run a solver to completion. Returns (path, number of tiles explored)."""
    gen = solver(maze)
    explored = 0
    while True:
        try:
            next(gen)
            explored += 1
        except StopIteration as stop:  # the generator's `return` value lives here
            return stop.value, explored
