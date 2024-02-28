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
            move1=pokemon.Move('Protect'),
            move2=pokemon.Move('Follow Me'),
            move3=pokemon.Move('Helping Hand'),
            move4=pokemon.Move('Flamethrower')
        ),
        pokemon.Pokemon(
            species='Kingambit',
            nickname='Kingambit',
            tera_type='Dragon',
            move1=pokemon.Move('Kowtow Cleave'),
            move2=pokemon.Move('Sucker Punch'),
            move3=pokemon.Move('Iron Head'),
            move4=pokemon.Move('Low Kick')
        ),
        pokemon.Pokemon(
            species='Glimmora',
            nickname='Glimmora',
            tera_type='Grass',
            move1=pokemon.Move('Spiky Shield'),
            move2=pokemon.Move('Sludge Bomb'),
            move3=pokemon.Move('Meteor Beam'),
            move4=pokemon.Move('Earth Power')
        ),
        pokemon.Pokemon(
            species='Amoonguss',
            nickname='Amoonguss',
            tera_type='Water',
            move1=pokemon.Move('Protect'),
            move2=pokemon.Move('Spore'),
            move3=pokemon.Move('Rage Powder'),
            move4=pokemon.Move('Pollen Puff')
        ),
        pokemon.Pokemon(
            species='Flutter Mane',
            nickname='Flutter Mane',
            tera_type='Fairy',
            move1=pokemon.Move('Protect'),
            move2=pokemon.Move('Moonblast'),
            move3=pokemon.Move('Shadow Ball'),
            move4=pokemon.Move('Dazzling Gleam')
        ),
        pokemon.Pokemon(
            species='Zapdos-Galar',
            nickname='Zapdos-Galar',
            tera_type='Flying',
            move1=pokemon.Move('Close Combat'),
            move2=pokemon.Move('Brave Bird'),
            move3=pokemon.Move('U-turn'),
            move4=pokemon.Move('Knock Off')
        ),
    ])


def _get_expected_nickname_team() -> pokemon.Team:
    return pokemon.Team(pokemon=[
        pokemon.Pokemon(
            species='Iron Hands',
            nickname='Maradona',
            tera_type='Grass',
            move1=pokemon.Move('Fake Out'),
            move2=pokemon.Move('Close Combat'),
            move3=pokemon.Move('Wild Charge'),
            move4=pokemon.Move('Volt Switch')
        ),
        pokemon.Pokemon(
            species='Amoonguss',
            nickname='Shrom41Mor',
            tera_type='Steel',
            move1=pokemon.Move('Spore'),
            move2=pokemon.Move('Rage Powder'),
            move3=pokemon.Move('Pollen Puff'),
            move4=pokemon.Move('Protect')
        ),
        pokemon.Pokemon(
            species='Pelipper',
            nickname='Beaker',
            tera_type='Flying',
            move1=pokemon.Move('Hurricane'),
            move2=pokemon.Move('Hydro Pump'),
            move3=pokemon.Move('Tailwind'),
            move4=pokemon.Move('Protect')
        ),
        pokemon.Pokemon(
            species='Palafin',
            nickname='Torqoise',
            tera_type='Water',
            move1=pokemon.Move('Jet Punch'),
            move2=pokemon.Move('Wave Crash'),
            move3=pokemon.Move('Haze'),
            move4=pokemon.Move('Protect')
        ),
        pokemon.Pokemon(
            species='Baxcalibur',
            nickname='BlockBuster',
            tera_type='Poison',
            move1=pokemon.Move('Glaive Rush'),
            move2=pokemon.Move('Ice Shard'),
            move3=pokemon.Move('Icicle Crash'),
            move4=pokemon.Move('Protect')
        ),
        pokemon.Pokemon(
            species='Dragonite',
            nickname='ShiningArmor',
            tera_type='Flying',
            move1=pokemon.Move('Extreme Speed'),
            move2=pokemon.Move('Tera Blast'),
            move3=pokemon.Move('Ice Spinner'),
            move4=pokemon.Move('Protect')
        ),
    ])


if __name__ == '__main__':
    unittest.main()
