import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_ranger as ranger, combat_conditions as conditions, combat_abilities as abilities, job_loadouts as jobs
from backend.game import new_game
from tests import test_rogue_jobs as fixtures


class RangerTests(unittest.TestCase):
 def fixture(self, keys=()):
  b,a,t=fixtures.RogueTests().fixture()
  a.update(job_id='ranger',attack_elevation_rule='ballistic',attack_range=5,skills=[deepcopy(jobs.SKILLS['job:ranger:'+k]) for k in keys])
  t.update(hp=500,max_hp=500)
  return b,a,t
 def use(self,b,key,t):
  with patch('backend.combat._advance_to_player'):
   return combat.apply_player_command(b,{'action':'skill','skill_id':'job:ranger:'+key,'target_id':t['id']})
 def hit(self):return patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1))
 def skill(self,key):return jobs.SKILLS['job:ranger:'+key]
 def test_pool_slots_and_no_cooldown(self):
  c=new_game({'starting_role':'ranger'})['characters'][0]
  self.assertEqual(len(c['equipped_skills']),3)
  self.assertEqual(len([k for k in jobs.SKILLS if k.startswith('job:ranger:')]),8)
  for key in ('mark_quarry','poison_attack'):self.assertEqual(abilities.validate(self.skill(key))['cost']['cooldown'],0)
  bad=deepcopy(self.skill('longshot'));bad['cost']['cooldown']=0
  with self.assertRaises(ValueError):abilities.validate(bad)
 def test_mark_is_main_action_and_owner_specific(self):
  b,a,t=self.fixture(['mark_quarry']);other={**deepcopy(a),'id':'other'}
  conditions.mark(b,other,t,3,0);t['statuses'][0]['quarry']=True
  self.use(b,'mark_quarry',t)
  self.assertTrue(a['acted']);self.assertEqual(b['turn_index'],1);self.assertEqual(len(t['statuses']),2)
  a['statuses']=[{'id':'blind'}];t['evasion']=100
  self.assertEqual(combat._attack_preview(b,a,t,'ballistic')['chance'],100)
  self.assertTrue(ranger.marked(other,t));self.assertFalse(ranger.marked({'id':'outsider'},t))
 def test_mark_expiry_and_replacement(self):
  b,a,t=self.fixture();conditions.mark(b,a,t,3,0);t['statuses'][0]['quarry']=True
  for turn in range(3):t['status_activation']=[turn+4,1];conditions.finish_activation(t)
  self.assertFalse(ranger.marked(a,t))
  conditions.mark(b,a,t,3,0);conditions.mark(b,a,a,3,0)
  self.assertFalse(conditions.has(t,'mark'))
 def test_longshot_requires_mark_without_spending(self):
  b,a,t=self.fixture(['longshot']);before=deepcopy(a)
  with self.assertRaisesRegex(ValueError,'Mark Quarry'):self.use(b,'longshot',t)
  self.assertEqual(a,before);self.assertIsNone(combat.battle_view(b)['skill_previews'][self.skill('longshot')['id']][t['id']])
 def test_distance_curve(self):
  b,a,t=self.fixture()
  self.assertEqual([ranger.power(a,{**t,'x':a['x']+d,'y':a['y']},'longshot') for d in (1,2,3,4,5,6)],[100,100,150,175,200,200])
 def test_longshot_critical_after_armor_before_barrier(self):
  b,a,t=self.fixture(['longshot']);t.update(x=6,armor=5)
  conditions.mark(b,a,t,3,0);t['statuses'][-1]['quarry']=True;conditions.barrier(t,10,2,a)
  with self.hit(),patch('backend.combat_ranger.roll',return_value=1):self.use(b,'longshot',t)
  self.assertEqual(t['hp'],450) # (35 attack - 5 armor)*2 - 10 shield.
  self.assertEqual(abilities.availability(a,self.skill('longshot'))['cooldown_remaining'],2)
 def test_multi_independent_hits_and_mark_accuracy(self):
  b,a,t=self.fixture(['multi_shot']);conditions.mark(b,a,t,3,0);t['statuses'][-1]['quarry']=True
  with patch('backend.combat_ranger.roll',return_value=4):self.use(b,'multi_shot',t)
  self.assertEqual(t['hp'],440)
  packets=[e for e in b['animation_events'] if e.get('attack_event')]
  self.assertEqual(len(packets),4);self.assertTrue(all(e['hit'] for e in packets));self.assertEqual(len({e['attack_packet'] for e in packets}),4)
 def test_multi_base_accuracy(self):
  b,a,t=self.fixture();s={**self.skill('multi_shot'),'ranger_accuracy':50}
  self.assertEqual(combat._attack_preview(b,a,t,'ballistic',s)['chance'],50)
 def test_multi_one_equipment_proc_and_flat_bonus_budget(self):
  b,a,t=self.fixture(['multi_shot']);a['on_hit']={'id':'burn','chance':100,'turns':2};a['perk_modifiers']={'damage_goblin':5};t['race']='Goblin'
  with self.hit(),patch('backend.combat_ranger.roll',return_value=4):self.use(b,'multi_shot',t)
  self.assertEqual(t['hp'],435);self.assertEqual(b['proc_counter'],1)
 def test_multi_forecast_consumes_one_barrier_across_arrows(self):
  b,a,t=self.fixture(['multi_shot']);conditions.barrier(t,20,2,a)
  preview=ranger.preview(b,a,t,self.skill('multi_shot'));self.assertEqual((preview['damage_on_hit'],preview['damage_max']),(10,40))
  with self.hit(),patch('backend.combat_ranger.roll',return_value=4):self.use(b,'multi_shot',t)
  self.assertEqual(t['hp'],460)
 def test_multi_keeps_one_technique_buffs_and_defensive_form(self):
  b,a,t=self.fixture(['multi_shot']);conditions.apply(a,'rally_power',1,a);conditions.apply(t,'iron_reversal',1,t)
  preview=ranger.preview(b,a,t,self.skill('multi_shot'))
  with self.hit(),patch('backend.combat_ranger.roll',return_value=4):self.use(b,'multi_shot',t)
  self.assertEqual(500-t['hp'],preview['damage_max']);self.assertFalse(conditions.has(a,'rally_power'));self.assertFalse(conditions.has(t,'iron_reversal'))
 def test_poison_uses_target_max_hp_instead_of_weapon_attack(self):
  b,a,t=self.fixture();a['attack']=50;ranger.poison(b,a,t,1)
  combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],450)
 def test_selective_pestilence_resistance_is_visible_and_applied(self):
  b,a,t=self.fixture(['pestilence_shot']);t['status_resistances']={'pestilence':100}
  with self.hit():self.use(b,'pestilence_shot',t)
  self.assertFalse(conditions.has(t,'pestilence'));self.assertEqual(conditions.resistance_view(t)['statuses']['pestilence'],100)
 def test_mark_does_not_bypass_walls(self):
  b,a,t=self.fixture();conditions.mark(b,a,t,3,0);t['statuses'][-1]['quarry']=True
  with patch('backend.combat.crossed_walls',return_value=[{'id':'wall'}]):self.assertFalse(combat._can_attack(b,a,t,5))
 def test_poison_two_or_four_and_imbue(self):
  for mark,count in ((False,2),(True,4)):
   b,a,t=self.fixture(['poison_attack'])
   if mark:conditions.mark(b,a,t,3,0);t['statuses'][-1]['quarry']=True
   with self.hit():self.use(b,'poison_attack',t)
   self.assertEqual(t['hp'],470);s=next(s for s in t['statuses'] if s['id']=='poison');self.assertEqual(len(s['layers']),count)
   self.assertTrue(conditions.has(a,'poison_imbue'));self.assertEqual(ranger.dot_potential(t),50*count*(count+1)/2)
 def test_imbue_multi_and_miss_preservation(self):
  b,a,t=self.fixture(['multi_shot']);a['statuses']=[{'id':'poison_imbue'}]
  with patch('backend.combat_ranger.roll',return_value=3),self.hit():self.use(b,'multi_shot',t)
  self.assertEqual(len(t['statuses'][0]['layers']),3);self.assertFalse(conditions.has(a,'poison_imbue'))
  b,a,t=self.fixture(['multi_shot']);a['statuses']=[{'id':'poison_imbue'}]
  with patch('backend.combat_ranger.roll',return_value=2),patch('backend.combat._attack_hits',return_value=(False,{'chance':50,'damage_bonus':0},99)):self.use(b,'multi_shot',t)
  self.assertTrue(conditions.has(a,'poison_imbue'));self.assertFalse(conditions.has(t,'poison'))
 def test_basic_attack_spends_imbue_on_contact(self):
  b,a,t=self.fixture();a['statuses']=[{'id':'poison_imbue'}]
  with self.hit():combat._perform_attack(b,a,t,'ballistic')
  self.assertFalse(conditions.has(a,'poison_imbue'));self.assertEqual(t['statuses'][0]['stacks'],1)
 def test_poison_immune_and_legacy_conversion(self):
  b,a,t=self.fixture();t['race']='Automaton';ranger.poison(b,a,t,4);self.assertFalse(conditions.has(t,'poison'))
  t['race']='Human';t['statuses']=[{'id':'poison','turns':2,'source_id':a['id'],'source_name':a['name'],'tick_damage':7}];ranger.poison(b,a,t,1)
  combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],400);conditions.finish_activation(t);self.assertEqual(t['statuses'][0]['stacks'],1)
  t['status_activation']=[20,1];combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],350);conditions.finish_activation(t);self.assertFalse(conditions.has(t,'poison'))
 def test_stacks_decay_one_per_turn_not_independent_duration(self):
  b,a,t=self.fixture();ranger.poison(b,a,t,2)
  combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],400);conditions.finish_activation(t);self.assertEqual(t['statuses'][0]['stacks'],1)
  t['status_activation']=[20,1];ranger.poison(b,a,t,1);combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],300);conditions.finish_activation(t);self.assertEqual(t['statuses'][0]['stacks'],1)
 def test_pestilence_all_damage_and_attack(self):
  b,a,t=self.fixture(['pestilence_shot'])
  with self.hit():self.use(b,'pestilence_shot',t)
  self.assertEqual(combat.martial.attack_power({**t,'attack':20}),15)
  self.assertEqual(combat._damage_before_barrier(b,a,t),25)
  self.assertEqual(combat._damage_before_barrier(b,{'id':a['id'],'attack':20,'status_tick':True},t),25)
  conditions.apply(t,'open_guard',1,a);self.assertEqual(combat._damage_before_barrier(b,a,t),30)
  self.assertEqual(combat._damage_before_barrier(b,{'attack':20,'status_tick':True},t),25)
 def test_rupture_real_remaining_duration_allies(self):
  b,a,t=self.fixture(['rupturing_blow']);ally={**a,'id':'ally'}
  ranger.poison(b,ally,t,2);conditions.add_stack(t,'bleed',3,ally)
  potential=ranger.dot_potential(t);self.assertEqual(potential,175)
  with self.hit():self.use(b,'rupturing_blow',t)
  self.assertEqual(t['hp'],382);self.assertFalse(conditions.has(t,'bleed'));self.assertFalse(conditions.has(t,'poison'))
 def test_rupture_miss_preserves_dots(self):
  b,a,t=self.fixture(['rupturing_blow']);ranger.poison(b,a,t,1)
  with patch('backend.combat._attack_hits',return_value=(False,{'chance':90,'damage_bonus':0},100)):self.use(b,'rupturing_blow',t)
  self.assertTrue(conditions.has(t,'poison'))
 def test_rapid_pool_cooldown_and_main_remaining(self):
  b,a,t=self.fixture(['rapid_fire','longshot','poison_attack'])
  self.assertEqual([s['ranger_kind'] for s in ranger.candidates(b,a,t)],['poison_attack'])
  with self.hit():self.use(b,'rapid_fire',t)
  self.assertEqual(t['hp'],470);self.assertFalse(a['acted']);self.assertEqual(b['turn_index'],0);self.assertTrue(a['rogue_walk_locked'])
  self.assertEqual(abilities.availability(a,self.skill('rapid_fire'))['cooldown_remaining'],4)
  self.assertTrue(abilities.availability(a,self.skill('poison_attack'))['available'])
  with self.hit():self.use(b,'poison_attack',t)
  self.assertTrue(a['acted']);self.assertEqual(b['turn_index'],1)
 def test_rapid_does_not_spend_selected_cooldown(self):
  b,a,t=self.fixture(['rapid_fire','multi_shot'])
  with patch('backend.combat_ranger.roll',side_effect=lambda b,a,k,lo,hi:lo),self.hit():self.use(b,'rapid_fire',t)
  self.assertTrue(abilities.availability(a,self.skill('multi_shot'))['available'])
 def test_rapid_basic_fallback(self):
  b,a,t=self.fixture(['rapid_fire','longshot'])
  with self.hit():self.use(b,'rapid_fire',t)
  self.assertEqual(t['hp'],480);self.assertFalse(a['acted'])
 def test_rapid_fallback_forecasts_weapon_range_approach(self):
  b,a,t=self.fixture(['rapid_fire']);a['attack_range']=3;t['x']=6
  view=combat.battle_view(b);forecast=view['skill_previews']['job:ranger:rapid_fire'][t['id']]
  self.assertEqual(forecast['move_to'],{'x':3,'y':2});self.assertEqual(forecast['rapid_pool'],['Basic Attack'])
 def test_rapid_rejects_attacks_on_cooldown(self):
  b,a,t=self.fixture(['rapid_fire','multi_shot']);abilities.spend(a,self.skill('multi_shot'))
  self.assertEqual(ranger.candidates(b,a,t),[])
  with self.hit():self.use(b,'rapid_fire',t)
  self.assertEqual(t['hp'],480)
 def test_sharpshooter_stationary_and_preview_recovery(self):
  b,a,t=self.fixture(['poison_attack']);a['passives']=[self.skill('sharpshooter')];ranger.start(a);ranger.finish(a)
  self.assertEqual(a['attack_range'],7);self.assertEqual(ranger.skill_for(a,self.skill('longshot'))['range'],7)
  self.assertEqual(combat._damage_before_barrier(b,a,t),22)
  a['x']=1;ranger.sync(a);self.assertFalse(ranger.steady(a));self.assertEqual(a['attack_range'],5)
  a['x']=2;ranger.sync(a);self.assertTrue(ranger.steady(a))
  a['x']=1;combat._apply_tile_entry(b,a);a['x']=2;ranger.sync(a);self.assertFalse(ranger.steady(a))
 def test_sharpshooter_moved_activation_no_bonus(self):
  b,a,t=self.fixture();a['passives']=[self.skill('sharpshooter')];ranger.start(a);a['x']=1;ranger.committed_move(a);ranger.finish(a)
  self.assertFalse(ranger.steady(a))
 def test_stationary_range_does_not_survive_an_approach(self):
  b,a,t=self.fixture(['poison_attack']);a['passives']=[self.skill('sharpshooter')];ranger.start(a);ranger.finish(a);b['width']=14;t.update(x=10,y=2)
  _,path=ranger.position(b,a,t,self.skill('poison_attack'),*combat._movement_tree(b,a));self.assertEqual(path['move_to']['x'],5)
  approach={**a,'x':3};self.assertEqual(ranger.skill_for(approach,self.skill('poison_attack'))['range'],5)
 def test_sharpshooter_starts_after_stationary_main_action(self):
  b,a,t=self.fixture(['poison_attack']);a['passives']=[self.skill('sharpshooter')];ranger.start(a)
  with self.hit():self.use(b,'poison_attack',t)
  self.assertEqual(t['hp'],470);self.assertTrue(ranger.steady(a))
 def test_pestilence_amplifies_poison_ticks_and_cashout(self):
  b,a,t=self.fixture(['rupturing_blow']);ranger.poison(b,a,t,2);conditions.apply(t,'pestilence',3,a)
  combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],375)
  with self.hit():self.use(b,'rupturing_blow',t)
  self.assertEqual(t['hp'],243) # 125 DoT + 38 direct + 94 remaining-stack cashout.
 def test_view_is_pure_and_random_rolls_not_previewed(self):
  b,a,t=self.fixture(['mark_quarry','rapid_fire','multi_shot','poison_attack']);before=deepcopy(b)
  for _ in range(3):combat.battle_view(b)
  self.assertEqual(b,before)
 def test_ai_ends_activation(self):
  b,a,t=self.fixture(['mark_quarry','rapid_fire','multi_shot','poison_attack']);self.assertTrue(ranger.auto(b,a,[t]));self.assertTrue(a['acted'])
 def test_ai_does_not_walk_after_rapid_fire_kills_near_target(self):
  b,a,t=self.fixture(['rapid_fire','poison_attack']);t['hp']=10
  other={**deepcopy(t),'id':'other','x':8,'hp':500};b['units']['other']=other
  with self.hit():self.assertTrue(ranger.auto(b,a,[t,other]))
  self.assertTrue(a['acted']);self.assertEqual(a['x'],2);self.assertEqual(other['hp'],500)
 def test_legacy_loadout_preserves_order_practice(self):
  c=new_game({'starting_role':'ranger'})['characters'][0];c.update(ranger_kit_version=0,job_practice=20,learned_skills=['job:ranger:mark','job:ranger:poison','job:ranger:footwork'],equipped_skills=['job:ranger:poison','job:ranger:mark','job:ranger:footwork'],combat_skill_order=['job:ranger:footwork','job:ranger:poison'])
  jobs.initialize(c);self.assertEqual(c['equipped_skills'],['job:ranger:poison_attack','job:ranger:mark_quarry','job:ranger:sharpshooter']);self.assertEqual(c['job_practice'],20);self.assertEqual(len(c['learned_skills']),8)

if __name__=='__main__':unittest.main()
