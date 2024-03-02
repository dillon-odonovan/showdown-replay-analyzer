import unittest
import unittest.mock

from .context import pokemon, pokepaste
from .html_utils import create_mock

_URL = 'https://pokepast.es/some-random-id'


class PokepasteParserTests(unittest.TestCase):
    def test_pokepaste_parser(self):
        with unittest.mock.patch('requests.get', return_value=create_mock('pokepaste-example.html')) as mock:
            parsed_team = pokepaste.parse_pokepaste(_URL)
            mock.assert_called_once_with(_URL, timeout=30)
        expected_team = _get_expected_team()
        self.assertEqual(parsed_team, expected_team)

    def test_pokepaste_parser_nicknames(self):
        with unittest.mock.patch('requests.get', return_value=create_mock('pokepaste-nicknames-example.html')) as mock:
            parsed_team = pokepaste.parse_pokepaste(_URL)
            mock.assert_called_once_with(_URL, timeout=30)
        expected_team = _get_expected_nickname_team()
        self.assertEqual(parsed_team, expected_team)


def _get_expected_team() -> pokemon.Team:
    return pokemon.Team(pokemon=[
        pokemon.Pokemon(
            species='Magmar',
            nickname='Magmar',
            tera_type='Grass',
            moves=[
                pokemon.Move('Protect'),
                pokemon.Move('Follow Me'),
                pokemon.Move('Helping Hand'),
                pokemon.Move('Flamethrower')
            ]
        ),
        pokemon.Pokemon(
            species='Kingambit',
            nickname='Kingambit',
            tera_type='Dragon',
            moves=[
                pokemon.Move('Kowtow Cleave'),
                pokemon.Move('Sucker Punch'),
                pokemon.Move('Iron Head'),
                pokemon.Move('Low Kick')
            ]
        ),
        pokemon.Pokemon(
            species='Glimmora',
            nickname='Glimmora',
            tera_type='Grass',
            moves=[
                pokemon.Move('Spiky Shield'),
                pokemon.Move('Sludge Bomb'),
                pokemon.Move('Meteor Beam'),
                pokemon.Move('Earth Power')
            ]
        ),
        pokemon.Pokemon(
            species='Amoonguss',
            nickname='Amoonguss',
            tera_type='Water',
            moves=[
                pokemon.Move('Protect'),
                pokemon.Move('Spore'),
                pokemon.Move('Rage Powder'),
                pokemon.Move('Pollen Puff')
            ]
        ),
        pokemon.Pokemon(
            species='Flutter Mane',
            nickname='Flutter Mane',
            tera_type='Fairy',
            moves=[
                pokemon.Move('Protect'),
                pokemon.Move('Moonblast'),
                pokemon.Move('Shadow Ball'),
                pokemon.Move('Dazzling Gleam')
            ]
        ),
        pokemon.Pokemon(
            species='Zapdos-Galar',
            nickname='Zapdos-Galar',
            tera_type='Flying',
            moves=[
                pokemon.Move('Close Combat'),
                pokemon.Move('Brave Bird'),
                pokemon.Move('U-turn'),
                pokemon.Move('Knock Off')
            ]
        ),
    ])


def _get_expected_nickname_team() -> pokemon.Team:
    return pokemon.Team(pokemon=[
        pokemon.Pokemon(
            species='Iron Hands',
            nickname='Maradona',
            tera_type='Grass',
            moves=[
                pokemon.Move('Fake Out'),
                pokemon.Move('Close Combat'),
                pokemon.Move('Wild Charge'),
                pokemon.Move('Volt Switch')
            ]
        ),
        pokemon.Pokemon(
            species='Amoonguss',
            nickname='Shrom41Mor',
            tera_type='Steel',
            moves=[
                pokemon.Move('Spore'),
                pokemon.Move('Rage Powder'),
                pokemon.Move('Pollen Puff'),
                pokemon.Move('Protect')
            ]
        ),
        pokemon.Pokemon(
            species='Pelipper',
            nickname='Beaker',
            tera_type='Flying',
            moves=[
                pokemon.Move('Hurricane'),
                pokemon.Move('Hydro Pump'),
                pokemon.Move('Tailwind'),
                pokemon.Move('Protect')
            ]
        ),
        pokemon.Pokemon(
            species='Palafin',
            nickname='Torqoise',
            tera_type='Water',
            moves=[
                pokemon.Move('Jet Punch'),
                pokemon.Move('Wave Crash'),
                pokemon.Move('Haze'),
                pokemon.Move('Protect')
            ]
        ),
        pokemon.Pokemon(
            species='Baxcalibur',
            nickname='BlockBuster',
            tera_type='Poison',
            moves=[
                pokemon.Move('Glaive Rush'),
                pokemon.Move('Ice Shard'),
                pokemon.Move('Icicle Crash'),
                pokemon.Move('Protect')
            ]
        ),
        pokemon.Pokemon(
            species='Dragonite',
            nickname='ShiningArmor',
            tera_type='Flying',
            moves=[
                pokemon.Move('Extreme Speed'),
                pokemon.Move('Tera Blast'),
                pokemon.Move('Ice Spinner'),
                pokemon.Move('Protect')
            ]
        ),
    ])


if __name__ == '__main__':
    unittest.main()
