import unittest
import unittest.mock

from .context import pokemon, showdown
from .html_utils import get_resource_location

_SHOWDOWN_REPLAY_RESOURCE = 'Gen9VGC2024RegFBo3-2024-02-24-tearsricochet-quartermachine.html'


class ShowdownReplayParserTests(unittest.TestCase):
    def test_showdown_replay_retrieval_factory_url(self):
        factory = showdown.ShowdownReplayRetrievalStrategyFactory()
        location = 'https://replay.pokemonshowdown.com/id'
        strategy = factory.resolve_strategy(location)
        self.assertIsInstance(
            strategy,
            showdown.ShowdownUrlReplayRetrievalStrategy
        )

    def test_showdown_replay_retrieval_factory_download(self):
        factory = showdown.ShowdownReplayRetrievalStrategyFactory()
        location = get_resource_location(_SHOWDOWN_REPLAY_RESOURCE)
        strategy = factory.resolve_strategy(location)
        self.assertIsInstance(
            strategy,
            showdown.ShowdownDownloadReplayRetrievalStrategy
        )

    def test_showdown_downloaded_replay_retrieval_strategy(self):
        location = get_resource_location(_SHOWDOWN_REPLAY_RESOURCE)
        battle_log = showdown.ShowdownDownloadReplayRetrievalStrategy().retrieve_replay(location)
        expected_battle_log = _get_expected_battle_log()
        self.assertEqual(battle_log, expected_battle_log)

    def test_parse_replay(self):
        location = get_resource_location(_SHOWDOWN_REPLAY_RESOURCE)
        battle_log = showdown.ShowdownDownloadReplayRetrievalStrategy().retrieve_replay(location)
        parsed_replay = showdown.parse_replay(battle_log)
        expected_replay = _get_expected_showdown_replay()
        self.assertEqual(parsed_replay, expected_replay)

    def test_parse_replay_no_tera(self):
        battle_log = r'''
        |player|p1|Tears ricochet|170|1529
        |player|p2|Quarter Machine|2|1730
        |showteam|p1|Regidrago||DragonFang|DragonsMaw|DragonEnergy,DracoMeteor,EarthPower,Protect||||||50|,,,,,Steel]Flutter Mane||BoosterEnergy|Protosynthesis|Moonblast,IcyWind,Thunderbolt,Protect||||||50|,,,,,Electric
        |showteam|p2|Flutter Mane||BoosterEnergy|Protosynthesis|Protect,Moonblast,ShadowBall,DazzlingGleam||||||50|,,,,,Fairy]Tornadus||FocusSash|Prankster|Protect,BleakwindStorm,Tailwind,RainDance|||M|||50|,,,,,Ghost
        |switch|p1a: Flutter Mane|Flutter Mane, L50|100\/100
        |switch|p1b: Regidrago|Regidrago, L50|100\/100
        |switch|p2a: Tornadus|Tornadus, L50, M|157\/157
        |switch|p2b: Flutter Mane|Flutter Mane, L50|137\/137
        |win|Quarter Machine'''
        parsed_replay = showdown.parse_replay(battle_log)
        p1_regidrago = pokemon.Pokemon(
            species='Regidrago',
            nickname='Regidrago',
            tera_type='Steel',
            moves=[
                pokemon.Move(name='Dragon Energy'),
                pokemon.Move(name='Draco Meteor'),
                pokemon.Move(name='Earth Power'),
                pokemon.Move(name='Protect')
            ]
        )
        p1_flutter = pokemon.Pokemon(
            species='Flutter Mane',
            nickname='Flutter Mane',
            tera_type='Electric',
            moves=[
                pokemon.Move(name='Moonblast'),
                pokemon.Move(name='Icy Wind'),
                pokemon.Move(name='Thunderbolt'),
                pokemon.Move(name='Protect')
            ]
        )
        p2_flutter = pokemon.Pokemon(
            species='Flutter Mane',
            nickname='Flutter Mane',
            tera_type='Fairy',
            moves=[
                pokemon.Move(name='Protect'),
                pokemon.Move(name='Moonblast'),
                pokemon.Move(name='Shadow Ball'),
                pokemon.Move(name='Dazzling Gleam')
            ]
        )
        p2_tornadus = pokemon.Pokemon(
            species='Tornadus',
            nickname='Tornadus',
            tera_type='Ghost',
            moves=[
                pokemon.Move(name='Protect'),
                pokemon.Move(name='Bleakwind Storm'),
                pokemon.Move(name='Tailwind'),
                pokemon.Move(name='Rain Dance')
            ]
        )
        p1 = showdown.PlayerInfo(
            player_name='Tears ricochet',
            team=pokemon.Team([p1_regidrago, p1_flutter]),
            tera_pokemon=None,
            leads=[p1_flutter, p1_regidrago],
            brought_to_battle=[p1_flutter, p1_regidrago]
        )
        p2 = showdown.PlayerInfo(
            player_name='Quarter Machine',
            team=pokemon.Team([p2_flutter, p2_tornadus]),
            tera_pokemon=None,
            leads=[p2_tornadus, p2_flutter],
            brought_to_battle=[p2_tornadus, p2_flutter]
        )
        expected_replay = showdown.ShowdownReplay(
            player1_info=p1,
            player2_info=p2,
            winner=2,
            is_ots=True
        )
        self.assertEqual(parsed_replay, expected_replay)

    def test_parse_replay_struggle(self):
        battle_log = r'''
        |player|p1|Tears ricochet|170|1529
        |player|p2|Quarter Machine|2|1730
        |showteam|p1|Regidrago||DragonFang|DragonsMaw|DragonEnergy,DracoMeteor,EarthPower,Protect||||||50|,,,,,Steel]Flutter Mane||BoosterEnergy|Protosynthesis|Moonblast,IcyWind,Thunderbolt,Protect||||||50|,,,,,Electric
        |showteam|p2|Flutter Mane||BoosterEnergy|Protosynthesis|Protect,Moonblast,ShadowBall,DazzlingGleam||||||50|,,,,,Fairy]Tornadus||FocusSash|Prankster|Protect,BleakwindStorm,Tailwind,RainDance|||M|||50|,,,,,Ghost
        |switch|p1a: Flutter Mane|Flutter Mane, L50|100\/100
        |switch|p1b: Regidrago|Regidrago, L50|100\/100
        |switch|p2a: Tornadus|Tornadus, L50, M|157\/157
        |switch|p2b: Flutter Mane|Flutter Mane, L50|137\/137
        |move|p1a: Flutter Mane|Struggle|p2a: Tornadus
        |win|Quarter Machine'''
        parsed_replay = showdown.parse_replay(battle_log)
        p1_regidrago = pokemon.Pokemon(
            species='Regidrago',
            nickname='Regidrago',
            tera_type='Steel',
            moves=[
                pokemon.Move(name='Dragon Energy'),
                pokemon.Move(name='Draco Meteor'),
                pokemon.Move(name='Earth Power'),
                pokemon.Move(name='Protect')
            ]
        )
        p1_flutter = pokemon.Pokemon(
            species='Flutter Mane',
            nickname='Flutter Mane',
            tera_type='Electric',
            moves=[
                pokemon.Move(name='Moonblast'),
                pokemon.Move(name='Icy Wind'),
                pokemon.Move(name='Thunderbolt'),
                pokemon.Move(name='Protect')
            ],
            _struggle=pokemon.Move(name='Struggle', times_used=1)
        )
        p2_flutter = pokemon.Pokemon(
            species='Flutter Mane',
            nickname='Flutter Mane',
            tera_type='Fairy',
            moves=[
                pokemon.Move(name='Protect'),
                pokemon.Move(name='Moonblast'),
                pokemon.Move(name='Shadow Ball'),
                pokemon.Move(name='Dazzling Gleam')
            ]
        )
        p2_tornadus = pokemon.Pokemon(
            species='Tornadus',
            nickname='Tornadus',
            tera_type='Ghost',
            moves=[
                pokemon.Move(name='Protect'),
                pokemon.Move(name='Bleakwind Storm'),
                pokemon.Move(name='Tailwind'),
                pokemon.Move(name='Rain Dance')
            ]
        )
        p1 = showdown.PlayerInfo(
            player_name='Tears ricochet',
            team=pokemon.Team([p1_regidrago, p1_flutter]),
            tera_pokemon=None,
            leads=[p1_flutter, p1_regidrago],
            brought_to_battle=[p1_flutter, p1_regidrago]
        )
        p2 = showdown.PlayerInfo(
            player_name='Quarter Machine',
            team=pokemon.Team([p2_flutter, p2_tornadus]),
            tera_pokemon=None,
            leads=[p2_tornadus, p2_flutter],
            brought_to_battle=[p2_tornadus, p2_flutter]
        )
        expected_replay = showdown.ShowdownReplay(
            player1_info=p1,
            player2_info=p2,
            winner=2,
            is_ots=True
        )
        self.assertEqual(parsed_replay, expected_replay)


