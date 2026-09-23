# Game Name TBD

CSCI 4160U Game Development — semester game project.

A 2D puzzle-platformer about being the only worker in a facility built for a crew. Every run you
perform is recorded; reset the room and it replays as a translucent *afterimage* that repeats
your inputs exactly — standing on pressure plates, blocking hazards, and acting as a platform
you can stand on. Solve each room by layering takes until enough of you exist at once for one of
you to reach the exit.

See [`docs/gdd.md`](docs/gdd.md) for the full design.

Built with **Python** and **raylib** (via the [`raylib` Python bindings](https://pypi.org/project/raylib/),
imported as `pyray`). raylib is a course requirement.

## Requirements

- Python 3.11 or newer
- The dependencies in `requirements.txt` (just `raylib`, which bundles the raylib library itself —
  there is nothing to compile and no system package to install)

## Build and run

```sh
git clone https://github.com/mohsin123-04/gamedev-final-assignment.git
cd gamedev-final-assignment
python -m venv .venv
.venv\Scripts\activate        # Windows.  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

If the window opens and you can move with the arrow keys, the setup is correct.

## Controls

| Key | Action |
|---|---|
| Arrow keys | Move |
| `Esc` | Quit |

## Repository layout

```
src/                the game
assets/             anything loaded at runtime (art, sound, fonts)
data/               tuning values and level data, loaded rather than hardcoded
docs/gdd.md         Game Design Document
docs/postmortem.md  written at the end, started early
ATTRIBUTION.md      AI use and third-party assets
```

## Status

Checkpoint 1. The game design is being finalised; `src/main.py` is currently a movement
spike used to verify the raylib toolchain end to end.
