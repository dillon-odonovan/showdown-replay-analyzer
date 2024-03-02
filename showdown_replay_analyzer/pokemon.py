"""Core representation of Pokemon and related classes
"""

import dataclasses
from typing import List


@dataclasses.dataclass
class Move:
    """A Pokemon Move and how many times it was used

    Attributes:
        name: The name of the move
        times_used: The number of times the move has been used in battle
    """
    name: str
    times_used: int = 0

    def increment_count(self) -> None:
        """Increment the number of times this move was used."""
        self.times_used += 1


@dataclasses.dataclass
class Pokemon:
    """

    Attributes:
        species: The species of the Pokemon
        nickname: The nickname of the Pokemon
        tera_type: The Tera type of the Pokemon
        move1: The first move of the Pokemon
        move2: The second move of the Pokemon
        move3: The third move of the Pokemon
        move4: The fourth move of the Pokemon
    """
    species: str
    nickname: str = None
    tera_type: str = None
    move1: Move = None
    move2: Move = None
    move3: Move = None
    move4: Move = None

    def add_move(self, move_name: str) -> None:
        """Adds a new move to this Pokemon.

        Arguments:
            move_name: The name of the move

        Raises:
            RuntimeError: If this Pokemon already has 4 moves.
        """
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
        """Finds a move by name.

        Arguments:
            move_name: The name of the move

        Returns:
            The move with the given name or None if no move with that name exists.
        """
        try:
            return next(move
                        for move in [self.move1, self.move2, self.move3, self.move4]
                        if move.name == move_name.replace(' ', ''))
        except StopIteration:
            return None


@dataclasses.dataclass
class Team:
    """A collection of Pokemon

    Attributes:
        pokemon: A list of Pokemon in this Team.
    """
    pokemon: List[Pokemon]

    def add_pokemon(self, pokemon: Pokemon) -> None:
        """Adds a Pokemon to this Team.

        Arguments:
            pokemon: The Pokemon to add to this Team.

        Raises:
            RuntimeError: If this Team already has 6 Pokemon.
        """
        if len(self.pokemon) == 6:
            raise RuntimeError('A Team can only have a maximum of 6 Pokemon')
        self.pokemon.append(pokemon)

    def find_by_nickname(self, nickname: str) -> Pokemon:
        """Finds a Pokemon by nickname.

        Arguments:
            nickname: The nickname of the Pokemon to find.

        Returns:
            The Pokemon with the given nickname or None if no Pokemon with that nickname exists.
        """
        try:
            return next(p for p in self.pokemon if p.nickname.split('-')[0] == nickname)
        except StopIteration:
            return None

    def find_by_species(self, species: str) -> Pokemon:
        """Finds a Pokemon by species.

        Arguments:
            species: The species of the Pokemon to find.

        Returns:
            The Pokemon with the given species or None if no Pokemon with that species exists.
        """
        try:
            return next(p
                        for p in self.pokemon
                        if p.species == species or p.species.split('-')[0] == species)
        except StopIteration:
            return None
