import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_cleric as cleric, job_loadouts as jobs
from tests.test_mage_jobs import MageTests

class ClericTests(unittest.TestCase):
 def fixture(self,keys=('mend','heal','sanctuary','rest','smite','holy_light'),priest=False):
  b,a,t=MageTests().fixture([])
  a.update(job_id='cleric',skills=[deepcopy(jobs.SKILLS['job:cleric:'+k]) for k in keys],passives=[deepcopy(jobs.SKILLS['job:cleric:battle_priest'])] if priest else [],intelligence=12)
  ally={**deepcopy(a),'id':'ally','x':a['x']+1,'hp':10,'max_hp':100,'skills':[],'passives':[],'statuses':[]}
  b['units']['ally']=ally
  cleric.adapt(a)
  return b,a,t,ally
 def skill(self,a,key):return next(s for s in a['skills'] if s['cleric_kind']==key)
 def test_pool_and_migration_are_stable(self):
  self.assertEqual(len([s for s in jobs.SKILLS if s.startswith('job:cleric:')]),8)
  old={'job_id':'cleric','learned_skills':['job:cleric:cleanse','job:cleric:steadfast'],'equipped_skills':['job:cleric:cleanse'],'job_practice':10}
  jobs.initialize(old);first=deepcopy(old);jobs.initialize(old)
  self.assertEqual(old,first);self.assertIn('job:cleric:heal',old['equipped_skills']);self.assertEqual(old['job_practice'],10)
 def test_mend_is_capped_and_heal_uses_target_hp(self):
  b,a,t,ally=self.fixture()
  self.assertEqual(cleric.healing(a,ally,'mend'),12)
  a['intelligence']=100;self.assertEqual(cleric.healing(a,ally,'mend'),15)
  cleric.execute(b,a,ally,self.skill(a,'heal'));self.assertEqual(ally['hp'],50)
  self.assertEqual(a['ability_state']['job:cleric:heal']['uses'],1)
 def test_exhaustion_is_per_battle_and_resume_does_not_reset_it(self):
  b,a,t,ally=self.fixture();s=self.skill(a,'heal')
  a['ability_state']={s['id']:{'uses':2}}
  combat._ensure_battle_schema(b)
  self.assertFalse(combat.abilities.availability(a,s)['available'])
  with self.assertRaises(ValueError):cleric.command(b,a,s,{'target_id':ally['id']})
  other=self.fixture()[1];self.assertTrue(combat.abilities.availability(other,self.skill(other,'heal'))['available'])
 def test_rest_recovery_session_and_no_duplicate_finish(self):
  b,a,t,ally=self.fixture();a['hp']=10
  a['ability_state']={'job:cleric:'+k:{'uses':v} for k,v in cleric.LIMITS.items()}
  cleric.execute(b,a,a,self.skill(a,'rest'))
  for turn in range(1,4):
   a['status_activation']=[turn,0];cleric.finish(b,a);cleric.finish(b,a)
  self.assertEqual(a['cleric_rest']['turns'],3)
  self.assertEqual([a['ability_state']['job:cleric:'+k]['uses'] for k in cleric.LIMITS],[2,1,0])
  cleric.stop_rest(a);a['acted']=False;cleric.execute(b,a,a,self.skill(a,'rest'));self.assertEqual(a['cleric_rest']['turns'],0)
 def test_rest_vulnerability_applies_to_dots_and_direct_hit_interrupts(self):
  b,a,t,ally=self.fixture();cleric.execute(b,a,a,self.skill(a,'rest'))
  self.assertEqual(cleric.incoming(a,20),35)
  self.assertEqual(combat._damage_before_barrier(b,{'attack':20,'status_tick':True,'percent_dot':'poison'},a),cleric.incoming(a,20))
  combat._deal_damage(b,t,a,resolved_damage=1);self.assertNotIn('cleric_rest',a)
 def test_priest_transforms_all_three_heals_and_keeps_rest(self):
  b,a,t,ally=self.fixture(priest=True)
  for key,cd in [('mend',3),('heal',5),('sanctuary',6)]:
   s=self.skill(a,key);self.assertTrue(s['self_only']);self.assertEqual(s['cost'],{'cooldown':cd,'charges':None})
   with self.assertRaises(ValueError):cleric.command(b,a,s,{'target_id':ally['id']})
  self.assertEqual(self.skill(a,'sanctuary')['name'],'Regeneration')
  a['ability_state']={'job:cleric:heal':{'uses':8}}
  cleric.execute(b,a,a,self.skill(a,'rest'));a['status_activation']=[1,0];cleric.finish(b,a)
  self.assertEqual(a['ability_state']['job:cleric:heal']['uses'],8)
 def test_regeneration_exactly_three_start_ticks(self):
  b,a,t,ally=self.fixture(priest=True);a['hp']=1
  cleric.execute(b,a,a,self.skill(a,'sanctuary'))
  for _ in range(4):cleric.start(b,a)
  self.assertEqual(a['hp'],19);self.assertFalse(combat.conditions.has(a,'cleric_regeneration'))
 def test_sanctuary_square_scaled_healing_no_movement_follow(self):
  b,a,t,ally=self.fixture();s=self.skill(a,'sanctuary')
  cleric.execute(b,a,ally,s);zone=b['zones'][0]
  self.assertEqual(len(zone['cells']),9);self.assertEqual(zone['heal'],6)
  previous=deepcopy(zone['cells']);a['x']+=2;self.assertEqual(zone['cells'],previous)
  combat._trigger_zones(b,ally,'start');self.assertEqual(ally['hp'],16)
  combat._trigger_zones(b,ally,'start');self.assertEqual(ally['hp'],16)
 def test_smite_quick_action_movement_and_two_damage_components(self):
  b,a,t,ally=self.fixture();a.update(attack=20,attack_elevation_rule='melee',armor=0);t.update(armor=0,x=a['x']+1,y=a['y'])
  cleric.execute(b,a,a,self.skill(a,'smite'));self.assertFalse(a['acted']);self.assertEqual(combat._movement_limit(a),1)
  before=t['hp']
  with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
   combat._perform_attack(b,a,t,'melee')
  self.assertEqual(before-t['hp'],32)
  events=[e for e in b['animation_events'] if e['type']=='combat_feedback' and e.get('amount')]
  self.assertTrue(any(e['kind']=='magic' and e['amount']==12 for e in events))
  self.assertTrue(all('attack_packet' in e for e in events))
 def test_holy_light_cross_hits_enemies_and_blinds_not_diagonals_or_allies(self):
  b,a,t,ally=self.fixture();a.update(x=3,y=3);t.update(x=3,y=4)
  diagonal={**deepcopy(t),'id':'diagonal','x':4,'y':4};b['units']['diagonal']=diagonal
  ally.update(x=3,y=2);before=ally['hp'];s=self.skill(a,'holy_light')
  with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)),patch('backend.combat_mage.roll',return_value=1):cleric.execute(b,a,a,s)
  self.assertEqual(t['hp'],482);self.assertTrue(combat.conditions.has(t,'blind'));self.assertEqual(diagonal['hp'],500);self.assertEqual(ally['hp'],before)
 def test_preview_is_read_only_and_priest_sanctuary_is_not_ground(self):
  b,a,t,ally=self.fixture();before=deepcopy(b);combat.battle_view(b);self.assertEqual(b,before)
  b,a,t,ally=self.fixture(priest=True);view=combat.battle_view(b)
  self.assertNotIn('job:cleric:sanctuary',view['ground_skill_previews'])
  self.assertIn(a['id'],view['skill_previews']['job:cleric:sanctuary'])

 def test_rest_real_command_completes_turn_and_cancel_is_free(self):
  b,a,t,ally=self.fixture();b.update(turn_order=[a['id'],ally['id']],turn_index=0)
  combat._current_unit(b)
  with patch('backend.combat._advance_to_player'):
   combat.apply_player_command(b,{'action':'skill','skill_id':'job:cleric:rest','target_id':a['id']})
  self.assertEqual(a['cleric_rest']['turns'],1);self.assertEqual(b['turn_index'],1)
  a['acted']=False;b['turn_index']=0
  combat.apply_player_command(b,{'action':'skill','skill_id':'job:cleric:rest','target_id':a['id']})
  self.assertNotIn('cleric_rest',a);self.assertEqual(b['turn_index'],0);self.assertFalse(a['acted'])
 def test_mend_real_command_spends_only_one_charge(self):
  b,a,t,ally=self.fixture();b.update(turn_order=[a['id'],ally['id']],turn_index=0)
  with patch('backend.combat._advance_to_player'):
   combat.apply_player_command(b,{'action':'skill','skill_id':'job:cleric:mend','target_id':ally['id']})
  self.assertEqual(ally['hp'],22);self.assertEqual(a['ability_state']['job:cleric:mend']['uses'],1)
 def test_smite_respects_magic_resistance_barrier_and_no_double_exorcist(self):
  b,a,t,ally=self.fixture();a.update(attack=20,attack_elevation_rule='melee',passives=[deepcopy(jobs.SKILLS['job:cleric:exorcist'])]);t.update(armor=0,racial_resistances=['magic'],race='Undead')
  combat.conditions.barrier(t,25,2,t)
  cleric.execute(b,a,a,self.skill(a,'smite'))
  with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)),patch('backend.combat_cleric.exorcist') as proc:
   combat._perform_attack(b,a,t,'melee')
  self.assertEqual(t['hp'],495);self.assertEqual(proc.call_count,1)
 def test_control_interrupts_rest_before_recovery(self):
  b,a,t,ally=self.fixture();cleric.execute(b,a,a,self.skill(a,'rest'));before=a['hp']
  combat.conditions.apply(a,'stun',1,t);cleric.finish(b,a)
  self.assertNotIn('cleric_rest',a);self.assertEqual(a['hp'],before)
 def test_priest_smite_cooldown_and_exorcist_chance(self):
  b,a,t,ally=self.fixture(priest=True);a['passives'].append(deepcopy(jobs.SKILLS['job:cleric:exorcist']));t['race']='Undead'
  self.assertEqual(self.skill(a,'smite')['cost']['cooldown'],4)
  with patch('backend.combat_cleric.random.Random') as rng:
   rng.return_value.randint.return_value=40
   cleric.exorcist(b,a,t)
  self.assertTrue(combat.conditions.has(t,'stun'))
 def test_rest_caps_charge_recovery_and_invalid_heal_spends_nothing(self):
  b,a,t,ally=self.fixture();cleric.execute(b,a,a,self.skill(a,'rest'))
  for i in range(1,10):a['status_activation']=[i,0];cleric.finish(b,a)
  self.assertTrue(all(v['uses']>=0 for v in a['ability_state'].values()))
  a['acted']=False;ally['hp']=ally['max_hp'];before=deepcopy(a['ability_state'])
  with self.assertRaises(ValueError):cleric.command(b,a,self.skill(a,'mend'),{'target_id':ally['id']})
  self.assertEqual(a['ability_state'],before)

 def test_smite_forecast_consumes_guard_once_for_both_components(self):
  b,a,t,ally=self.fixture();a.update(attack=20,attack_elevation_rule='melee');t.update(armor=0,guarding=True)
  cleric.execute(b,a,a,self.skill(a,'smite'))
  with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
   forecast=combat._strike_preview(b,a,t,'melee',1)['damage_on_hit'];before=t['hp']
   combat._perform_attack(b,a,t,'melee')
  self.assertEqual(forecast,before-t['hp'])
  self.assertEqual(forecast,27)

 def test_auto_heals_under_peace_and_honors_restricted_attack_target(self):
  b,a,t,ally=self.fixture();a['hp']=a['max_hp'];ally['hp']=10
  with patch('backend.combat_bard.can_attack',return_value=False):self.assertTrue(cleric.auto(b,a))
  self.assertGreater(ally['hp'],10)
  a['acted']=False;ally['hp']=ally['max_hp']
  with patch('backend.combat_cleric.execute') as execute:
   cleric.auto(b,a,[])
   self.assertFalse(any(call.args[3].get('cleric_kind')=='holy_light' for call in execute.call_args_list))

 def test_holy_light_is_exactly_the_smallest_cross(self):
  b,a,t,ally=self.fixture();a.update(x=3,y=3)
  self.assertEqual({(p['x'],p['y']) for p in cleric.cells(b,a,'holy_light')},
                   {(3,3),(2,3),(4,3),(3,2),(3,4)})
  t.update(x=3,y=5);before=t['hp']
  cleric.execute(b,a,a,self.skill(a,'holy_light'))
  self.assertEqual(t['hp'],before)

 def test_smite_lasts_casting_turn_and_two_following_turns(self):
  b,a,t,ally=self.fixture();a.update(status_version=1,status_activation=[1,0])
  cleric.execute(b,a,a,self.skill(a,'smite'))
  for stamp in ([1,0],[2,0]):
   a['status_activation']=stamp;combat.conditions.finish_activation(a)
   self.assertTrue(combat.conditions.has(a,'cleric_smite'))
  a['status_activation']=[3,0];combat.conditions.finish_activation(a)
  self.assertFalse(combat.conditions.has(a,'cleric_smite'))

 def test_battle_priest_reduces_direct_and_dot_damage_and_heals_forty_percent(self):
  b,a,t,ally=self.fixture(priest=True);a.update(armor=0,hp=20,max_hp=100)
  t.update(attack=20,gear_rules={},perk_modifiers={},element=None)
  self.assertEqual(combat._damage_before_barrier(b,t,a),17)
  self.assertEqual(combat._damage_before_barrier(b,{'attack':20,'status_tick':True,'percent_dot':'poison'},a),17)
  cleric.execute(b,a,a,self.skill(a,'heal'));self.assertEqual(a['hp'],60)

if __name__=='__main__':unittest.main()
