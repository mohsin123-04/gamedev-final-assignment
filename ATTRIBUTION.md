# Attribution

Everything in this project that did not originate with me, kept current as the work happens
rather than reconstructed at the end.

## AI use

**Claude Code (Anthropic)** wrote or edited these files:

- `src/config.py` — engine constants (window, timestep); gameplay tuning removed when it moved to data/.
- `src/input.py` — `ActionSet` plus the keyboard and tape input sources.
- `src/entities.py` — the `Entity` data type and the shared `step()` simulation (speed is now passed in from data).
- `src/state.py` — the `Mode` state machine and `GameState`; spawn, size and take limit now read from the loaded room.
- `src/room.py` — the room data loader (`Room` + `load_room`) that reads `data/room01.json` at boot.
- `src/assets.py` — the boot-time asset loader (texture + sounds loaded once, before the loop).
- `src/main.py` — the fixed-timestep loop, update/render split, texture drawing and sound playback.
- `tools/make_assets.py` — the generator script that produces the self-made assets below.
- `docs/architecture.md` — the Checkpoint 2 architecture write-up.
- `docs/gdd.md` — drafted from my design notes.
- `README.md`, `data/README.md`, `assets/README.md`, `docs/postmortem.md`, this file — documentation.

Written unaided: the choice of genre and twist, and the decision to reject a
lab-activity-derived design.

## Third-party assets

None. Every asset in `assets/` is my own work, generated from scratch by
`tools/make_assets.py` (no third-party art, sound, font or music is used):

- `assets/player.png` — 48×48 player/afterimage sprite, drawn with PIL. A light,
  near-white avatar so the game can tint it (red for the live player, blue for afterimages).
- `assets/reset.wav` — short blip played when a take is banked, synthesised with the Python
  stdlib `wave` module.
- `assets/exit.wav` — two-note chime played when the room is solved, likewise synthesised.

Re-running `python tools/make_assets.py` regenerates all three byte-for-byte, so the
"made by me" claim is reproducible rather than merely asserted.
