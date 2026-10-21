# Afterimage

CSCI 4160U Game Development, semester game project.

A 2D puzzle-platformer about being the only worker in a facility built for a crew. Every run you
perform is recorded; reset the room and it replays as a translucent *afterimage* that repeats
your inputs exactly: standing on pressure plates, blocking hazards, and acting as a platform
you can stand on. Solve each room by layering takes until enough of you exist at once for one of
you to reach the exit.

See [`docs/gdd.md`](docs/gdd.md) for the full design.

Built with **Python** and **raylib** (via the [`raylib` Python bindings](https://pypi.org/project/raylib/),
imported as `pyray`). raylib is a course requirement.

## Requirements

- Python 3.11 or newer
- The dependencies in `requirements.txt` (just `raylib`, which bundles the raylib library itself,
  so there is nothing to compile and no system package to install)

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
| Arrow keys / WASD | Move the live player |
| `R` | Reset: bank this take as an afterimage, start a new one |
| `P` | Pause / resume |
| `Enter` | On ROOM SOLVED, run the room again |
| `Esc` | Quit |

Cross the green exit on the right to solve the room. Each reset layers another afterimage that
replays your inputs exactly; after four takes the room restarts.

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

Checkpoint 3 (Data & Assets). Building on the CP2 architecture skeleton (entities as data in one
collection, an explicit `PLAYING` / `PAUSED` / `ROOM_SOLVED` state machine, a fixed-timestep loop
with a clean update/render split):

- **Data-driven behaviour.** Room tuning lives in [`data/room01.json`](data/room01.json), loaded at
  boot by [`src/room.py`](src/room.py). Editing `player_speed`, `take_limit` or `exit_x` visibly
  changes the game with no code change — see [`data/README.md`](data/README.md).
- **Assets preloaded at boot.** The player texture and two sound effects are loaded once in
  [`src/assets.py`](src/assets.py) before the loop, not when first used — see
  [`assets/README.md`](assets/README.md). All three are self-made by
  [`tools/make_assets.py`](tools/make_assets.py).

Collision and the enemy AI arrive in later checkpoints. See
[`docs/architecture.md`](docs/architecture.md).
