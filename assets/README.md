# assets/

Runtime assets (art, sound, fonts). Every asset here is loaded **once at boot** by
`src/assets.py` (`Assets.load()`), before the game loop starts — never at the moment it is
first used. Every file is listed in `../ATTRIBUTION.md`.

| File | Type | Loaded at boot as | Used for |
|---|---|---|---|
| `player.png` | texture (48×48 RGBA) | `Texture2D` | drawn for the live player (red tint) and every afterimage (blue tint) |
| `reset.wav` | sound | `Sound` | played when a take is banked (`R`) |
| `exit.wav` | sound | `Sound` | played when a body reaches the exit |

All three are my own work, generated from scratch by `../tools/make_assets.py`
(PIL for the sprite, the stdlib `wave` module for the audio). Run that script to regenerate them.
