# CP4 — Enemy AI: the Sentry

**Student:** Mohsin (100875639) · **Class:** CSCI 4160U Game Development

Afterimage is a puzzle-platformer with no combat, so its one enemy is designed to fit the
fiction and feed the existing mechanic rather than to be a threat bolted on top. The facility
"built for a crew" is patrolled by a **sentry**: a security drone that walks a fixed route and
moves to intercept anyone it sees. Everything below is implemented in
[`src/enemy.py`](../src/enemy.py), tuned from [`data/room01.json`](../data/room01.json), and
wired into the simulation in [`src/state.py`](../src/state.py) and [`src/main.py`](../src/main.py).

## 1. State machine (the *behaviour*)

Two states, `EnemyState.PATROL` and `EnemyState.CHASE` (`src/enemy.py`), with two named
transitions. The current state is drawn on screen above the sentry during play, and the
detection ring changes colour with it, so both the states and the transitions are visible in
the demo.

```
                 spots a body
        (a body enters detect_radius)
   ┌───────────────────────────────────────┐
   │                                        ▼
┌────────┐                              ┌────────┐
│ PATROL │                              │ CHASE  │
│ walk   │                              │ seek   │
│ route  │ ◄─────────────────────────── │ body   │
└────────┘                              └────────┘
             loses the trail
   (nothing within lose_radius for
        give_up_ticks in a row)
```

- **PATROL → CHASE — "spots a body":** the live player comes within `detect_radius`. The sentry
  hunts the live player only — afterimages are faint echoes it can't see (see §3).
- **CHASE → PATROL — "loses the trail":** nothing is within the larger `lose_radius` for
  `give_up_ticks` consecutive ticks. `lose_radius > detect_radius` is deliberate hysteresis so
  the sentry doesn't flip-flop at the edge of its vision; the tick counter means a target has to
  stay gone, not just blink out for one frame.

## 2. Movement (the *how*)

A deliberate **hybrid**, one behaviour per state:

- **PATROL — scripted waypoints.** The sentry walks an authored list of points from the room
  data, looping. A patrol route is *level content* — the designer decides where the guard walks
  — so computing it at runtime would be solving a problem that doesn't exist.
- **CHASE — seek steering.** A single seek: step straight toward the target at `chase_speed`,
  clamped so it doesn't overshoot (`_seek` in `src/enemy.py`). `chase_speed` (200) is tuned
  **below** `player_speed` (240), so the chase is a pressure to be escaped, not a death sentence
  — which is also what makes "loses the trail" reachable: the player can open the gap. (Those
  values were set deliberately in the CP5 balancing pass — see [`cp5-balance.md`](cp5-balance.md).)

### Why not pathfinding / A\*

The rooms are small, single-screen and open — there is no maze to route through. A\* here would
be the textbook "impressive but unneeded" mistake: cost and complexity for a path that a
straight-line seek already produces. Seek + a scripted route is the honest fit for this
geometry. If a later room adds interior walls, the chase behaviour is the one place that would
change, and *then* a grid pathfinder would be justified — not before.

## 3. How it interacts with the player (through systems already built)

The sentry is not a moving wall. It plugs into two systems that already existed before CP4:

- **The take/reset system.** When the sentry's AABB overlaps the **live player**, the game calls
  the existing `GameState.reset_take()` — the current take dies, is banked, and immediately
  replays as an afterimage up to the moment of the catch. This is exactly the design the GDD
  already describes ("a take that died still counts and still replays up to the moment it died"),
  reached through code CP2/CP3 already shipped rather than anything new.
- **The entity/recording system.** The sentry chases the **live player only**; afterimages are
  echoes it can't see. An earlier version let it chase the *nearest body* of all of them so a ghost
  could decoy it — but because a ghost is never "caught," parking one beside the sentry pinned it in
  CHASE forever and left the live player free, so the adversary cancelled itself out. Hunting the
  live player keeps the sentry a constant threat; the catch still banks the take as an afterimage,
  so the enemy stays woven into the recording mechanic rather than sitting beside it.

## 4. Determinism

The sentry is a pure function of the simulation: it reads body positions and advances on the
fixed timestep, with no wall-clock and no RNG. It is rebuilt from its spec at the start of every
take (`_rebuild_entities` in `src/state.py`), so each take — and every afterimage replaying from
frame 0 — meets the same sentry starting from the same spot. This is required, not optional:
the whole game rests on replays being identical, and a nondeterministic chaser would break that.

## Demo checklist (for the lab session)

1. **PATROL:** sentry walks its route; label reads `PATROL`, ring is amber.
2. **Transition → CHASE:** walk into the ring; label flips to `CHASE`, ring turns red, a line
   snaps to the player — "spots a body".
3. **Movement:** it seeks you; run — because it's slower, you can pull away.
4. **Transition → PATROL:** open the gap and wait ~1.5 s; it gives up and returns to the route —
   "loses the trail".
5. **Interaction:** let it touch you; the take is banked as a dead afterimage (reset sound), and
   the run continues with that ghost in play — and the sentry ignores that ghost, staying locked on
   the live you, so the pressure never lets up.
