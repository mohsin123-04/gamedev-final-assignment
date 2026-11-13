# assets/

Runtime assets (art, sound, fonts). Everything here is loaded once at boot by `src/assets.py`
(`Assets.load()`) before the game loop starts, not the first time it's used. Every file is also
listed in `../ATTRIBUTION.md`.

| File | Type | Loaded at boot as | Used for |
|---|---|---|---|
| `player.png` | texture (48×48 RGBA) | `Texture2D` | the live player (red tint) and every afterimage (blue tint) |
| `reset.wav` | sound | `Sound` | plays when a take is banked (`R`) |
| `exit.wav` | sound | `Sound` | plays when a body reaches the exit |

I made all three myself with `../tools/make_assets.py` (PIL for the sprite, Python's `wave`
module for the sounds). Run that script to regenerate them.
