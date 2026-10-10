import random
import re
import unittest

from backend.character_names import catalogue, generate_name, name_key, name_rng
from backend.races import RACE_CATALOG, generated_genders
from backend.game import _make_generic, _make_procedural, new_game, normalize_state
from backend.combat import create_contract_battle, create_goblin_warcamp_battle, _ensure_battle_schema
from tools.import_race_names import compile_pools, ROOT


class CharacterNameTests(unittest.TestCase):
    def assert_compatible(self, name, race, gender, leader=False):
        entry = catalogue()['races'][race]
        pool = entry['leader_given_names' if leader else 'given_names']
        allowed = pool[gender] + pool['shared']
        def regex(fmt):
            pattern = re.escape(fmt)
            for key, values in {'given':allowed, **entry['second_names']}.items():
                pattern = pattern.replace(re.escape('{'+key+'}'), '(?:'+'|'.join(re.escape(v) for v in values)+')')
            return pattern
        self.assertTrue(any(re.fullmatch(regex(fmt), name) for fmt in entry['leader_formats' if leader else 'ordinary_formats']
                            if '{title}' not in fmt and '{epithet}' not in fmt), (race, gender, name))

    def test_import_matches_runtime_and_canonical_catalogue(self):
        data, report = compile_pools(ROOT/'docs/content/drafts/names')
        self.assertEqual(data, catalogue())
        self.assertEqual(set(data['races']), set(RACE_CATALOG))
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['removed'], [])
        self.assertEqual(report['totals'], {'given_names':5840,'leader_given_names':1008,'second_names':1680})

    def test_all_races_genders_and_tiers_generate_compatible_unique_names(self):
        for race in RACE_CATALOG:
            for gender in generated_genders(race):
                for leader in (False, True):
                    rng = random.Random(f'{race}:{gender}:{leader}'); used = []
                    for _ in range(40):
                        name = generate_name(race, gender, rng, leader=leader, used_names=used)
                        self.assertLessEqual(len(name),48)
                        self.assertNotIn(name_key(name),{name_key(n) for n in used})
                        self.assert_compatible(name,race,gender,leader)
                        used.append(name)

    def test_seed_reproducible_and_naming_does_not_consume_combat_rng(self):
        a=random.Random(34); b=random.Random(34)
        self.assertEqual(generate_name('Human','female',name_rng(a)),generate_name('Human','female',name_rng(b)))
        self.assertEqual(a.getstate(),b.getstate())
        self.assertEqual(a.getstate(),random.Random(34).getstate())

    def test_titles_and_epithets_require_explicit_context(self):
        for race in RACE_CATALOG:
            gender=generated_genders(race)[0]
            for seed in range(10):self.assert_compatible(generate_name(race,gender,random.Random(seed),leader=True),race,gender,True)
        entry=catalogue()['races']['Goblin']
        record=next(r for r in entry['leader_titles'] if r['gender'] in {'male','any'})
        names=[generate_name('Goblin','male',random.Random(seed),leader=True,role_context=record['role_context']) for seed in range(100)]
        self.assertTrue(any(record['text'] in n for n in names))

    def test_recruit_integration_uses_final_gender_and_existing_roster_exclusions(self):
        for profile in ('goblin','goblin_boss','dryad','banshee','automaton','dragonkin','vampire'):
            first=_make_procedural(profile,random.Random(29))
            second=_make_procedural(profile,random.Random(29),[first['name']])
            self.assertNotEqual(first['name'],second['name'])
            self.assert_compatible(first['name'],first['race'],first['gender'],profile=='goblin_boss')
        person=_make_generic('fighter',random.Random(7))
        self.assert_compatible(person['name'],'Human',person['gender'])

    def test_new_contracts_use_race_specific_names_and_keep_player_name(self):
        state=new_game({'name':'Tarin Fen'})
        for mission,race in [('highway_ambush','Human'),('goblin_pickpockets','Goblin'),('ruined_well','Human'),('hobgoblin_vanguard','Hobgoblin'),('bone_patrol','Undead')]:
            battle=create_contract_battle(state,[state['characters'][0]['id']],'name-test',mission,defer_start=True)
            enemies=[u for u in battle['units'].values() if u['team']=='enemy']
            self.assertEqual(len({name_key(u['name']) for u in enemies}),len(enemies))
            for u in enemies:
                # E-rank profiles remove the leader flag after initial roster generation.
                entry=catalogue()['races'][u['race']]
                all_given={v for group in ('given_names','leader_given_names') for values in entry[group].values() for v in values}
                self.assertTrue(any(v in u['name'] for v in all_given))
            self.assertEqual(battle['units'][state['characters'][0]['id']]['name'],'Tarin Fen')

    def test_existing_people_and_battle_names_are_not_rewritten(self):
        state=new_game({'name':'My Hero'})
        state['characters'].append(_make_procedural('goblin',random.Random(1)))
        state['characters'][-1]['name']='Nikka Rusttooth'
        names=[c['name'] for c in state['characters']]
        normalize_state(state)
        self.assertEqual([c['name'] for c in state['characters']],names)
        battle=create_goblin_warcamp_battle(state,[state['characters'][0]['id']],'saved',defer_start=True)
        battle['units']['gob_guard']['name']='Old Saved Goblin'
        _ensure_battle_schema(battle)
        self.assertEqual(battle['units']['gob_guard']['name'],'Old Saved Goblin')

    def test_disallowed_gender_rejected(self):
        with self.assertRaises(ValueError):generate_name('Dryad','male',random.Random(1))
