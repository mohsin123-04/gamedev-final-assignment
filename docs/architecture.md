# Afterimage: Architecture (Checkpoint 2)

**Student Name:** Mohsin
**Class:** CSCI 4160U Game Development
**Repository:** https://github.com/mohsin123-04/gamedev-final-assignment
**Title:** Afterimage

This document sets the architecture before the gameplay code exists, because the central
mechanic (afterimages that replay recorded input) is only possible if three properties are
structural from the first commit rather than retrofitted later: a **fixed timestep**, **no
hidden randomness**, and **input treated as a value, not a device read**. Everything below
exists to make those properties cheap to keep and expensive to accidentally break.

## 1. Entities as data

A `player` and an `afterimage` are **the same type**. They differ in exactly one field: where
this tick's input comes from. That is the whole mechanic, expressed as data.

```python
@dataclass
class Entity:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    w: int = 64
    h: int = 64
    on_ground: bool = False
    source: InputSource          # keyboard, or a recorded tape
    kind: EntityKind             # PLAYER | AFTERIMAGE  (affects rendering only)
    age: int = 0                 # ticks alive; drives the fade on old afterimages
    alive: bool = True           # a take that hit a hazard stops but is kept
```

- Every entity lives in **one collection**, `state.entities: list[Entity]`, and the loop
  iterates that list. There are no loose `player_x` / `player_y` variables anywhere. This is
  the CP2 rubric's requirement in its own words: *entities are data in a collection, not
  scattered variables.*
- Entities hold **no behaviour** beyond their data. The simulation is a function
  `step(entity, actions, room) -> None` applied uniformly to every entity in the list.
- An afterimage is created by taking the banked `Entity` shape and swapping its `source` from
  the keyboard to a `TapeSource` over its recorded `ActionSet`s. Nothing else changes: same
  starting position, same `step` code.
- Devices (plates, doors, hazards, the battery cube, spawn, exit) are likewise **data records**,
  not objects with logic. Their behaviour lives in systems, see §4.

This is the payoff of "entities as data": the code that moves the live player is byte-for-byte
the code that replays a ghost, so a tape can never diverge from what the player actually did.

## 2. Input as a value (the `ActionSet`)

No gameplay code ever asks the keyboard a question. Each tick produces one immutable value:

```python
@dataclass(frozen=True)
class ActionSet:
    left: bool = False
    right: bool = False
    jump: bool = False           # edge-triggered inside step(), via jump buffering
```

- `KeyboardSource.poll()` reads raylib **once per tick** and returns an `ActionSet`.
- `TapeSource.poll()` returns the next recorded `ActionSet` from its tape and advances.
- A **tape** is just `list[ActionSet]` (about 1 byte/tick, so a 60 s take is ~4 KB). Recording
  the live player is appending each tick's `ActionSet`; replaying is iterating the list.

Because `step()` only ever receives an `ActionSet`, a tape is a drop-in substitute for a human.
This is the single rule the rest of the architecture protects.

## 3. The fixed-timestep loop: a *visible* update/render split

The loop is the one place where real time enters the program, and it is deliberately the only
place. Simulation advances in exact `1/60 s` steps; rendering happens as often as the display
allows. The split is literal: two functions, never interleaved.

```python
DT = 1.0 / 60.0

def main():
    rl.init_window(1280, 720, TITLE)
    state = GameState.new()
    accumulator = 0.0

    while not rl.window_should_close():
        accumulator += rl.get_frame_time()
        while accumulator >= DT:        # UPDATE: fixed, deterministic, no drawing
            update(state, DT)
            accumulator -= DT

        render(state)                   # RENDER: reads state, never mutates it
```

- `update(state, dt)` **mutates** game state and must never call a drawing function or read
  wall-clock time. `dt` is always exactly `DT`.
- `render(state)` **only reads** state and draws. It must never mutate simulation state.
- A slow frame runs `update` extra times to catch up; it can never change *where* an afterimage
  lands, because the ghost's motion is a pure function of its tape and `DT`.

