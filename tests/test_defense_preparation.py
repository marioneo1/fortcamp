import unittest
from copy import deepcopy

from backend import combat as c, combat_defense as d, combat_engineer as e, combat_conditions as conditions
from backend.game import new_game
from backend.job_loadouts import SKILLS


class DefensePreparationTests(unittest.TestCase):
    def battle(self, job='fighter', kinds=()):
        state=new_game({'name':'Builder','starting_role':job})
        actor=state['characters'][0]
        keys=[f'job:{job}:{kind}' for kind in kinds]
        if keys:actor.update(learned_skills=keys,equipped_skills=keys)
        return c.create_frontier_watch_defense_battle(state,['player'],'defense-v2-test')

    def place(self,b,kind,x,y,**extra):
        option=next(o for o in b['preparation']['available'] if o.get('deploy_kind',o['id'])==kind)
        c._place_prepared_defense(b,{'placement_id':option['id'],'x':x,'y':y,**extra})
        return b['preparation']['placements'][-1]

    def test_loadout_unlocks_are_free_and_not_from_unequipped_skills_or_gear(self):
        b=self.battle('engineer',('sentry_turret','proximity_charge'))
        options=b['preparation']['available']
        free=[o for o in options if o['cost']==0]
        self.assertEqual({o['deploy_kind'] for o in free},{'sentry_turret','proximity_charge'})
        self.assertEqual(next(o for o in options if o['id']=='proximity_dynamite')['cost'],2)
        self.assertEqual(next(o for o in self.battle()['preparation']['available'] if o['id']=='proximity_dynamite')['cost'],3)
        self.assertEqual(self.battle()['preparation']['base_budget'],16)
        self.assertFalse(any(o['id'] in {'spike_trap','snare_trap','watch_platform'} for o in options))

    def test_no_barrier_caps_but_point_costs_and_monotonic_ids_apply(self):
        b=self.battle()
        for y in (2,3,4,5):self.place(b,'palisade',5,y)
        self.assertEqual(len(b['preparation']['placements']),4)
        row=b['preparation']['placements'][1]
        c._remove_prepared_defense(b,{'target_id':row['id']})
        new=self.place(b,'wall',5,3)
        self.assertNotEqual(row['id'],new['id'])
        self.assertEqual(len({r['id'] for r in b['preparation']['placements']}),4)
        self.assertEqual(b['preparation']['remaining'],12)

    def test_npc_tripline_does_not_unlock_unequipped_caltrops(self):
        b=self.battle('rogue')
        actor=b['units']['player']
        actor['skills']=[deepcopy(SKILLS['npc:bandit:tripline'])]
        self.assertFalse(any(o.get('deploy_kind')=='caltrops' for o in d.options(b['units'])))

    def test_turret_limits_shared_with_combat_and_removal_restores_slots(self):
        b=self.battle('engineer',('sentry_turret','heavy_emplacement'))
        actor=b['units']['player'];budget=b['preparation']['remaining']
        for y in (2,3,4):self.place(b,'sentry_turret',5,y)
        self.place(b,'heavy_emplacement',6,2)
        self.assertEqual(b['preparation']['remaining'],budget)
        self.assertTrue(all(not u['under_construction'] for u in e.machines(b,actor)))
        with self.assertRaisesRegex(ValueError,'slots'):self.place(b,'sentry_turret',5,4)
        with self.assertRaisesRegex(ValueError,'slots'):self.place(b,'heavy_emplacement',6,2)
        with self.assertRaises(ValueError):c._deploy_prepared_unit(b,{'target_id':e.machines(b,actor)[0]['id'],'x':1,'y':2})
        c._remove_prepared_defense(b,{'target_id':b['preparation']['placements'][0]['id']})
        self.place(b,'sentry_turret',5,2)
        self.assertEqual(len(e.machines(b,actor)),4)

    def test_engineer_mine_limit_one_and_normal_battle_limit_unchanged(self):
        b=self.battle('engineer',('proximity_charge',))
        row=self.place(b,'proximity_charge',5,2)
        with self.assertRaisesRegex(ValueError,'armed mine'):self.place(b,'proximity_charge',5,3)
        self.assertEqual(b['units']['player']['defense_mine_limit'],1)
        c._remove_prepared_defense(b,{'target_id':row['id']})
        self.assertFalse(b['engineer_hazards'])
        self.place(b,'proximity_charge',5,3)
        self.assertNotIn('defense_mine_limit',c._player_unit(new_game({'starting_role':'engineer'}),new_game({'starting_role':'engineer'})['characters'][0],1,1))

    def test_multiple_caltrop_strips_rotate_validate_and_remove_without_replacing_each_other(self):
        b=self.battle('rogue',('caltrops',))
        first=self.place(b,'caltrops',6,2)
        second=self.place(b,'caltrops',8,5,vertical=True)
        self.assertEqual(len(b['zones']),2)
        self.assertEqual({(p['x'],p['y']) for p in b['zones'][1]['cells']},{(8,4),(8,5),(8,6)})
        self.assertEqual(b['preparation']['remaining'],b['preparation']['budget'])
        with self.assertRaises(ValueError):self.place(b,'caltrops',5,1)
        c._remove_prepared_defense(b,{'target_id':first['id']})
        self.assertEqual([z['id'] for z in b['zones']],[second['zone_id']])

    def test_pit_interrupts_route_once_and_climbing_consumes_main_action(self):
        b=self.battle();self.place(b,'pit',5,3)
        enemy=next(u for u in b['units'].values() if u['team']=='enemy')
        enemy.update(x=4,y=3,hp=100,max_hp=100,armor=0,statuses=[],racial_resistances=[],racial_weaknesses=[])
        start=(4,3);path=[(5,3),(6,3),(7,3)]
        c._record_movement(b,enemy,start,path);enemy.update(x=7,y=3)
        c._apply_zone_route(b,enemy,path)
        self.assertEqual((enemy['x'],enemy['y']),(5,3))
        self.assertEqual(enemy['hp'],75)
        self.assertTrue(conditions.has(enemy,'pit_trapped'))
        c._apply_tile_entry(b,enemy);self.assertEqual(enemy['hp'],75)
        self.assertFalse(c._can_attack(b,enemy,b['units']['player'],99))
        enemy.update(acted=False,ability_activation=1)
        e.start(b,enemy)
        c._climb_out(b,enemy,(4,3))
        self.assertTrue(enemy['acted'])
        self.assertFalse(conditions.has(enemy,'pit_trapped'))

    def test_pit_ignores_allies_flying_and_handles_forced_entry_without_double_fall(self):
        b=self.battle();self.place(b,'pit',5,3)
        actor=b['units']['player'];actor.update(x=5,y=3)
        hp=actor['hp'];d.pit_entry(b,actor);self.assertEqual(actor['hp'],hp)
        enemy=next(u for u in b['units'].values() if u['team']=='enemy')
        enemy.update(x=5,y=3,movement_type='flying',hp=100,max_hp=100)
        d.pit_entry(b,enemy);self.assertEqual(enemy['hp'],100)
        enemy.update(x=4,y=3,movement_type='ground',armor=0,statuses=[],displacement_resistance=0)
        actor.update(x=3,y=3)
        c._apply_displacement(b,actor,enemy,{'mode':'push','distance':2,'collision_damage':False},0)
        self.assertEqual(enemy['hp'],75)
        self.assertTrue(conditions.has(enemy,'pit_trapped'))

    def test_proximity_dynamite_waits_for_entry_and_blast_pushes_without_stun(self):
        b=self.battle();self.place(b,'proximity_dynamite',5,3)
        actor=b['units']['player'];actor.update(x=3,y=3,hp=200,max_hp=200,displacement_resistance=0,statuses=[])
        e.start(b,actor);self.assertEqual(len(b['engineer_hazards']),1)
        actor.update(x=4,y=3);e.entry(b,actor)
        self.assertFalse(b['engineer_hazards'])
        self.assertLess(actor['hp'],200)
        self.assertEqual((actor['x'],actor['y']),(3,3))
        self.assertFalse(conditions.has(actor,'stun'))

    def test_prepared_timed_dynamite_survives_first_start(self):
        b=self.battle('engineer',('dynamite',));self.place(b,'dynamite',5,3)
        actor=b['units']['player']
        actor['ability_activation']=1;e.start(b,actor)
        self.assertEqual(len(b['engineer_hazards']),1)
        actor['ability_activation']=2;e.start(b,actor)
        self.assertFalse(b['engineer_hazards'])

    def test_preview_does_not_trigger_armed_blast(self):
        from backend.combat_hazard_preview import forecast
        b=self.battle();self.place(b,'proximity_dynamite',5,3)
        actor=b['units']['player'];snapshot=deepcopy(b)
        warning=forecast(b,actor,[(3,3),(4,3),(5,3)],c._combat_active,c._damage_before_barrier,c._living)
        self.assertGreater(warning['damage'],0)
        self.assertIn('proximity_blast',warning['effects'])
        self.assertEqual(b,snapshot)
