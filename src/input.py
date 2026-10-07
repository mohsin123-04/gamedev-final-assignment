"""Input as a value: gameplay gets an ActionSet per tick, from the keyboard or a recorded tape."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pyray as rl


@dataclass(frozen=True)
class ActionSet:
    """One tick of intent. Immutable so a recorded tape can never be altered by replaying it."""
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False


class InputSource(Protocol):
    """Anything that can hand the simulation one ActionSet per tick."""
    def poll(self) -> ActionSet: ...


class KeyboardSource:
    """Reads the real keyboard. The only place in the game that touches live input."""

    def poll(self) -> ActionSet:
        return ActionSet(
            up=rl.is_key_down(rl.KeyboardKey.KEY_UP) or rl.is_key_down(rl.KeyboardKey.KEY_W),
            down=rl.is_key_down(rl.KeyboardKey.KEY_DOWN) or rl.is_key_down(rl.KeyboardKey.KEY_S),
            left=rl.is_key_down(rl.KeyboardKey.KEY_LEFT) or rl.is_key_down(rl.KeyboardKey.KEY_A),
            right=rl.is_key_down(rl.KeyboardKey.KEY_RIGHT) or rl.is_key_down(rl.KeyboardKey.KEY_D),
        )


class TapeSource:
    """Replays a tape of ActionSets, one per tick. Past the end of the tape it holds still."""

    def __init__(self, tape: list[ActionSet]):
        self.tape = tape
        self.i = 0

    def poll(self) -> ActionSet:
        if self.i < len(self.tape):
            a = self.tape[self.i]
            self.i += 1
            return a
        return ActionSet()  # tape finished: the afterimage stops where its take ended
