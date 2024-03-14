"""Retrieve and parse Pokemon Showdown replays

Example usage:
    
    strategy = ShowdownReplayRetrievalStrategyFactory.resolve_strategy(location)
    battle_log = strategy.retrieve_replay(location)
    replay = parse_replay(battle_log)
"""
import abc
import collections
import dataclasses
import itertools
import os
import textwrap
from typing import List

import bs4
import requests

from .pokemon import Pokemon, Team


class ShowdownReplayRetrievalStrategy(abc.ABC):
    """Interface for retrieving Showdown replays."""

    @abc.abstractmethod
    def retrieve_replay(self, location: str) -> str:
        """Retrieves the Showdown replay from the provided location.

        Args:
            location: The location of the showdown replay.

        Returns:
            The Showdown replay battle log as a string.
        """
        raise NotImplementedError()


class ShowdownUrlReplayRetrievalStrategy(ShowdownReplayRetrievalStrategy):
    """Retrieves replays uploaded to replay.pokemonshowdown.com."""

    def retrieve_replay(self, location: str) -> str:
        return requests.get(f'{location}.json', timeout=30).text


class ShowdownDownloadReplayRetrievalStrategy(ShowdownReplayRetrievalStrategy):
    """Retrieves replays downloaded as local files on disk."""

    def retrieve_replay(self, location: str) -> str:
        with open(location, 'r', encoding='utf8') as f:
            showdown_replay_raw_html = f.read()
            parsed_html = bs4.BeautifulSoup(
                showdown_replay_raw_html,
                'html.parser'
            )
            battle_log_data = parsed_html.find(
                'script',
                class_='battle-log-data'
            )
            return textwrap.dedent(battle_log_data.text)


class ShowdownReplayRetrievalStrategyFactory:
    """Factory class to create instances of ShowdownReplayRetrievalStrategy."""

    @staticmethod
    def resolve_strategy(location: str) -> ShowdownReplayRetrievalStrategy:
        """Resolves the appropriate ShowdownReplayRetrievalStrategy for the provided location.

        The location can be a local file or a URL.
        If the location is a local file, the ShowdownDownloadReplayRetrievalStrategy is returned.
        If the location is a URL, the ShowdownUrlReplayRetrievalStrategy is returned.
        If the location is neither a local file nor a URL, a ValueError is raised.

        Args:
            location: The location of the showdown replay.

        Returns:
            The corresponding ShowdownReplayRetrievalStrategy for the provided location.

        Raises:
            ValueError: If the location is neither a local file nor a Pokemon Showdown URL.
        """
        if os.path.isfile(location):
            return ShowdownDownloadReplayRetrievalStrategy()
        if location.startswith('https://replay.pokemonshowdown.com'):
            return ShowdownUrlReplayRetrievalStrategy()
        raise ValueError(f'Location {location} is not yet supported.')


@dataclasses.dataclass
class PlayerInfo:
    """A player's information parsed from a Showdown Replay.

    Attributes:
        player_name: The name of the player.
        team: All Pokemon of the player's team.
    """
    player_name: str
    team: Team
    is_winner: bool = True


@dataclasses.dataclass
class ShowdownReplay:
    """The information of each player, the winner, and OTS status from a Showdown Replay.

    Attributes:
        player1_info: The parsed information for Player 1.
        player2_info: The parsed information for Player 2.
        winner: The winner of the battle (1 for Player 1, 2 for Player 2)
        is_ots: If the game played included Open Team Sheets (OTS)
    """
    player1_info: PlayerInfo
    player2_info: PlayerInfo
    winner: int
    is_ots: bool = True


