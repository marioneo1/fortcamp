import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat as c, combat_druid as d, job_loadouts as jobs
from tests import test_mage_jobs as fixtures

class DruidTests(unittest.TestCase):
 def fixture(self,passives=()):
  b,a,t=fixtures.MageTests().fixture([])
  a.update(job_id='druid',attack=20,intelligence=12,move=3,armor=0,evasion=0,gear_rules={},perk_modifiers={},
   attack_elevation_rule='melee',weapon='Staff',weapon_type='staff',attack_range=1,hp=80,max_hp=100,
   skills=[deepcopy(jobs.SKILLS['job:druid:'+k]) for k in ('prowler','bulwark','rat','rejuvenation','bramble_wall','living_armor')],
   passives=[deepcopy(jobs.SKILLS['job:druid:'+k]) for k in passives],ability_activation=1,status_version=1,status_activation=[1,0])
  t.update(armor=0,attack=20,gear_rules={},perk_modifiers={},element=None,evasion=0,x=3,y=2)
  b.update(animation_events=[],action_count=0);c._ensure_battle_schema(b)
  return b,a,t
 def skill(self,a,key):return next(s for s in a['skills'] if s['druid_kind']==key)
 def cast(self,b,a,target,key,**cmd):
  return d.command(b,a,self.skill(a,key),{'target_id':target['id'],**cmd})
 def next_turn(self,b,a):
  a['ability_activation']+=1;a['status_activation']=[a['ability_activation'],0];a['acted']=False
  d.start(b,a)
 def test_eight_pool_and_legacy_migration_preserve_choices_and_practice(self):
  self.assertEqual(len([k for k in jobs.SKILLS if k.startswith('job:druid:')]),8)
  a={'job_id':'druid','learned_skills':['job:druid:bark','job:druid:thorns'],'equipped_skills':['job:druid:bark'],'job_practice':15}
  jobs.initialize(a);before=deepcopy(a);jobs.initialize(a);self.assertEqual(a,before)
  self.assertEqual(a['equipped_skills'],['job:druid:living_armor']);self.assertEqual(a['job_practice'],15)
 def test_forms_are_quick_persistent_once_per_activation_and_share_hp(self):
  b,a,t=self.fixture();before=a['hp'];self.assertFalse(self.cast(b,a,a,'prowler'))
  self.assertFalse(a['acted']);self.assertEqual(a['move'],5)
  with self.assertRaisesRegex(ValueError,'one form change'):self.cast(b,a,a,'bulwark')
  self.next_turn(b,a);self.cast(b,a,a,'bulwark');self.assertEqual(a['move'],1)
  a['hp']-=10
  for _ in range(5):self.next_turn(b,a);c.spaces.expire_form(a)
  self.assertEqual(d.form(a),'bulwark');self.cast(b,a,a,'bulwark')
  self.assertIsNone(d.form(a));self.assertEqual((a['hp'],a['move'],a['weapon']),(before-10,3,'Staff'))
 def test_move_then_switch_does_not_retroactively_invalidate_legal_path(self):
  b,a,t=self.fixture();t.update(x=7,y=7);self.cast(b,a,a,'prowler');self.next_turn(b,a)
  c._position_player(b,a,{'x':5,'y':2});self.cast(b,a,a,'bulwark')
  self.assertEqual((a['x'],a['y'],a['move']),(5,2,1));self.assertEqual(c._movement_limit(a),0)
  self.assertEqual(set(c._movement_tree(b,a)[0]),{(5,2)})
  self.next_turn(b,a);self.assertEqual(c._movement_limit(a),1)
 def test_unspent_movement_uses_new_form_budget(self):
  b,a,t=self.fixture();t.update(x=7,y=7);c._position_player(b,a,{'x':2,'y':3});self.cast(b,a,a,'prowler')
  self.assertEqual(c._movement_limit(a),4)
 def test_animal_cannot_cast_spells_and_humanoid_return_allows_them(self):
  b,a,t=self.fixture();self.cast(b,a,a,'prowler')
  with self.assertRaisesRegex(ValueError,'humanoid'):self.cast(b,a,a,'rejuvenation')
  self.next_turn(b,a);self.cast(b,a,a,'prowler');self.assertTrue(self.cast(b,a,a,'rejuvenation'))
 def test_global_bleed_doubles_and_wild_opener_is_once_per_target_battle(self):
  b,a,t=self.fixture(('wild_instinct',));self.cast(b,a,a,'prowler')
  d.landed(b,a,t,1);self.assertEqual(c.conditions.dots.count(t['statuses'][0]),2)
  d.landed(b,a,t,2);self.assertEqual(c.conditions.dots.count(t['statuses'][0]),4)
  self.next_turn(b,a);self.cast(b,a,a,'prowler');self.next_turn(b,a);self.cast(b,a,a,'prowler')
  d.landed(b,a,t,3);self.assertEqual(c.conditions.dots.count(t['statuses'][0]),8)
 def test_prowler_doubles_bleed_created_by_an_ally(self):
  b,a,t=self.fixture();self.cast(b,a,a,'prowler')
  for _ in range(3):c.conditions.add_stack(t,'bleed',1,{'id':'rogue','name':'Rogue'})
  d.landed(b,a,t,1);self.assertEqual(c.conditions.dots.count(t['statuses'][0]),6)
 def test_form_damage_and_mitigation_do_not_protect_bulwark_from_dots(self):
  b,a,t=self.fixture();self.cast(b,a,a,'prowler')
  self.assertEqual(c._damage_before_barrier(b,a,t),24);self.assertEqual(c._damage_before_barrier(b,t,a),24)
  self.next_turn(b,a);self.cast(b,a,a,'bulwark')
  self.assertEqual(c._damage_before_barrier(b,a,t),25);self.assertEqual(c._damage_before_barrier(b,t,a),15)
  self.assertEqual(c._damage_before_barrier(b,{'attack':20,'percent_dot':'poison','status_tick':True},a),20)
 def test_bulwark_push_uses_standard_resistance_and_packet(self):
  b,a,t=self.fixture(('wild_instinct',));self.cast(b,a,a,'bulwark')
  with patch('backend.combat_druid.roll',return_value=1),patch('backend.combat._apply_displacement') as push:
   d.landed(b,a,t,42,30)
  self.assertEqual(push.call_args.kwargs,{'original_damage':30,'attack_packet':42})
 def test_rat_aimed_ten_percent_but_aoe_and_guaranteed_hits_bypass(self):
  b,a,t=self.fixture();self.cast(b,a,a,'rat');self.assertEqual(a['evasion'],90)
  self.assertEqual(c._attack_preview(b,t,a,'melee')['chance'],10)
  self.assertEqual(c._attack_preview(b,t,a,'ignore',jobs.SKILLS['job:mage:fireball'])['chance'],100)
  with patch('backend.combat_ranger.marked',return_value=True):self.assertEqual(c._attack_preview(b,t,a,'ballistic')['chance'],100)
 def test_rat_damage_is_lethal_even_nonlethal_and_survival_gear(self):
  for source in ({'attack':1},{'attack':1,'status_tick':True,'percent_dot':'burn'}, {'attack':1,'nonlethal_floor':True,'knockout_finisher':100}):
   b,a,t=self.fixture();self.cast(b,a,a,'rat');a['gear_rules']={'lifeline':True}
   c._deal_damage(b,{**t,**source},a,intent='nonlethal')
   self.assertEqual((a['hp'],a['alive'],a['condition']),(0,False,'dead'))
 def test_zero_damage_absorbed_by_barrier_does_not_kill_rat(self):
  b,a,t=self.fixture();self.cast(b,a,a,'rat');c.conditions.barrier(a,100,2,a)
  c._deal_damage(b,t,a);self.assertEqual(a['hp'],80)
 def test_rejuvenation_ticks_exactly_three_times_without_instant_heal(self):
  b,a,t=self.fixture();a['hp']=10;self.cast(b,a,a,'rejuvenation');self.assertEqual(a['hp'],10)
  for _ in range(4):self.next_turn(b,a)
  self.assertEqual(a['hp'],40);self.assertFalse(c.conditions.has(a,'druid_rejuvenation'))
 def test_persistent_living_armor_ticks_four_times_and_reduces_all_damage(self):
  b,a,t=self.fixture(('natures_persistence',));a['hp']=10;self.cast(b,a,a,'living_armor')
  self.assertEqual(c._damage_before_barrier(b,t,a),15)
  for _ in range(4):self.next_turn(b,a);d.finish(a)
  self.assertEqual(a['hp'],38);self.assertFalse(c.conditions.has(a,'living_armor'))
 def test_living_armor_retaliation_is_once_per_attack_not_per_hit(self):
  b,a,t=self.fixture(('natures_persistence',));self.cast(b,a,a,'living_armor')
  for _ in range(3):c._deal_damage(b,t,a,resolved_damage=1)
  bleed=next(s for s in t['statuses'] if s['id']=='bleed');self.assertEqual(c.conditions.dots.count(bleed),1)
  b['action_count']+=1;c._deal_damage(b,t,a,resolved_damage=1)
  self.assertEqual(c.conditions.dots.count(bleed),2)
 def test_wall_three_cells_one_hp_pool_blocking_and_destroy_together(self):
  b,a,t=self.fixture();t.update(x=7,y=7)
  self.assertTrue(d.command(b,a,self.skill(a,'bramble_wall'),{'x':3,'y':3,'rotation':0}))
  wall=[tile for tile in b['terrain'] if tile.get('bramble_group')];self.assertEqual(len(wall),3)
  self.assertTrue(all(c._blocked(b,w['x'],w['y']) for w in wall))
  self.assertEqual({w['hp'] for w in wall},{20});a['attack']=10;c._damage_terrain(b,a,wall[1]['id'])
  self.assertEqual({w['hp'] for w in wall},{10});c._damage_terrain(b,a,wall[2]['id'])
  self.assertTrue(all(w['destroyed'] and not w['blocking'] and w['hp']==0 for w in wall))
 def test_wall_placement_rejects_occupants_edges_and_invalid_rotation_without_spending(self):
  b,a,t=self.fixture();before=deepcopy(a)
  for x,y,r in [(3,2,0),(0,0,0),(3,3,2)]:
   with self.assertRaises(ValueError):d.command(b,a,self.skill(a,'bramble_wall'),{'x':x,'y':y,'rotation':r})
  self.assertEqual(a,before)
 def test_wall_lash_once_per_movement_event_and_feedback_at_contact(self):
  b,a,t=self.fixture(('natures_persistence',));t.update(x=7,y=7)
  d.command(b,a,self.skill(a,'bramble_wall'),{'x':3,'y':3,'rotation':0});t.update(x=3,y=2)
  with patch('backend.combat_druid.roll',return_value=1):
   d.adjacent_reactions(b,t,'event1');d.adjacent_reactions(b,t,'event1')
  self.assertEqual(t['hp'],490);self.assertTrue(c.conditions.has(t,'bind'))
  lash=next(e for e in b['animation_events'] if e['type']=='druid_lash')
  damage=next(e for e in b['animation_events'] if e['type']=='combat_feedback' and e.get('amount')==10)
  self.assertEqual(lash['attack_packet'],damage['attack_packet']);self.assertLess(b['animation_events'].index(lash),b['animation_events'].index(damage))
 def test_wall_persistence_stats_retaliation_and_expiration(self):
  b,a,t=self.fixture(('natures_persistence',));t.update(x=7,y=7)
  d.command(b,a,self.skill(a,'bramble_wall'),{'x':3,'y':3,'rotation':1});wall=[w for w in b['terrain'] if w.get('bramble_group')]
  self.assertEqual({w['hp'] for w in wall},{50});self.assertEqual({w['lash_damage'] for w in wall},{10})
  c._damage_terrain(b,t,wall[0]['id']);self.assertTrue(c.conditions.has(t,'bleed'))
  for _ in range(3):self.next_turn(b,a)
  self.assertTrue(all(not w['destroyed'] for w in wall))
  self.next_turn(b,a)
  self.assertTrue(all(w['destroyed'] and not w['blocking'] for w in wall))
 def test_view_uses_animal_portrait_and_return_button_without_mutating_character(self):
  b,a,t=self.fixture();a.update(portrait='original.png',portrait_full='original.png',portrait_frame={'x':.2,'y':.3,'size':.4},portrait_frame_source='manual',portrait_frame_key='original.png');self.cast(b,a,a,'prowler');self.next_turn(b,a)
  before=deepcopy(b);v=c.battle_view(b);self.assertEqual(b,before)
  unit=v['units'][a['id']];self.assertIn('portrait_prowler.png',unit['portrait'])
  self.assertEqual(next(s for s in unit['skills'] if s['druid_kind']=='prowler')['name'],'Humanoid Form')
  self.assertEqual(a['portrait'],'original.png')
  self.assertEqual(unit['portrait_frame'],{'x':.5,'y':.5,'size':1,'image':'square'})

 def test_rat_forecast_warns_lethal_damage_and_dead_owner_wall_withers(self):
  b,a,t=self.fixture();self.cast(b,a,a,'rat')
  t.update(x=3,y=2,attack=10)
  preview=c._strike_preview(b,t,a,'melee',1)
  self.assertEqual(preview['damage_on_hit'],a['hp'])
  self.assertIn('lethal',preview['damage_note'])
  b,a,t=self.fixture();t.update(x=7,y=7)
  d.command(b,a,self.skill(a,'bramble_wall'),{'x':3,'y':3,'rotation':0})
  a.update(alive=False,hp=0);d.cleanup(b)
  self.assertTrue(all(w['destroyed'] and not w['blocking'] for w in b['terrain'] if w.get('bramble_group')))

 def test_armor_multi_target_multihit_retaliates_once_per_target(self):
  b,a,t=self.fixture(('natures_persistence',));self.cast(b,a,a,'living_armor')
  ally=deepcopy(a);ally['id']='ally';b['units']['ally']=ally
  for target in [a,ally,a,ally]:d.retaliate(b,t,target)
  self.assertEqual(c.conditions.dots.count(next(s for s in t['statuses'] if s['id']=='bleed')),2)

 def test_auto_returns_to_humanoid_for_wounded_ally_and_never_selects_rat(self):
  b,a,t=self.fixture();self.cast(b,a,a,'prowler');self.next_turn(b,a);a['hp']=20
  self.assertTrue(d.auto(b,a,[t]))
  self.assertIsNone(d.form(a));self.assertTrue(c.conditions.has(a,'druid_rejuvenation'))

 def test_committed_movement_reacts_once_but_preview_is_free(self):
  b,a,t=self.fixture();t.update(x=7,y=7)
  d.command(b,a,self.skill(a,'bramble_wall'),{'x':3,'y':3,'rotation':0})
  t.update(x=3,y=1);t['druid_settled_position']=[3,1]
  before=deepcopy(b);c.battle_view(b);self.assertEqual(b,before)
  t.update(x=3,y=2)
  with patch('backend.combat_druid.roll',return_value=100):
   c._apply_tile_entry(b,t);c._apply_tile_entry(b,t)
  self.assertEqual(len([e for e in b['animation_events'] if e['type']=='druid_lash']),1)

 def test_beast_attack_delivery_restores_original_weapon_on_return(self):
  b,a,t=self.fixture();a['melee_style']='hack';self.cast(b,a,a,'prowler')
  self.assertEqual(a['melee_style'],'slash');self.next_turn(b,a);self.cast(b,a,a,'bulwark')
  self.assertEqual(a['melee_style'],'blunt');self.next_turn(b,a);self.cast(b,a,a,'bulwark')
  self.assertEqual(a['melee_style'],'hack')

 def test_humanoid_views_preserve_all_job_skill_names_and_descriptions(self):
  for job in jobs.JOBS:
   with self.subTest(job=job):
    b,a,t=self.fixture()
    a.update(job_id=job,skills=[deepcopy(s) for key,s in jobs.SKILLS.items() if key.startswith('job:'+job+':') and s['type']=='active'][:5])
    a['special']=deepcopy(a['skills'][-1]);expected=deepcopy(a)
    result=c.battle_view(b)['units'][a['id']]
    self.assertEqual([(s['id'],s['name'],s['description']) for s in result['skills'] if s.get('source_kind')!='innate'],[(s['id'],s['name'],s['description']) for s in expected['skills']])
    self.assertFalse(any(s.get('form_return') for s in result['skills']))
    self.assertEqual(result['special']['name'],expected['special']['name'])
    self.assertEqual(a,expected)

 def test_support_targets_exist_before_selecting_spell_and_cast_on_self_or_ally(self):
  for key in ('rejuvenation','living_armor'):
   for own in (True,False):
    with self.subTest(skill=key,own_target=own):
     b,a,t=self.fixture();a['special']=self.skill(a,'bramble_wall')
     ally=deepcopy(a);ally.update(id='ally',x=2,y=4);b['units']['ally']=ally
     target=a if own else ally;v=c.battle_view(b)
     self.assertIn(target['id'],v['attack_previews'])
     self.assertTrue(v['skill_previews']['job:druid:'+key][target['id']]['support'])
     self.assertTrue(self.cast(b,a,target,key))
     self.assertTrue(c.conditions.has(target,'druid_rejuvenation' if key=='rejuvenation' else 'living_armor'))

 def test_rat_direct_damage_is_fixed_one_even_with_modifiers_and_pre_resolved_damage(self):
  b,a,t=self.fixture(('wild_instinct',));self.cast(b,a,a,'rat');a['attack']=999
  c.conditions.apply(t,'pestilence',2,a);t['armor']=0
  self.assertEqual(c._damage_before_barrier(b,a,t,bonus=999),1)
  self.assertEqual(c._strike_preview(b,a,t,'melee',1)['damage_on_hit'],1)
  before=t['hp'];self.assertEqual(c._deal_damage(b,a,t,resolved_damage=99),1);self.assertEqual(t['hp'],before-1)



 def test_bramble_remains_fade_then_disappear_without_owner(self):
  b,a,t=self.fixture();b['round']=3
  d.command(b,a,self.skill(a,'bramble_wall'),{'x':3,'y':3,'rotation':0})
  a['hp']=0;a['alive']=False;d.cleanup(b)
  wall=[w for w in b['terrain'] if w.get('bramble_group')]
  self.assertEqual(len(wall),3);self.assertTrue(all(w['destroyed'] and not w['bramble_fading'] for w in wall))
  b['round']=4;d.cleanup(b);self.assertTrue(all(w['bramble_fading'] for w in b['terrain'] if w.get('bramble_group')))
  d.cleanup(b);self.assertTrue(all(w['bramble_died_round']==3 for w in wall))
  b['round']=5;d.cleanup(b);self.assertFalse(any(w.get('bramble_group') for w in b['terrain']))

 def test_control_can_refresh_overlap_and_reapply_after_expiration(self):
  b,a,t=self.fixture();t.update(status_version=1,status_activation=[1,1],control_immunity=2)
  for sid in ('stun','bind','freeze'):
   self.assertTrue(c.conditions.apply(t,sid,2,a));self.assertTrue(c.conditions.apply(t,sid,3,a))
  t['status_activation']=[2,1];c.conditions.finish_activation(t)
  for sid in ('stun','bind','freeze'):c.conditions.remove(t,sid)
  self.assertTrue(c.conditions.apply(t,'stun',2,a))
  self.assertFalse(c.conditions.resistance_view(t)['control_recovery'])

 def test_inspection_armor_explains_actual_flat_math_and_read_only_view(self):
  from backend.combat_inspection import explanations
  b,a,t=self.fixture();t['armor']=10;c.conditions.apply(t,'armor_fracture',2,a)
  v=c.battle_view(b);inspected=v['units'][t['id']]
  self.assertEqual(inspected['effective_armor'],7)
  self.assertIn('Against 20 power: 13 damage',explanations(inspected)['Armor'])
  self.assertNotIn('stat_explanations',t)
