"""Afterimage entry point: the fixed-timestep loop and the update/render split (controls in README)."""
from __future__ import annotations

import pyray as rl

import devices
from assets import Assets
from config import DT, TARGET_FPS, TITLE, WINDOW_H, WINDOW_W
from enemy import EnemyState, overlaps, update_enemy
from entities import EntityKind, step
from room import load_room
from state import GameState, Mode


# ---------------------------------------------------------------- update (logic only) ---

def update(state: GameState, dt: float) -> None:
    """Advance the simulation one fixed tick. Mutates state; never draws; never reads time."""
    if state.mode != Mode.PLAYING:
        return
    room = state.room

    # device state for this tick, from where the bodies are right now
    pressed = devices.pressed_plates(room, state.entities)
    for pid in pressed:
        if pid in room.latched:
            state.latched_open.add(pid)      # a latched plate stays open once struck
    open_cells = devices.open_door_cells(room, pressed, state.latched_open)
    state.pressed = pressed                  # stashed so render draws the same state
    state.open_cells = open_cells

    def is_solid(c: int, r: int) -> bool:
        return devices.solid_at(room, open_cells, c, r)

    for e in state.entities:
        a = e.source.poll()
        step(e, a, dt, room.player_speed, is_solid, room.tile_size)
        if e.kind == EntityKind.PLAYER:
            state.current_tape.append(a)  # record the live player's intent, one ActionSet/tick

    # any body reaching the exit solves the room (not just the live player)
    if devices.any_at_exit(room, state.entities):
        state.solve()
        return

    # a hazard ends the current take: bank it (it replays as an afterimage up to the hit)
    if devices.on_hazard(room, state.player):
        if state.reset_take():
            state.caught = True
        return

    # CP4: the sentry advances in the same deterministic tick. Catching the player ends the take.
    if state.enemy is not None:
        update_enemy(state.enemy, state.entities, dt)
        if overlaps(state.enemy, state.player) and state.reset_take():
            state.caught = True


# ---------------------------------------------------------------- render (draw only) ---

def render(state: GameState, assets: Assets) -> None:
    """Draw the current state. Reads only; never mutates the simulation."""
    rl.begin_drawing()
    rl.clear_background(rl.Color(18, 18, 24, 255))

    _draw_room(state)

    ghost_count = max(len(state.entities) - 1, 1)
    for i, e in enumerate(state.entities):
        if e.kind == EntityKind.AFTERIMAGE:
            alpha = int(70 + 110 * (i + 1) / ghost_count)   # older ghosts (lower i) are fainter
            tint = rl.Color(120, 200, 255, min(alpha, 190))
        else:
            tint = rl.Color(235, 70, 70, 255)
        _draw_body(assets, e.x, e.y, e.w, e.h, tint)

    if state.enemy is not None:
        _draw_enemy(assets, state.enemy)

    _draw_hud(state)
    if state.mode == Mode.PAUSED:
        _draw_banner("PAUSED", "P to resume")
    elif state.mode == Mode.ROOM_SOLVED:
        _draw_banner("ROOM SOLVED", "Enter to run it again")

    rl.end_drawing()


def _draw_room(state: GameState) -> None:
    """Draw the tile grid: exit, walls, hazards, plates and doors."""
    room = state.room
    ts = room.tile_size

    for (c, r) in room.exit_cells:
        rl.draw_rectangle(c * ts, r * ts, ts, ts, rl.Color(30, 60, 45, 255))
        rl.draw_rectangle_lines(c * ts, r * ts, ts, ts, rl.Color(80, 200, 120, 255))

    for (c, r) in room.walls:
        rl.draw_rectangle(c * ts, r * ts, ts, ts, rl.Color(46, 46, 60, 255))
        rl.draw_rectangle_lines(c * ts, r * ts, ts, ts, rl.Color(62, 62, 80, 255))

    for (c, r) in room.hazards:
        rl.draw_rectangle(c * ts, r * ts, ts, ts, rl.Color(70, 20, 28, 255))
        _draw_spikes(c, r, ts)

    for pid, cells in room.plates.items():
        down = pid in state.pressed
        fill = rl.Color(90, 190, 130, 255) if down else rl.Color(70, 72, 92, 255)
        for (c, r) in cells:
            inset = ts // 6
            rl.draw_rectangle(c * ts + inset, r * ts + inset, ts - 2 * inset, ts - 2 * inset, fill)
            _draw_tile_label(pid.upper(), c, r, ts, rl.Color(20, 24, 28, 255))

    for (c, r), pid in room.door_cells.items():
        if (c, r) in state.open_cells:
            rl.draw_rectangle_lines(c * ts, r * ts, ts, ts, rl.Color(120, 100, 70, 120))
        else:
            rl.draw_rectangle(c * ts, r * ts, ts, ts, rl.Color(120, 96, 60, 255))
            rl.draw_rectangle_lines(c * ts, r * ts, ts, ts, rl.Color(160, 130, 85, 255))
            _draw_tile_label(pid.upper(), c, r, ts, rl.Color(30, 24, 16, 255))


def _draw_spikes(c: int, r: int, ts: int) -> None:
    """A row of little triangles, so a hazard tile reads as dangerous."""
    n = 3
    step_w = ts / n
    base = (r + 1) * ts - 4
    col = rl.Color(220, 80, 90, 255)
    for k in range(n):
        x0 = c * ts + k * step_w
        rl.draw_triangle(
            rl.Vector2(x0, base), rl.Vector2(x0 + step_w, base),
            rl.Vector2(x0 + step_w / 2, r * ts + 6), col,
        )


