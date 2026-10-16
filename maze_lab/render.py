"""Turn a Maze (plus solver state) into a string for the terminal."""
from __future__ import annotations

import sys
import time
from typing import Container

from .maze import WALL, Maze, Point

RESET = "\033[0m"
HOME = "\033[H"
CLEAR = "\033[2J"
HIDE_CURSOR, SHOW_CURSOR = "\033[?25l", "\033[?25h"

# 256-colour background codes
COLORS = {
    "wall": 236, "explored": 31, "path": 220,
    "start": 40, "end": 196, "current": 255,
}
PLAIN = {
    "wall": "██", "open": "  ", "explored": "..", "path": "**",
    "start": "S ", "end": "E ", "current": "()",
}


def _cell(kind: str, color: bool) -> str:
    if not color:
        return PLAIN[kind]
    if kind == "open":
        return "  "
    return f"\033[48;5;{COLORS[kind]}m  {RESET}"


def render(
    maze: Maze,
    explored: Container[Point] = (),
    path: Container[Point] = (),
    current: Point | None = None,
    color: bool = True,
) -> str:
    lines = []
    for r, row in enumerate(maze.grid):
        parts = []
        for c, tile in enumerate(row):
            p = (r, c)
            if p == maze.start:
                kind = "start"
            elif p == maze.end:
                kind = "end"
            elif p in path:
                kind = "path"
            elif p == current:
                kind = "current"
            elif p in explored:
                kind = "explored"
            elif tile == WALL:
                kind = "wall"
            else:
                kind = "open"
            parts.append(_cell(kind, color))
        lines.append("".join(parts))
    return "\n".join(lines)


class Screen:
    """Redraws frames in place using ANSI escape codes. Context manager so the
    cursor is always restored, even on Ctrl-C."""

    def __init__(self, delay: float, enabled: bool = True) -> None:
        self.delay, self.enabled = delay, enabled

    def __enter__(self) -> "Screen":
        if self.enabled:
            sys.stdout.write(CLEAR + HIDE_CURSOR)
        return self

    def __exit__(self, *exc) -> None:
        if self.enabled:
            sys.stdout.write(SHOW_CURSOR)
            sys.stdout.flush()

    def draw(self, frame: str, caption: str = "") -> None:
        if not self.enabled:
            return
        sys.stdout.write(f"{HOME}{frame}\n{caption}\033[K\n")
        sys.stdout.flush()
        time.sleep(self.delay)
