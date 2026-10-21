"""Explicit game states (Mode enum) and GameState, which owns the entity collection and tapes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from entities import Entity, EntityKind
from input import ActionSet, KeyboardSource, TapeSource
from room import Room


class Mode(Enum):
    PLAYING = auto()             # performing the current take; recording to current_tape
    PAUSED = auto()              # frozen; the simulation does not advance
    ROOM_SOLVED = auto()         # a body reached the exit; waiting to run the room again


@dataclass
class GameState:
    mode: Mode
    room: Room                          # loaded from data/; supplies spawn, size, speed, limits
    entities: list[Entity]              # THE collection: every player and afterimage
    tapes: list[list[ActionSet]]        # banked takes, each replayed as one afterimage
    current_tape: list[ActionSet]       # the take being recorded by the live player right now

    @classmethod
    def new(cls, room: Room) -> "GameState":
        gs = cls(mode=Mode.PLAYING, room=room, entities=[], tapes=[], current_tape=[])
        gs._rebuild_entities()
        return gs

    @property
    def player(self) -> Entity:
        """The live, keyboard-driven body. Always the last entity in the collection."""
        return self.entities[-1]

    @property
    def takes_used(self) -> int:
        return len(self.tapes)

    def _spawn(self, source) -> Entity:
        """A body at the room's data-driven spawn, sized from the room data."""
        return Entity(
            x=self.room.spawn_x, y=self.room.spawn_y,
            source=source, kind=EntityKind.PLAYER if isinstance(source, KeyboardSource) else EntityKind.AFTERIMAGE,
            w=self.room.player_size, h=self.room.player_size,
        )

    # --- transitions: the only code that mutates mode or the collection ---

    def _rebuild_entities(self) -> None:
        """Rebuild the collection: one afterimage per banked tape (replaying from frame 0) plus a fresh player."""
        self.entities = [self._spawn(TapeSource(list(tape))) for tape in self.tapes]
        self.entities.append(self._spawn(KeyboardSource()))
        self.current_tape = []

    def reset_take(self) -> None:
        """The core verb: bank the current take and start a new one alongside its afterimage."""
        self.tapes.append(self.current_tape)
        if self.takes_used >= self.room.take_limit:
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
