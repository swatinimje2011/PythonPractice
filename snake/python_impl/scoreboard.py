"""Persistent top-five leaderboard for Snake."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class ScoreEntry(TypedDict):
    name: str
    score: int


class Scoreboard:
    """Store each player's best score and retain the five highest records."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).with_name("high_scores.json")

    def top_scores(self) -> list[ScoreEntry]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(data, list):
            return []

        entries: list[ScoreEntry] = []
        for item in data:
            if (
                isinstance(item, dict)
                and isinstance(item.get("name"), str)
                and isinstance(item.get("score"), int)
                and item["score"] >= 0
            ):
                name = item["name"].strip()
                if name:
                    entries.append({"name": name, "score": item["score"]})
        return self._rank(entries)[:5]

    def record(self, name: str, score: int) -> list[ScoreEntry]:
        player = name.strip() or "Player"
        entries = self.top_scores()
        normalized_name = player.casefold()
        matching = [entry for entry in entries if entry["name"].casefold() == normalized_name]
        best_score = max([score, *(entry["score"] for entry in matching)])
        display_name = matching[0]["name"] if matching else player
        entries = [entry for entry in entries if entry["name"].casefold() != normalized_name]
        entries.append({"name": display_name, "score": best_score})
        ranked = self._rank(entries)[:5]

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(ranked, indent=2) + "\n", encoding="utf-8")
        return ranked

    @staticmethod
    def _rank(entries: list[ScoreEntry]) -> list[ScoreEntry]:
        return sorted(entries, key=lambda entry: (-entry["score"], entry["name"].casefold()))
