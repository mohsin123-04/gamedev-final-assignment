"""Assets, loaded once at boot — not at the moment of first use.

`Assets.load()` is called a single time in main(), right after the window and audio
device come up and before the game loop starts. Every texture and sound the game needs
is pulled off disk and onto the GPU / into the mixer there, so no frame ever pays to
load an asset mid-play. `render()` and the event handlers just reference what is already
resident here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pyray as rl

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


@dataclass
class Assets:
    player_tex: rl.Texture2D     # drawn for the live player and every afterimage (tinted)
    reset_sfx: rl.Sound          # plays when a take is banked (R)
    exit_sfx: rl.Sound           # plays when a body reaches the exit

    @classmethod
    def load(cls) -> "Assets":
        """Load everything up front. Requires an initialised window + audio device."""
        player_tex = rl.load_texture(str(ASSETS_DIR / "player.png"))
        rl.set_texture_filter(player_tex, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
        return cls(
            player_tex=player_tex,
            reset_sfx=rl.load_sound(str(ASSETS_DIR / "reset.wav")),
            exit_sfx=rl.load_sound(str(ASSETS_DIR / "exit.wav")),
        )

    def unload(self) -> None:
        """Release GPU textures and sound buffers on shutdown."""
        rl.unload_texture(self.player_tex)
        rl.unload_sound(self.reset_sfx)
        rl.unload_sound(self.exit_sfx)
