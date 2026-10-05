import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from backend.capture_weapons import capture_preview
from backend.combat import (create_goblin_warcamp_battle, battle_view, apply_player_command,
                            _capture_attempt, _deal_damage, _player_auto_turn, _ensure_battle_schema)
from backend.content import ITEMS, GENERAL_LOOT_TABLE, MISSION_TEMPLATES
from backend.game import new_game, combat_metrics, normalize_state
from backend.starter_equipment import STARTING_ROLES


class CaptureStarterTests(unittest.TestCase):
    def battle(self, role='captor', weapon=None):
        state = new_game({'starting_role': role})
        if weapon:
            state['inventory'].append({'instance_id':'test', 'item_id':weapon})
            state['characters'][0]['equipment']['weapon']='test'
        battle = create_goblin_warcamp_battle(state, ['player'], 'capture-tests')
        battle.update(terrain=[], elevation=[], turn_order=['player', 'gob_guard', 'gob_chief', 'gob_archer', 'gob_horn'], turn_index=0)
        actor, target = battle['units']['player'], battle['units']['gob_guard']
        actor.update(x=2,y=2)
        target.update(x=3,y=2,hp=10,max_hp=30)
        return state,battle,actor,target

    def test_every_role_has_matching_poor_gear_and_only_one_basic_training(self):
        for role, definition in STARTING_ROLES.items():
            with self.subTest(role=role):
                state=new_game({'starting_role':role, 'traits':['fire_magic','guard'], 'perks':{'magic':'master'}})
                char=state['characters'][0]
                self.assertEqual(char['traits'],[definition['perk']] if definition['perk'] else [])
                self.assertEqual([k for k,v in char['perks'].items() if v!='none'],[definition['proficiency']])
                self.assertEqual(char['perks'][definition['proficiency']],'basic')
                gear={i['item_id'] for i in state['inventory']}
                self.assertEqual(gear,set(definition['kit'])|{'worn_jacket','work_boots'})
                self.assertTrue(all(ITEMS[k]['rarity']=='common' and ITEMS[k].get('power',0)<=1 for k in definition['kit']))

    def test_medic_can_treat_and_mage_is_not_forced_into_fire_magic(self):
        legacy=new_game({'traits':['medic']})
        medic=create_goblin_warcamp_battle(legacy,['player'],'legacy-medic')['units']['player']
        self.assertIn('field_care',[s['id'] for s in medic['skills']])
        state,_,mage,_=self.battle('mage')
        self.assertEqual(mage['scaling'],'int')
        self.assertNotIn('fire_magic',state['characters'][0]['traits'])
        with self.assertRaises(ValueError):new_game({'starting_role':'medic'})

    def test_invalid_role_rejected_and_existing_saves_keep_equipment(self):
        with self.assertRaises(ValueError):new_game({'starting_role':'master assassin'})
        state=new_game({'traits':['medic']})
        equipment=deepcopy(state['characters'][0]['equipment'])
        normalize_state(state)
        self.assertEqual(state['characters'][0]['equipment'],equipment)

    def test_failed_restraint_damages_without_procs_and_is_retryable(self):
        _,b,a,t=self.battle()
        t['evasion']=0
        expected=battle_view(b)['attack_previews'][t['id']]['subdue']['damage_on_hit']
        a.update(attack=1000,element='fire',on_hit={'id':'burn','chance':100,'turns':3})
        with patch('backend.combat.random.Random') as rng, patch('backend.combat._advance_to_player'):
            rng.return_value.randint.return_value=100
            apply_player_command(b,{'action':'subdue','target_id':t['id']})
        self.assertEqual(t['hp'],10-expected)
        self.assertEqual(t['condition'],'active')
        self.assertEqual(t['statuses'],[])
        self.assertTrue(a['acted'])
        self.assertFalse(a['special_used'])
        a['acted']=False;b['turn_index']=0
        with patch('backend.combat.random.Random') as rng:
            rng.return_value.randint.return_value=1
            apply_player_command(b,{'action':'subdue','target_id':t['id']})
        self.assertEqual(t['condition'],'unconscious')
        self.assertTrue(t['alive'])
        self.assertGreater(a['combat_record']['total_damage'],0)
        self.assertEqual(a['combat_record']['subdues'],1)
        self.assertFalse(any(e['type']=='death_burst' for e in b['animation_events']))

    def test_capture_weapon_has_only_subdue_preview_and_rejects_attack(self):
        _,b,a,t=self.battle()
        previews=battle_view(b)['attack_previews'][t['id']]
        self.assertIsNone(previews['attack'])
        self.assertIsNotNone(previews['subdue'])
        before=(a['x'],a['y'],t['hp'],b.get('roll_counter'))
        with self.assertRaisesRegex(ValueError,'only use Subdue'):
            apply_player_command(b,{'action':'attack','target_id':t['id']})
        self.assertEqual((a['x'],a['y'],t['hp'],b.get('roll_counter')),before)

    def test_balanced_stats_wounds_control_and_boss_resistance(self):
        _,b,a,t=self.battle()
        a['capture_attributes']={'str':12,'dex':12,'int':12}
        balanced=capture_preview(a,t)['chance']
        a['capture_attributes']={'str':28,'dex':4,'int':4}
        self.assertLess(capture_preview(a,t)['chance'],balanced)
        t['hp']=t['max_hp'];healthy=capture_preview(a,t)['chance']
        t['hp']=1;wounded=capture_preview(a,t)['chance']
        self.assertGreater(wounded,healthy)
        t['statuses']=[{'id':'bind'}]
        self.assertGreater(capture_preview(a,t)['chance'],wounded)
        t['statuses']=[];t['boss']=True
        self.assertLess(capture_preview(a,t)['chance'],wounded)

    def test_preview_matches_attempt_and_polling_cannot_roll(self):
        _,b,a,t=self.battle(weapon='goblin_net_bow')
        preview=battle_view(b)['attack_previews'][t['id']]['subdue']
        self.assertTrue(preview['capture'])
        for _ in range(4):battle_view(b)
        self.assertNotIn('roll_counter',b)
        with patch('backend.combat.random.Random') as rng:
            rng.return_value.randint.return_value=preview['chance']+1
            _capture_attempt(b,a,t)
        self.assertEqual(t['hp'],10-preview['damage_on_hit'])
        self.assertEqual(b['roll_counter'],1)
        self.assertIn(f"vs {preview['chance']}% capture chance",b['log'][-1])

    def test_capture_range_and_structures(self):
        _,b,a,t=self.battle(weapon='patrol_capture_net')
        t['x']=4
        self.assertIsNotNone(battle_view(b)['attack_previews'][t['id']]['subdue'])
        t['x']=7
        with self.assertRaises(ValueError):_capture_attempt(b,a,t)
        b['terrain']=[{'id':'wall','kind':'wall','name':'Wall','x':3,'y':2,'destructible':True,'hp':10,'armor':0}]
        self.assertEqual(battle_view(b)['terrain_targets'],[])
        with self.assertRaisesRegex(ValueError,'structures'):
            apply_player_command(b,{'action':'attack','target_id':'wall'})
        self.assertEqual(b['terrain'][0]['hp'],10)

    def test_no_unarmed_blunt_or_glove_capture_loophole(self):
        for weapon in ['worn_mallet','knotted_staff','watchmans_cudgel','mercykeepers_maul','triage_baton']:
            _,b,a,t=self.battle('fighter',weapon)
            a['gear_rules']['subdue_gloves']=True
            a['nonlethal_capable']=True
            self.assertIsNone(battle_view(b)['attack_previews'][t['id']]['subdue'])
            with self.assertRaisesRegex(ValueError,'capture weapon'):
                apply_player_command(b,{'action':'subdue','target_id':t['id']})
            self.assertEqual(t['hp'],10)

    def test_cudgel_only_converts_killing_direct_blow_on_5_percent_roll(self):
        for roll, condition in [(5,'unconscious'),(6,'dead')]:
            _,b,a,t=self.battle('fighter','watchmans_cudgel')
            a['attack']=100
            with patch('backend.combat.random.Random') as rng:
                rng.return_value.randint.return_value=roll
                _deal_damage(b,a,t)
            self.assertEqual(t['condition'],condition)
        _,b,a,t=self.battle('fighter','watchmans_cudgel')
        a['attack']=2;t['hp']=100
        _deal_damage(b,a,t)
        self.assertNotIn('finisher_counter',b)
        a.update(attack=1000,status_tick=True)
        _deal_damage(b,a,t)
        self.assertEqual(t['condition'],'dead')

    def test_cudgel_does_not_convert_an_unrelated_gear_spell(self):
        _,b,a,t=self.battle('fighter','watchmans_cudgel')
        with patch('backend.combat.random.Random') as rng:
            rng.return_value.randint.return_value=1
            _deal_damage(b,a,t,ability={'attack':1000,'source_name':'Field Projector','elevation_rule':'ignore'})
        self.assertEqual(t['condition'],'dead')
        self.assertNotIn('finisher_counter',b)

    def test_auto_capture_does_not_use_lethal_basic_or_spend_focus(self):
        _,b,a,t=self.battle(weapon='goblin_net_bow')
        for unit in b['units'].values():
            if unit['team']=='enemy' and unit is not t:unit.update(alive=False,conscious=False,condition='dead')
        for obj in b['objects'].values():obj['state']='opened' if obj['id']=='prisoner_pen' else 'disabled'
        with patch('backend.combat.random.Random') as rng:
            rng.return_value.randint.return_value=1
            _player_auto_turn(b,a,'balanced')
        self.assertEqual(t['condition'],'unconscious')
        self.assertFalse(a['special_used'])

    def test_saved_blunt_permissions_are_removed_and_old_net_becomes_capture(self):
        for weapon,enabled in [('worn_mallet',False),('goblin_net_bow',True)]:
            _,b,a,t=self.battle('fighter',weapon)
            a.pop('capture_weapon');a['nonlethal_capable']=True
            _ensure_battle_schema(b)
            self.assertEqual(bool(a['capture_weapon']),enabled)
            self.assertEqual(a['nonlethal_capable'],enabled)

    def test_capture_does_not_contribute_damage_role_rating(self):
        state,_,_,_=self.battle()
        self.assertEqual(combat_metrics(state,state['characters'][0])['dps'],0)

    def test_capture_loot_progresses_and_exclusives_are_not_in_general_pool(self):
        general={iid:rank for iid,rank,_ in GENERAL_LOOT_TABLE}
        self.assertEqual(general['patrol_capture_net'],'E')
        self.assertEqual(general['weighted_capture_net'],'D')
        for iid in ['warcamp_master_mesh','starless_containment_lens']:
            self.assertNotIn(iid,general)
            self.assertIn('mission_exclusive',ITEMS[iid]['tags'])
        drop=next(r for r in MISSION_TEMPLATES['door_between_dead_stars']['reward_rolls'] if r.get('reward',{}).get('item')=='starless_containment_lens')
        self.assertTrue(drop['requires_chain_parent'])
        self.assertLess(drop['chance'],10)
        root=Path(__file__).resolve().parents[1]
        for item in ITEMS.values():
            if item.get('capture_weapon'):self.assertTrue((root/('frontend/public'+item['icon'])).exists())





    def test_restraint_stops_at_one_hp_and_does_not_bypass_boss_capture(self):
        _,b,a,t=self.battle()
        t.update(hp=2,boss=True,evasion=0)
        with patch('backend.combat._capture_preview',return_value={'chance':0,'hit_chance':100}):
            for _ in range(6):_capture_attempt(b,a,t)
        self.assertEqual(t['hp'],1)
        self.assertEqual(t['condition'],'active')
        self.assertTrue(t['alive'])
        self.assertEqual(a['combat_record']['total_damage'],1)
        self.assertFalse(any(e['type'] in {'death_burst','knockout'} for e in b['animation_events']))

    def test_missed_net_does_not_damage_and_barrier_absorbs_landed_squeeze(self):
        from backend import combat_conditions as conditions
        _,b,a,t=self.battle()
        with patch('backend.combat._capture_preview',return_value={'chance':0,'hit_chance':0}):_capture_attempt(b,a,t)
        self.assertEqual(t['hp'],10)
        self.assertFalse(next(e for e in b['animation_events'] if e['type']=='net_cast')['hit'])
        conditions.barrier(t,20,2,a)
        preview=battle_view(b)['attack_previews'][t['id']]['subdue']
        self.assertEqual(preview['damage_on_hit'],0)
        with patch('backend.combat._capture_preview',return_value={'chance':0,'hit_chance':100}):_capture_attempt(b,a,t)
        self.assertEqual(t['hp'],10)
        self.assertLess(next(s['amount'] for s in t['statuses'] if s['id']=='barrier'),20)

    def test_capture_damage_scales_slowly_and_remains_below_standard_weapons(self):
        from backend.capture_weapons import capture_power
        for stats in [4,12,50,200]:
            actor={'capture_weapon':{'base':8},'capture_attributes':dict.fromkeys(('str','dex','int'),stats)}
            self.assertLess(capture_power(actor),5+stats//2)


if __name__=='__main__':unittest.main()
