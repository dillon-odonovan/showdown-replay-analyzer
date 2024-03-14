"""Core representation of Pokemon and related classes
"""

import dataclasses
import re
from typing import List


_CAPITAL_WORDS = re.compile(r'([a-z])([A-Z])')


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
        moves: The moves of the Pokemon
        was_brought: Whether this Pokemon was brought to battle
        was_lead: Whether this Pokemon was one of the lead Pokemon in battle
        was_terastallized: Whether this Pokemon was terastallized in battle
    """
    species: str
    nickname: str = None
    tera_type: str = None
    moves: List[Move] = dataclasses.field(default_factory=lambda: [])
    was_brought: bool = False
    was_lead: bool = False
    was_terastallized: bool = False
    _struggle: Move = dataclasses.field(
        default_factory=lambda: Move('Struggle')
    )

    def add_move(self, move_name: str) -> Move:
        """Adds a new move to this Pokemon.

        Arguments:
            move_name: The name of the move

        Returns:
            The created move

        Raises:
            RuntimeError: If this Pokemon already has 4 moves.
        """
        move_name = self._sanitize_move(move_name)

        if move_name == 'Struggle':
            return self._struggle

        if len(self.moves) == 4:
            raise RuntimeError(f'A Pokemon can only have a maximum of 4 moves. Current Moves = {
                               self.moves}. New Move: {move_name}')

        move = Move(name=move_name)
        self.moves.append(move)
        return move

    def find_move(self, move_name: str) -> Move:
        """Finds a move by name.

        Arguments:
            move_name: The name of the move

        Returns:
            The move with the given name or None if no move with that name exists.
        """
        try:
            if move_name == 'Struggle':
                return self._struggle

            return next(
                move
                for move in self.moves
                if move.name == move_name
            )
        except StopIteration:
            return None

    @staticmethod
    def _sanitize_move(move_name: str) -> str:
        if move_name == 'FreezeDry':
            return 'Freeze-Dry'

        if move_name == 'WillOWisp':
            return 'Will-O-Wisp'

        if move_name == 'Uturn':
            move_name = 'U-turn'

        return _CAPITAL_WORDS.sub(r'\1 \2', move_name)

    def __str__(self) -> str:
        return f'{self.species},{','.join([f"{m.name},{m.times_used}" for m in sorted(self.moves, key=lambda x: x.name)])},{self.tera_type},{self.was_brought},{self.was_lead},{self.was_terastallized}'


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
            return next(
                p
                for p in self.pokemon
                if nickname == p.nickname.split('-Tera')[0]
            )
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
            return next(
                p
                for p in self.pokemon
                if p.species in (species or p.species.split('-')[0])
            )
        except StopIteration:
            return None
