# Snake (Python)

A classic desktop Snake game built with Python and PySide6. The game rules are
in `game.py`, separate from the Qt interface in `main.py`. At launch, the game
asks for a player name and keeps a local leaderboard of the five players with
the highest personal scores.

From the repository root, install the dependency and start the game:

```bash
python -m pip install -r snake/python_impl/requirements.txt
python snake/python_impl/main.py
```

Use the arrow keys or WASD to steer, Space to pause or resume, R to restart,
and F11 to toggle fullscreen (press F11 again to return to windowed mode).
Check **Beginner level (slow)** for a slower pace; when unchecked, the game
runs at normal Pro speed. Press Escape to quit. Player scores are stored in
`high_scores.json` beside the game files.

Run the game logic tests with:

```bash
python -m unittest discover -s snake/python_impl -p 'test_*.py'
```