def _get_expected_battle_log() -> str:
    return r'''
|j|☆Tears ricochet
|j|☆Quarter Machine

|n|☆Tears ricochet|tearsricochet
|n|☆Quarter Machine|quartermachine
|html|<table width="100%"><tr><td align="left">Tears ricochet<\/td><td align="right">Quarter Machine<\/tr><tr><td align="left"><i class="fa fa-circle-o"><\/i> <i class="fa fa-circle-o"><\/i> <\/td><td align="right"><i class="fa fa-circle-o"><\/i> <i class="fa fa-circle-o"><\/i> <\/tr><\/table><h2><strong>Game 1<\/strong> of <a href="\/game-bestof3-gen9vgc2024regfbo3-2066960967">a best-of-3<\/a><\/h2>
|t:|1708821855
|gametype|doubles
|player|p1|Tears ricochet|170|1529
|player|p2|Quarter Machine|2|1730
|teamsize|p1|6
|teamsize|p2|6
|gen|9
|tier|[Gen 9] VGC 2024 Reg F (Bo3)
|rated|
|rule|Species Clause: Limit one of each Pokémon
|rule|Item Clause: Limit one of each item
|clearpoke
|poke|p1|Ogerpon-Hearthflame, L50, F|
|poke|p1|Regidrago, L50|
|poke|p1|Rillaboom, L50, M|
|poke|p1|Urshifu-*, L50, F|
|poke|p1|Flutter Mane, L50|
|poke|p1|Farigiraf, L50, F|
|poke|p2|Amoonguss, L50, M|
|poke|p2|Urshifu-*, L50, M|
|poke|p2|Flutter Mane, L50|
|poke|p2|Tornadus, L50, M|
|poke|p2|Incineroar, L50, F|
|poke|p2|Landorus, L50, M|
|teampreview|4
|showteam|p1|Ogerpon-Hearthflame||HearthflameMask|MoldBreaker|IvyCudgel,GrassyGlide,FollowMe,SpikyShield|||F|||50|,,,,,Fire]Regidrago||DragonFang|DragonsMaw|DragonEnergy,DracoMeteor,EarthPower,Protect||||||50|,,,,,Steel]Rillaboom||AssaultVest|GrassySurge|GrassyGlide,FakeOut,HighHorsepower,WoodHammer|||M|||50|,,,,,Fire]Urshifu||FocusSash|UnseenFist|WickedBlow,CloseCombat,SuckerPunch,Protect|||F|||50|,,,,,Dark]Flutter Mane||BoosterEnergy|Protosynthesis|Moonblast,IcyWind,Thunderbolt,Protect||||||50|,,,,,Electric]Farigiraf||SitrusBerry|ArmorTail|Psychic,DazzlingGleam,TrickRoom,HelpingHand|||F|||50|,,,,,Fairy
|showteam|p2|Amoonguss||SitrusBerry|Regenerator|Protect,SludgeBomb,Spore,RagePowder|||M|||50|,,,,,Water]Urshifu-Rapid-Strike||ChoiceScarf|UnseenFist|CloseCombat,SurgingStrikes,AquaJet,Uturn|||M|||50|,,,,,Water]Flutter Mane||BoosterEnergy|Protosynthesis|Protect,Moonblast,ShadowBall,DazzlingGleam||||||50|,,,,,Fairy]Tornadus||FocusSash|Prankster|Protect,BleakwindStorm,Tailwind,RainDance|||M|||50|,,,,,Ghost]Incineroar||SafetyGoggles|Intimidate|FakeOut,PartingShot,FlareBlitz,KnockOff|||F|||50|,,,,,Dragon]Landorus||LifeOrb|SheerForce|Protect,EarthPower,Substitute,SludgeBomb|||M|||50|,,,,,Steel
|inactive|Battle timer is ON: inactive players will automatically lose when time's up. (requested by Tears ricochet)
|inactive|Time left: 90 sec this turn | 420 sec total | 90 sec grace
|
|t:|1708821904
|start
|switch|p1a: Flutter Mane|Flutter Mane, L50|100\/100
|switch|p1b: Regidrago|Regidrago, L50|100\/100
|switch|p2a: Tornadus|Tornadus, L50, M|157\/157
|switch|p2b: Flutter Mane|Flutter Mane, L50|137\/137
|-enditem|p1a: Flutter Mane|Booster Energy
|-activate|p1a: Flutter Mane|ability: Protosynthesis|[fromitem]
|-start|p1a: Flutter Mane|protosynthesisspe
|-enditem|p2b: Flutter Mane|Booster Energy
|-activate|p2b: Flutter Mane|ability: Protosynthesis|[fromitem]
|-start|p2b: Flutter Mane|protosynthesisspa
|turn|1
|inactive|Time left: 55 sec this turn | 420 sec total
|
|t:|1708821926
|switch|p1b: Ogerpon|Ogerpon-Hearthflame, L50, F|100\/100
|-ability|p1b: Ogerpon|Mold Breaker
|move|p2a: Tornadus|Tailwind|p2a: Tornadus
|-sidestart|p2: Quarter Machine|move: Tailwind
|move|p2b: Flutter Mane|Shadow Ball|p1a: Flutter Mane
|-supereffective|p1a: Flutter Mane
|-damage|p1a: Flutter Mane|1\/100
|move|p1a: Flutter Mane|Icy Wind|p2b: Flutter Mane|[spread] p2a,p2b
|-supereffective|p2a: Tornadus
|-damage|p2a: Tornadus|101\/157
|-damage|p2b: Flutter Mane|118\/137
|-unboost|p2a: Tornadus|spe|1
|-unboost|p2b: Flutter Mane|spe|1
|
|upkeep
|turn|2
|inactive|Time left: 55 sec this turn | 415 sec total
|
|t:|1708821942
|move|p1a: Flutter Mane|Protect|p1a: Flutter Mane
|-singleturn|p1a: Flutter Mane|Protect
|move|p1b: Ogerpon|Spiky Shield|p1b: Ogerpon
|-singleturn|p1b: Ogerpon|move: Protect
|move|p2b: Flutter Mane|Dazzling Gleam|p1a: Flutter Mane|[spread] 
|-activate|p1a: Flutter Mane|move: Protect
|-activate|p1b: Ogerpon|move: Protect
|move|p2a: Tornadus|Bleakwind Storm|p1b: Ogerpon|[spread] 
|-activate|p1a: Flutter Mane|move: Protect
|-activate|p1b: Ogerpon|move: Protect
|
|upkeep
|turn|3
|inactive|Time left: 55 sec this turn | 400 sec total
|inactive|Tears ricochet has 30 seconds left.
|
|t:|1708821972
|-terastallize|p1b: Ogerpon|Fire
|detailschange|p1b: Ogerpon|Ogerpon-Hearthflame-Tera, L50, F, tera:Fire
|-ability|p1b: Ogerpon|Embody Aspect (Hearthflame)|boost
|-boost|p1b: Ogerpon|atk|1
|move|p1a: Flutter Mane|Icy Wind|p2b: Flutter Mane|[spread] p2b
|-miss|p1a: Flutter Mane|p2a: Tornadus
|-damage|p2b: Flutter Mane|102\/137
|-unboost|p2b: Flutter Mane|spe|1
|move|p2a: Tornadus|Bleakwind Storm|p1b: Ogerpon|[spread] p1a,p1b
|-damage|p1a: Flutter Mane|0 fnt
|-damage|p1b: Ogerpon|63\/100
|-unboost|p1b: Ogerpon|spe|1
|faint|p1a: Flutter Mane
|-end|p1a: Flutter Mane|Protosynthesis|[silent]
|move|p2b: Flutter Mane|Dazzling Gleam|p1b: Ogerpon
|-resisted|p1b: Ogerpon
|-damage|p1b: Ogerpon|35\/100
|move|p1b: Ogerpon|Ivy Cudgel|p2a: Tornadus|[anim] Ivy Cudgel Fire
|-damage|p2a: Tornadus|0 fnt
|faint|p2a: Tornadus
|
|upkeep
|inactive|Time left: 55 sec this turn | 385 sec total
|inactive|Tears ricochet has 30 seconds left.
|
|t:|1708822000
|switch|p1a: Regidrago|Regidrago, L50|100\/100
|switch|p2a: Landorus|Landorus, L50, M|165\/165
|turn|4
|inactive|Time left: 55 sec this turn | 370 sec total
|
|t:|1708822019
|switch|p1b: Rillaboom|Rillaboom, L50, M|100\/100
|-fieldstart|move: Grassy Terrain|[from] ability: Grassy Surge|[of] p1b: Rillaboom
|-terastallize|p2b: Flutter Mane|Fairy
|move|p1a: Regidrago|Protect|p1a: Regidrago
|-singleturn|p1a: Regidrago|Protect
|move|p2a: Landorus|Substitute|p2a: Landorus
|-start|p2a: Landorus|Substitute
|-damage|p2a: Landorus|124\/165
|move|p2b: Flutter Mane|Dazzling Gleam|p1b: Rillaboom|[spread] p1b
|-activate|p1a: Regidrago|move: Protect
|-damage|p1b: Rillaboom|64\/100
|
|-heal|p2b: Flutter Mane|110\/137|[from] Grassy Terrain
|-heal|p1b: Rillaboom|69\/100|[from] Grassy Terrain
|-sideend|p2: Quarter Machine|move: Tailwind
|upkeep
|turn|5
|inactive|Time left: 55 sec this turn | 355 sec total
|inactive|Quarter Machine has 30 seconds left.
|
|t:|1708822050
|-end|p2b: Flutter Mane|Protosynthesis|[silent]
|switch|p2b: Amoonguss|Amoonguss, L50, M|215\/215
|move|p1b: Rillaboom|Grassy Glide|p2a: Landorus
|-end|p2a: Landorus|Substitute
|move|p2a: Landorus|Sludge Bomb|p1b: Rillaboom
|-supereffective|p1b: Rillaboom
|-damage|p1b: Rillaboom|6\/100
|move|p1a: Regidrago|Draco Meteor|p2a: Landorus
|-damage|p2a: Landorus|0 fnt
|-unboost|p1a: Regidrago|spa|2
|faint|p2a: Landorus
|
|-heal|p1b: Rillaboom|12\/100|[from] Grassy Terrain
|upkeep
|inactive|Time left: 55 sec this turn | 330 sec total
|
|t:|1708822060
|switch|p2a: Flutter Mane|Flutter Mane, L50, tera:Fairy|110\/137
|turn|6
|inactive|Time left: 55 sec this turn | 325 sec total
|
|t:|1708822074
|move|p2a: Flutter Mane|Protect|p2a: Flutter Mane
|-singleturn|p2a: Flutter Mane|Protect
|move|p1b: Rillaboom|Grassy Glide|p2a: Flutter Mane
|-activate|p2a: Flutter Mane|move: Protect
|move|p1a: Regidrago|Earth Power|p2a: Flutter Mane
|-activate|p2a: Flutter Mane|move: Protect
|move|p2b: Amoonguss|Spore|p1a: Regidrago
|-status|p1a: Regidrago|slp|[from] move: Spore
|
|-heal|p2a: Flutter Mane|118\/137|[from] Grassy Terrain
|-heal|p1b: Rillaboom|18\/100|[from] Grassy Terrain
|upkeep
|turn|7
|inactive|Time left: 55 sec this turn | 315 sec total
|
|t:|1708822083
|move|p1b: Rillaboom|Grassy Glide|p2a: Flutter Mane
|-damage|p2a: Flutter Mane|36\/137
|move|p2a: Flutter Mane|Dazzling Gleam|p1a: Regidrago|[spread] p1a,p1b
|-supereffective|p1a: Regidrago
|-damage|p1a: Regidrago|8\/100 slp
|-damage|p1b: Rillaboom|0 fnt
|faint|p1b: Rillaboom
|cant|p1a: Regidrago|slp
|move|p2b: Amoonguss|Sludge Bomb|p1a: Regidrago
|-damage|p1a: Regidrago|0 fnt
|faint|p1a: Regidrago
|
|-heal|p2a: Flutter Mane|44\/137|[from] Grassy Terrain
|upkeep
|inactive|Time left: 55 sec this turn | 310 sec total
|
|t:|1708822087
|switch|p1b: Ogerpon|Ogerpon-Hearthflame-Tera, L50, F, tera:Fire|35\/100
|-ability|p1b: Ogerpon|Embody Aspect (Hearthflame)|boost
|-boost|p1b: Ogerpon|atk|1
|turn|8
|inactive|Time left: 55 sec this turn | 310 sec total
|
|t:|1708822094
|move|p2a: Flutter Mane|Protect|p2a: Flutter Mane
|-singleturn|p2a: Flutter Mane|Protect
|move|p2b: Amoonguss|Protect|p2b: Amoonguss
|-singleturn|p2b: Amoonguss|Protect
|move|p1b: Ogerpon|Ivy Cudgel|p2b: Amoonguss|[anim] Ivy Cudgel Fire
|-activate|p2b: Amoonguss|move: Protect
|
|-heal|p2a: Flutter Mane|52\/137|[from] Grassy Terrain
|-heal|p1b: Ogerpon|41\/100|[from] Grassy Terrain
|-fieldend|move: Grassy Terrain
|upkeep
|turn|9
|inactive|Time left: 55 sec this turn | 305 sec total
|
|t:|1708822102
|move|p2b: Amoonguss|Rage Powder|p2b: Amoonguss
|-singleturn|p2b: Amoonguss|move: Rage Powder
|move|p2a: Flutter Mane|Shadow Ball|p1b: Ogerpon
|-damage|p1b: Ogerpon|0 fnt
|faint|p1b: Ogerpon
|
|win|Quarter Machine
|inactive|Time left: 55 sec this turn | 300 sec total
|tempnotify|choice|Next game|It's time for game 2 in your best-of-3!
|tempnotify|choice|Next game|It's time for game 2 in your best-of-3!
|c|&|\/uhtml controls,<div class="infobox"><p style="margin:6px">Are you ready for game 2, Quarter Machine?<\/p><p style="margin:6px"><button class="button notifying" name="send" value="\/msgroom game-bestof3-gen9vgc2024regfbo3-2066960967,\/confirmready">I'm ready!<\/button><\/p><\/div>
|tempnotifyoff|choice
|c|&|\/uhtml controls,<div class="infobox"><p style="margin:6px">Are you ready for game 2, Quarter Machine?<\/p><p style="margin:6px"><button class="button" disabled><i class="fa fa-check"><\/i> I'm ready!<\/button> &ndash; waiting for opponent...<\/p><\/div>
||Quarter Machine is ready for game 2.
'''


