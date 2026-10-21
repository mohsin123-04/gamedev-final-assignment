"""Rooms as data: tuning and level values are loaded from data/ at boot, never hardcoded.

This is the CP3 move the architecture promised (docs/architecture.md §4, §6): the values
that shape a room's behaviour live in a data file, so changing the file changes the game
without touching code. Loaded once when the game boots, then handed to GameState.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# data/ sits next to src/, both under the repo root.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_ROOM = DATA_DIR / "room01.json"


@dataclass(frozen=True)
class Room:
    """One room's tunable values, as loaded from a data file. Immutable once loaded."""
    name: str

    # --- the three data values that visibly change behaviour (see data/README.md) ---
    player_speed: float      # 1) pixels/second every body (player + afterimages) moves at
    take_limit: int          # 2) afterimages allowed before the room resets itself
    exit_x: int              # 3) x of the green exit wall; cross it to solve the room

    # --- supporting room layout, also data-driven ---
    player_size: int
    spawn_x: float
    spawn_y: float


def load_room(path: Path = DEFAULT_ROOM) -> Room:
    """Read a room data file and build a Room. Raises if a required key is missing."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return Room(
        name=d["name"],
        player_speed=float(d["player_speed"]),
        take_limit=int(d["take_limit"]),
        exit_x=int(d["exit_x"]),
        player_size=int(d["player_size"]),
        spawn_x=float(d["spawn_x"]),
        spawn_y=float(d["spawn_y"]),
    )
