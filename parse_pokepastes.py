import collections
import json

from showdown_replay_analyzer import pokepaste


pokepastes = []


def main():
    pokemon_stats = {}
    for paste in pokepastes:
        team = pokepaste.parse_pokepaste(paste)
        for p in team.pokemon:
            if p.species not in pokemon_stats:
                pokemon_stats[p.species] = {
                    'count': 0,
                    'ability': collections.Counter(),
                    'item': collections.Counter(),
                    'moves': {},
                    'tera': collections.Counter(),
                }
            pokemon = pokemon_stats[p.species]
            pokemon['count'] += 1
            for move in p.moves:
                if move.name not in pokemon['moves']:
                    pokemon['moves'][move.name] = 0
                pokemon['moves'][move.name] += 1
            pokemon['tera'][p.tera_type] += 1
            pokemon['ability'][p.ability] += 1
            pokemon['item'][p.item] += 1
    print('[', end='')
    for i, x in enumerate(sorted(list(pokemon_stats.items()),
                                 key=lambda x: x[1]['count'],
                                 reverse=True)):
        print('{', end='')
        print(f'"species": "{x[0]}",', end='')
        print(f'"count": {x[1]['count']},', end='')
        print(f'"ability": {json.dumps(_sort_dict(x[1]['ability']))},', end='')
        print(f'"item": {json.dumps(_sort_dict(x[1]['item']))},', end='')
        print(f'"moves": {json.dumps(_sort_dict(x[1]['moves']))},', end='')
        print(f'"tera": {json.dumps(_sort_dict(x[1]['tera']))}', end='')
        print(f'}}{'' if i == len(pokemon_stats.keys()) - 1 else ','}', end='')
    print(']')


def _sort_dict(d):
    return dict(sorted(d.items(), key=lambda item: (-item[1], item[0])))


if __name__ == '__main__':
    main()
