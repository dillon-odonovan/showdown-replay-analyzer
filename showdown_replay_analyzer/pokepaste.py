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
        species = _parse_species(spans)
        nickname = _parse_nickname(pokepaste_pokemon) or species
        tera_type = _parse_tera_type(spans)
        moves = _parse_moves(spans)
        pokemon.append(
            Pokemon(
                species=species,
                nickname=nickname,
                tera_type=tera_type,
                moves=moves
            )
        )

    return Team(pokemon)


def _parse_species(spans) -> str:
    return spans[0].string


def _parse_nickname(pokepaste_pokemon) -> str:
    possible_nickname = next(pokepaste_pokemon.children)
    if not possible_nickname.name == 'span':
        return possible_nickname[:-2]
    return None


def _parse_tera_type(spans) -> str:
    return next(
        span.next_sibling.string
        for span in spans
        if span.string.startswith('Tera Type')
    )


def _parse_moves(spans) -> List[Move]:
    return [
        Move(span.next_sibling.strip())
        for span in
        spans[-4:]
    ]
