import collections
import io
import itertools
import json
import os
import pathlib

from showdown_replay_analyzer import showdown

IGNORED_POKEMON = []
IGNORED_USERS = []
REPLAY_DIRS = [
    '/Users/dillonodonovan/Downloads/replays/2025-06-02',
    '/Users/dillonodonovan/Downloads/replays/2025-06-03',
    '/Users/dillonodonovan/Downloads/replays/2025-06-04',
    '/Users/dillonodonovan/Downloads/replays/2025-06-05',
    '/Users/dillonodonovan/Downloads/replays/2025-06-06',
    '/Users/dillonodonovan/Downloads/replays/2025-06-07',
    '/Users/dillonodonovan/Downloads/replays/2025-06-08',
    '/Users/dillonodonovan/Downloads/replays/2025-06-10',
    '/Users/dillonodonovan/Downloads/replays/2025-06-12',
]
USERNAMES = ['boxxtape', 'dillodon']
SCHEMA = [
    {'name': 'playerName', 'type': str},
    {'name': 'pokemon', 'type': str},
    {'name': 'move1', 'type': str},
    {'name': 'move1Count', 'type': int},
    {'name': 'move2', 'type': str},
    {'name': 'move2Count', 'type': int},
    {'name': 'move3', 'type': str},
    {'name': 'move3Count', 'type': int},
    {'name': 'move4', 'type': str},
    {'name': 'move4Count', 'type': int},
    {'name': 'teraType', 'type': str},
    {'name': 'brought', 'type': bool},
    {'name': 'lead', 'type': bool},
    {'name': 'terastallized', 'type': bool},
    {'name': 'win', 'type': bool}
]


def _generate_pokemon_statistics(
        player_usage: dict,
        player_info: showdown.PlayerInfo,
        c: itertools.count,
        out_csv: io.TextIOWrapper,
        replay_id: str
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

        out_csv.write(f'{next(c)},{replay_id},{player_info.player_name},{pokemon},{
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

    out_dir = pathlib.Path('.out/usage.csv')
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    with open(out_dir, 'w', encoding='utf-8', newline='') as usage_csv:
        for replay_dir in REPLAY_DIRS:
            for root, dirs, files in os.walk(os.path.abspath(replay_dir)):
                for file in files:
                    location = os.path.join(root, file)
                    strategy = factory.resolve_strategy(location)
                    (replay_id, battle_log) = strategy.retrieve_replay(location)
                    replay = showdown.parse_replay(replay_id, battle_log)
                    winner_name = replay.player1_info.player_name \
                        if replay.winner == 1 \
                        else replay.player2_info.player_name

                    if replay.player1_info.player_name in IGNORED_USERS \
                            or replay.player2_info.player_name in IGNORED_USERS:
                        continue

                    user_info: showdown.PlayerInfo
                    opponent_info: showdown.PlayerInfo

                    if replay.player1_info.player_name in USERNAMES:
                        user_info = replay.player1_info
                        opponent_info = replay.player2_info
                    else:
                        opponent_info = replay.player1_info
                        user_info = replay.player2_info

                    should_continue = False
                    for p in user_info.team.pokemon:
                        if p.species in IGNORED_POKEMON:
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
                        usage_csv,
                        replay_id
                    )

                    _generate_pokemon_statistics(
                        opponent_usage,
                        opponent_info,
                        counter,
                        usage_csv,
                        replay_id
                    )

    player_file = pathlib.Path('.out/player-usage.json')
    player_file.parent.mkdir(parents=True, exist_ok=True)
    player_file.write_text(json.dumps(user_usage), encoding='utf-8')

    opponent_file = pathlib.Path('.out/opponent-usage.json')
    opponent_file.parent.mkdir(parents=True, exist_ok=True)
    opponent_file.write_text(json.dumps(opponent_usage), encoding='utf-8')
