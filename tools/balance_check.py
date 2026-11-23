"""CP5 balancing evidence harness for Afterimage.

Measures the room instead of guessing by feel:
  1. ESCAPE   -- can the player open a gap on the sentry once chased? (chase_speed)
  2. SNEAK    -- is there a timing window to cross the patrol line unseen? (detect_radius)
  3. TAKES    -- how many afterimages does the room actually require? (take_limit)

Pure sim: reuses the real enemy.update_enemy / overlaps against the shipped room data, so the
numbers come from the same code the game runs. No window, no raylib.

Run from the repo root:  .venv\\Scripts\\python tools\\balance_check.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from config import DT
from room import load_room
from enemy import Enemy, EnemySpec, EnemyState, update_enemy, overlaps

ROOM = load_room(REPO / "data" / "room01.json")


@dataclass
class Body:
    x: float
    y: float
    w: int
    h: int

    @property
    def cx(self): return self.x + self.w / 2.0
    @property
    def cy(self): return self.y + self.h / 2.0


def _spec(**over) -> EnemySpec:
    e = ROOM.enemy
    d = dict(spawn_x=e.spawn_x, spawn_y=e.spawn_y, size=e.size,
             patrol_speed=e.patrol_speed, chase_speed=e.chase_speed,
             detect_radius=e.detect_radius, lose_radius=e.lose_radius,
             give_up_ticks=e.give_up_ticks, waypoints=list(e.waypoints))
    d.update(over)
    return EnemySpec(**d)


def dist(a, b) -> float:
    return ((a.cx - b.cx) ** 2 + (a.cy - b.cy) ** 2) ** 0.5


# ---------------------------------------------------------------- 1. ESCAPE
def escape_test(chase_speed: float) -> str:
    """Put the sentry in CHASE at exactly detect_radius, then have the player flee
    directly away at player_speed in open space (best case). Does the gap open or close?"""
    spec = _spec(chase_speed=chase_speed)
    en = Enemy.from_spec(spec)
    en.x, en.y = 600.0, 400.0
    en.state = EnemyState.CHASE
    ps = ROOM.player_speed
    body = Body(x=en.cx + spec.detect_radius, y=en.cy - ROOM.player_size / 2.0,
                w=ROOM.player_size, h=ROOM.player_size)
    start = dist(en, body)
    for t in range(1, 901):  # up to 15 s
        dx, dy = body.cx - en.cx, body.cy - en.cy
        m = (dx * dx + dy * dy) ** 0.5 or 1.0
        body.x += dx / m * ps * DT
        body.y += dy / m * ps * DT
        update_enemy(en, [body], DT)
        if overlaps(en, body):
            return f"CAUGHT after {t*DT:4.2f}s  (gap {start:.0f}->0 px)"
        if en.state == EnemyState.PATROL:
            return f"ESCAPED after {t*DT:4.2f}s (gap {start:.0f}->{dist(en,body):.0f} px, sentry gave up)"
    return f"stalemate after 15s (gap {start:.0f}->{dist(en,body):.0f} px)"


# ---------------------------------------------------------------- 2. SNEAK
def sneak_test(detect_radius: float) -> str:
    """Walk a player right along row 7 across the patrol line, for every patrol phase.
    Fraction of phases in which the sentry never flips to CHASE = the timing window."""
    spec = _spec(detect_radius=detect_radius)
    ts = ROOM.tile_size
    row_y = 7 * ts + (ts - ROOM.player_size) / 2.0
    start_x = 2 * ts
    door_x = 17 * ts
    (ax, ay), (bx, by) = spec.waypoints[0], spec.waypoints[1]
    leg = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
    period = max(1, int(2 * leg / (spec.patrol_speed * DT)))
    ok = 0
    for phase in range(period):
        en = Enemy.from_spec(spec)
        for _ in range(phase):
            update_enemy(en, [], DT)
        body = Body(x=start_x, y=row_y, w=ROOM.player_size, h=ROOM.player_size)
        seen = False
        for _ in range(2000):
            body.x += ROOM.player_speed * DT
            update_enemy(en, [body], DT)
            if en.state == EnemyState.CHASE:
                seen = True
                break
            if body.x >= door_x:
                break
        if not seen:
            ok += 1
    pct = 100.0 * ok / period
    verdict = "no window (always seen)" if ok == 0 else f"window exists ({ok}/{period} phases)"
    return f"{pct:5.1f}% of crossings stay unseen -- {verdict}"


# ---------------------------------------------------------------- 3. TAKES
def takes_report() -> str:
    """Structural minimum: plate 'a' is not latched, so a body must hold it while another
    reaches the exit through door A. That is 1 afterimage + 1 live body = 1 reset minimum."""
    latched = len(ROOM.latched)
    plates = list(ROOM.plates)
    need = 0 if latched else 1
    return (f"plates={plates} latched={ROOM.latched or '{}'}  -> "
            f"min afterimages to solve = {need}; "
            f"take_limit={ROOM.take_limit} gives {ROOM.take_limit - need} spare")


if __name__ == "__main__":
    e = ROOM.enemy
    print(f"SHIPPED: player_speed={ROOM.player_speed:.0f}  chase_speed={e.chase_speed:.0f}  "
          f"detect_radius={e.detect_radius:.0f}  lose_radius={e.lose_radius:.0f}  take_limit={ROOM.take_limit}")
    print()
    print("1) ESCAPE  (flee straight away at player_speed; gap opens or closes?)")
    for cs in (e.chase_speed, 300, 220, 200, 180):
        print(f"     chase_speed={cs:3.0f}: {escape_test(cs)}")
    print()
    print("2) SNEAK   (cross the patrol line on row 7; timing window?)")
    for dr in (e.detect_radius, 200, 160, 150, 140):
        print(f"     detect_radius={dr:3.0f}: {sneak_test(dr)}")
    print()
    print("3) TAKES")
    print(f"     {takes_report()}")
