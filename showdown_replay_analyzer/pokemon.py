import dataclasses
from typing import List


@dataclasses.dataclass
class Move:
    name: str
    times_used: int = 0


@dataclasses.dataclass
class Pokemon:
    species: str
    nickname: str
    tera_type: str
    move1: Move
    move2: Move
    move3: Move
    move4: Move


@dataclasses.dataclass
class Team:
    pokemon: List[Pokemon]
