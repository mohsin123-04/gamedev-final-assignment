"""Room devices: pressure plates, doors and hazards, plus the solid-tile test used for collision.

Everything here is a pure function of the room data and the current body positions -- no state of
its own, no wall-clock, no RNG -- so it stays inside the deterministic simulation the afterimage
replay depends on. A "body" is anything with x, y, w, h (the live player or an afterimage).

Plate / door rule:
  - A plate is PRESSED while any body overlaps one of its cells.
  - A HELD door is open only while its plate is pressed (lowercase plate id, e.g. "a", drives the
    door of the matching uppercase letter "A").
  - A LATCHED door opens the moment its plate is first pressed and stays open for the rest of the
    take (ids listed in the room's "latched"). The caller tracks which latches have been struck.
"""
from __future__ import annotations

from room import Room


def _overlaps_cell(body, c: int, r: int, ts: int) -> bool:
    """True if the body's AABB overlaps tile (c, r)."""
    return (
        body.x < (c + 1) * ts and body.x + body.w > c * ts and
        body.y < (r + 1) * ts and body.y + body.h > r * ts
    )


def pressed_plates(room: Room, bodies) -> set[str]:
    """The set of plate ids currently held down by at least one body."""
    held: set[str] = set()
    for pid, cells in room.plates.items():
        for (c, r) in cells:
            if any(_overlaps_cell(b, c, r, room.tile_size) for b in bodies):
                held.add(pid)
                break
    return held


def open_door_cells(room: Room, pressed: set[str], latched_open: set[str]) -> set[tuple[int, int]]:
    """Which door cells are open this tick, from the pressed plates and the struck latches."""
    cells: set[tuple[int, int]] = set()
    for cell, pid in room.door_cells.items():
        if pid in room.latched:
            if pid in latched_open:
                cells.add(cell)
        elif pid in pressed:
            cells.add(cell)
    return cells


def solid_at(room: Room, open_cells: set[tuple[int, int]], c: int, r: int) -> bool:
    """True if tile (c, r) blocks movement: outside the grid, a wall, or a closed door."""
    if c < 0 or r < 0 or c >= room.cols or r >= room.rows:
        return True
    if (c, r) in room.walls:
        return True
    if (c, r) in room.door_cells and (c, r) not in open_cells:
        return True
    return False


def any_at_exit(room: Room, bodies) -> bool:
    """True if any body has reached an exit cell (the room's win condition)."""
    ts = room.tile_size
    return any(
        _overlaps_cell(b, c, r, ts)
        for b in bodies for (c, r) in room.exit_cells
    )


def on_hazard(room: Room, body) -> bool:
    """True if the body is touching a hazard cell (which ends its take)."""
    ts = room.tile_size
    return any(_overlaps_cell(body, c, r, ts) for (c, r) in room.hazards)
