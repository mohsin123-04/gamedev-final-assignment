"""Explicit game states (Mode enum) and GameState, which owns the entity collection and tapes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from config import PLAYER_SIZE, WINDOW_H, WINDOW_W
from entities import Entity, EntityKind
from input import ActionSet, KeyboardSource, TapeSource

SPAWN_X = 80.0
SPAWN_Y = WINDOW_H / 2 - PLAYER_SIZE / 2
EXIT_X = WINDOW_W - 140          # crossing this x solves the room
TAKE_LIMIT = 4                   # afterimages allowed before the room resets itself


class Mode(Enum):
    PLAYING = auto()             # performing the current take; recording to current_tape
    PAUSED = auto()              # frozen; the simulation does not advance
    ROOM_SOLVED = auto()         # a body reached the exit; waiting to run the room again


@dataclass
class GameState:
    mode: Mode
    entities: list[Entity]              # THE collection: every player and afterimage
    tapes: list[list[ActionSet]]        # banked takes, each replayed as one afterimage
    current_tape: list[ActionSet]       # the take being recorded by the live player right now

    @classmethod
    def new(cls) -> "GameState":
        gs = cls(mode=Mode.PLAYING, entities=[], tapes=[], current_tape=[])
        gs._rebuild_entities()
        return gs

    @property
    def player(self) -> Entity:
        """The live, keyboard-driven body. Always the last entity in the collection."""
        return self.entities[-1]

    @property
    def takes_used(self) -> int:
        return len(self.tapes)

    # --- transitions: the only code that mutates mode or the collection ---

    def _rebuild_entities(self) -> None:
        """Rebuild the collection: one afterimage per banked tape (replaying from frame 0) plus a fresh player."""
        self.entities = [
            Entity(SPAWN_X, SPAWN_Y, source=TapeSource(list(tape)), kind=EntityKind.AFTERIMAGE)
            for tape in self.tapes
        ]
        self.entities.append(
            Entity(SPAWN_X, SPAWN_Y, source=KeyboardSource(), kind=EntityKind.PLAYER)
        )
        self.current_tape = []

    def reset_take(self) -> None:
        """The core verb: bank the current take and start a new one alongside its afterimage."""
        self.tapes.append(self.current_tape)
        if self.takes_used >= TAKE_LIMIT:
            self.restart_room()
        else:
            self._rebuild_entities()

    def restart_room(self) -> None:
        """Clear every take and start the room over."""
        self.tapes = []
        self.mode = Mode.PLAYING
        self._rebuild_entities()

    def toggle_pause(self) -> None:
        if self.mode == Mode.PLAYING:
            self.mode = Mode.PAUSED
        elif self.mode == Mode.PAUSED:
            self.mode = Mode.PLAYING

    def solve(self) -> None:
        self.mode = Mode.ROOM_SOLVED
