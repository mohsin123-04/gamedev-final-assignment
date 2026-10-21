"""Afterimage entry point: the fixed-timestep loop and the update/render split (controls in README)."""
from __future__ import annotations

import pyray as rl

from assets import Assets
from config import DT, TARGET_FPS, TITLE, WINDOW_H, WINDOW_W
from entities import EntityKind, step
from room import load_room
from state import GameState, Mode


# ---------------------------------------------------------------- update (logic only) ---

def update(state: GameState, dt: float) -> None:
    """Advance the simulation one fixed tick. Mutates state; never draws; never reads time."""
    if state.mode != Mode.PLAYING:
        return

    for e in state.entities:
        a = e.source.poll()
        step(e, a, dt, state.room.player_speed)   # speed is data-driven, from data/room01.json
        if e.kind == EntityKind.PLAYER:
            state.current_tape.append(a)  # record the live player's intent, one ActionSet/tick

    if state.player.x + state.player.w >= state.room.exit_x:
        state.solve()


# ---------------------------------------------------------------- render (draw only) ---

def render(state: GameState, assets: Assets) -> None:
    """Draw the current state. Reads only; never mutates the simulation."""
    rl.begin_drawing()
    rl.clear_background(rl.Color(18, 18, 24, 255))

    # the exit (position is data-driven: data/room01.json -> exit_x)
    exit_x = state.room.exit_x
    rl.draw_rectangle(exit_x, 0, WINDOW_W - exit_x, WINDOW_H, rl.Color(30, 50, 40, 255))
    rl.draw_line(exit_x, 0, exit_x, WINDOW_H, rl.Color(80, 200, 120, 255))

    ghost_count = max(len(state.entities) - 1, 1)
    for i, e in enumerate(state.entities):
        if e.kind == EntityKind.AFTERIMAGE:
            alpha = int(70 + 110 * (i + 1) / ghost_count)   # older ghosts (lower i) are fainter
            tint = rl.Color(120, 200, 255, min(alpha, 190))
        else:
            tint = rl.Color(235, 70, 70, 255)
        _draw_body(assets, e.x, e.y, e.w, e.h, tint)

    _draw_hud(state)
    if state.mode == Mode.PAUSED:
        _draw_banner("PAUSED", "P to resume")
    elif state.mode == Mode.ROOM_SOLVED:
        _draw_banner("ROOM SOLVED", "Enter to run it again")

    rl.end_drawing()


def _draw_body(assets: Assets, x: float, y: float, w: int, h: int, tint: rl.Color) -> None:
    """Draw the preloaded player texture scaled to the entity's data-driven size, in `tint`."""
    tex = assets.player_tex
    src = rl.Rectangle(0, 0, float(tex.width), float(tex.height))
    dst = rl.Rectangle(x, y, float(w), float(h))
    rl.draw_texture_pro(tex, src, dst, rl.Vector2(0, 0), 0.0, tint)


def _draw_hud(state: GameState) -> None:
    rl.draw_text(f"MODE: {state.mode.name}", 16, 14, 24, rl.RAYWHITE)
    rl.draw_text(f"TAKES: {state.takes_used} / {state.room.take_limit}", 16, 44, 24, rl.RAYWHITE)
    rl.draw_text(
        "move: arrows/WASD    R: reset take    P: pause    reach the green exit",
        16, WINDOW_H - 32, 20, rl.Color(170, 170, 180, 255),
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
        rl.play_sound(assets.reset_sfx)              # preloaded at boot, not loaded here
        state.reset_take()
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

        render(state, assets)           # RENDER: reads state, never mutates it

    assets.unload()
    rl.close_audio_device()
    rl.close_window()


if __name__ == "__main__":
    main()
