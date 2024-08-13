"""Parse a Pokemon Team from a Pokepaste URL.

Example usage:

    team = parse_pokepaste(url)
"""

from typing import List

import bs4
import requests

from .pokemon import Move, Pokemon, Team


def parse_pokepaste(url: str) -> Team:
    """Parse a Pokemon Team from a Pokepaste URL.

    Args:
        url: The URL of the Pokepaste.

    Returns:
        A Team object containing the Pokemon parsed from the Pokepaste.
    """
    pokemon: List[Pokemon] = []

    pokepaste_raw_html = requests.get(url, timeout=30).text
    pokepaste_parsed_html = bs4.BeautifulSoup(
        pokepaste_raw_html,
        'html.parser'
    )
    pokepaste_pokemon_htmls = pokepaste_parsed_html.find_all('pre')

    for pokepaste_pokemon in pokepaste_pokemon_htmls:
        spans = pokepaste_pokemon.find_all('span')
        species = _parse_species(pokepaste_pokemon)
        nickname = _parse_nickname(pokepaste_pokemon) or species
        tera_type = _parse_tera_type(spans)
        moves = _parse_moves(spans)
        ability = _parse_ability(spans)
        item = _parse_item(pokepaste_pokemon)
        pokemon.append(
            Pokemon(
                species=species,
                nickname=nickname,
                tera_type=tera_type,
                moves=moves,
                ability=ability,
                item=item,
            )
        )

    return Team(pokemon)


def _parse_species(pokepaste_pokemon) -> str:
    contents = pokepaste_pokemon.contents
    if contents[0].name == 'span':
        return contents[0].string
    return contents[0].string.split(' @')[0].split(' (')[0]


def _parse_nickname(pokepaste_pokemon) -> str:
    possible_nickname = next(pokepaste_pokemon.children)
    if not possible_nickname.name == 'span':
        return possible_nickname[:-2]
    return None


def _parse_tera_type(spans) -> str:
    return next(
        span.next_sibling.string.strip()
        for span in spans
        if span.string.startswith('Tera Type')
    )


def _parse_moves(spans) -> List[Move]:
    moves = []
    for span in spans[-4:]:
        move = span.next_sibling
        if move.isspace():
            continue
        move_split = move.strip().split('\n')
        if len(move_split) == 1:
            x = move_split[0].split('- ')
            y = x[0] if len(x) == 1 else x[1]
            moves.append(Move(y.strip()))
        else:
            moves.append(Move(move_split[0].strip()))
            moves.append(Move(move_split[1][2:].strip()))

    return moves


def _parse_ability(spans) -> str:
    return next(
        span.next_sibling.string.strip()
        for span in spans
        if span.string.startswith('Ability')
    )


def _parse_item(pokepaste_pokemon) -> str:
    x = '|'.join([x.string for x in pokepaste_pokemon.contents])
    y = x.split('@')[1].split('|')
    return y[1].strip() if y[0].isspace() else y[0].strip()
