"""Entities as data: player and afterimage are one type, differing only in their input source."""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto

from config import PLAYER_SIZE, PLAYER_SPEED
from input import ActionSet, InputSource


class EntityKind(Enum):
    PLAYER = auto()
    AFTERIMAGE = auto()      # affects rendering only, never the simulation


@dataclass
class Entity:
    x: float
    y: float
    source: InputSource      # KeyboardSource for the live player, TapeSource for a ghost
    kind: EntityKind
    w: int = PLAYER_SIZE
    h: int = PLAYER_SIZE
    age: int = 0             # ticks alive; drives the fade on older afterimages


def _normalize(x: float, y: float) -> tuple[float, float]:
    """Unit vector in the direction of (x, y); (0, 0) if the input is zero."""
    length = math.hypot(x, y)
    if length == 0.0:
        return 0.0, 0.0
    return x / length, y / length


def step(e: Entity, a: ActionSet, dt: float) -> None:
    """Advance one entity one fixed tick; pure in (e, a, dt) so a tape always replays identically."""
    ix = (1.0 if a.right else 0.0) - (1.0 if a.left else 0.0)
    iy = (1.0 if a.down else 0.0) - (1.0 if a.up else 0.0)
    dx, dy = _normalize(ix, iy)
    e.x += dx * PLAYER_SPEED * dt
    e.y += dy * PLAYER_SPEED * dt
    e.age += 1
