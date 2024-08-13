import collections
import io
import itertools
import json
import os
import pathlib

from showdown_replay_analyzer import showdown

_IGNORED_POKEMON = []
_IGNORED_USERS = []
_REPLAYS_DIR = '/Users/dillonodonovan/Downloads/replays/2024-04-22-shadow-rider'
_USERNAMES = ['ironpumpernickel']


def _generate_pokemon_statistics(
        player_usage: dict,
        player_info: showdown.PlayerInfo,
        c: itertools.count,
        out_csv: io.TextIOWrapper
):
    for pokemon in player_info.team.pokemon:
        if pokemon.species not in player_usage:
            player_usage[pokemon.species] = {
                'lead': 0,
                'brought': 0,
                'moves': collections.Counter(),
                'wins': 0,
                'tera': {}
            }
        pokemon_usage = player_usage[pokemon.species]
        if pokemon.was_lead:
            pokemon_usage['lead'] += 1
        if pokemon.was_brought:
            pokemon_usage['brought'] += 1
            if player_info.is_winner:
                pokemon_usage['wins'] += 1
        for move in pokemon.moves:
            pokemon_usage['moves'][move.name] += move.times_used
        if pokemon.was_terastallized:
            if pokemon.tera_type not in pokemon_usage['tera']:
                pokemon_usage['tera'][pokemon.tera_type] = {
                    'used': 0,
                    'wins': 0
                }
            pokemon_usage['tera'][pokemon.tera_type]['used'] += 1
            if player_info.is_winner:
                pokemon_usage['tera'][pokemon.tera_type]['wins'] += 1

        out_csv.write(f'{next(c)},{player_info.player_name},{pokemon},{
            player_info.is_winner and pokemon.was_brought}\n')


if __name__ == '__main__':
    flat = []
    user_usage = {
        'total': 0
    }
    opponent_usage = {
        'total': 0
    }
    factory = showdown.ShowdownReplayRetrievalStrategyFactory()

    counter = itertools.count(1)

    with open('.out/usage.csv', 'w', encoding='utf-8') as usage_csv:
        for root, dirs, files in os.walk(os.path.abspath(_REPLAYS_DIR)):
            for file in files:
                location = os.path.join(root, file)
                strategy = factory.resolve_strategy(location)
                battle_log = strategy.retrieve_replay(location)
                replay = showdown.parse_replay(battle_log)
                winner_name = replay.player1_info.player_name \
                    if replay.winner == 1 \
                    else replay.player2_info.player_name

                if replay.player1_info.player_name in _IGNORED_USERS \
                        or replay.player2_info.player_name in _IGNORED_USERS:
                    continue

                user_info: showdown.PlayerInfo
                opponent_info: showdown.PlayerInfo

                if replay.player1_info.player_name in _USERNAMES:
                    user_info = replay.player1_info
                    opponent_info = replay.player2_info
                else:
                    opponent_info = replay.player1_info
                    user_info = replay.player2_info

                should_continue = False
                for p in user_info.team.pokemon:
                    if p.species in _IGNORED_POKEMON:
                        should_continue = True
                        break
                if should_continue:
                    continue

                user_usage['total'] += 1
                opponent_usage['total'] += 1

                _generate_pokemon_statistics(
                    user_usage,
                    user_info,
                    counter,
                    usage_csv
                )

                _generate_pokemon_statistics(
                    opponent_usage,
                    opponent_info,
                    counter,
                    usage_csv
                )

    player_file = pathlib.Path('.out/player-usage.json')
    player_file.parent.mkdir(parents=True, exist_ok=True)
    player_file.write_text(json.dumps(user_usage), encoding='utf-8')

    opponent_file = pathlib.Path('.out/opponent-usage.json')
    opponent_file.parent.mkdir(parents=True, exist_ok=True)
    opponent_file.write_text(json.dumps(opponent_usage), encoding='utf-8')