def _draw_tile_label(text: str, c: int, r: int, ts: int, color: rl.Color) -> None:
    w = rl.measure_text(text, 16)
    rl.draw_text(text, c * ts + ts // 2 - w // 2, r * ts + ts // 2 - 8, 16, color)


def _draw_body(assets: Assets, x: float, y: float, w: int, h: int, tint: rl.Color) -> None:
    """Draw the preloaded player texture scaled to the entity's data-driven size, in `tint`."""
    tex = assets.player_tex
    src = rl.Rectangle(0, 0, float(tex.width), float(tex.height))
    dst = rl.Rectangle(x, y, float(w), float(h))
    rl.draw_texture_pro(tex, src, dst, rl.Vector2(0, 0), 0.0, tint)


def _draw_enemy(assets: Assets, enemy) -> None:
    """Draw the sentry and make its state machine legible for the demo: the patrol route, the
    detection circle, a line to its target while chasing, and a label of the current state."""
    cx, cy = int(enemy.cx), int(enemy.cy)
    chasing = enemy.state == EnemyState.CHASE

    wps = enemy.spec.waypoints
    for i in range(len(wps)):
        ax, ay = wps[i]
        bx, by = wps[(i + 1) % len(wps)]
        rl.draw_line(int(ax), int(ay), int(bx), int(by), rl.Color(90, 80, 60, 120))
        rl.draw_circle_lines(int(ax), int(ay), 5, rl.Color(150, 130, 90, 160))

    ring = rl.Color(235, 90, 70, 110) if chasing else rl.Color(210, 170, 70, 80)
    rl.draw_circle_lines(cx, cy, enemy.spec.detect_radius, ring)

    if chasing and enemy.has_target:
        rl.draw_line(cx, cy, int(enemy.target_x), int(enemy.target_y), rl.Color(235, 90, 70, 200))

    tint = rl.Color(255, 120, 60, 255) if chasing else rl.Color(230, 190, 90, 255)
    _draw_body(assets, enemy.x, enemy.y, enemy.w, enemy.h, tint)

    label = enemy.state.name   # "PATROL" / "CHASE" -- the state machine, on screen
    lw = rl.measure_text(label, 18)
    rl.draw_text(label, cx - lw // 2, int(enemy.y) - 22, 18, tint)


def _draw_hud(state: GameState) -> None:
    rl.draw_text(f"MODE: {state.mode.name}", 16, 14, 24, rl.RAYWHITE)
    rl.draw_text(f"TAKES: {state.takes_used} / {state.room.take_limit}", 16, 44, 24, rl.RAYWHITE)
    rl.draw_text(
        "move: arrows/WASD    R: reset take    P: pause    hold the plate, open the door, reach the green exit",
        16, WINDOW_H - 30, 18, rl.Color(170, 170, 180, 255),
    )


def _draw_banner(title: str, hint: str) -> None:
    rl.draw_rectangle(0, WINDOW_H // 2 - 70, WINDOW_W, 140, rl.Color(0, 0, 0, 160))
    tw = rl.measure_text(title, 56)
    rl.draw_text(title, WINDOW_W // 2 - tw // 2, WINDOW_H // 2 - 56, 56, rl.RAYWHITE)
    hw = rl.measure_text(hint, 26)
    rl.draw_text(hint, WINDOW_W // 2 - hw // 2, WINDOW_H // 2 + 8, 26, rl.Color(180, 180, 190, 255))


# ---------------------------------------------------------------- events + loop ---

def handle_events(state: GameState, assets: Assets) -> None:
    """Edge-triggered input (state transitions and the reset verb); per frame, not per tick."""
    if rl.is_key_pressed(rl.KeyboardKey.KEY_P):
        state.toggle_pause()
    if state.mode == Mode.PLAYING and rl.is_key_pressed(rl.KeyboardKey.KEY_R):
        if state.reset_take():                       # only if a take was actually banked
            rl.play_sound(assets.reset_sfx)          # preloaded at boot, not loaded here
    if state.mode == Mode.ROOM_SOLVED and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
        state.restart_room()


def main() -> None:
    rl.init_window(WINDOW_W, WINDOW_H, TITLE)
    rl.init_audio_device()
    rl.set_target_fps(TARGET_FPS)

    # Boot-time loads: room data and every asset come in once, before the loop.
    room = load_room()
    assets = Assets.load()
    state = GameState.new(room)
    accumulator = 0.0

    while not rl.window_should_close():
        handle_events(state, assets)

        was_solved = state.mode == Mode.ROOM_SOLVED
        accumulator += rl.get_frame_time()
        while accumulator >= DT:        # UPDATE: fixed, deterministic, no drawing
            update(state, DT)
            accumulator -= DT
        if state.mode == Mode.ROOM_SOLVED and not was_solved:
            rl.play_sound(assets.exit_sfx)   # fired on the transition, so it plays exactly once
        if state.caught:                     # the current take died this frame
            rl.play_sound(assets.reset_sfx)
            state.caught = False

        render(state, assets)           # RENDER: reads state, never mutates it

    assets.unload()
    rl.close_audio_device()
    rl.close_window()


if __name__ == "__main__":
    main()
