# AFTERIMAGE - Game Design Document

**Student Name:** Mohsin
**Student ID:** _(fill in)_
**Date:** 2026-09-23
**Class:** CSCI 4160U Game Development
**Repository Link:** https://github.com/mohsin123-04/gamedev-final-assignment

## Description

**Description:**

AFTERIMAGE is a single-player 2D puzzle-platformer about being the only worker in a facility
that was built for a crew. Every room needs more hands than one person has: a door that only
stays open while something heavy rests on a plate, a ledge with no way up, a gap that has to be
crossed while a gate is held.

The answer is always the same one. You perform a run, then reset the room. Your run comes back
as an *afterimage* - a translucent copy of you that repeats exactly what you did, input for
input, frame for frame. It stands on the plate you stood on. It is solid enough to stand on
yourself. Solve the room by layering takes until enough of you exist at once to get one of you
to the exit.

The player never gets a new ability. What changes across the game is what a room asks of the
arrangement, and how few takes it can be done in.

## Core Gameplay Loop

**The Gameplay Loop:**

1. **Enter a room** and read it: where is the exit, what is holding the door shut, what is out
   of reach.
2. **Plan a division of labour** - decide what this take is for. Usually one job: hold a plate,
   be a step, carry the cube partway.
3. **Perform the take.** Ordinary platforming, with the whole room live around you.
4. **Reset** (one key). The take is banked and immediately replays as an afterimage while you
   start the next one alongside it.
5. **Repeat** until the arrangement is complete and one of you can reach the exit.
6. **Leave**, with a take count recorded against the room's par - then the next room asks for
   something the last one taught you.

The loop is deliberately short and restart-cheap: a reset is instant and is the *core verb*,
not a punishment. Failure and progress use the same button.

**Primary Mechanics:**

- **Run and jump** on a tile grid - responsive platforming with coyote time and jump buffering,
  because the whole game is retrying and the movement must never be the reason a take failed.
- **Reset-and-record.** Every take is recorded as a tape of inputs. Resetting the room banks the
  current take and starts a new one; all banked takes replay from the same starting frame.
- **Afterimages are physical.** A replaying take is a real body in the world: it triggers
  plates, blocks a hazard, and is a solid platform you can stand on.

**Secondary Mechanics:**

- **Pressure plates and doors** - the main consumer of a take. Held plates (open only while
  weighted) versus latched plates (stay open once struck) change what a take is worth.
- **The take limit.** Each room allows a fixed number of afterimages. This is the puzzle
  constraint: not *can* you solve it, but can you solve it in four bodies.
- **Hazards** end the current take where they touch it. A take that died still counts and still
  replays up to the moment it died - a dead afterimage can be a deliberate, useful thing.
- **The battery cube** - a carryable object, so a take can move something rather than only be
  somewhere.

**Tertiary Mechanics:**

- **Obstruction.** Afterimages replay *inputs*, not positions. If you stand where a past self
  was going to walk, it is blocked, and everything it was going to do afterward happens in the
  wrong place. Wrecking your own plan by standing in the wrong spot is a real failure state and,
  later, a deliberate tool.
- **Age fade.** Older afterimages are drawn fainter, so the order of takes is readable at a
  glance.
- **Par and best-take counters** per room, for players who want to come back and do it in fewer.

## MDA Framework

**Mechanics:**

A fixed-timestep simulation over a tile grid with axis-separated AABB collision. Player intent
is captured as an action set per tick - never read from the keyboard inside the simulation - so
a "player" and an "afterimage" are the same entity type differing only in where their input
comes from: the keyboard, or a recorded tape. Rooms are data: a tile grid plus placed devices
(plates, doors, hazards, spawn, exit) and a take limit, loaded from files in `data/`. Device
state changes are published as events, so a door reacts to a plate without either knowing about
the other.

**Dynamics:**

Because takes are cumulative and fixed, play becomes *scheduling*. Players decompose a room into
roles, then decide an order - and discover that order matters, because take 3 can stand on take
1 but take 1 can never stand on take 3. Self-scaffolding emerges: a take whose entire purpose is
to crouch in a gap so a later take can cross it. The take limit turns "a solution" into "an
efficient solution" and produces the game's optimisation pressure. Obstruction produces its own
dynamic - the room is most dangerous when it is nearly solved, because a careless step ruins
four good takes at once.

**Aesthetics:**

Primarily **Challenge**, with **Discovery** doing the early work (each room is a small question
about what the mechanic can do) and **Expression** in the back half, where rooms admit several
orderings and a solution reads as the player's own. There is a quiet, unusual **Fellowship**:
the game manufactures the feeling of co-operative play with no second player in the building.
**Submission** carries the retry loop - resets are so cheap that play becomes rhythmic.

## Player Experience

