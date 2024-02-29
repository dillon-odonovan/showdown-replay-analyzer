import dataclasses
from typing import List


@dataclasses.dataclass
class Move:
    name: str
    times_used: int = 0

    def increment_count(self) -> None:
        self.times_used += 1


@dataclasses.dataclass
class Pokemon:
    species: str
    nickname: str = None
    tera_type: str = None
    move1: Move = None
    move2: Move = None
    move3: Move = None
    move4: Move = None

    def add_move(self, move_name: str) -> None:
        if self.move4:
            raise RuntimeError('A Pokemon can only have a maximum of 4 moves')

        move = Move(name=move_name, times_used=1)

        if self.move3:
            self.move4 = move
        elif self.move2:
            self.move3 = move
        elif self.move1:
            self.move2 = move
        else:
            self.move1 = move

    def find_move(self, move_name: str) -> Move:
        try:
            return next(move
                        for move in [self.move1, self.move2, self.move3, self.move4]
                        if move.name == move_name.replace(' ', ''))
        except StopIteration:
            return None


@dataclasses.dataclass
class Team:
    pokemon: List[Pokemon]

    def add_pokemon(self, pokemon: Pokemon) -> None:
        if len(self.pokemon) == 6:
            raise RuntimeError('A Team can only have a maximum of 6 Pokemon')
        self.pokemon.append(pokemon)

    def find_by_nickname(self, nickname: str) -> Pokemon:
        try:
            return next(p for p in self.pokemon if p.nickname.split('-')[0] == nickname)
        except StopIteration:
            return None

    def find_by_species(self, species: str) -> Pokemon:
        try:
            return next(p for p in self.pokemon if p.species == species or p.species.split('-')[0] == species)
        except StopIteration:
            return None
