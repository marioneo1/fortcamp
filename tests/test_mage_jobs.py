import unittest,json
from copy import deepcopy
from unittest.mock import patch
from backend import combat,combat_mage as mage,combat_conditions as conditions,combat_abilities as abilities,job_loadouts as jobs
from backend.game import new_game
from tests import test_rogue_jobs as fixtures

class MageTests(unittest.TestCase):
 def fixture(self,keys=(),debuffer=False):
  b,a,t=fixtures.RogueTests().fixture()
  a.update(job_id='mage',attack_elevation_rule='ignore',attack_range=4,skills=[deepcopy(jobs.SKILLS['job:mage:'+k]) for k in keys],passives=[deepcopy(jobs.SKILLS['job:mage:debuffer'])] if debuffer else [])
  t.update(hp=500,max_hp=500);b["animation_events"]=[]
  return b,a,t
 def hit(self):return patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1))
 def use(self,b,key,t=None,**kw):
  with patch('backend.combat._advance_to_player'):
   return combat.apply_player_command(b,{'action':'skill','skill_id':'job:mage:'+key,**({'target_id':t['id']} if t else {}),**kw})
 def skill(self,key):return jobs.SKILLS['job:mage:'+key]
 def add(self,b,t,key,x,y,team='enemy'):
  u={**deepcopy(t),'id':key,'x':x,'y':y,'team':team,'statuses':[]};b['units'][key]=u;return u
 def test_pool_and_slots(self):
  a=new_game({'starting_role':'mage'})['characters'][0];self.assertEqual(len(a['equipped_skills']),3)
  self.assertEqual(len([s for s in jobs.SKILLS if s.startswith('job:mage:')]),8)
  for s in jobs.SKILLS.values():
   if s.get('mage_kind'):abilities.validate(s)
 def test_legacy_migration_idempotent_and_order(self):
  a={'job_id':'mage','learned_skills':['job:mage:embers','job:mage:ward','job:mage:footwork'],'equipped_skills':['job:mage:ward','job:mage:embers'],'combat_skill_order':['job:mage:ward','job:mage:embers']}
  jobs.initialize(a);before=deepcopy(a);jobs.initialize(a);self.assertEqual(a,before);self.assertEqual(a['equipped_skills'],['job:mage:enchant_weapon','job:mage:fireball']);jobs.snapshot(a)
 def test_chain_sequential_reach_one_hit(self):
  b,a,t=self.fixture(['chain_lightning']);t.update(x=3,y=2);u=self.add(b,t,'second',5,2);v=self.add(b,t,'third',7,2);far=self.add(b,t,'far',7,6)
  with self.hit(),patch('backend.combat_mage.roll',return_value=100):self.use(b,'chain_lightning',t)
  self.assertEqual([500-u['hp'] for u in (t,u,v,far)],[30,25,25,0]);self.assertEqual(len([e for e in b['animation_events'] if e['type']=='mage_cast']),3)
 def test_wet_chain_damage_and_persistence(self):
  b,a,t=self.fixture(['chain_lightning']);conditions.apply(t,'wet',2,a);u=self.add(b,t,'other',t['x']+2,t['y']);conditions.apply(u,'wet',2,a)
  with self.hit(),patch('backend.combat_mage.roll',return_value=1):self.use(b,'chain_lightning',t)
  self.assertEqual(t['hp'],450);self.assertEqual(u['hp'],465);self.assertTrue(conditions.has(t,'wet'));self.assertTrue(conditions.has(t,'paralyze'))
 def test_chain_blocks_walls_and_does_not_mutate_preview(self):
  b,a,t=self.fixture(['chain_lightning']);before=deepcopy(b);combat.battle_view(b);combat.battle_view(b);self.assertEqual(b,before)
  u=self.add(b,t,'u',t['x']+1,t['y'])
  with self.hit(),patch('backend.combat._line_of_sight',side_effect=lambda b,a,t:t['id']!='u' if 'id' in t else True):mage.chain(b,a,t)
  self.assertEqual(u['hp'],500)
 def test_fireball_wet_blister_and_ground(self):
  b,a,t=self.fixture(['fireball']);conditions.apply(t,'wet',2,a)
  with self.hit(),patch('backend.combat_mage.roll',return_value=1):self.use(b,'fireball',t)
  self.assertEqual(t['hp'],470);self.assertFalse(conditions.has(t,'wet'));self.assertTrue(conditions.has(t,'blister'));self.assertTrue(conditions.has(t,'burn'));self.assertEqual(b['zones'][0]['kind'],'scorched')
 def test_freeze_break_full_damage_wet_and_recovery(self):
  b,a,t=self.fixture()
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  conditions.start_activation(b,t);self.assertTrue(t['forced_skip'])
  combat._deal_damage(b,a,t);self.assertEqual(t['hp'],480);self.assertFalse(conditions.has(t,'freeze'));self.assertTrue(conditions.has(t,'wet'));self.assertFalse(t.get('control_immunity',0))
 def test_freeze_expiry_wet_and_dot_does_not_break(self):
  b,a,t=self.fixture()
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  combat._deal_damage(b,{'id':a['id'],'name':a['name'],'attack':3,'status_tick':True},t);self.assertTrue(conditions.has(t,'freeze'))
  for i in range(2):t['status_activation']=[10+i,0];conditions.finish_activation(t)
  self.assertTrue(conditions.has(t,'wet'));self.assertFalse(conditions.has(t,'freeze'))
 def test_resisted_boss_freeze_still_wet(self):
  b,a,t=self.fixture();t.update(boss=True,status_resistances={'freeze':100})
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  self.assertFalse(conditions.has(t,'freeze'));self.assertTrue(conditions.has(t,'wet'))
 def test_boss_freeze_duration_not_doubled(self):
  b,a,t=self.fixture(debuffer=True);t['boss']=True
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  s=next(s for s in t['statuses'] if s['id']=='freeze');self.assertEqual(s['turns'],1);conditions.remove(t,'freeze');self.assertEqual(next(s for s in t['statuses'] if s['id']=='wet')['turns'],4)
 def test_freeze_shield_absorption_does_not_break(self):
  b,a,t=self.fixture()
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  conditions.barrier(t,50,2,a);combat._deal_damage(b,a,t);self.assertTrue(conditions.has(t,'freeze'))
 def test_flash_freeze_not_cast_activation_or_views(self):
  b,a,t=self.fixture(['flash_freeze'])
  with patch('backend.combat_mage.roll',return_value=1):self.use(b,'flash_freeze',t)
  self.assertFalse(conditions.has(t,'freeze'));self.assertEqual(len(b['mage_delays']),1)
  combat.battle_view(b);self.assertFalse(conditions.has(t,'freeze'));a['ability_activation']+=1;a['acted']=False;a['status_activation']=[2,0]
  with patch('backend.combat_mage.roll',return_value=1):mage.settle(b,a,'end')
  self.assertTrue(conditions.has(t,'freeze'));self.assertEqual(b['mage_delays'],[])
 def test_flash_freeze_enemy_can_leave(self):
  b,a,t=self.fixture(['flash_freeze']);self.use(b,'flash_freeze',t);t.update(x=7,y=7);a['ability_activation']+=1;mage.settle(b,a,'end');self.assertFalse(conditions.has(t,'freeze'))
 def test_meteor_release_spends_next_activation_and_persists(self):
  b,a,t=self.fixture(['meteor']);self.use(b,'meteor',t);self.assertEqual(t['hp'],500);self.assertTrue(conditions.has(a,'channeling'))
  b=json.loads(json.dumps(b));a=b['units'][a['id']];t=b['units'][t['id']];a['ability_activation']+=1
  with self.hit():mage.settle(b,a,'start')
  self.assertEqual(t['hp'],420);self.assertTrue(a['forced_skip']);self.assertEqual(len(b['zones']),1);self.assertEqual(b['zones'][0]['expires_at'],a['ability_activation']+2);self.assertFalse(conditions.has(a,'channeling'))
 def test_meteor_interrupts_displacement_and_mute(self):
  for mode in ('movement','mute','stun','death'):
   with self.subTest(mode=mode):
    b,a,t=self.fixture(['meteor']);self.use(b,'meteor',t)
    if mode=='movement':a['x']+=1
    elif mode=='death':a['alive']=False
    else:conditions.apply(a,mode,1,t)
    mage.check_channel(b,a);self.assertFalse(a.get('mage_channel'));self.assertEqual(b['mage_delays'],[])
 def test_meteor_damage_does_not_interrupt(self):
  b,a,t=self.fixture(['meteor']);self.use(b,'meteor',t);combat._deal_damage(b,{**t,'attack':1},a);self.assertTrue(a.get('mage_channel'))
 def test_singularity_displacement_uses_hazards(self):
  b,a,t=self.fixture(['singularity']);t.update(x=4,y=2);a.update(x=0,y=2)
  with self.hit():self.use(b,'singularity',x=3,y=2)
  self.assertEqual(t['hp'],495);self.assertEqual((t['x'],t['y']),(3,2));self.assertTrue(any(e.get('forced') for e in b['animation_events']))
 def test_typhoon_hits_allies_and_wets_everyone_except_caster(self):
  b,a,t=self.fixture(['typhoon']);ally=self.add(b,t,'ally',a['x'],a['y']+1,'player');hp=a['hp']
  with self.hit(),patch('backend.combat_mage.roll',return_value=1):self.use(b,'typhoon',a)
  self.assertLess(ally['hp'],500);self.assertTrue(conditions.has(ally,'wet'));self.assertTrue(conditions.has(t,'wet'));self.assertEqual(a['hp'],hp);self.assertFalse(conditions.has(a,'wet'))
 def test_enchant_requires_choice_before_spending(self):
  b,a,t=self.fixture(['enchant_weapon']);before=deepcopy(b)
  with self.assertRaisesRegex(ValueError,'Choose Fire'):self.use(b,'enchant_weapon',a)
  self.assertEqual(b,before)
 def test_fire_enchant_multi_hit_burn_layers_and_tick(self):
  b,a,t=self.fixture(['enchant_weapon']);self.use(b,'enchant_weapon',a,element='fire');a['attack_elevation_rule']='melee'
  with patch('backend.combat_mage.roll',return_value=1):
   for _ in range(3):combat._deal_damage(b,deepcopy(a),t)
  s=next(s for s in t['statuses'] if s['id']=='burn');self.assertEqual(len(s['layers']),3);hp=t['hp'];combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],hp-30);conditions.finish_activation(t);self.assertEqual(s['stacks'],2)
 def test_frost_enchant_next_hit_breaks_and_can_refreeze(self):
  b,a,t=self.fixture(['enchant_weapon']);self.use(b,'enchant_weapon',a,element='frost');a['attack_elevation_rule']='melee'
  with patch('backend.combat_mage.roll',return_value=1):
   combat._deal_damage(b,deepcopy(a),t);self.assertTrue(conditions.has(t,'freeze'));combat._deal_damage(b,deepcopy(a),t);self.assertTrue(conditions.has(t,'freeze'));self.assertTrue(conditions.has(t,'wet'))
 def test_lightning_enchant_once_per_target_across_source_copies(self):
  b,a,t=self.fixture(['enchant_weapon']);self.use(b,'enchant_weapon',a,element='lightning');a['attack_elevation_rule']='melee';conditions.apply(t,'wet',2,a)
  with patch('backend.combat_mage.roll',return_value=1):combat._deal_damage(b,deepcopy(a),t)
  conditions.remove(t,'paralyze');t['control_immunity']=0
  with patch('backend.combat_mage.roll',return_value=1):combat._deal_damage(b,deepcopy(a),t)
  self.assertFalse(conditions.has(t,'paralyze'));self.assertEqual(next(s for s in a['statuses'] if s['id']=='weapon_enchant')['paralyzed_targets'],[t['id']])
 def test_debuffer_half_spell_double_burn_wet_enchant_not_basic(self):
  b,a,t=self.fixture(['fireball'],True)
  with self.hit(),patch('backend.combat_mage.roll',return_value=1):self.use(b,'fireball',t)
  self.assertEqual(t['hp'],485);self.assertEqual(next(s for s in t['statuses'] if s['id']=='burn')['stacks'],2);combat._deal_damage(b,a,t);self.assertEqual(t['hp'],465)
  conditions.apply(a,'weapon_enchant',mage.duration(a,2),a);self.assertEqual(next(s for s in a['statuses'] if s['id']=='weapon_enchant')['turns'],4)
 def test_blister_accuracy_and_all_damage(self):
  b,a,t=self.fixture();conditions.apply(a,'blister',2,t)
  self.assertEqual(combat._attack_preview(b,a,t,'ignore')['chance'],90);combat._deal_damage(b,a,t);self.assertEqual(t['hp'],482)
  combat._deal_damage(b,{'id':a['id'],'name':a['name'],'attack':10,'status_tick':True},t);self.assertEqual(t['hp'],473)
 def test_scorched_reentries_and_caster_damage(self):
  b,a,t=self.fixture();mage.scorch(b,a,t,2);t['zone_location']=[0,0];hp=t['hp']
  combat._apply_zone_route(b,t,[(3,2),(4,2),(3,2)]);self.assertEqual(t['hp'],hp-60)
  a['zone_location']=[0,0];hp=a['hp'];combat._apply_zone_route(b,a,[(3,2)]);self.assertEqual(a['hp'],hp-2);self.assertTrue(conditions.has(a,'burn'))
 def test_ai_spell_and_no_friendly_typhoon(self):
  b,a,t=self.fixture(['fireball']);a['skills']=a['skills'][:1];t.update(x=6,y=2)
  with self.hit():self.assertTrue(mage.auto(b,a,[t]))
  self.assertTrue(a['acted']);self.assertLess(t['hp'],500)
 def test_previews_ground_support_and_no_mutation(self):
  b,a,t=self.fixture(['fireball','enchant_weapon','typhoon']);before=deepcopy(b);view=combat.battle_view(b)
  self.assertIn(f"{t['x']},{t['y']}",view['ground_skill_previews'][self.skill('fireball')['id']]);self.assertTrue(view['skill_previews'][self.skill('enchant_weapon')['id']][a['id']]['support']);self.assertEqual(b,before)
 def test_bad_ground_and_no_control_or_resource_mutation(self):
  b,a,t=self.fixture(['fireball']);before=deepcopy(b)
  with self.assertRaises(ValueError):self.use(b,'fireball',x=-1,y=2)
  self.assertEqual(b,before)

 def test_enchant_basic_magical_weapon_and_absorbed_hit_but_not_spell(self):
  b,a,t=self.fixture(['enchant_weapon']);self.use(b,'enchant_weapon',a,element='fire');conditions.barrier(t,50,2,a)
  with patch('backend.combat_mage.roll',return_value=1):combat._deal_damage(b,a,t)
  self.assertTrue(conditions.has(t,'burn'));self.assertEqual(t['hp'],500)
  before=next(s for s in t['statuses'] if s['id']=='burn')['stacks']
  with self.hit(),patch('backend.combat_mage.roll',return_value=1):mage.damage(b,a,t,'chain_lightning',150,1)
  self.assertEqual(next(s for s in t['statuses'] if s['id']=='burn')['stacks'],before)
 def test_debuffer_scorched_adds_two_stacks_each_entry(self):
  b,a,t=self.fixture(debuffer=True);mage.scorch(b,a,t,2);t['zone_location']=[0,0]
  with patch('backend.combat_mage.roll',return_value=1):combat._apply_zone_route(b,t,[(3,2),(4,2),(3,2)])
  self.assertEqual(next(s for s in t['statuses'] if s['id']=='burn')['stacks'],6)
 def test_freeze_cleansing_returns_wet(self):
  b,a,t=self.fixture()
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  conditions.remove(t,'freeze');self.assertTrue(conditions.has(t,'wet'));self.assertFalse(t.get('control_immunity',0))
 def test_meteor_consumes_rally_once_and_keeps_snapshot_bonus(self):
  b,a,t=self.fixture(['meteor']);conditions.apply(a,'rally_power',1,a);self.use(b,'meteor',t)
  self.assertFalse(conditions.has(a,'rally_power'));a['ability_activation']+=1
  with self.hit():mage.settle(b,a,'start')
  self.assertEqual(t['hp'],400);self.assertFalse(conditions.has(a,'rally_power'))

 def test_unstoppable_thaw_keeps_wet_and_spends_once(self):
  from backend import combat_martial as martial
  b,a,t=self.fixture()
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  t.update(fury=3,passives=[{'id':'job:barbarian:unstoppable'}])
  martial.try_unstoppable(t)
  self.assertFalse(conditions.has(t,'freeze'));self.assertTrue(conditions.has(t,'wet'));self.assertEqual(t['fury'],2)
 def test_healing_does_not_allow_frozen_ally_to_act(self):
  b,a,t=self.fixture();t['team']='player';t['hp']=400
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  conditions.start_activation(b,t);self.assertTrue(t['forced_skip'])
  combat._apply_support(b,a,t,{'name':'Heal','heal':5})
  self.assertEqual(t['hp'],405);self.assertTrue(t['forced_skip']);self.assertTrue(conditions.has(t,'freeze'))
 def test_lab_loadout_and_element_schema(self):
  from backend import battle_lab as lab
  keys=['fireball','flash_freeze','singularity','meteor','debuffer']
  state,party=lab.job_test_party([lab.JobTester(job_id='mage',practice=20,skill_ids=['job:mage:'+k for k in keys])])
  character=next(c for c in state['characters'] if c['id']==party[0])
  self.assertEqual(character['equipped_skills'],['job:mage:'+k for k in keys])
  request=lab.CommandRequest(action='skill',skill_id='job:mage:enchant_weapon',target_id=party[0],element='frost')
  self.assertEqual(request.model_dump()['element'],'frost')
 def test_preview_caches_are_local_and_rebuilt_after_wall_changes(self):
  b,a,t=self.fixture(['fireball','flash_freeze','meteor']);before=deepcopy(b)
  first=combat.battle_view(b);self.assertEqual(b,before)
  self.assertFalse(any(k.startswith('_mage_preview') or k.startswith('_routing') for k in first))
  b['terrain'].append({'id':'new-wall','x':t['x']-1,'y':t['y'],'blocking':True,'blocks_sight':True})
  second=combat.battle_view(b);self.assertNotEqual(first['ground_skill_previews'],second['ground_skill_previews'])

