import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat as c, combat_captor as cap, combat_conditions as conditions, job_loadouts as jobs
from tests import test_engineer_jobs as fixtures

class CaptorTests(unittest.TestCase):
 def fixture(self):
  b,a,t=fixtures.EngineerTests().fixture();a.update(job_id='captor',weapon='Frayed Capture Net',capture_weapon={'base':8,'range':2,'elevation_rule':'ballistic'},capture_attributes={'str':8,'dex':8,'int':8},passives=[],skills=[deepcopy(s) for s in jobs.SKILLS.values() if s.get('captor_kind')])
  t.update(x=a['x']+1,y=a['y'],hp=80,max_hp=80,intelligence=4,agility=4,armor=40,evasion=0,base_capture_chance=35)
  cap.normalize(a);cap.normalize(t);return b,a,t
 def cast(self,b,a,key,**cmd):return cap.command(b,a,jobs.SKILLS['job:captor:'+key],cmd)
 def test_eight_skills_and_migration_idempotent(self):
  self.assertEqual(len([s for s in jobs.SKILLS if s.startswith('job:captor:')]),8)
  a={'job_id':'captor','learned_skills':['job:captor:bind'],'equipped_skills':['job:captor:bind','job:captor:anchored']}
  jobs.initialize(a);before=deepcopy(a);jobs.initialize(a);self.assertEqual(a,before);self.assertIn('job:captor:bola',a['equipped_skills']);self.assertIn('job:captor:clean_capture',a['equipped_skills'])
 def test_subdue_reduces_resolve_not_hp_and_never_procs_weapon_damage(self):
  b,a,t=self.fixture();a.update(element='fire',on_hit={'id':'burn','chance':100,'turns':3})
  with patch.object(cap,'roll',return_value=0):c._capture_attempt(b,a,t)
  self.assertEqual(t['hp'],80);self.assertLess(t['resolve'],80);self.assertFalse(t['capture_ready']);self.assertFalse(t['statuses']);self.assertTrue(any(e['type']=='net_cast' for e in b['animation_events']))
 def test_armor_does_not_defend_resolve_int_agi_do(self):
  b,a,t=self.fixture();v=cap.preview(b,a,t)['resolve_damage'];t['armor']=0;self.assertEqual(v,cap.preview(b,a,t)['resolve_damage']);t.update(intelligence=40,agility=40);self.assertLess(cap.preview(b,a,t)['resolve_damage'],v)
 def test_isolation_unique_statuses_and_four_times_cap(self):
  b,a,t=self.fixture();self.assertEqual(cap.multiplier(b,a,t,'subduing_blow'),2.5)
  for sid in ('hobbled','disarm','stun'):conditions.apply(t,sid,2,a)
  self.assertEqual(cap.multiplier(b,a,t,'subduing_blow'),4)
  for _ in range(6):conditions.add_stack(t,'hobbled',4,a)
  self.assertEqual(cap.multiplier(b,a,t,'subduing_blow'),4)
  b['units']['third']={**a,'id':'third','x':t['x']+1};self.assertEqual(cap.multiplier(b,a,t,'subduing_blow'),1.5)
 def test_failed_capture_is_retryable_success_unconscious_and_collected(self):
  b,a,t=self.fixture();t['resolve']=0
  with patch.object(cap,'roll',return_value=99):self.assertFalse(cap.attempt(b,a,t))
  self.assertEqual(t['hp'],80)
  with patch.object(cap,'roll',return_value=0):self.assertTrue(cap.attempt(b,a,t))
  self.assertTrue(t['alive']);self.assertFalse(t['conscious']);self.assertEqual(t['condition'],'unconscious');self.assertTrue(t['captured'])
  c._secure_battlefield_loot(b);self.assertIn(t['id'],b['auto_captured_ids'])
 def test_clean_capture_scales_with_health_and_boss_base(self):
  b,a,t=self.fixture();t.update(boss=True,base_capture_chance=1);self.assertEqual(cap.odds(a,t),1)
  a['passives']=[jobs.SKILLS['job:captor:clean_capture']];self.assertEqual(cap.odds(a,t),2);a['hp']=50;self.assertEqual(cap.odds(a,t),1.5)
 def test_bola_four_stacks_and_hobbled_hook_quick(self):
  b,a,t=self.fixture()
  with patch.object(cap,'roll',return_value=0):self.assertTrue(self.cast(b,a,'bola',target_id=t['id']))
  self.assertEqual(cap.stacks(t,'hobbled'),4);self.assertEqual(t['hp'],80);a['acted']=False
  with patch.object(cap,'roll',return_value=0):self.assertFalse(self.cast(b,a,'hook_and_drag',target_id=t['id']))
  self.assertFalse(a['acted'])
 def test_hold_can_start_before_ready_consumes_stacks_and_ticks_resolve(self):
  b,a,t=self.fixture()
  for _ in range(7):conditions.add_stack(t,'hobbled',4,a)
  self.cast(b,a,'restraining_hold',target_id=t['id']);self.assertEqual(a['captor_hold']['remaining'],7);self.assertFalse(cap.stacks(t,'hobbled'))
  before=t['resolve'];cap.finish(b,a);self.assertEqual(t['resolve'],before)
  a['ability_activation']+=1
  with patch.object(cap,'roll',return_value=99):cap.finish(b,a)
  self.assertLess(t['resolve'],before);self.assertEqual(t['hp'],80);self.assertEqual(a['captor_hold']['remaining'],6)
  cap.start(b,t);self.assertTrue(t['forced_skip'])
 def test_hold_capture_ticks_and_cooldown_after_release(self):
  b,a,t=self.fixture();t['resolve']=0
  for _ in range(6):conditions.add_stack(t,'hobbled',4,a)
  self.cast(b,a,'restraining_hold',target_id=t['id']);a['ability_activation']+=1
  with patch.object(cap,'attempt',return_value=False) as attempt:cap.finish(b,a);self.assertEqual(attempt.call_count,1)
  cap.release(b,a);self.assertNotIn('captor_held_by',t);self.assertEqual(a['ability_state']['job:captor:restraining_hold']['ready_at'],a['ability_activation']+3)
 def test_hold_interference_displacement_and_incapacitation(self):
  for trigger in ('third','movement','stun','death'):
   with self.subTest(trigger=trigger):
    b,a,t=self.fixture();conditions.add_stack(t,'hobbled',4,a);self.cast(b,a,'restraining_hold',target_id=t['id'])
    if trigger=='third':b['units']['third']={**a,'id':'third','x':t['x']+1,'captor_hold':None}
    elif trigger=='movement':t['y']+=1
    elif trigger=='stun':conditions.apply(a,'stun',1,t)
    else:a['conscious']=False
    cap.cleanup(b);self.assertNotIn('captor_hold',a);self.assertNotIn('captor_held_by',t)
 def test_blitz_movement_evasion_and_delayed_cooldown(self):
  b,a,t=self.fixture();old=c._movement_limit(a);chance=c._attack_preview(b,t,a,'melee')['chance'];self.assertFalse(self.cast(b,a,'blitz'));self.assertEqual(c._movement_limit(a),old+3);self.assertLess(c._attack_preview(b,t,a,'melee')['chance'],chance)
  a['ability_activation']+=1;cap.start(b,a);self.assertTrue(cap.status(a,'captor_blitz'));a['ability_activation']+=1;cap.start(b,a);self.assertFalse(cap.status(a,'captor_blitz'));self.assertEqual(a['ability_state']['job:captor:blitz']['ready_at'],clock(a)+2)
 def test_abduct_separate_budget_and_target_follows_legal_path(self):
  b,a,t=self.fixture();conditions.add_stack(t,'hobbled',4,a);base=cap.drag_routes(b,a,t);self.assertTrue(base)
  self.cast(b,a,'blitz');expanded=cap.drag_routes(b,a,t);self.assertGreater(max(p['cost'] for p in expanded.values()),max(p['cost'] for p in base.values()))
  key,route=max(expanded.items(),key=lambda p:p[1]['cost']);x,y=map(int,key.split(','));self.assertTrue(self.cast(b,a,'abduct',target_id=t['id'],x=x,y=y))
  self.assertEqual((a['x'],a['y']),(x,y));self.assertEqual((t['x'],t['y']),(route['target_end']['x'],route['target_end']['y']));self.assertEqual(c.bard.forced_target(b,t)['id'],a['id'])
 def test_previews_are_readonly_and_hold_survives_json_save(self):
  b,a,t=self.fixture();conditions.add_stack(t,'hobbled',4,a);self.cast(b,a,'restraining_hold',target_id=t['id']);loaded=json.loads(json.dumps(b));cap.cleanup(loaded);self.assertIn('captor_hold',loaded['units'][a['id']]);before=deepcopy(b);c.battle_view(b);self.assertEqual(b,before)
 def test_basic_attack_stays_lethal_and_punches_with_capture_equipment(self):
  b,a,t=self.fixture();a.update(special=None);t.update(armor=0,hp=1)
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   c._perform_attack(b,a,t,'melee')
  self.assertEqual(t['condition'],'dead');self.assertTrue(any(e.get('melee_style')=='fist' for e in b['animation_events']))

 def test_player_commands_offer_both_basics_and_execute_quick_then_main(self):
  b,a,t=self.fixture();a['special']=deepcopy(jobs.SKILLS['job:captor:subduing_blow'])
  view=c.battle_view(b);self.assertIsNotNone(view['attack_previews'][t['id']]['attack']);self.assertIsNotNone(view['attack_previews'][t['id']]['subdue']);self.assertTrue(view['skill_previews'][a['special']['id']])
  with patch('backend.combat._advance_to_player'):
   c.apply_player_command(b,{'action':'skill','skill_id':'job:captor:blitz','target_id':a['id']})
   self.assertFalse(a['acted'])
   with patch.object(cap,'roll',side_effect=lambda b,a,t,k:0 if k=='hit' else 99):c.apply_player_command(b,{'action':'skill','skill_id':'job:captor:subduing_blow','target_id':t['id']})
  self.assertTrue(a['acted']);self.assertEqual(t['hp'],80);self.assertLess(t['resolve'],80)
 def test_hold_release_available_as_self_target_and_no_action(self):
  b,a,t=self.fixture();conditions.add_stack(t,'hobbled',4,a);self.cast(b,a,'restraining_hold',target_id=t['id']);a['acted']=False;a['special']=deepcopy(jobs.SKILLS['job:captor:restraining_hold'])
  view=c.battle_view(b);skill=next(s for s in view['units'][a['id']]['skills'] if s.get('captor_kind')=='restraining_hold')
  self.assertEqual(skill['name'],'Release Hold');self.assertIn(a['id'],view['skill_previews'][skill['id']]);self.assertFalse(cap.command(b,a,jobs.SKILLS[skill['id']],{'target_id':a['id']}));self.assertFalse(a['acted'])
 def test_hold_tick_idempotent_and_disarm_allows_spells(self):
  b,a,t=self.fixture();conditions.add_stack(t,'hobbled',4,a);self.cast(b,a,'restraining_hold',target_id=t['id']);a['ability_activation']+=1
  with patch.object(cap,'roll',return_value=99):cap.finish(b,a);before=t['resolve'];cap.finish(b,a);self.assertEqual(t['resolve'],before)
  cap.release(b,a);conditions.apply(a,'disarm',2,t);a['acted']=False
  self.assertFalse(c.abilities.availability(a,jobs.SKILLS['job:captor:subduing_blow'])['available']);self.assertTrue(c.abilities.availability(a,jobs.SKILLS['job:mage:fireball'])['available'])
 def test_captured_rat_is_unconscious_not_killed_and_map_completion_collects(self):
  b,a,t=self.fixture();t.update(form={'id':'rat','persistent':True},resolve=0)
  with patch.object(cap,'roll',return_value=0):cap.attempt(b,a,t)
  self.assertEqual(t['condition'],'unconscious');self.assertFalse(any(e['type']=='death_burst' for e in b['animation_events']))
  b.update(status='complete',outcome='failure')
  with patch('backend.combat._check_end_rules'):c._check_end(b)
  self.assertIn(t['id'],b['auto_captured_ids'])

 def test_pass_through_interferes_with_hold_even_without_hazards(self):
  b,a,t=self.fixture();conditions.add_stack(t,'hobbled',4,a);self.cast(b,a,'restraining_hold',target_id=t['id'])
  other=deepcopy(a);other.update(id='interferer',x=t['x']+3,y=t['y']);other.pop('captor_hold',None);other['statuses']=[];b['units'][other['id']]=other
  b['zones']=[];b['engineer_hazards']=[]
  c._apply_zone_route(b,other,[(t['x']+1,t['y']),(t['x']+2,t['y'])])
  self.assertNotIn('captor_hold',a);self.assertNotIn('captor_held_by',t)

 def test_every_resolve_attack_can_capture_on_threshold_or_retry(self):
  for kind in ('subdue','subduing_blow','bola','hook_and_drag'):
   for resolve in (1,0):
    with self.subTest(kind=kind,resolve=resolve):
     b,a,t=self.fixture();t['resolve']=resolve
     self.assertTrue(cap.preview(b,a,t,kind)['capture'])
     with patch.object(cap,'roll',return_value=0):
      if kind=='subdue':cap.strike(b,a,t,kind)
      else:self.cast(b,a,kind,target_id=t['id'])
     self.assertTrue(t['captured']);self.assertEqual(t['condition'],'unconscious');self.assertTrue(t['alive'])
     self.assertFalse(cap.status(t,'stun'));self.assertFalse(cap.status(t,'hobbled'))
 def test_failed_resolve_capture_and_misses_leave_target_conscious(self):
  b,a,t=self.fixture();t['resolve']=1;hp=t['hp']
  with patch.object(cap,'roll',side_effect=lambda b,a,t,k:0 if k=='hit' else 99):cap.strike(b,a,t,'subduing_blow')
  self.assertEqual(t['resolve'],0);self.assertEqual(t['hp'],hp);self.assertTrue(t['conscious']);self.assertFalse(t.get('captured'))
  before=len(b['log'])
  with patch.object(cap,'roll',return_value=99):cap.strike(b,a,t,'bola')
  self.assertEqual(len(b['log']),before);self.assertFalse(t.get('captured'))

def clock(a):return a.get('ability_activation',0)