def parse_replay(battle_log: str) -> ShowdownReplay:
    """Parses a Showdown Replay into a ShowdownReplay object.

    Args:
        battle_log: The raw battle log of the Showdown Replay

    Returns:
        The parsed ShowdownReplay object
    """
    player1: str = None
    player2: str = None
    player1_team: Team = Team(pokemon=[])
    player2_team: Team = Team(pokemon=[])
    player1_brought = collections.OrderedDict()
    player2_brought = collections.OrderedDict()

    is_ots = '|showteam|' in battle_log

    for line in battle_log.split('\n'):
        if not line:
            continue

        command_parts = line.split('|')
        if len(command_parts) == 1:
            continue

        command = command_parts[1]

        match command:
            case 'player':
                # |player|p1|player|avatar|elo
                if player1 and player2:
                    continue
                player_number = _resolve_player(command_parts)
                player_name = command_parts[3]
                if _is_player1(player_number):
                    player1 = player_name
                else:
                    player2 = player_name

            case 'poke':
                # |poke|p1|Species, Level, Gender|
                # only useful if not OTS
                if is_ots:
                    continue
                player_number = _resolve_player(command_parts)
                species = _resolve_species(command_parts)
                team = player1_team \
                    if _is_player1(player_number)\
                    else player2_team
                pokemon = Pokemon(species=species)
                team.add_pokemon(pokemon)

            case 'showteam':
                # |showteam|p1|Species|?|Item|Ability|Move1,Move2,Move3,Move4|?|?|Gender|?|?|50|,,,,,Tera]...
                # only useful if OTS
                if not is_ots:
                    continue
                player_number = _resolve_player(command_parts)
                next_pokemon = command_parts[3]
                command_parts = command_parts[4:]
                index_buffer = 0
                while next_pokemon:
                    species = next_pokemon
                    moves = command_parts[3 - index_buffer].split(',')
                    tera_type_and_next_pokemon = command_parts[10 - index_buffer] \
                        .split(',')[-1] \
                        .split(']')
                    tera_type = tera_type_and_next_pokemon[0]
                    next_pokemon = tera_type_and_next_pokemon[1] \
                        if len(tera_type_and_next_pokemon) > 1 \
                        else None
                    command_parts = command_parts[12 - index_buffer:]
                    index_buffer = 1
                    pokemon = Pokemon(
                        species=species,
                        nickname=species.split('-')[0],
                        tera_type=tera_type
                    )
                    for move in moves:
                        pokemon.add_move(move_name=move)
                    team = player1_team \
                        if _is_player1(player_number) \
                        else player2_team
                    team.add_pokemon(pokemon)

            case 'switch':
                # |switch|p1a: nickname|Species, Level|CurrentHp\/TotalHp|
                player_number = _resolve_player(command_parts)
                nickname = _resolve_nickname(command_parts)
                species = _resolve_species(command_parts).split('-Tera')[0]
                team = player1_team \
                    if _is_player1(player_number) \
                    else player2_team
                brought = player1_brought \
                    if _is_player1(player_number) \
                    else player2_brought
                pokemon = team.find_by_species(species)
                pokemon.nickname = nickname
                brought[pokemon.species] = pokemon

            case 'move':
                # |move|p1a: nickname|move name|p2a: nickname|
                player_number = _resolve_player(command_parts)
                nickname = _resolve_nickname(command_parts)
                team = player1_team if player_number == 'p1' else player2_team
                move_name = command_parts[3]
                pokemon = team.find_by_nickname(nickname)

                move = pokemon.find_move(move_name)
                if not move:
                    move = pokemon.add_move(move_name)
                move.increment_count()

            case '-terastallize':
                # |-terastallize|p1a: nickname|type|
                player_number = _resolve_player(command_parts)
                nickname = _resolve_nickname(command_parts)
                team = player1_team \
                    if _is_player1(player_number) \
                    else player2_team
                pokemon = team.find_by_nickname(nickname)
                pokemon.was_terastallized = True

            case 'win':
                # |win|player|
                winner_name = command_parts[2]
                winner = int(winner_name == player2) + 1

    player1_info = PlayerInfo(
        player_name=player1,
        team=player1_team,
        is_winner=winner_name == player1
    )

    for player1_lead in _resolve_leads(player1_brought):
        player1_team.find_by_species(player1_lead.species).was_lead = True

    for player2_lead in _resolve_leads(player2_brought):
        player2_team.find_by_species(player2_lead.species).was_lead = True

    for p1_b in player1_brought:
        player1_team.find_by_species(p1_b).was_brought = True

    for p2_b in player2_brought:
        player2_team.find_by_species(p2_b).was_brought = True

    player2_info = PlayerInfo(
        player_name=player2,
        team=player2_team,
        is_winner=winner_name == player2
    )

    return ShowdownReplay(player1_info=player1_info,
                          player2_info=player2_info,
                          winner=winner)


def _resolve_player(command_parts: List[str]) -> str:
    # 'p1a: ...'
    return command_parts[2][:2]


def _resolve_nickname(command_parts: List[str]) -> str:
    # 'p1a: nickname'
    return command_parts[2][5:]


def _resolve_species(command_parts: List[str]) -> str:
    # 'Species, Level'
    return command_parts[3].split(',')[0]


def _resolve_leads(d: collections.OrderedDict) -> list:
    return list(itertools.islice(d.values(), 2))


def _is_player1(player: str) -> bool:
    return player == 'p1'
