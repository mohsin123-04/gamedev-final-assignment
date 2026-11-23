# Afterimage

CSCI 4160U Game Development, semester game project.

A 2D puzzle game where you're the only worker in a facility that was built for a whole crew.
Every run you do gets recorded, and when you reset the room it plays back as a faint "afterimage"
that repeats your inputs exactly. Those copies can stand on pressure plates, block hazards, or
act as a platform. You solve a room by stacking up enough takes that one of you can finally get
to the exit.

Full design is in [`docs/gdd.md`](docs/gdd.md).

Built with Python and raylib (the [`raylib` Python bindings](https://pypi.org/project/raylib/),
imported as `pyray`). raylib is a course requirement.

## Requirements

- Python 3.11 or newer
- The packages in `requirements.txt`. That's just `raylib`, which ships the library itself, so
  there's nothing to compile and no system package to install.

## Build and run

```sh
git clone https://github.com/mohsin123-04/gamedev-final-assignment.git
cd gamedev-final-assignment
python -m venv .venv
.venv\Scripts\activate        # Windows.  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

If a window opens and you can move with the arrow keys, it's working.

## Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Move the live player |
| `R` | Reset: bank this take as an afterimage, start a new one |
| `P` | Pause / resume |
| `Enter` | On ROOM SOLVED, run the room again |
| `Esc` | Quit |

Any body reaching a green exit tile solves the room, so the trick is to layer afterimages: one of
you holds the pressure plate to keep its door open while another slips through. Watch out for the
hazards and the patrolling sentry. Every reset saves your run as an afterimage that replays your
inputs, and once you hit the take limit the room starts over.

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

Checkpoint 5 (Balancing). This sits on top of the CP2 skeleton: entities are data in one
collection, there's a `PLAYING` / `PAUSED` / `ROOM_SOLVED` state machine, and the loop keeps a
fixed timestep with update and render kept separate. What's in so far:

- Data-driven behaviour. The room is a tile grid plus a few tuning numbers in
  [`data/room01.json`](data/room01.json), read at boot by [`src/room.py`](src/room.py). Change a
  value like `player_speed`, `take_limit` or `enemy.detect_radius`, or edit the level `grid`, and
  the game behaves differently without any code change. See [`data/README.md`](data/README.md).
- Assets loaded at boot. The player texture and the two sound effects load once in
  [`src/assets.py`](src/assets.py) before the loop starts, not when they're first used. See
  [`assets/README.md`](assets/README.md). I made all three myself with
  [`tools/make_assets.py`](tools/make_assets.py).
- Grid world and devices. Tile collision, pressure plates wired to doors, and hazards that end a
  take, in [`src/devices.py`](src/devices.py).
- Enemy AI. A sentry that patrols a set of waypoints and switches to chasing when a body gets
  close, with a bit of hysteresis so it doesn't flicker between the two. Code in
  [`src/enemy.py`](src/enemy.py), notes in [`docs/cp4-ai.md`](docs/cp4-ai.md).
- Balancing. The sentry's `chase_speed` and `detect_radius` and the room's `take_limit` were
  retuned (in data, no recompile) toward a deliberate difficulty shape, backed by measurements
  from [`tools/balance_check.py`](tools/balance_check.py). Before/after in
  [`docs/cp5-balance.md`](docs/cp5-balance.md).

Architecture write-up is in [`docs/architecture.md`](docs/architecture.md).
