# CP5 — Balancing: Room 01

**Student:** Mohsin (100875639) · **Class:** CSCI 4160U Game Development

Three values in [`data/room01.json`](../data/room01.json) were retuned to shape the room's
difficulty. Nothing in the code changed — the values are data, loaded at boot by
[`src/room.py`](../src/room.py), so retuning never needs a recompile (the CP3 setup still holds).

## The shape I was tuning toward

Room 01 should be **flat and easy to move through, with one deliberate tension spike at the
sentry in the middle**. The difficulty should come from *routing past the sentry* — watching its
patrol and picking a moment to cross — not from running out of takes.

```
difficulty
   |              ___
   |             /   \        the sentry: time the crossing, or get chased
   |   _________/     \_________
   |  /                         \
   +------------------------------------> progress
     spawn        mid-room          exit
```

## What changed, and the evidence behind it

I measured the room with a small headless script,
[`tools/balance_check.py`](../tools/balance_check.py), that reuses the real sentry code
(`enemy.update_enemy`) against the room data, so these are numbers, not a feeling. Run it with
`.venv\Scripts\python tools\balance_check.py`.

| Value | Before | After | Why — from the numbers |
|---|---|---|---|
| `chase_speed` | 300 | **200** | Fleeing straight away at full speed, measured from the moment of detection: at **300** the sentry **catches you in 2.13 s** (the gap only closes — unevadable). At **200** you **escape in 4.65 s** and it gives up. Below `player_speed` (240), the chase is a threat you can beat, not an automatic catch. |
| `detect_radius` | 200 | **150** | Crossing the patrol line on row 7, checked across all 310 patrol phases: at **200**, **0 %** of timings get past unseen — there is no counterplay. At **150**, **16 %** of timings (50/310) get through — a window of about 0.8 s each patrol cycle, so a well-timed crossing is possible but not free. |
| `take_limit` | 4 | **3** | The puzzle needs **one afterimage at minimum** (one body holds plate `a` so another can take the open door to the exit). 4 left 3 spare takes; 3 leaves 2 — still room for a mistake, but takes now mean something. |

`player_speed` stayed at **240** — it's the reference the other values are balanced against.

## Why this is the shape, not just "easier"

- The sentry went from **impossible to escape** (caught every time) to **escapable with effort**
  (about 4.6 s of fleeing to shake it) — that is the tension spike being survivable, not removed.
- There was **no way to sneak past before** (seen on 100 % of timings); now there's a **real but
  narrow window**, which is the "route past it" skill the room is built around.
- Takes were tightened toward the true minimum so scarcity isn't the challenge — the sentry is.

The `chase_speed < player_speed` change also lines up the sentry with how
[`docs/cp4-ai.md`](cp4-ai.md) and the `enemy.py` comment always described it ("evadable"); the
old shipped value (300) had drifted above `player_speed` and contradicted that.
