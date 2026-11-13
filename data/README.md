# data/

Tuning and level values that get loaded at runtime instead of being hardcoded. `src/room.py`
(`load_room`) reads them once at boot and hands back a `Room`.

## `room01.json`

A room is a tile grid (the level layout) plus some tuning numbers. Both are data, so you can edit
the file, run the game again, and see it change without touching any code.

### Three numbers you can change to see the behaviour change

| Key | What it does | Try it |
|---|---|---|
| `player_speed` | How fast every body moves, in pixels per second (the live player and all the afterimages). At 240 that works out to 4.0 px per tick. | Set it to `480` and everything moves twice as fast; `120` and it's half speed. |
| `take_limit` | How many afterimages you get before the room resets. The HUD shows it as `TAKES: n / limit`. | Set it to `2` and the room restarts after two resets instead of four. |
| `enemy.detect_radius` | How close a body has to get before the sentry notices it and starts chasing. It's inside the `enemy` block. | Bump it to `400` and the sentry sees you from way across the room; drop it to `80` and you can sneak past. |

The other top-level keys are data too: `tile_size` (pixels per grid cell), `player_size` (the
body's hitbox), and `latched` (which plates stay down once you step on them).

### The level is the grid

`grid` is a list of strings that all have to be the same length. Each character is one tile. This
is what replaced the old `exit_x` number from CP3 — the exit, the walls and the hazards are all
just positions in the grid now, so editing the map counts as a data change on its own.

```
#  wall (solid)        .  or space  floor
S  spawn (one)         E  exit  (reach any to solve)
^  hazard (ends a take)
a-z  pressure plate    A-Z  door, opened by the plate with the same letter
```

Plates and doors match up by letter, so plate `a` opens door `A`. Move the `E` tiles, knock out a
`#` to open a path, or shift the `^` hazards, then run the game again and the room is different.

### `enemy` (CP4)

An optional block that drops one sentry into the room. Leave it out and there's no enemy. Its
settings live in the data file for the same reason everything else does: the AI is tuned here, not
in code. There's more on how it works in [`docs/cp4-ai.md`](../docs/cp4-ai.md).

| Key | What it does |
|---|---|
| `spawn_x`, `spawn_y`, `size` | Where the sentry starts and how big its hitbox is. |
| `patrol_speed` | Speed along its waypoint route while patrolling. |
| `chase_speed` | Speed while chasing a body. If it's below `player_speed` you can outrun it; above it (300 vs 240 as shipped) you can't, which is on purpose here. |
| `detect_radius` | A body this close switches the sentry from patrol to chase. |
| `lose_radius` | It only gives up and goes back to patrol once everything is past this bigger radius. The gap between the two radii stops it flickering between states. |
| `give_up_ticks` | How many ticks in a row with nothing inside `lose_radius` before it goes back to patrolling (90 ticks is 1.5 seconds at 60 fps). |
| `waypoints` | The patrol route, a list of `[x, y]` points it walks in order and loops. |

### Numbers, for reference

```
player_speed   120 -> 2.0 px/tick     240 -> 4.0 px/tick     480 -> 8.0 px/tick
take_limit       2 -> restarts after 2 takes     4 -> after 4
detect_radius  a body inside this radius switches the sentry from patrol to chase
```
