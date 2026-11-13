"""The Sentry: a facility patrol enemy driven by a two-state machine (PATROL, CHASE).

Movement is a deliberate hybrid (the reasoning is written up in docs/cp4-ai.md):
  - PATROL walks authored waypoints (scripted). A facility patrol route is level content,
    not something worth solving at runtime.
  - CHASE steers straight at the nearest body (seek steering). The rooms are small, open and
    single-screen, so A* pathfinding would be cost for no benefit.

Everything here is a pure function of simulation state (body positions) and the fixed timestep
-- no wall-clock, no RNG -- because the afterimage replay architecture depends on determinism.
This module imports nothing from the rest of the game, so the AI stays decoupled: a "body" is
anything with x, y, w, h (a player or an afterimage Entity).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto


class EnemyState(Enum):
    PATROL = auto()   # walking the authored waypoint route, scanning for a body
    CHASE = auto()    # a body was spotted; steer straight at the nearest one


@dataclass
class EnemySpec:
    """The sentry's tunable values, loaded from room data (data/room01.json -> "enemy")."""
    spawn_x: float
    spawn_y: float
    size: int
    patrol_speed: float            # px/s along the waypoint route
    chase_speed: float             # px/s while seeking (kept below player_speed, so it is evadable)
    detect_radius: float           # PATROL -> CHASE once a body is this close
    lose_radius: float             # CHASE -> PATROL only past this (larger => hysteresis, no flicker)
    give_up_ticks: int             # ticks with no body inside lose_radius before giving up the chase
    waypoints: list[tuple[float, float]]


@dataclass
class Enemy:
    """A live sentry. Built fresh from its spec at the start of every take (see state.py),
    so each take -- and therefore every afterimage replaying from frame 0 -- faces the same
    sentry behaviour from the same starting conditions."""
    spec: EnemySpec
    x: float
    y: float
    state: EnemyState = EnemyState.PATROL
    waypoint_i: int = 0            # the patrol waypoint currently being walked toward
    lost_ticks: int = 0            # consecutive ticks with no target in range (the give-up timer)
    target_x: float = 0.0          # last targeted body centre, kept only for the debug line
    target_y: float = 0.0
    has_target: bool = False       # whether a body is currently being tracked (drives rendering)

    @classmethod
    def from_spec(cls, spec: EnemySpec) -> "Enemy":
        return cls(spec=spec, x=spec.spawn_x, y=spec.spawn_y)

    @property
    def w(self) -> int:
        return self.spec.size

    @property
    def h(self) -> int:
        return self.spec.size

    @property
    def cx(self) -> float:
        return self.x + self.spec.size / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.spec.size / 2.0


def _seek(from_x: float, from_y: float, to_x: float, to_y: float, speed: float, dt: float) -> tuple[float, float]:
    """One tick of seek steering: a step of length `speed*dt` straight toward the target,
    clamped so a close target is reached exactly rather than overshot."""
    dx, dy = to_x - from_x, to_y - from_y
    dist = math.hypot(dx, dy)
    if dist == 0.0:
        return 0.0, 0.0
    step_len = min(speed * dt, dist)
    return dx / dist * step_len, dy / dist * step_len


def _nearest_body(enemy: Enemy, bodies) -> tuple[object, float]:
    """The body whose centre is closest to the sentry centre, with that distance.
    Returns (None, inf) if there are no bodies."""
    best, best_d = None, math.inf
    for b in bodies:
        d = math.hypot((b.x + b.w / 2.0) - enemy.cx, (b.y + b.h / 2.0) - enemy.cy)
        if d < best_d:
            best, best_d = b, d
    return best, best_d


def update_enemy(enemy: Enemy, bodies, dt: float) -> None:
    """Advance the sentry one fixed tick: run the state machine, then move. Mutates `enemy`."""
    spec = enemy.spec
    target, dist = _nearest_body(enemy, bodies)
    if target is not None:
        enemy.target_x = target.x + target.w / 2.0
        enemy.target_y = target.y + target.h / 2.0
    enemy.has_target = target is not None and (
        enemy.state == EnemyState.CHASE or dist <= spec.detect_radius
    )

    # --- transitions (named to match docs/cp4-ai.md) ---
    if enemy.state == EnemyState.PATROL:
        # "spots a body": a body has entered the detection radius.
        if target is not None and dist <= spec.detect_radius:
            enemy.state = EnemyState.CHASE
            enemy.lost_ticks = 0
    else:  # CHASE
        # "loses the trail": nothing within the (larger) lose radius for give_up_ticks in a row.
        if target is None or dist > spec.lose_radius:
            enemy.lost_ticks += 1
            if enemy.lost_ticks >= spec.give_up_ticks:
                enemy.state = EnemyState.PATROL
                enemy.lost_ticks = 0
        else:
            enemy.lost_ticks = 0

    # --- movement, chosen by state ---
    if enemy.state == EnemyState.CHASE and target is not None:
        mx, my = _seek(enemy.x, enemy.y, target.x, target.y, spec.chase_speed, dt)
    else:
        mx, my = _patrol_step(enemy, dt)
    enemy.x += mx
    enemy.y += my


def _patrol_step(enemy: Enemy, dt: float) -> tuple[float, float]:
    """Scripted waypoint walk: seek the current waypoint and, on arrival, advance to the next
    (the route loops). Returns the movement for this tick."""
    spec = enemy.spec
    if not spec.waypoints:
        return 0.0, 0.0
    wx, wy = spec.waypoints[enemy.waypoint_i]
    mx, my = _seek(enemy.x, enemy.y, wx, wy, spec.patrol_speed, dt)
    # _seek clamps the final step onto the waypoint, so check arrival after applying it.
    if math.hypot(wx - (enemy.x + mx), wy - (enemy.y + my)) <= 1.0:
        enemy.waypoint_i = (enemy.waypoint_i + 1) % len(spec.waypoints)
    return mx, my


def overlaps(enemy: Enemy, body) -> bool:
    """AABB overlap test between the sentry and a body -- used to catch the live player."""
    return (
        enemy.x < body.x + body.w and enemy.x + enemy.w > body.x and
        enemy.y < body.y + body.h and enemy.y + enemy.h > body.y
    )
