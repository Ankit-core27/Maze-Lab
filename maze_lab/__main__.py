"""Command-line entry point:  python -m maze_lab --help"""
from __future__ import annotations

import argparse
import random
import sys
import time

from .maze import Maze
from .render import Screen, render
from .solvers import SOLVERS, run


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="maze_lab", description="Generate a maze and watch algorithms solve it."
    )
    p.add_argument("--rows", type=int, default=21, help="maze height (default 21)")
    p.add_argument("--cols", type=int, default=41, help="maze width (default 41)")
    p.add_argument("--seed", type=int, help="same seed => same maze")
    p.add_argument("--loops", type=float, default=0.15,
                   help="0-1: fraction of extra walls to remove (default 0.15)")
    p.add_argument("--algo", choices=SOLVERS, default="astar", help="solver to animate")
    p.add_argument("--delay", type=float, default=0.01, help="seconds per frame")
    p.add_argument("--compare", action="store_true",
                   help="skip animation; benchmark all solvers in a table")
    p.add_argument("--no-animate", action="store_true", help="print only the final result")
    p.add_argument("--no-color", action="store_true", help="plain ASCII output")
    return p.parse_args(argv)


def compare(maze: Maze) -> None:
    print(f"{'algorithm':<10}{'path length':>12}{'tiles explored':>16}{'time (ms)':>12}")
    for name, solver in SOLVERS.items():
        t0 = time.perf_counter()
        path, explored = run(solver, maze)
        ms = (time.perf_counter() - t0) * 1000
        length = len(path) - 1 if path else "-"
        print(f"{name:<10}{length:>12}{explored:>16}{ms:>12.2f}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    color = not args.no_color
    animate = not (args.no_animate or args.compare) and sys.stdout.isatty()
    seed = args.seed if args.seed is not None else random.randrange(10**6)

    if args.compare:
        maze = Maze.generate(args.rows, args.cols, seed, args.loops)
        print(f"seed={seed}  size={maze.rows}x{maze.cols}\n")
        compare(maze)
        return 0

    with Screen(args.delay, animate) as screen:
        # 1) generation: watch the maze being carved
        rng = random.Random(seed)
        maze = Maze.blank(args.rows, args.cols)
        for i, room in enumerate(maze.carve(rng)):
            if i % 2 == 0:
                screen.draw(render(maze, current=room, color=color), "carving maze...")
        if args.loops:
            maze.add_loops(rng, args.loops)

        # 2) solving: the solver yields each tile it explores
        gen = SOLVERS[args.algo](maze)
        explored: set = set()
        path = None
        while True:
            try:
                tile = next(gen)
            except StopIteration as stop:
                path = stop.value
                break
            explored.add(tile)
            screen.draw(render(maze, explored, current=tile, color=color),
                        f"{args.algo}: explored {len(explored)} tiles")

        final = render(maze, explored, set(path or ()), color=color)
        caption = (f"{args.algo}: path length {len(path) - 1}, explored {len(explored)} tiles"
                   if path else f"{args.algo}: no path found")
        screen.draw(final, caption)

    if not animate:
        print(final)
        print(caption)
    print(f"seed={seed}  (rerun with --seed {seed} to get this maze again)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
