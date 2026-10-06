import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat,combat_rogue as rogue,combat_conditions as conditions,combat_abilities as abilities,job_loadouts as jobs,combat_spaces as spaces
from backend.game import new_game
from tests import test_combat_abilities as fixtures

class RogueTests(unittest.TestCase):
 def fixture(self,keys=()):
  b,a,t=fixtures.AbilityFoundationTests().fixture('fighter');b.update(units={a['id']:a,t['id']:t},zones=[],terrain=[],ground_tiles=[],decorations=[])
  a.update(job_id='rogue',attack=20,armor=0,evasion=0,perk_modifiers={},gear_rules={},element=None,on_hit=None,capture_weapon=None,attack_elevation_rule='melee',statuses=[],reactions=[],passives=[],skills=[deepcopy(jobs.SKILLS['job:rogue:'+k]) for k in keys])
  t.update(armor=0,evasion=0,perk_modifiers={},gear_rules={},statuses=[],reactions=[],race='Human',boss=False,kind='guard')
  b.update(turn_index=0,round=1,status='active');a['loyalty']=100;combat._current_unit(b);a['loyalty_activation']=[1,0];t['zone_location']=[t['x'],t['y']]
  return b,a,t
 def use(self,b,command):
  with patch('backend.combat._advance_to_player'):return combat.apply_player_command(b,command)
 def test_starter_and_eight_skills(self):
  c=new_game({'starting_role':'rogue'})['characters'][0];self.assertEqual(len(c['equipped_skills']),3)
  self.assertEqual(len([k for k in jobs.SKILLS if k.startswith('job:rogue:')]),8)
 def test_cardinal_geometry(self):
  b,a,t=self.fixture();self.assertEqual(rogue.position_power(b,a,t)[0],100)
  ally={**deepcopy(a),'id':'ally','x':3,'y':1};b['units']['ally']=ally;self.assertEqual(rogue.position_power(b,a,t)[0],150)
  ally.update(x=4,y=2);self.assertEqual(rogue.position_power(b,a,t)[0],200)
  b['units']['other']={**ally,'id':'other','x':3,'y':1};self.assertEqual(rogue.position_power(b,a,t)[0],220)
  b['units']['last']={**ally,'id':'last','x':3,'y':3};self.assertEqual(rogue.position_power(b,a,t)[0],250)
  ally['conscious']=False;self.assertEqual(rogue.position_power(b,a,t)[0],220)
 def test_virtual_side_and_dedup(self):
  b,a,t=self.fixture();a.update(x=1,y=2);b['units']['ally']={**deepcopy(a),'id':'ally','x':4}
  self.assertEqual(rogue.position_power(b,a,t,True)[0],200);self.assertEqual(a['x'],1)
  b['units']['ally']['x']=2;self.assertEqual(rogue.position_power(b,a,t,True)[0],100)
 def test_stack_damage_cap_and_positive_exclusion(self):
  b,a,t=self.fixture();conditions.add_stack(t,'bleed',2,a);conditions.add_stack(t,'bleed',2,a);conditions.add_stack(t,'hobbled',2,a);conditions.barrier(t,50,2,a)
  self.assertEqual(sum(rogue.counts(t).values()),3)
  s=jobs.SKILLS['job:rogue:exploit_weakness'];self.assertEqual(rogue.attack_skill(b,a,t,s)['effects'][0]['power_percent'],250)
  for _ in range(10):conditions.add_stack(t,'bleed',2,a)
  self.assertEqual(rogue.attack_skill(b,a,t,s)['effects'][0]['power_percent'],400)
 def test_cut_is_quick_damage_hobble_and_lock(self):
  b,a,t=self.fixture(['crippling_cut','cheap_shot','backflip'])
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   self.use(b,{'action':'skill','skill_id':a['skills'][0]['id'],'target_id':t['id']})
  self.assertEqual(t['hp'],95);self.assertTrue(conditions.has(t,'hobbled'));self.assertFalse(a['acted']);self.assertEqual(b['turn_index'],0)
  with self.assertRaisesRegex(ValueError,'walking is locked'):self.use(b,{'action':'move','x':1,'y':2})
  self.assertIn({'x':1,'y':2},rogue.flips(b,a))
  self.use(b,{'action':'skill','skill_id':'job:rogue:backflip','x':1,'y':2});self.assertEqual(a['x'],1);self.assertFalse(a['acted'])
 def test_main_ends_activation_after_quicks(self):
  b,a,t=self.fixture(['caltrops','crippling_cut','cheap_shot'])
  self.use(b,{'action':'skill','skill_id':'job:rogue:caltrops','x':3,'y':2,'rotation':0})
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   self.use(b,{'action':'skill','skill_id':'job:rogue:crippling_cut','target_id':t['id']})
   self.use(b,{'action':'skill','skill_id':'job:rogue:cheap_shot','target_id':t['id']})
  self.assertTrue(a['acted']);self.assertNotEqual(b['turn_index'],0);self.assertEqual(a['quick_actions_used'],2)
 def test_invalid_placement_does_not_spend(self):
  b,a,t=self.fixture(['shadowstep','caltrops','backflip']);before=deepcopy(a)
  for cmd in [{'action':'skill','skill_id':'job:rogue:shadowstep','target_id':t['id'],'x':t['x'],'y':t['y']},{'action':'skill','skill_id':'job:rogue:caltrops','x':0,'y':0},{'action':'skill','skill_id':'job:rogue:backflip','x':3,'y':3}]:
   with self.assertRaises(ValueError):self.use(b,cmd)
   self.assertEqual(a,before)
 def test_strip_and_traps_per_tile(self):
  b,a,t=self.fixture();self.assertEqual(len(rogue.strip(b,a,3,2,0)),3);self.assertEqual(rogue.strip(b,a,0,0,0),[])
  spaces.place_zone(b,a,{'zone':'caltrops','turns':2},[{'x':x,'y':2} for x in (3,4,5)])
  t['zone_location']=[2,2]
  for x in (3,4,5):t['x']=x;combat._apply_tile_entry(b,t)
  self.assertEqual(rogue.counts(t),{'bleed':3,'hobbled':3})
 def test_expert_ignores_traps_not_other_zones(self):
  b,a,t=self.fixture();t['passives']=[jobs.SKILLS['job:rogue:trap_expert']]
  spaces.place_zone(b,a,{'zone':'caltrops','turns':2},[{'x':3,'y':2}]);combat._apply_tile_entry(b,t);self.assertEqual(t['statuses'],[])
 def test_stack_expiry_independent(self):
  b,a,t=self.fixture();t['status_activation']=[1,1];conditions.add_stack(t,'bleed',1,a);conditions.add_stack(t,'bleed',2,a)
  t['status_activation']=[2,1];conditions.finish_activation(t);self.assertEqual(rogue.counts(t)['bleed'],1)
  t['status_activation']=[3,1];conditions.finish_activation(t);self.assertNotIn('bleed',rogue.counts(t))
 def test_knife_uses_virtual_geometry_and_contact_packet(self):
  b,a,t=self.fixture(['cheap_shot','throwing_knife']);a['x']=1;b['units']['ally']={**deepcopy(a),'id':'ally','x':4}
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   self.use(b,{'action':'skill','skill_id':'job:rogue:cheap_shot','knife_skill_id':'job:rogue:throwing_knife','target_id':t['id']})
  self.assertEqual(t['hp'],60);self.assertEqual(a['x'],1);self.assertTrue(a['acted'])
  knife=next(e for e in b['animation_events'] if e['type']=='rogue_knife');self.assertEqual(knife['contact_ms'],280)
  self.assertFalse(abilities.availability(a,jobs.SKILLS['job:rogue:throwing_knife'])['available'])
 def test_knife_adjacent_invalid_does_not_spend(self):
  b,a,t=self.fixture(['cheap_shot','throwing_knife']);before=deepcopy(a)
  with self.assertRaises(ValueError):self.use(b,{'action':'skill','skill_id':'job:rogue:cheap_shot','knife_skill_id':'job:rogue:throwing_knife','target_id':t['id']})
  self.assertEqual(a,before)
 def test_ai_quick_then_main(self):
  b,a,t=self.fixture(['crippling_cut','exploit_weakness']);self.assertTrue(combat._auto_rogue_turn(b,a,[t]));self.assertTrue(a['acted']);self.assertEqual(a['quick_actions_used'],1)
 def test_ai_approach(self):
  b,a,t=self.fixture(['cheap_shot']);t['x']=5;self.assertTrue(combat._auto_rogue_turn(b,a,[t]));self.assertTrue(a['acted'])
 def test_view_is_pure_and_has_custom_placement(self):
  b,a,t=self.fixture(['shadowstep','caltrops','backflip','throwing_knife']);before=deepcopy(b);view=combat.battle_view(b)
  self.assertEqual(b,before);self.assertEqual(len(view['rogue_previews']),4)
  self.assertIn(t['id'],view['rogue_previews']['job:rogue:shadowstep']['targets'])

 def test_push_and_pull_trigger_each_crossed_tile_once(self):
  for mode in ('push','pull'):
   b,a,t=self.fixture();t['displacement_resistance']=0
   if mode=='pull':t['x']=6
   cells=[{'x':x,'y':2} for x in ((4,5,6) if mode=='push' else (3,4,5))]
   spaces.place_zone(b,a,{'zone':'caltrops','turns':2},cells)
   combat._apply_displacement(b,a,t,{'mode':mode,'distance':3},20,9)
   self.assertEqual(rogue.counts(t),{'bleed':3,'hobbled':3})
   combat._apply_tile_entry(b,t);self.assertEqual(rogue.counts(t)['bleed'],3)
 def test_preview_route_is_free_commit_is_idempotent(self):
  b,a,t=self.fixture();t.update(x=6,y=6)
  spaces.place_zone(b,t,{'zone':'caltrops','turns':2},[{'x':3,'y':2}])
  a.update(x=4,y=2,movement_origin={'x':2,'y':2},movement_path=[{'x':3,'y':2},{'x':4,'y':2}])
  combat.battle_view(b);self.assertEqual(a['statuses'],[])
  combat._commit_player_movement(b,a);self.assertEqual(rogue.counts(a)['bleed'],1)
  combat._commit_player_movement(b,a);self.assertEqual(rogue.counts(a)['bleed'],1)
 def test_real_immobilization_still_blocks_quick_mobility(self):
  b,a,t=self.fixture();conditions.apply(a,'bind',1,t);self.assertEqual(rogue.landings(b,a,t),[]);self.assertEqual(rogue.flips(b,a),[])
 def test_other_bleed_application_preserves_existing_layers(self):
  b,a,t=self.fixture();conditions.add_stack(t,'bleed',2,a);conditions.add_stack(t,'bleed',2,a)
  conditions.apply(t,'bleed',1,t);self.assertEqual(rogue.counts(t)['bleed'],3)
  self.assertEqual(t['statuses'][0]['layers'][-1]['source_id'],t['id'])
 def test_bleed_charged_once_at_main_finish_not_per_quick(self):
  b,a,t=self.fixture(['caltrops','crippling_cut']);conditions.add_stack(a,'bleed',2,t);conditions.add_stack(a,'bleed',2,t)
  self.use(b,{'action':'skill','skill_id':'job:rogue:caltrops','x':3,'y':2,'rotation':0})
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   self.use(b,{'action':'skill','skill_id':'job:rogue:crippling_cut','target_id':t['id']})
  self.assertEqual(a['hp'],100)
  self.use(b,{'action':'guard'});self.assertEqual(a['hp'],92)
 def test_retired_loadout_migration_is_idempotent_and_preserves_practice(self):
  c=new_game({'starting_role':'rogue'})['characters'][0];c.pop('rogue_kit_version',None)
  c.update(learned_skills=['job:rogue:bleed','job:rogue:blind','job:rogue:footwork'],equipped_skills=['job:rogue:bleed','job:rogue:blind','job:rogue:footwork'],combat_skill_order=['job:rogue:blind','job:rogue:bleed'],job_practice=1)
  jobs.initialize(c);self.assertEqual(c['job_practice'],1);self.assertEqual(c['combat_skill_order'][0],'job:rogue:crippling_cut');self.assertIn('job:rogue:trap_expert',c['equipped_skills'])
  before=deepcopy(c);jobs.initialize(c);self.assertEqual(c,before)
 def test_knife_miss_spends_both_cooldowns(self):
  b,a,t=self.fixture(['cheap_shot','throwing_knife']);a['x']=1
  with patch('backend.combat._attack_hits',return_value=(False,{'chance':50,'damage_bonus':0},99)):
   self.use(b,{'action':'skill','skill_id':'job:rogue:cheap_shot','knife_skill_id':'job:rogue:throwing_knife','target_id':t['id']})
  self.assertEqual(t['hp'],100);self.assertEqual(set(a['ability_state']),{'job:rogue:cheap_shot','job:rogue:throwing_knife'})
 def test_auto_shadow_chooses_position_then_finishes_once(self):
  b,a,t=self.fixture(['shadowstep','cheap_shot']);t['x']=5
  self.assertTrue(combat._auto_rogue_turn(b,a,[t]));self.assertEqual(a['quick_actions_used'],1);self.assertTrue(a['acted']);self.assertEqual(b['turn_index'],1)
