import abc
import collections
import dataclasses
import itertools
import os
import textwrap
from typing import List

import bs4
import requests

from .pokemon import Move, Pokemon, Team


class ShowdownReplayRetrievalStrategy(abc.ABC):
    @abc.abstractmethod
    def retrieve_replay(self, location: str) -> str:
        raise NotImplementedError()


class ShowdownUrlReplayRetrievalStrategy(ShowdownReplayRetrievalStrategy):
    def retrieve_replay(self, location: str) -> str:
        return requests.get(f'{location}.json', timeout=30).text


class ShowdownDownloadReplayRetrievalStrategy(ShowdownReplayRetrievalStrategy):
    def retrieve_replay(self, location: str) -> str:
        with open(location, 'r', encoding='utf8') as f:
            showdown_replay_raw_html = f.read()
            parsed_html = bs4.BeautifulSoup(showdown_replay_raw_html,
                                            'html.parser')
            battle_log_data = parsed_html.find('script',
                                               class_='battle-log-data')
            return textwrap.dedent(battle_log_data.text)


class ShowdownReplayRetrievalStrategyFactory:
    def resolve_strategy(self, location: str) -> ShowdownReplayRetrievalStrategy:
        if os.path.isfile(location):
            return ShowdownDownloadReplayRetrievalStrategy()
        elif location.startswith('https://replay.pokemonshowdown.com'):
            return ShowdownUrlReplayRetrievalStrategy()
        else:
            raise RuntimeError(f'Location {location} is not yet supported.')


@dataclasses.dataclass
class PokemonNickname:
    species: str
    nickname: str


@dataclasses.dataclass
class PlayerInfo:
    player_name: str
    team: Team
    tera_pokemon: Pokemon
    leads: List[Pokemon]
    brought_to_battle: List[Pokemon]


@dataclasses.dataclass
class ShowdownReplay:
    player1_info: PlayerInfo
    player2_info: PlayerInfo
    winner: int
    is_ots: bool = True


def parse_replay(battle_log: str) -> ShowdownReplay:
    player1: str
    player2: str
    player1_team: Team = Team(pokemon=[])
    player2_team: Team = Team(pokemon=[])
    player1_brought = collections.OrderedDict()
    player2_brought = collections.OrderedDict()

    is_ots = '|showteam|' in battle_log

    for line in battle_log.split('\n'):
        if not line:
            continue
        command_parts = line.split('|')
        command = command_parts[1]

        match command:
            case 'player':
                # |player|p1|player|number|
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
                    pokemon = Pokemon(species=species,
                                      nickname=species.split('-')[0],
                                      tera_type=tera_type,
                                      move1=Move(moves[0]),
                                      move2=Move(moves[1]),
                                      move3=Move(moves[2]),
                                      move4=Move(moves[3]))
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
                if move:
                    move.increment_count()
                else:
                    pokemon.add_move(move_name)

            case '-terastallize':
                # |-terastallize|p1a: nickname|type|
                player_number = _resolve_player(command_parts)
                nickname = _resolve_nickname(command_parts)
                team = player1_team \
                    if _is_player1(player_number) \
                    else player2_team
                pokemon = team.find_by_nickname(nickname)
                if _is_player1(player_number):
                    p1_tera = pokemon
                else:
                    p2_tera = pokemon

            case 'win':
                # |win|player|
                winner_name = command_parts[2]
                winner = int(winner_name == player2) + 1

    player1_info = PlayerInfo(player_name=player1,
                              team=player1_team,
                              tera_pokemon=p1_tera,
                              leads=_resolve_leads(player1_brought),
                              brought_to_battle=list(player1_brought.values()))
    player2_info = PlayerInfo(player_name=player2,
                              team=player2_team,
                              tera_pokemon=p2_tera,
                              leads=_resolve_leads(player2_brought),
                              brought_to_battle=list(player2_brought.values()))

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
