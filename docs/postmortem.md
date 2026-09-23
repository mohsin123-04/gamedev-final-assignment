# Postmortem

Written at the end, started now. Notes are added as things happen, while the reasons are
still fresh — a postmortem reconstructed in December from memory is worth less than one
kept as a log.

## What went right

_(to be filled in)_

## What went wrong

_(to be filled in)_

## What I would do differently

_(to be filled in)_

---

## Running log

**2026-09-23** — Concept locked: AFTERIMAGE, a recording/afterimage puzzle-platformer. Rejected
a straight platformer as too close to the Chapter 4 lab activity, and rejected several simpler
concepts (grid puzzle, dodge) for having too little to put in `data/` and no room to grow to
December. The determinism requirement — fixed timestep, no unseeded RNG, input as a value — is
a design constraint from day one rather than something to retrofit; if that turns out to be
wrong, this is the entry to revisit.

**2026-09-23** — Repository set up to the required shape. Python + raylib (`pyray`) chosen over
the course's default Odin + raylib: the framework requirement is satisfied either way, and I am
faster in Python. Toolchain verified by running a movement spike. Game concept not yet locked.