**How should they feel? (Incorporate LeBlanc's Taxonomy of Pleasures):**

The target feeling is *competent conspiracy with yourself*. Early on the pleasure is
**Discovery** - the moment a player stops seeing the afterimage as a replay and realises it is
furniture they can stand on. In the middle game it is **Challenge**: rooms are short, failure is
instant, and the player is never more than fifteen seconds from trying a better plan.
**Expression** arrives when rooms stop having one answer and a player's solution starts to look
like a personality. Underneath all of it is the **Fellowship** already mentioned, which is the
feeling the game exists to produce: the warmth of a crew, assembled entirely out of one person
being patient with themselves. **Submission** describes the loop at its best - the reset key
gets pressed without thinking. **Abnegation**, **Sensation**, **Fantasy** and **Narrative** are
deliberately minor; this is a thinking game with a light institutional frame, not a spectacle.

The feeling the game must *avoid* is tedium: a nearly-solved room should never require perfectly
re-performing four earlier takes. This is why banked takes are permanent and only the current
take is ever at risk.

**Game Inspirations:**

- *The Misadventures of P.B. Winterbottom* and *Chronotron* - the direct ancestors of
  cooperate-with-your-recording puzzle design.
- *Braid* - time as a mechanic rather than a theme, and rooms as arguments.
- *Portal* - room-as-test-chamber structure, and how far a dry institutional voice carries a
  game with no story to speak of.
- *Celeste* - restart-cheap design and movement that is never the reason you failed.
- *Super Meat Boy* - specifically the end-of-level replay showing every attempt at once; this
  game turns that spectacle into the mechanic itself.

**Non-Game Inspirations:**

- **Multitrack recording.** One musician layering a rhythm part, then a bass line, then a
  melody, building an ensemble alone in a room. The core loop is a tape machine with punch-in,
  and the vocabulary - *take*, *track*, *overdub* - is borrowed on purpose.
- **Theatre blocking and rehearsal** - staging bodies in a space so that the right thing is in
  the right place at the right beat.
- **Stop-motion animation**, where a performance is assembled from many separate, patient,
  unglamorous passes.

**Genre:**

Single-player 2D puzzle-platformer, room-based, in the sub-genre variously called time-cooperation
or recording-puzzle games. Puzzle-first: the platforming is the language, not the test.

**Target Audience (Incorporate Bartle's Taxonomy):**

Players who enjoy short, dense, retry-friendly puzzle games - the *Baba Is You* / *Portal* /
*Braid* audience - and students and developers curious about the mechanic itself. Age is not a
gate; patience is.

Bartle's taxonomy was written for multi-user worlds, so it maps onto a single-player game only
by analogy, and the analogy is the honest way to use it:

- **Explorers** are the core audience. The rooms are a space of *mechanical* possibility rather
  than geography, and the game's best moments are the ones where a player finds a use for an
  afterimage the designer did not sign-post.
- **Achievers** are served by par take-counts, a best-take record per room, and completion of the
  optional hard rooms - a visible ladder that is about efficiency rather than accumulation.
- **Socializers** are served indirectly. Solutions are short and visual, so they are eminently
  shareable; the intended social life of the game is people showing each other three-take
  solutions to a five-take room.
- **Killers** in Bartle's sense - players acting on other players - have no target here. The
  nearest honest equivalent is competitive optimisation against other people's take counts, and
  the design does not pursue it further than the leaderboard-shaped par system.

**Progression Over Time:**

Progression is by **understanding**, not by unlocked abilities or upgraded stats: the player's
verb set on the last room is identical to the first. What escalates is what a room asks.

- **Act 1 - Teaching.** One device per room. A plate that needs holding; an afterimage that has
  to be a step. Generous take limits. The act's job is the sentence "I can stand on myself."
- **Act 2 - Pressure.** Hazards and latched plates. Take limits tighten to the point where a
  take must do two jobs, which forces planning before performing rather than during.
- **Act 3 - Interference.** Obstruction becomes the subject: rooms where the solution requires
  deliberately blocking a past self, and where order of takes is the whole puzzle. Moving
  platforms and the battery cube appear so the world is no longer static between takes.
- **Optional - Par rooms.** Post-completion challenges against strict take counts, for players
  who want to go back and be elegant.

**Themes:**

Self-reliance taken to an absurd conclusion - a facility built for a crew, staffed by one person
who compensates by becoming several. The mechanic carries the theme without dialogue: your past
selves are *fixed*, they cannot adapt to you, and every new plan must be built around decisions
you already made and can no longer change. Working around your own past mistakes is the
literal verb of the game. The institutional setting keeps it dry rather than melancholy: this is
about labour and competence, not grief.

**Platform & Tools:**

- **Platform:** Windows desktop, developed and tested on Windows 11. Nothing in the stack is
  platform-specific, so macOS and Linux builds are expected to work; keyboard only, 1280x720.
- **Language and framework:** Python 3.11 with **raylib** via the official `raylib` Python
  bindings (`pyray`) - the course's framework requirement, used for windowing, input, drawing
  and audio.
- **Content:** room layouts and tuning values as plain text/JSON in `data/`, loaded at runtime
  and reloadable without a rebuild.
- **Tooling:** git and GitHub for version control, VS Code, and an in-game debug overlay for
  frame timings and tape inspection.

**Anything else unusual that needs explaining (if applicable):**

**The game is only possible if the simulation is deterministic, and that constrains the
architecture from day one.** An afterimage is not a recording of positions - that would be
enormous and would not interact with anything. It is a recording of *inputs*: one small action
set per tick, replayed through the identical update code the live player uses. Replaying the
same inputs must therefore produce the same motion every time, which requires three rules that
are cheap to adopt now and nearly impossible to retrofit:

1. **A fixed timestep.** The simulation advances in exact 1/60 s steps and never uses wall-clock
   frame time, so a slow frame cannot change where an afterimage lands.
2. **No hidden randomness.** Gameplay contains no unseeded RNG; anything random is seeded from
   the room and the seed is stored with the tape.
3. **Input is a value, not a device read.** No gameplay code may ask the keyboard anything
   directly - it receives an action set, which is exactly what makes a tape substitutable for a
   player.

The cost is modest: a tape is roughly one byte per tick, so a sixty-second take is about 4 KB,
and holding a dozen of them in memory is free. The benefit beyond the mechanic itself is that
the game is trivially replayable and therefore trivially debuggable - a bug report can be a tape.