Enforcing the rule: `update` takes no raylib drawing handle; `render` receives state as
read-only by convention (and we can assert no entity positions changed across a render in debug
builds).

## 4. Rooms as data, devices via events

A room is loaded from `data/`, never hardcoded:

```
room := { tiles: grid, devices: [ {type, x, y, params...} ], spawn, exit, take_limit }
```

Device interaction is **decoupled through events** so neither side knows about the other:

- A plate publishes `PlateDown(id)` / `PlateUp(id)` when an entity's AABB overlaps it.
- A door subscribes to the plate id it is wired to and opens/closes on those events.
- A hazard publishes `Killed(entity)`; the sim marks that entity `alive = False` and stops
  polling its source, but keeps it in the world (a dead take still replays up to its death).

Events are drained once per `update` tick, so they too are deterministic. This keeps the device
roster open-ended for later acts (latched plates, moving platforms, the battery cube) without
touching the player code.

## 5. Explicit game states

A single enum drives a dispatch; there is no implicit "are we paused?" boolean soup.

```python
class Mode(Enum):
    PLAYING      # performing the current take; recording to the active tape
    PAUSED       # frozen; render dims, update is skipped
    ROOM_SOLVED  # an entity reached the exit; show take count vs par, wait for advance
    ROOM_FAILED  # take limit spent with no solution; offer full reset
```

- `update` and `render` both branch on `state.mode`. **Reset** (the core verb) is a transition
  *within* `PLAYING`: bank the current tape, spawn its afterimage, start a fresh live entity.
- Only `PLAYING` advances the simulation. `PAUSED` and the two end states freeze it, which keeps
  determinism trivially intact across pauses.

## 6. Module layout

A tag in brackets shows when each module lands; the `[CP2]` ones exist and run today.

```
src/
  main.py        [CP2]      fixed-timestep loop; owns update()/render() dispatch
  state.py       [CP2]      GameState, Mode enum, transitions (reset take, restart room)
  entities.py    [CP2]      Entity, EntityKind, step()  (the uniform simulation)
  input.py       [CP2]      ActionSet, KeyboardSource, TapeSource
  config.py      [CP2]      DT, window size, tuning (moves to data/ at CP3)
  physics.py     [Oct 26]   axis-separated AABB collision against the tile grid
  room.py        [CP3]      Room loader + device records
  events.py      [CP3+]     tiny publish/drain event bus
  ai.py          [CP4]      enemy: state machine + steering/pathfinding (see §7)
```

`ai.py` is a placeholder for now. Whatever the CP4 enemy becomes, it is just another `Entity`
whose `source` is an AI controller producing an `ActionSet` per tick, so it rides the same
uniform `step()` and the same fixed-timestep loop as the player and afterimages, and requires
**no change** to §1-§5. This is why the slot can stay open without blocking CP2.

Dependencies point one way: `main -> state -> {entities, room, events}`, with `input` and
`physics` as leaf helpers. No module imports `main`.

## 7. Scope lock

The design in `docs/gdd.md` is **locked** for the remainder of the project, with one open item:

- **Open (CP4):** the enemy that CP4 (Nov 2) requires (a state machine plus steering or
  pathfinding) is **not yet designed**, because the GDD as written has no enemies. To be
  resolved before the Oct 26 studio. The architecture already accommodates it (see `ai.py`
  above): an enemy is just an `Entity` with an AI input source, so deciding it later costs
  nothing structurally.
- **Locked:** the title (**Afterimage**), the single-verb design (no new abilities), the
  reset-and-record loop, input-tape afterimages, the three-act progression, and the determinism
  constraints above. Features not in the GDD (networking, procedural rooms, a level editor
  shipped to players) are **out of scope** for this submission and will be recorded as "future
  work" in the postmortem instead.

## Checkpoint 2 coverage

| CP2 requirement | Where it lives |
|---|---|
| Entities as data | §1 `Entity`, §4 device records |
| Explicit game states | §5 `Mode` enum + dispatch |
| Visible update/render split | §3 fixed-timestep loop, two functions |
| Scope locked | §7 |
