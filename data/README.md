# data/

Tuning and level values, loaded at runtime rather than hardcoded. Loaded once at boot by
`src/room.py` (`load_room`) and handed to the game as a `Room`.

## `room01.json`

Three of these values visibly change the game when you edit the file and relaunch — no code
change needed:

| Key | What it does | Try it |
|---|---|---|
| `player_speed` | Pixels/second every body (the live player **and** every afterimage) moves at. | Set it to `800` and everyone moves twice as fast; `200` and half as fast. |
| `take_limit` | Afterimages allowed before the room resets itself. Shown in the HUD as `TAKES: n / limit`. | Set it to `2` and the room restarts after two resets instead of four. |
| `exit_x` | X position of the green exit wall; cross it to solve the room. | Lower it (e.g. `400`) and the exit sits much closer to the spawn. |

The remaining keys (`player_size`, `spawn_x`, `spawn_y`) set the body size and start position
and are data-driven too.

Measured effect of each value (ticks for the player to run straight to the exit):

```
player_speed  200 -> 305 ticks     400 -> 153     800 -> 77
exit_x        300 ->  27 ticks      700 ->  87    1140 -> 153
take_limit      2 -> restarts after 2 banked takes    4 -> after 4    6 -> after 6
```
