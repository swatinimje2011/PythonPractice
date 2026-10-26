"""Focused unit tests for the framework-independent Snake rules."""

import random
import tempfile
import unittest
from pathlib import Path

from game import Direction, SnakeGame
from scoreboard import Scoreboard


class SnakeGameTests(unittest.TestCase):
    def make_game(self) -> SnakeGame:
        return SnakeGame(columns=8, rows=8, rng=random.Random(7))

    def test_moves_forward_without_changing_length(self) -> None:
        game = self.make_game()
        original_length = len(game.snake)
        game.step()
        self.assertEqual(game.snake[0], (5, 4))
        self.assertEqual(len(game.snake), original_length)

    def test_food_increases_score_and_length(self) -> None:
        game = self.make_game()
        game.food = (5, 4)
        old_length = len(game.snake)
        game.step()
        self.assertEqual(game.score, 10)
        self.assertEqual(len(game.snake), old_length + 1)
        self.assertNotIn(game.food, game.snake)

    def test_rejects_reverse_direction(self) -> None:
        game = self.make_game()
        self.assertFalse(game.change_direction(Direction.LEFT))
        self.assertEqual(game.direction, Direction.RIGHT)

    def test_wall_collision_ends_game(self) -> None:
        game = self.make_game()
        game.snake = [(7, 4), (6, 4), (5, 4)]
        game.food = (0, 0)
        game.step()
        self.assertTrue(game.game_over)

    def test_self_collision_ends_game(self) -> None:
        game = self.make_game()
        game.snake = [(3, 3), (3, 4), (2, 4), (2, 3), (2, 2), (3, 2), (4, 2), (4, 3)]
        game.direction = Direction.LEFT
        game.food = (0, 0)
        game.step()
        self.assertTrue(game.game_over)

    def test_pause_stops_movement_and_restart_resets_state(self) -> None:
        game = self.make_game()
        game.toggle_pause()
        paused_snake = list(game.snake)
        game.step()
        self.assertEqual(game.snake, paused_snake)
        game.score = 4
        game.reset()
        self.assertFalse(game.paused)
        self.assertFalse(game.game_over)
        self.assertEqual(game.score, 0)
        self.assertEqual(len(game.snake), 3)


class ScoreboardTests(unittest.TestCase):
    def test_keeps_best_score_per_player_and_only_top_five(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            scoreboard = Scoreboard(Path(directory) / "scores.json")
            for name, score in [("Ada", 50), ("Ben", 40), ("Cy", 30), ("Dee", 20),
                                ("Eli", 10), ("Fran", 5)]:
                scoreboard.record(name, score)

            scoreboard.record("ada", 25)
            records = scoreboard.record("Gus", 15)

            self.assertEqual(len(records), 5)
            self.assertEqual(records[0], {"name": "Ada", "score": 50})
            self.assertNotIn("Fran", {entry["name"] for entry in records})
            self.assertEqual(scoreboard.top_scores(), records)


if __name__ == "__main__":
    unittest.main()
