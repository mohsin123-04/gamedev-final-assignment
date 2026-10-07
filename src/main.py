"""Afterimage entry point: the fixed-timestep loop and the update/render split (controls in README)."""
import pyray as rl

from config import DT, TARGET_FPS, TITLE, WINDOW_H, WINDOW_W
from entities import EntityKind, step
from state import EXIT_X, TAKE_LIMIT, GameState, Mode


# ---------------------------------------------------------------- update (logic only) ---

def update(state: GameState, dt: float) -> None:
    """Advance the simulation one fixed tick. Mutates state; never draws; never reads time."""
    if state.mode != Mode.PLAYING:
        return

    for e in state.entities:
        a = e.source.poll()
        step(e, a, dt)
        if e.kind == EntityKind.PLAYER:
            state.current_tape.append(a)  # record the live player's intent, one ActionSet/tick

    if state.player.x + state.player.w >= EXIT_X:
        state.solve()


# ---------------------------------------------------------------- render (draw only) ---

def render(state: GameState) -> None:
    """Draw the current state. Reads only; never mutates the simulation."""
    rl.begin_drawing()
    rl.clear_background(rl.Color(18, 18, 24, 255))

    # the exit
    rl.draw_rectangle(EXIT_X, 0, WINDOW_W - EXIT_X, WINDOW_H, rl.Color(30, 50, 40, 255))
    rl.draw_line(EXIT_X, 0, EXIT_X, WINDOW_H, rl.Color(80, 200, 120, 255))

    ghost_count = max(len(state.entities) - 1, 1)
    for i, e in enumerate(state.entities):
        if e.kind == EntityKind.AFTERIMAGE:
            alpha = int(70 + 110 * (i + 1) / ghost_count)   # older ghosts (lower i) are fainter
            color = rl.Color(120, 200, 255, min(alpha, 190))
        else:
            color = rl.Color(235, 70, 70, 255)
        rl.draw_rectangle(int(e.x), int(e.y), e.w, e.h, color)

    _draw_hud(state)
    if state.mode == Mode.PAUSED:
        _draw_banner("PAUSED", "P to resume")
    elif state.mode == Mode.ROOM_SOLVED:
        _draw_banner("ROOM SOLVED", "Enter to run it again")

    rl.end_drawing()


def _draw_hud(state: GameState) -> None:
    rl.draw_text(f"MODE: {state.mode.name}", 16, 14, 24, rl.RAYWHITE)
    rl.draw_text(f"TAKES: {state.takes_used} / {TAKE_LIMIT}", 16, 44, 24, rl.RAYWHITE)
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

def handle_events(state: GameState) -> None:
    """Edge-triggered input (state transitions and the reset verb); per frame, not per tick."""
    if rl.is_key_pressed(rl.KeyboardKey.KEY_P):
        state.toggle_pause()
    if state.mode == Mode.PLAYING and rl.is_key_pressed(rl.KeyboardKey.KEY_R):
        state.reset_take()
    if state.mode == Mode.ROOM_SOLVED and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
        state.restart_room()


def main() -> None:
    rl.init_window(WINDOW_W, WINDOW_H, TITLE)
    rl.set_target_fps(TARGET_FPS)

    state = GameState.new()
    accumulator = 0.0

    while not rl.window_should_close():
        handle_events(state)

        accumulator += rl.get_frame_time()
        while accumulator >= DT:        # UPDATE: fixed, deterministic, no drawing
            update(state, DT)
            accumulator -= DT

        render(state)                   # RENDER: reads state, never mutates it

    rl.close_window()


if __name__ == "__main__":
    main()
