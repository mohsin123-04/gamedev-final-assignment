"""Engine constants for Afterimage.

Gameplay tuning (player speed and size, take limit, spawn, exit) moved to data/ at CP3
and is loaded via src/room.py. What remains here is engine-level and not per-room: the
fixed timestep and the window itself.
"""

# Simulation
DT = 1.0 / 60.0            # fixed timestep: the sim only ever advances in exact 1/60 s steps

# Window
WINDOW_W = 1280
WINDOW_H = 720
TITLE = "Afterimage"
TARGET_FPS = 60
