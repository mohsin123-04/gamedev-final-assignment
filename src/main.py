import math
import pyray as rl


def normalize0(x: float, y: float) -> tuple[float, float]:
    """Unit vector in the direction of (x, y); (0, 0) if the input is zero."""
    length = math.hypot(x, y)
    if length == 0:
        return 0.0, 0.0
    return x / length, y / length


def main():
    rl.init_window(1280, 720, "My Python + Raylib game")
    rl.set_target_fps(60)

    player_x, player_y = 0.0, 0.0
    speed = 400.0  # pixels per second

    while not rl.window_should_close():
        input_x, input_y = 0.0, 0.0
        if rl.is_key_down(rl.KeyboardKey.KEY_UP):
            input_y -= 1
        if rl.is_key_down(rl.KeyboardKey.KEY_DOWN):
            input_y += 1
        if rl.is_key_down(rl.KeyboardKey.KEY_LEFT):
            input_x -= 1
        if rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):
            input_x += 1

        # normalized direction * speed * delta time -> frame-rate independent
        dir_x, dir_y = normalize0(input_x, input_y)
        dt = rl.get_frame_time()
        player_x += dir_x * speed * dt
        player_y += dir_y * speed * dt

        rl.begin_drawing()
        rl.clear_background(rl.Color(160, 200, 255, 255))
        rl.draw_rectangle(int(player_x), int(player_y), 64, 64, rl.RED)
        rl.end_drawing()

    rl.close_window()


if __name__ == "__main__":
    main()
