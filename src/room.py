"""Rooms as data: a room is a character grid plus tuning values, loaded from data/ at boot.

The grid is the level. Each character is one tile:
    #  wall (solid)            .  or space  floor
    S  spawn (one)             E  exit  (reach any to solve)
    ^  hazard (ends a take)
    a-z  pressure plate        A-Z  door, opened by the plate of the same letter
Plate/door ids pair by letter: plate "a" drives door "A". Plates in the "latched" list stay open
once struck; the rest hold open only while a body stands on them. Loaded once at boot (the CP3
"rooms are data" move), then handed to GameState.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from enemy import EnemySpec   # the sentry's tuning is loaded from room data too (CP4)

# data/ sits next to src/, both under the repo root.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_ROOM = DATA_DIR / "room01.json"


@dataclass(frozen=True)
class Room:
    """One room: its grid of devices plus the values that tune it. Immutable once loaded."""
    name: str
    tile_size: int
    cols: int
    rows: int

    # --- tuning (data/README.md) ---
    player_speed: float      # pixels/second every body (player + afterimages) moves at
    take_limit: int          # afterimages allowed before the room resets itself
    player_size: int

    # --- geometry, parsed from the grid (tile coordinates) ---
    spawn_x: float
    spawn_y: float
    walls: frozenset = frozenset()
    hazards: frozenset = frozenset()
    exit_cells: frozenset = frozenset()
    plates: dict = field(default_factory=dict)        # plate id -> list of (c, r) cells
    door_cells: dict = field(default_factory=dict)    # (c, r) -> plate id that opens it
    latched: frozenset = frozenset()                  # plate ids whose doors latch open

    # --- CP4: the room's sentry, if it has one (None => no enemy in this room) ---
    enemy: EnemySpec | None = None


def _load_enemy(d: dict) -> EnemySpec | None:
    """Build an EnemySpec from the optional "enemy" block of a room file, or None if absent."""
    if "enemy" not in d:
        return None
    e = d["enemy"]
    return EnemySpec(
        spawn_x=float(e["spawn_x"]),
        spawn_y=float(e["spawn_y"]),
        size=int(e["size"]),
        patrol_speed=float(e["patrol_speed"]),
        chase_speed=float(e["chase_speed"]),
        detect_radius=float(e["detect_radius"]),
        lose_radius=float(e["lose_radius"]),
        give_up_ticks=int(e["give_up_ticks"]),
        waypoints=[(float(p[0]), float(p[1])) for p in e["waypoints"]],
    )


def load_room(path: Path = DEFAULT_ROOM) -> Room:
    """Read a room data file, parse its grid into devices, and build a Room."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)

    grid: list[str] = d["grid"]
    rows = len(grid)
    cols = len(grid[0])
    if any(len(line) != cols for line in grid):
        raise ValueError(f"{path.name}: all grid rows must be the same length ({cols})")

    ts = int(d["tile_size"])
    player_size = int(d["player_size"])

    walls: set = set()
    hazards: set = set()
    exit_cells: set = set()
    plates: dict = {}
    door_cells: dict = {}
    spawn = None

    for r, line in enumerate(grid):
        for c, ch in enumerate(line):
            cell = (c, r)
            if ch == "#":
                walls.add(cell)
            elif ch == "^":
                hazards.add(cell)
            elif ch == "E":
                exit_cells.add(cell)
            elif ch == "S":
                spawn = cell
            elif ch.islower() and ch.isalpha():
                plates.setdefault(ch, []).append(cell)
            elif ch.isupper() and ch.isalpha():
                door_cells[cell] = ch.lower()
            # "." or " " is floor: nothing to record

    if spawn is None:
        raise ValueError(f"{path.name}: grid has no spawn 'S'")
    if not exit_cells:
        raise ValueError(f"{path.name}: grid has no exit 'E'")

    sc, sr = spawn
    spawn_x = sc * ts + (ts - player_size) / 2.0   # centre the body in its spawn tile
    spawn_y = sr * ts + (ts - player_size) / 2.0

    return Room(
        name=d["name"],
        tile_size=ts,
        cols=cols,
        rows=rows,
        player_speed=float(d["player_speed"]),
        take_limit=int(d["take_limit"]),
        player_size=player_size,
        spawn_x=spawn_x,
        spawn_y=spawn_y,
        walls=frozenset(walls),
        hazards=frozenset(hazards),
        exit_cells=frozenset(exit_cells),
        plates={pid: list(cells) for pid, cells in plates.items()},
        door_cells=door_cells,
        latched=frozenset(d.get("latched", [])),
        enemy=_load_enemy(d),
    )
