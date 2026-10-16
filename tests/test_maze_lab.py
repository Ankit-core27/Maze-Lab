import unittest

from maze_lab.maze import Maze
from maze_lab.solvers import SOLVERS, astar, bfs, dfs, run


def is_valid_path(maze: Maze, path) -> bool:
    if not path or path[0] != maze.start or path[-1] != maze.end:
        return False
    if not all(maze.is_open(p) for p in path):
        return False
    return all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(path, path[1:]))


class MazeTests(unittest.TestCase):
    def test_sizes_forced_odd(self):
        m = Maze.generate(10, 20, seed=1)
        self.assertEqual((m.rows, m.cols), (11, 21))

    def test_same_seed_same_maze(self):
        self.assertEqual(Maze.generate(15, 15, 7).grid, Maze.generate(15, 15, 7).grid)

    def test_different_seed_different_maze(self):
        self.assertNotEqual(Maze.generate(15, 15, 1).grid, Maze.generate(15, 15, 2).grid)

    def test_start_and_end_open(self):
        m = Maze.generate(21, 21, 3)
        self.assertTrue(m.is_open(m.start) and m.is_open(m.end))

    def test_outer_border_is_wall(self):
        m = Maze.generate(15, 15, 4, loops=1.0)
        self.assertTrue(all(m.grid[0]) and all(m.grid[-1]))
        self.assertTrue(all(row[0] and row[-1] for row in m.grid))


class SolverTests(unittest.TestCase):
    def test_every_solver_finds_valid_path(self):
        for seed in range(10):
            m = Maze.generate(21, 31, seed, loops=0.2)
            for name, solver in SOLVERS.items():
                path, _ = run(solver, m)
                self.assertTrue(is_valid_path(m, path), f"{name} seed={seed}")

    def test_bfs_and_astar_are_shortest(self):
        for seed in range(10):
            m = Maze.generate(21, 31, seed, loops=0.3)
            b, _ = run(bfs, m)
            a, _ = run(astar, m)
            d, _ = run(dfs, m)
            self.assertEqual(len(b), len(a))
            self.assertLessEqual(len(b), len(d))

    def test_astar_explores_no_more_than_bfs(self):
        m = Maze.generate(41, 41, 5, loops=0.3)
        _, nb = run(bfs, m)
        _, na = run(astar, m)
        self.assertLessEqual(na, nb)

    def test_unsolvable_returns_none(self):
        m = Maze.blank(7, 7)  # all wall except nothing carved
        m.grid[1][1] = m.grid[5][5] = 0  # two isolated rooms
        for solver in SOLVERS.values():
            path, _ = run(solver, m)
            self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()
