# Maze Lab

> Terminal maze generator and BFS / DFS / A* path-finding visualiser. Pure Python, standard library only.

🔗 https://github.com/Ankit-core27/Maze-Lab

🌐 **Live demo:** https://ankit-core27.github.io/Maze-Lab/ (runs in your browser, no install needed)

Generates random mazes and animates BFS, DFS and A* solving them, in your terminal.
**Pure Python 3.10+, standard library only.**

```bash
git clone https://github.com/Ankit-core27/Maze-Lab.git
cd Maze-Lab
python -m maze_lab
```

```bash
python -m maze_lab                        # animated: carve a maze, then solve with A*
python -m maze_lab --algo bfs --delay 0.02
python -m maze_lab --algo dfs --seed 7    # same seed => same maze
python -m maze_lab --compare --rows 41 --cols 81   # benchmark table
python -m maze_lab --no-color --no-animate         # plain ASCII
python -m unittest discover -v            # run the tests
```

Example `--compare` output (41x81 maze):

```
algorithm  path length  tiles explored   time (ms)
bfs                132            1711        3.55
dfs                278             308        0.53
astar              132             958        3.32
```
BFS and A* both find the shortest path (132). A* explores ~45% fewer tiles.
DFS is fast but finds a path more than twice as long.

## Layout

| File | What it teaches |
|---|---|
| `maze_lab/maze.py` | dataclasses, type hints, **generators**, iterative DFS, seeded `random.Random` |
| `maze_lab/solvers.py` | BFS (`deque`), DFS (`list` as stack), A* (`heapq`), generators with `return` values |
| `maze_lab/render.py` | ANSI escape codes, context managers (`__enter__`/`__exit__`) |
| `maze_lab/__main__.py` | `argparse`, wiring everything together |
| `docs/` | Browser demo: the same Python files running in the browser via [Pyodide](https://pyodide.org), drawn on a `<canvas>` |
| `tests/test_maze_lab.py` | `unittest`, property-style tests (e.g. "A* path length == BFS path length") |

## How it works (read in this order)

1. **The maze is a grid of tiles.** `1` = wall, `0` = open. Rooms live on odd
   coordinates; even coordinates are wall slots between rooms. That is why sizes
   are forced odd (`rows | 1`).
2. **Generation = randomised DFS ("recursive backtracker").** Start in a room, pick a
   random unvisited neighbouring room, knock down the wall between, repeat. Stuck?
   Pop the stack (backtrack). It uses an explicit stack, not recursion, to avoid
   Python's recursion limit.
3. **`carve()` is a generator.** It `yield`s after every room. The animation
   just loops over it and draws; `Maze.generate()` loops over it and discards. Same
   code, two uses, no callbacks.
4. **Loops.** A DFS maze has exactly one route between any two points, so every
   solver would return the same path. `add_loops` removes extra walls so the
   algorithms behave differently.
5. **Solvers share one skeleton**: take a tile from the frontier, yield it, stop if
   it's the goal, push unseen neighbours, remember each tile's `parent`. The only
   difference is the frontier:
   - queue (FIFO) → BFS → explores in rings → **shortest path**
   - stack (LIFO) → DFS → dives deep → **any path**
   - priority queue → A* → always expands lowest `f = g + h` → **shortest path, fewer tiles**
6. **Path reconstruction**: follow `parents` from the goal back to the start, reverse.
7. **A\* details**: `h` is Manhattan distance. It's *admissible* (never overestimates
   on a 4-direction grid), which is what guarantees the shortest path. The counter in
   the heap tuple is a tie-breaker so ties never compare the point tuples.
   "Stale entry" skip: we may push a tile more than once; the first pop is the best.
8. **Generator `return`**: solvers `yield` explored tiles and `return` the path. The
   path arrives in `StopIteration.value`. See `run()` in `solvers.py`.

## Interview talking points

- **Complexity**: BFS/DFS are O(V+E); A* is O((V+E) log V) with a binary heap, but
  explores fewer nodes in practice. On this grid V = number of open tiles.
- **Why generators?** Lazy, memory-friendly, and they let the *caller* control pacing
  (animate, count, or run flat out).
- **Why a seeded `random.Random` instance?** Reproducible mazes and tests, with no
  dependence on the global random state.
- **Why `Screen` is a context manager**: guarantees the cursor is restored even if
  the user hits Ctrl-C.
- **Testing approach**: properties instead of fixed outputs: any path is valid
  (starts/ends right, steps adjacent, no walls), BFS length == A* length <= DFS length,
  unsolvable mazes return `None`, same seed gives the same maze.

## Browser demo

`docs/index.html` loads Pyodide (CPython compiled to WebAssembly), copies
`maze.py` and `solvers.py` into its virtual filesystem and calls them directly.
The algorithms are the same code as the terminal app. JavaScript only draws the grid.
`docs/py/maze_lab/` holds copies of those files (GitHub Pages can only serve
from `docs/`). After changing the package, refresh them with:

```bash
cp maze_lab/{__init__,maze,solvers}.py docs/py/maze_lab/
```

Run it locally with `python -m http.server -d docs` and open http://localhost:8000.

## Ideas to extend it (great to mention in an interview)

- Add Dijkstra with weighted tiles ("mud") or a Greedy Best-First solver.
- Add Prim's or Kruskal's maze generation and compare the look of the mazes.
- Save/load mazes as JSON; add a `--solve-file` option.
- Add type checking with `mypy` and formatting with `black` / `ruff`.