def _get_expected_showdown_replay() -> showdown.ShowdownReplay:
    player1_ogerpon_hearthflame = pokemon.Pokemon(
        species='Ogerpon-Hearthflame',
        nickname='Ogerpon',
        tera_type='Fire',
        moves=[
            pokemon.Move('Ivy Cudgel', times_used=2),
            pokemon.Move('Grassy Glide'),
            pokemon.Move('Follow Me'),
            pokemon.Move('Spiky Shield', times_used=1)
        ]
    )
    player1_regidrago = pokemon.Pokemon(
        species='Regidrago',
        nickname='Regidrago',
        tera_type='Steel',
        moves=[
            pokemon.Move('Dragon Energy'),
            pokemon.Move('Draco Meteor', times_used=1),
            pokemon.Move('Earth Power', times_used=1),
            pokemon.Move('Protect', times_used=1)
        ]
    )
    player1_rillaboom = pokemon.Pokemon(
        species='Rillaboom',
        nickname='Rillaboom',
        tera_type='Fire',
        moves=[
            pokemon.Move('Grassy Glide', times_used=3),
            pokemon.Move('Fake Out'),
            pokemon.Move('High Horsepower'),
            pokemon.Move('Wood Hammer')
        ]
    )
    player1_urshifu = pokemon.Pokemon(
        species='Urshifu',
        nickname='Urshifu',
        tera_type='Dark',
        moves=[
            pokemon.Move('Wicked Blow'),
            pokemon.Move('Close Combat'),
            pokemon.Move('Sucker Punch'),
            pokemon.Move('Protect')
        ]
    )
    player1_flutter_mane = pokemon.Pokemon(
        species='Flutter Mane',
        nickname='Flutter Mane',
        tera_type='Electric',
        moves=[
            pokemon.Move('Moonblast'),
            pokemon.Move('Icy Wind', times_used=2),
            pokemon.Move('Thunderbolt'),
            pokemon.Move('Protect', times_used=1)
        ]
    )
    player1_farigiraf = pokemon.Pokemon(
        species='Farigiraf',
        nickname='Farigiraf',
        tera_type='Fairy',
        moves=[
            pokemon.Move('Psychic'),
            pokemon.Move('Dazzling Gleam'),
            pokemon.Move('Trick Room'),
            pokemon.Move('Helping Hand')
        ]
    )
    player1_team = pokemon.Team(
        pokemon=[
            player1_ogerpon_hearthflame,
            player1_regidrago,
            player1_rillaboom,
            player1_urshifu,
            player1_flutter_mane,
            player1_farigiraf
        ]
    )
    player1_info = showdown.PlayerInfo(
        player_name='Tears ricochet',
        team=player1_team,
        tera_pokemon=player1_ogerpon_hearthflame,
        leads=[player1_flutter_mane, player1_regidrago],
        brought_to_battle=[
            player1_flutter_mane,
            player1_regidrago,
            player1_ogerpon_hearthflame,
            player1_rillaboom
        ]
    )

    player2_amoonguss = pokemon.Pokemon(
        species='Amoonguss',
        nickname='Amoonguss',
        tera_type='Water',
        moves=[
            pokemon.Move('Protect', times_used=1),
            pokemon.Move('Sludge Bomb', times_used=1),
            pokemon.Move('Spore', times_used=1),
            pokemon.Move('Rage Powder', times_used=1)
        ]
    )
    player2_urshifu = pokemon.Pokemon(
        species='Urshifu-Rapid-Strike',
        nickname='Urshifu',
        tera_type='Water',
        moves=[
            pokemon.Move('Close Combat'),
            pokemon.Move('Surging Strikes'),
            pokemon.Move('Aqua Jet'),
            pokemon.Move('U-turn')
        ]
    )
    player2_flutter_mane = pokemon.Pokemon(
        species='Flutter Mane',
        nickname='Flutter Mane',
        tera_type='Fairy',
        moves=[
            pokemon.Move('Protect', times_used=2),
            pokemon.Move('Moonblast'),
            pokemon.Move('Shadow Ball', times_used=2),
            pokemon.Move('Dazzling Gleam', times_used=4)
        ]
    )
    player2_tornadus = pokemon.Pokemon(
        species='Tornadus',
        nickname='Tornadus',
        tera_type='Ghost',
        moves=[
            pokemon.Move('Protect'),
            pokemon.Move('Bleakwind Storm', times_used=2),
            pokemon.Move('Tailwind', times_used=1),
            pokemon.Move('Rain Dance')
        ]
    )
    player2_incineroar = pokemon.Pokemon(
        species='Incineroar',
        nickname='Incineroar',
        tera_type='Dragon',
        moves=[
            pokemon.Move('Fake Out'),
            pokemon.Move('Parting Shot'),
            pokemon.Move('Flare Blitz'),
            pokemon.Move('Knock Off')
        ]
    )
    player2_landorus = pokemon.Pokemon(
        species='Landorus',
        nickname='Landorus',
        tera_type='Steel',
        moves=[
            pokemon.Move('Protect'),
            pokemon.Move('Earth Power'),
            pokemon.Move('Substitute', times_used=1),
            pokemon.Move('Sludge Bomb', times_used=1)
        ]
    )
    player2_team = pokemon.Team(
        pokemon=[
            player2_amoonguss,
            player2_urshifu,
            player2_flutter_mane,
            player2_tornadus,
            player2_incineroar,
            player2_landorus
        ]
    )
    player2_info = showdown.PlayerInfo(
        player_name='Quarter Machine',
        team=player2_team,
        tera_pokemon=player2_flutter_mane,
        leads=[player2_tornadus, player2_flutter_mane],
        brought_to_battle=[
            player2_tornadus,
            player2_flutter_mane,
            player2_landorus,
            player2_amoonguss
        ]
    )
    return showdown.ShowdownReplay(
        player1_info=player1_info,
        player2_info=player2_info,
        winner=2
    )


if __name__ == '__main__':
    unittest.main()
