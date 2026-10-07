# Attribution

Everything in this project that did not originate with me, kept current as the work happens
rather than reconstructed at the end.

## AI use

**Claude Code (Anthropic)** wrote or edited these files:

- `src/config.py` — tuning constants (window size, timestep, player speed).
- `src/input.py` — `ActionSet` plus the keyboard and tape input sources.
- `src/entities.py` — the `Entity` data type and the shared `step()` simulation.
- `src/state.py` — the `Mode` state machine and `GameState` (entity collection, tapes, transitions).
- `src/main.py` — the fixed-timestep loop and the update/render split.
- `docs/architecture.md` — the Checkpoint 2 architecture write-up.
- `docs/gdd.md` — drafted from my design notes.
- `README.md`, `docs/postmortem.md`, this file — repository structure and documentation.

Written unaided: the choice of genre and twist, and the decision to reject a
lab-activity-derived design.

## Third-party assets

None yet. Every sprite, sound, font and music track added to `assets/` will be listed here
with its source and licence. Assets I make myself will say so.