class MageFriendlyFireTests(unittest.TestCase):
 fixture=MageTests.fixture
 hit=MageTests.hit
 use=MageTests.use
 skill=MageTests.skill
 add=MageTests.add
 def test_area_damage_hits_live_caster_and_allies(self):
  for kind in ('fireball','meteor','singularity'):
   with self.subTest(kind=kind):
    b,a,t=self.fixture();a.update(x=3,y=2,hp=500,max_hp=500)
    ally=self.add(b,t,'friend',3,3,'player');outside=self.add(b,t,'outside',7,7,'player')
    with self.hit(),patch('backend.combat_mage.roll',return_value=1):mage.impact(b,deepcopy(a),kind,{'x':3,'y':2})
    self.assertLess(a['hp'],500);self.assertLess(ally['hp'],500);self.assertEqual(outside['hp'],500)
    if kind in ('meteor','fireball'):self.assertTrue(conditions.has(a,'burn'));self.assertTrue(conditions.has(ally,'burn'))
 def test_delayed_freeze_includes_caster_and_allies(self):
  b,a,t=self.fixture(['flash_freeze']);ally=self.add(b,t,'friend',3,3,'player');outside=self.add(b,t,'outside',7,7,'player')
  self.use(b,'flash_freeze',t);a['ability_activation']+=1
  with patch('backend.combat_mage.roll',return_value=1):mage.settle(b,a,'end')
  for u in (a,t,ally):self.assertTrue(conditions.has(u,'freeze'))
  self.assertFalse(conditions.has(outside,'freeze'))
 def test_forecast_uses_proposed_caster_position_without_mutation(self):
  b,a,t=self.fixture();a.update(x=0,y=0);source={**deepcopy(a),'x':3,'y':3};before=deepcopy(b)
  row=mage.preview(b,source,{'x':3,'y':2},self.skill('fireball'))
  self.assertIn(a['id'],row['target_forecasts']);self.assertGreater(row['target_forecasts'][a['id']]['damage_on_hit'],0);self.assertEqual(b,before)
  source.update(x=7,y=7);self.assertNotIn(a['id'],mage.preview(b,source,{'x':3,'y':2},self.skill('fireball'))['target_forecasts'])
 def test_ai_rejects_caster_or_ally_in_blast(self):
  for kind in ('fireball','meteor','singularity','flash_freeze'):
   with self.subTest(kind=kind):
    b,a,t=self.fixture([kind]);self.assertFalse(mage.auto(b,a,[t]));self.assertFalse(a['acted'])
    a.update(x=0,y=2);t.update(x=4,y=2);ally=self.add(b,t,'friend',4,3,'player')
    self.assertFalse(mage.auto(b,a,[t]));ally.update(x=7,y=7)
    with self.hit():self.assertTrue(mage.auto(b,a,[t]))
 def test_dash_forecast_includes_own_fire_and_deduplicates_overlaps(self):
  b,a,t=self.fixture();mage.scorch(b,a,{'x':3,'y':2},2)
  ally=self.add(b,t,'friend',7,7,'player');mage.scorch(b,ally,{'x':3,'y':2},2)
  before=deepcopy(b);self.assertEqual(combat._dash_ground_damage(b,a,[(3,2),(4,2),(3,2)]),12);self.assertEqual(b,before)
  # A real route excludes the tile already occupied. Start outside this path
  # so all three entries, including the return to (3,2), legitimately count.
  t.update(x=2,y=2,zone_location=[2,2])
  self.assertEqual(combat._dash_ground_damage(b,t,[(3,2),(4,2),(3,2)]),60)
 def test_lethal_self_hit_finishes_other_victims(self):
  b,a,t=self.fixture(['fireball']);a['hp']=1;ally=self.add(b,t,'friend',3,3,'player')
  with self.hit():self.use(b,'fireball',t)
  self.assertFalse(combat._combat_active(a));self.assertLess(t['hp'],500);self.assertLess(ally['hp'],500)
  json.dumps(combat.battle_view(b))


 def test_boss_freeze_feedback_retains_elemental_ice_after_one_turn_expiry(self):
  b,a,t=self.fixture();t['boss']=True
  with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
  event=next(e for e in b['animation_events'] if e.get('status_id')=='freeze')
  ice=next(s for s in event['statuses_snapshot'] if s['id']=='freeze')
  self.assertTrue(ice['elemental_freeze']);self.assertEqual(ice['turns'],1)
  t['status_activation']=[99,0];conditions.start_activation(b,t);self.assertTrue(t['forced_skip']);conditions.finish_activation(t)
  self.assertFalse(conditions.has(t,'freeze'));self.assertTrue(conditions.has(t,'wet'));self.assertTrue(ice['elemental_freeze'])

if __name__=='__main__' :unittest.main()
