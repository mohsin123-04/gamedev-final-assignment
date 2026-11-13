"""Entities as data: player and afterimage are one type, differing only in their input source.

Movement is top-down and grid-collided: a body moves at a fixed speed in eight directions and is
stopped by solid tiles (walls and closed doors). Collision is axis-separated AABB against the tile
grid -- move on x and resolve, then move on y and resolve -- which is deterministic, so a tape
replays to the same place every time.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

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
    w: int                   # size comes from room data (data/room01.json), not a constant
    h: int
    age: int = 0             # ticks alive; drives the fade on older afterimages


def _normalize(x: float, y: float) -> tuple[float, float]:
    """Unit vector in the direction of (x, y); (0, 0) if the input is zero."""
    length = math.hypot(x, y)
    if length == 0.0:
        return 0.0, 0.0
    return x / length, y / length


def _cells(lo: float, size: int, ts: int) -> range:
    """The range of tile indices an AABB edge from `lo` to `lo+size` covers on one axis."""
    return range(int(math.floor(lo / ts)), int(math.floor((lo + size - 1) / ts)) + 1)


IsSolid = Callable[[int, int], bool]


def step(e: Entity, a: ActionSet, dt: float, speed: float, is_solid: IsSolid, ts: int) -> None:
    """Advance one entity one fixed tick, stopping at solid tiles.

    Pure in (e, a, dt, speed, is_solid, ts): given the same inputs and the same solid map it
    always produces the same motion, which is what lets a recorded tape replay identically.
    """
    ix = (1.0 if a.right else 0.0) - (1.0 if a.left else 0.0)
    iy = (1.0 if a.down else 0.0) - (1.0 if a.up else 0.0)
    dx, dy = _normalize(ix, iy)
    vx = dx * speed * dt
    vy = dy * speed * dt

    # move on x, then push out of any solid tile we entered
    e.x += vx
    if vx != 0.0:
        rows = _cells(e.y, e.h, ts)
        hits = [c for c in _cells(e.x, e.w, ts) for r in rows if is_solid(c, r)]
        if hits:
            if vx > 0:
                e.x = min(hits) * ts - e.w
            else:
                e.x = (max(hits) + 1) * ts

    # move on y, then push out of any solid tile we entered
    e.y += vy
    if vy != 0.0:
        cols = _cells(e.x, e.w, ts)
        hits = [r for r in _cells(e.y, e.h, ts) for c in cols if is_solid(c, r)]
        if hits:
            if vy > 0:
                e.y = min(hits) * ts - e.h
            else:
                e.y = (max(hits) + 1) * ts

    e.age += 1
