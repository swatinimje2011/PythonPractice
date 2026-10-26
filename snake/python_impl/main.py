"""PySide6 interface for the Snake game."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QKeyEvent, QPainter
from PySide6.QtWidgets import QApplication, QCheckBox, QInputDialog, QMainWindow, QWidget

from game import Direction, SnakeGame
from scoreboard import Scoreboard


class GameWidget(QWidget):
    CELL_SIZE = 26
    TICK_MS = 130
    BEGINNER_TICK_MS = 260
    HEADER_HEIGHT = 58
    FOOTER_HEIGHT = 26

    def __init__(
        self,
        player_name: str,
        scoreboard: Scoreboard,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.game = SnakeGame()
        self.player_name = player_name
        self.scoreboard = scoreboard
        self.high_scores = scoreboard.top_scores()
        self._score_recorded = False
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.board_width = self.game.columns * self.CELL_SIZE
        self.board_height = self.game.rows * self.CELL_SIZE
        self.setMinimumSize(
            self.board_width,
            self.board_height + self.HEADER_HEIGHT + self.FOOTER_HEIGHT,
        )

        self.beginner_checkbox = QCheckBox("Beginner level (slow)", self)
        self.beginner_checkbox.setToolTip("Checked: slower beginner speed. Unchecked: normal Pro speed.")
        self.beginner_checkbox.setStyleSheet("QCheckBox { color: #dce7e9; }")
        self.beginner_checkbox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.beginner_checkbox.setGeometry(self.board_width - 180, 16, 174, 26)
        self.beginner_checkbox.toggled.connect(self._set_beginner_speed)

        self.timer = QTimer(self)
        self.timer.setInterval(self.TICK_MS)
        self.timer.timeout.connect(self._tick)
        self.timer.start()
        self.fullscreen_callback = None

    def _set_beginner_speed(self, beginner: bool) -> None:
        self.timer.setInterval(self.BEGINNER_TICK_MS if beginner else self.TICK_MS)

    def _tick(self) -> None:
        was_game_over = self.game.game_over
        self.game.step()
        if self.game.game_over and not was_game_over:
            self._record_score()
        self.update()

    def _record_score(self) -> None:
        if not self._score_recorded:
            self.high_scores = self.scoreboard.record(self.player_name, self.game.score)
            self._score_recorded = True

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key_directions = {
            Qt.Key.Key_Up: Direction.UP,
            Qt.Key.Key_W: Direction.UP,
            Qt.Key.Key_Down: Direction.DOWN,
            Qt.Key.Key_S: Direction.DOWN,
            Qt.Key.Key_Left: Direction.LEFT,
            Qt.Key.Key_A: Direction.LEFT,
            Qt.Key.Key_Right: Direction.RIGHT,
            Qt.Key.Key_D: Direction.RIGHT,
        }
        if event.key() in key_directions:
            self.game.change_direction(key_directions[event.key()])
        elif event.key() == Qt.Key.Key_Space:
            self.game.toggle_pause()
        elif event.key() == Qt.Key.Key_R:
            self.game.reset()
            self._score_recorded = False
        elif event.key() == Qt.Key.Key_F11 or event.key() == Qt.Key.Key_F:
            if self.fullscreen_callback is not None:
                self.fullscreen_callback()
        elif event.key() == Qt.Key.Key_Escape:
            self.window().close()
        else:
            super().keyPressEvent(event)
            return
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt event naming
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#101820"))

        board_width = self.board_width
        board_height = self.board_height
        board_top = self.HEADER_HEIGHT
        painter.fillRect(0, board_top, board_width, board_height, QColor("#17252f"))

        painter.setPen(QColor("#dce7e9"))
        painter.setFont(QFont("Sans Serif", 12, QFont.Weight.Bold))
        painter.drawText(14, 37, f"{self.player_name}  |  Score: {self.game.score}")
        painter.setFont(QFont("Sans Serif", 9))
        painter.drawText(
            0,
            board_top + board_height + self.FOOTER_HEIGHT,
            board_width,
            self.FOOTER_HEIGHT,
            Qt.AlignmentFlag.AlignCenter,
            "Arrows/WASD: move   Space: pause   R: restart   F11: fullscreen   Esc: quit",
        )

        painter.setPen(QColor("#263943"))
        for x in range(self.game.columns + 1):
            px = x * self.CELL_SIZE
            painter.drawLine(px, board_top, px, board_top + board_height)
        for y in range(self.game.rows + 1):
            py = board_top + y * self.CELL_SIZE
            painter.drawLine(0, py, board_width, py)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#55d187"))
        for index, (x, y) in enumerate(self.game.snake):
            inset = 2 if index else 1
            painter.drawRoundedRect(
                x * self.CELL_SIZE + inset,
                board_top + y * self.CELL_SIZE + inset,
                self.CELL_SIZE - inset * 2,
                self.CELL_SIZE - inset * 2,
                6,
                6,
            )

        fx, fy = self.game.food
        painter.setBrush(QColor("#ff6b6b"))
        painter.drawEllipse(
            fx * self.CELL_SIZE + 5,
            board_top + fy * self.CELL_SIZE + 5,
            self.CELL_SIZE - 10,
            self.CELL_SIZE - 10,
        )

        if self.game.game_over:
            self._draw_game_over(painter)
        elif self.game.paused:
            self._draw_overlay(painter, "Paused — press Space to resume")

    def _draw_overlay(self, painter: QPainter, message: str) -> None:
        board_width = self.board_width
        board_height = self.board_height
        painter.fillRect(0, self.HEADER_HEIGHT, board_width, board_height, QColor(0, 0, 0, 150))
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Sans Serif", 18, QFont.Weight.Bold))
        painter.drawText(
            0,
            self.HEADER_HEIGHT,
            board_width,
            board_height,
            Qt.AlignmentFlag.AlignCenter,
            message,
        )

    def _draw_game_over(self, painter: QPainter) -> None:
        painter.fillRect(0, self.HEADER_HEIGHT, self.board_width, self.board_height, QColor(0, 0, 0, 190))
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Sans Serif", 18, QFont.Weight.Bold))
        painter.drawText(0, self.HEADER_HEIGHT + 54, self.board_width, 32, Qt.AlignmentFlag.AlignCenter,
                         f"Game over — {self.game.score} points")
        painter.setFont(QFont("Sans Serif", 13, QFont.Weight.Bold))
        painter.drawText(0, self.HEADER_HEIGHT + 112, self.board_width, 26, Qt.AlignmentFlag.AlignCenter,
                         "TOP 5 PLAYERS")
        painter.setFont(QFont("Sans Serif", 11))
        for index, entry in enumerate(self.high_scores[:5], start=1):
            row = f"{index}.  {entry['name'][:18]}".ljust(27) + f"{entry['score']} points"
            painter.drawText(80, self.HEADER_HEIGHT + 150 + index * 32, self.board_width - 160, 24,
                             Qt.AlignmentFlag.AlignLeft, row)
        painter.setFont(QFont("Sans Serif", 10))
        painter.drawText(0, self.HEADER_HEIGHT + self.board_height - 24, self.board_width, 20,
                         Qt.AlignmentFlag.AlignCenter, "Press R to play again")


class SnakeWindow(QMainWindow):
    def __init__(self, player_name: str, scoreboard: Scoreboard) -> None:
        super().__init__()
        self.setWindowTitle("Snake")
        self.game_widget = GameWidget(player_name, scoreboard, self)
        self.game_widget.fullscreen_callback = self.toggle_fullscreen
        self.setCentralWidget(self.game_widget)
        self.setFixedSize(
            20 * GameWidget.CELL_SIZE,
            20 * GameWidget.CELL_SIZE + GameWidget.HEADER_HEIGHT + GameWidget.FOOTER_HEIGHT,
        )

    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


def main() -> int:
    app = QApplication(sys.argv)
    name, accepted = QInputDialog.getText(None, "Welcome to Snake", "Enter your player name:")
    if not accepted:
        return 0
    name = name.strip() or "Player"
    scoreboard = Scoreboard()
    window = SnakeWindow(name, scoreboard)
    window.show()
    window.centralWidget().setFocus()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
