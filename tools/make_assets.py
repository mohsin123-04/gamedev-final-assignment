"""Generate Afterimage's self-made assets (texture + sound effects) into assets/.

Run from the repo root:  python tools/make_assets.py

Everything here is produced from scratch (PIL for the sprite, the stdlib `wave`
module for the audio), so the files in assets/ are original work. This script is
kept in the repo so those assets are fully reproducible and the "made by me"
claim in ATTRIBUTION.md is verifiable, not just asserted.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SAMPLE_RATE = 44_100


# ---------------------------------------------------------------- texture ---

def make_player_png(path: Path, size: int = 48) -> None:
    """A light, roughly-white avatar so raylib's per-draw tint colours it.

    The body is near-white (tints to a clean colour), the inner core is grey
    (tints darker, reading as depth), and the background is transparent. The
    same file is drawn red for the live player and blue for an afterimage,
    purely by changing the tint at draw time.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([3, 3, size - 4, size - 4], radius=10,
                        fill=(236, 236, 246, 255), outline=(255, 255, 255, 255), width=2)
    d.rounded_rectangle([14, 14, size - 15, size - 15], radius=6, fill=(150, 150, 172, 255))
    d.ellipse([16, 16, 25, 25], fill=(255, 255, 255, 235))   # highlight, upper-left
    img.save(path)


# ---------------------------------------------------------------- audio ---

def _write_wav(path: Path, samples: list[float]) -> None:
    """Write mono 16-bit PCM. Samples are floats in [-1, 1]; clipped on the way out."""
    frames = bytearray()
    for s in samples:
        v = int(max(-1.0, min(1.0, s)) * 32767)
        frames += struct.pack("<h", v)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(bytes(frames))


def _tone(freq: float, dur: float, decay: float = 6.0, amp: float = 0.6) -> list[float]:
    """One decaying sine tone."""
    n = int(SAMPLE_RATE * dur)
    return [amp * math.exp(-decay * i / n) * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
            for i in range(n)]


def make_reset_wav(path: Path) -> None:
    """A short downward blip for banking a take (the R verb)."""
    dur, n = 0.18, int(SAMPLE_RATE * 0.18)
    out = []
    for i in range(n):
        t = i / n
        freq = 620.0 - 380.0 * t                     # sweep 620 -> 240 Hz
        env = math.exp(-5.0 * t)
        out.append(0.5 * env * math.sin(2 * math.pi * freq * (i / SAMPLE_RATE)))
    _write_wav(path, out)


def make_exit_wav(path: Path) -> None:
    """A two-note rising chime for solving the room (C5 -> G5)."""
    out = _tone(523.25, 0.12, decay=5.0)             # C5
    out += _tone(783.99, 0.26, decay=4.0)            # G5
    _write_wav(path, out)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    make_player_png(ASSETS / "player.png")
    make_reset_wav(ASSETS / "reset.wav")
    make_exit_wav(ASSETS / "exit.wav")
    print(f"wrote player.png, reset.wav, exit.wav to {ASSETS}")


if __name__ == "__main__":
    main()
