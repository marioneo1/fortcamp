"""Rank arithmetic, twelve legal encounters and recruitable role continuity."""
import json
import unittest
from collections import deque
from copy import deepcopy

from backend import combat
from backend.battle_lab import catalogue, layout_presets
from backend.battle_maps import occupied_tiles, validate_battle_map
from backend.combat_pacing import enemy_budget, scaled, scale_unit
from backend.d_rank_locations import LOCATIONS
from backend.game import new_game
from backend.job_loadouts import JOBS
from backend.location_maps import location_blueprint
from backend.prison_recruitment import initialize_prisoner
from backend.races import race_gameplay
from backend.mission_decisions import setup_encounter


class RankScalingTests(unittest.TestCase):
    def test_ranks_are_e_relative_and_do_not_compound(self):
        for race in ('Human','Goblin','Undead','Ogre','Fairy'):
            for commander in (False,True):
                base=enemy_budget('E',commander,race_gameplay(race))
                for rank,percent in zip('EDCBAS',(100,130,160,190,220,250)):
                    actual=enemy_budget(rank,commander,race_gameplay(race))
                    for key,value in base.items():
                        self.assertEqual(actual[key],(value*percent+50)//100)
        self.assertEqual(scaled(100,'S'),250)
        self.assertEqual(scaled(5,'D'),7)
        self.assertEqual(scaled(0,'S'),0)

    def test_role_rules_are_not_scaled_and_metadata_survives_saving(self):
        unit=dict(hp=100,max_hp=100,attack=10,armor=4,strength=10,agility=10,
                  intelligence=10,move=3,attack_range=3,evasion=12,
                  resistances={'stun':25},cooldowns={'test':3})
        scale_unit(unit,'D')
        restored=json.loads(json.dumps(unit))
        self.assertEqual(restored['hp'],130)
        self.assertEqual(restored['strength'],13)
        self.assertEqual(restored['move'],3)
        self.assertEqual(restored['attack_range'],3)
        self.assertEqual(restored['evasion'],12)
        self.assertEqual(restored['resistances'],{'stun':25})
        self.assertEqual(restored['cooldowns'],{'test':3})


class DRankMapTests(unittest.TestCase):
    def battles(self):
        for location,mid in LOCATIONS.items():
            presets=layout_presets('contract:'+mid)
            self.assertEqual(len(presets),4)
            for preset in presets:
                yield location,mid,preset,combat.create_contract_battle(
                    new_game({'name':'QA'}),['player'],preset['seed'],mid,True)

    def test_all_twelve_plans_are_repeatable_legal_and_connected(self):
        templates=set()
        for location,mid,preset,battle in self.battles():
            raw=location_blueprint(location,preset['seed'])
            self.assertEqual(raw,location_blueprint(location,preset['seed']))
            self.assertEqual(validate_battle_map(location,raw),[])
            self.assertEqual(battle['template_id'],preset['id'])
            templates.add(preset['id'])
            probe=deepcopy(battle);probe['units']={}
            for tile in probe['terrain']:
                if tile['kind']=='gate':tile.update(state='opened',blocking=False,blocks_sight=False)
            positions={(u['x'],u['y']) for u in battle['units'].values()}
            bodies=[u for u in battle['units'].values() if not u.get('rider_id')]
            self.assertEqual(len({(u['x'],u['y']) for u in bodies}),len(bodies))
            for endpoint in ('extraction','enemy_extraction'):
                reached={(p['x'],p['y']) for p in probe[endpoint]['tiles']}
                queue=deque(reached)
                while queue:
                    x,y=queue.popleft()
                    for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                        if (nx,ny) not in reached and combat._can_step(probe,x,y,nx,ny,{'id':'walker'}):
                            reached.add((nx,ny));queue.append((nx,ny))
                self.assertTrue(positions<=reached,(mid,preset['id'],endpoint,positions-reached))
            for x,y in positions:self.assertFalse(combat._blocked(probe,x,y))
            solids=[p for t in raw['terrain'] if not t.get('edge_wall') for p in occupied_tiles(t)]
            self.assertEqual(len(solids),len(set(solids)))
            walls={p for t in raw['terrain'] if t.get('edge_wall') for p in occupied_tiles(t)}
            self.assertFalse(positions & walls,(mid,preset['id'],'spawn overlaps a boundary wall'))
        self.assertEqual(len(templates),12)

    def test_count_changes_preserve_the_difficulty_band_and_real_kits(self):
        budgets={mid:[] for mid in LOCATIONS.values()}
        for _,mid,_,battle in self.battles():
            enemies=[u for u in combat._living(battle,'enemy') if not u.get('boar_mount')]
            self.assertEqual(len(enemies),4 if battle['map_variation']==4 else 3)
            budgets[mid].append(sum(u['max_hp'] for u in enemies))
            for unit in enemies:
                self.assertGreaterEqual(unit['max_hp'],20)
                self.assertTrue(unit['portrait'])
                self.assertTrue(unit['skills'])
                self.assertFalse(unit['boss'])
                self.assertEqual(unit['rank_scaling']['rank'],'D')
                self.assertEqual(unit['rank_scaling']['method'],'attributes_once')
                self.assertEqual(unit['recruitable_snapshot']['adventurer_rank'],'D')
                self.assertEqual(unit['recruitable_snapshot']['attributes'],unit['rank_scaling']['attribute_baseline'])
                if mid=='goblin_boar_riders':
                    self.assertIn('rider',unit['origin_perks'])
                    self.assertEqual(combat._movement_limit(unit),unit['move']+(1 if unit.get('animal_mount_id') else 0))
                if mid=='bone_patrol':self.assertEqual(unit['armor_material'],'chain')
        for mid,values in budgets.items():self.assertLessEqual(max(values)/min(values),1.15,mid)

    def test_recruits_keep_unranked_attributes_rank_specialties_and_normal_starter_pool(self):
        for _,mid,_,battle in self.battles():
            if mid=='bone_patrol':continue
            for unit in combat._living(battle,'enemy'):
                if unit.get('boar_mount'):continue
                captive={'id':'recruit','name':unit['name'],'race':unit['race'],
                         'recruitable_snapshot':deepcopy(unit['recruitable_snapshot'])}
                initialize_prisoner(captive,now=0)
                candidate=captive['recruitment']['candidate']
                self.assertEqual(candidate['equipped_skills'],unit['skill_slot_order'])
                self.assertEqual(candidate['attributes'],unit['recruitable_snapshot']['attributes'])
                self.assertTrue(set(JOBS[unit['job_id']]['starter_skills'])<=set(candidate['learned_skills']))

    def test_lab_lists_all_four_layouts_for_each_mission(self):
        indexed={row['id']:row for row in catalogue()}
        for mid in LOCATIONS.values():
            self.assertEqual(len(indexed[mid]['variants'][0]['layout_presets']),4)

    def test_ambush_story_matches_a_patrol_and_keeps_legacy_sleep_definition(self):
        battle=combat.create_contract_battle(new_game({}),['player'],'story','bone_patrol',True)
        setup_encounter(battle,{'setup':'ambush'})
        view=combat.battle_view(battle)
        self.assertEqual(view['status_definitions']['ambush_sleep']['name'],'Unaware Patrol')
        self.assertEqual(combat.STATUS_DEFINITIONS['ambush_sleep']['name'],'Sleeping camp')
        self.assertTrue(all(any(s['id']=='ambush_sleep' for s in u['statuses']) for u in combat._living(battle,'enemy')))
        combat._wake_ambush(battle,battle['units']['contract_enemy_0'])
        self.assertFalse(any(s['id']=='ambush_sleep' for u in combat._living(battle,'enemy') for s in u['statuses']))
        self.assertIn('alerts the whole patrol',battle['log'][-1])


if __name__=='__main__':unittest.main()
