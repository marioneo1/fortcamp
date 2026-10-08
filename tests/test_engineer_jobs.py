import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat as c, combat_engineer as e, job_loadouts as jobs, combat_conditions as conditions
from tests import test_mage_jobs as fixtures

class EngineerTests(unittest.TestCase):
 def fixture(self):
  b,a,t=fixtures.MageTests().fixture([])
  a.update(job_id='engineer',attack=20,hp=100,max_hp=100,armor=2,attack_range=1,attack_elevation_rule='melee',ability_activation=1,skills=[deepcopy(v) for v in jobs.SKILLS.values() if v.get('engineer_kind')])
  t.update(x=6,y=2,hp=500,max_hp=500,armor=0)
  return b,a,t
 def cast(self,b,a,k,**cmd):return e.command(b,a,next(s for s in a['skills'] if s['engineer_kind']==k),cmd)
 def machine(self,b,a,k='sentry_turret'):
  return e.spawn(b,a,k,{'x':a['x']+1,'y':a['y']})
 def hit(self):return patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1))
 def test_pool_migration(self):
  self.assertEqual(len([k for k in jobs.SKILLS if k.startswith('job:engineer:')]),8)
  a={'job_id':'engineer','learned_skills':['job:engineer:turret','job:engineer:trap'],'equipped_skills':['job:engineer:turret'],'job_practice':20}
  jobs.initialize(a);before=deepcopy(a);jobs.initialize(a);self.assertEqual(a,before);self.assertEqual(a['equipped_skills'],['job:engineer:sentry_turret'])
 def test_build_two_full_turns_and_pause(self):
  b,a,t=self.fixture();p=e.placement(b,a)[0];self.cast(b,a,'sentry_turret',**p)
  e.finish(b,a);self.assertTrue(e.machines(b,a)[0]['under_construction']);self.assertEqual(a['construction']['remaining'],2)
  a['ability_activation']=2;e.finish(b,a);self.assertEqual(a['construction']['remaining'],1)
  a.update(ability_activation=3,forced_skip=True);e.finish(b,a);self.assertTrue(e.machines(b,a)[0]['under_construction'])
  a.update(ability_activation=4,forced_skip=False);e.finish(b,a);self.assertEqual(len(e.machines(b,a)),1);self.assertFalse(e.machines(b,a)[0]['under_construction'])
 def test_rapid_assembly_movement_and_consumption(self):
  b,a,t=self.fixture();self.cast(b,a,'rapid_assembly');self.assertFalse(a.get('acted'));self.assertGreater(c._movement_limit(a),0)
  self.assertTrue(any(v.get('skill')=='engineer_rapid_assembly' for v in b['animation_events']))
  self.assertTrue(any(any(cue['name']=='engineer_rapid_assembly' for cue in v.get('cues',[])) for v in b['animation_events']))
  self.assertTrue(any(s['id']=='engineer_rapid_assembly' for s in c.battle_view(b)['units'][a['id']]['statuses']))
  p=e.placement(b,a)[0];self.cast(b,a,'heavy_emplacement',**p);self.assertEqual(len(e.machines(b,a)),1);self.assertEqual(e.state(a,'rapid_assembly')['ready_at'],6)
  self.assertFalse(any(s['id']=='engineer_rapid_assembly' for s in c.battle_view(b)['units'][a['id']]['statuses']))
 def test_dynamite_cooldown_blocks_detonation_turn_then_recovers(self):
  b,a,t=self.fixture();self.cast(b,a,'dynamite',x=3,y=2)
  thrown=next(v for v in b['animation_events'] if v.get('skill')=='engineer_dynamite_throw')
  self.assertEqual(thrown['from'],{'x':a['x'],'y':a['y']})
  self.assertEqual((thrown['x'],thrown['y']),(3,2))
  self.assertEqual(thrown['hazard_snapshot']['id'],b['engineer_hazards'][0]['id'])
  a.update(ability_activation=2,acted=False);e.start(b,a)
  exploded=next(v for v in b['animation_events'] if v.get('skill')=='engineer_explosion')
  self.assertEqual(exploded['hazard_id'],thrown['hazard_id'])
  self.assertFalse(b['engineer_hazards'])
  self.assertEqual(c.abilities.availability(a,jobs.SKILLS[e.sid('dynamite')])['cooldown_remaining'],1)
  with self.assertRaises(ValueError):self.cast(b,a,'dynamite',x=3,y=2)
  a.update(ability_activation=3,acted=False);e.start(b,a)
  self.assertTrue(c.abilities.availability(a,jobs.SKILLS[e.sid('dynamite')])['available'])
 def test_unfinished_blocks_can_be_destroyed_and_releases_slot(self):
  b,a,t=self.fixture();p=e.placement(b,a)[0];self.cast(b,a,'sentry_turret',**p);u=e.machines(b,a)[0]
  self.assertTrue(c._blocked(b,p['x'],p['y']));self.assertEqual(u['hp'],2)
  a['ability_activation']=2;e.finish(b,a);self.assertEqual(t['hp'],500)
  c._deal_damage(b,t,u);self.assertEqual(u['hp'],1);c._deal_damage(b,t,u);e.cleanup(b)
  self.assertNotIn('construction',a);self.assertFalse(e.machines(b,a));self.assertFalse(u['extracted'])
  self.assertTrue(any(v['type']=='death_burst' and v['unit_id']==u['id'] for v in b['animation_events']))
  b['round']=u['machine_died_round']+1;e.cleanup(b);self.assertTrue(u['machine_fading']);self.assertFalse(u['extracted'])
  b['round']+=1;e.cleanup(b);self.assertTrue(u['extracted'])
 def test_completion_preserves_unfinished_damage(self):
  b,a,t=self.fixture();self.cast(b,a,'sentry_turret',**e.placement(b,a)[0]);u=e.machines(b,a)[0];c._deal_damage(b,t,u)
  for n in (2,3):a['ability_activation']=n;e.finish(b,a)
  self.assertFalse(u['under_construction']);self.assertEqual(u['hp'],1)
 def test_remote_scuttle_direct_preview_and_no_ejection(self):
  b,a,t=self.fixture();u=self.machine(b,a);origin=(a['x'],a['y']);s=jobs.SKILLS[e.sid('scuttle_protocol')]
  before=deepcopy(b);ground,units=e.previews(b,a,s);self.assertEqual(b,before);self.assertFalse(ground);self.assertIn(u['id'],units)
  self.assertIn(a['id'],units[u['id']]['target_forecasts']);self.cast(b,a,'scuttle_protocol',target_id=u['id'])
  self.assertFalse(u['alive']);self.assertEqual((a['x'],a['y']),origin)
 def test_mine_trigger_area_must_not_touch_enemy_and_aoe_detonates(self):
  b,a,t=self.fixture();t.update(x=4,y=2)
  self.assertNotIn({'x':3,'y':2},e.mine_placement(b,a))
  with self.assertRaises(ValueError):self.cast(b,a,'proximity_charge',x=3,y=2)
  p=e.mine_placement(b,a)[0];self.cast(b,a,'proximity_charge',**p);h=b['engineer_hazards'][0]
  e.area_hit(b,a,[p]);self.assertFalse(b['engineer_hazards'])
  event=next(v for v in b['animation_events'] if v.get('hazard_id')==h['id']);self.assertEqual(event['hazard_snapshot']['id'],h['id'])
 def test_direct_targeting_and_short_skill_copy(self):
  b,a,t=self.fixture();u=self.machine(b,a)
  for k in ('rapid_assembly','man_the_guns','dynamite','proximity_charge'):
   before=deepcopy(b);ground,units=e.previews(b,a,jobs.SKILLS[e.sid(k)]);self.assertEqual(before,b)
   if k in ('dynamite','proximity_charge'):self.assertTrue(ground)
   else:self.assertIn(a['id'] if k=='rapid_assembly' else u['id'],units)
  for skill in jobs.SKILLS.values():
   if skill.get('engineer_kind') or skill.get('summoner_kind'):self.assertLess(len(skill['description']),160);self.assertEqual(skill['description'].count('.'),1)
 def test_summoner_reclaim_copy_survives_engineer_presentation(self):
  from backend import combat_summoner as summoner
  from tests.test_summoner_jobs import SummonerTests
  b,a,t=SummonerTests().fixture()
  # Presentation passes run for every unit, regardless of its Job.
  s=deepcopy(jobs.SKILLS['job:summoner:bound_companion']);a['skills']=[s]
  positions=summoner.placement(b,a)
  summoner.command(b,a,s,{'positions':[positions[0]],'element':'fire'})
  view=c.battle_view(b);skill=next(s for s in view['units'][a['id']]['skills'] if s.get('summoner_kind')=='bound_companion')
  self.assertIn('Dismiss',skill['description']);self.assertIn('Reclaim',skill['name'])
 def test_unused_assembly_no_cooldown_and_no_mutation_on_bad_placement(self):
  b,a,t=self.fixture();self.cast(b,a,'rapid_assembly');before=deepcopy(b)
  with self.assertRaises(ValueError):self.cast(b,a,'sentry_turret',x=t['x'],y=t['y'])
  self.assertEqual(before,b);e.finish(b,a);self.assertEqual(e.state(a,'rapid_assembly').get('ready_at',0),0)
 def test_limits_refund_and_minimum_damage(self):
  b,a,t=self.fixture();u=self.machine(b,a);p=e.placement(b,a)[0]
  c._deal_damage(b,t,u);self.assertEqual(u['hp'],1);c._deal_damage(b,t,u);self.assertEqual(u['hp'],0)
  for p in e.placement(b,a)[:3]:e.spawn(b,a,'sentry_turret',p)
  with self.assertRaises(ValueError):self.cast(b,a,'sentry_turret',**e.placement(b,a)[0])
  e.destroy(b,e.machines(b,a)[0]);self.cast(b,a,'sentry_turret',**e.placement(b,a)[0]);self.assertIn('construction',a)
 def test_mount_manual_and_exit(self):
  b,a,t=self.fixture();u=self.machine(b,a);old=a['attack'];self.cast(b,a,'man_the_guns',target_id=u['id'])
  self.assertEqual(a['attack'],25);self.assertEqual(a['attack_range'],7);self.assertFalse(a.get('acted'))
  with self.hit():self.assertTrue(e.manual_attack(b,a,{'target_id':t['id']}))
  self.assertEqual(t['hp'],475);a['acted']=False;self.cast(b,a,'man_the_guns',**e.exits(b,a,u)[0]);self.assertEqual(a['attack'],old);self.assertNotIn('mounted_machine',a)
 def test_mounted_damage_routing_and_area(self):
  b,a,t=self.fixture();u=self.machine(b,a);self.cast(b,a,'man_the_guns',target_id=u['id'])
  c._deal_damage(b,t,a);self.assertEqual(u['hp'],1);self.assertEqual(a['hp'],100)
  c._deal_damage(b,{**t,'mage_spell':True},a);self.assertLess(a['hp'],100)
 def test_overclock_four_shots_and_break_cd(self):
  b,a,t=self.fixture();u=self.machine(b,a,'heavy_emplacement');self.cast(b,a,'man_the_guns',target_id=u['id']);self.cast(b,a,'overclock')
  with self.hit():
   self.assertFalse(e.manual_attack(b,a,{'target_id':t['id']}));self.assertTrue(e.manual_attack(b,a,{'target_id':t['id']}))
   a.update(ability_activation=2,acted=False);e.start(b,a);self.assertFalse(e.manual_attack(b,a,{'target_id':t['id']}));self.assertTrue(e.manual_attack(b,a,{'target_id':t['id']}))
  a.update(ability_activation=3,acted=False);e.start(b,a);self.assertFalse(u['alive']);self.assertNotIn('mounted_machine',a);self.assertEqual(e.state(a,'overclock')['ready_at'],8)
 def test_mine_friendly_and_stun_immune_disruption(self):
  for immune in (False,True):
   b,a,t=self.fixture();p=e.placement(b,a)[0];self.cast(b,a,'proximity_charge',**p)
   t.update(x=p['x'],y=p['y'],team='player')
   if immune:t['status_resistances']={'stun':100}
   e.entry(b,t);self.assertFalse(b['engineer_hazards']);self.assertTrue(t['engineer_interrupted']);self.assertFalse(c.bard.can_attack(t));self.assertEqual(conditions.has(t,'stun'),not immune)
 def test_dynamite_fuse_friendly_fire_and_fallback(self):
  b,a,t=self.fixture();t.update(x=3,y=2);a.update(x=2,y=2);self.cast(b,a,'dynamite',x=3,y=2)
  self.assertEqual(t['hp'],500);a['ability_activation']=2
  with patch('backend.combat_mage.roll',return_value=100):e.start(b,a)
  self.assertLess(t['hp'],500);self.assertLess(a['hp'],100);self.assertFalse(b['engineer_hazards'])
 def test_heavy_load_cycle_and_auto_no_manual_double(self):
  b,a,t=self.fixture();u=self.machine(b,a,'heavy_emplacement')
  with self.hit():
   e.finish(b,a);self.assertEqual(t['hp'],500)
   a['ability_activation']=2;e.finish(b,a);self.assertEqual(t['hp'],470)
   a['ability_activation']=3;e.finish(b,a);self.assertEqual(t['hp'],470)
   a['ability_activation']=4;e.finish(b,a);self.assertEqual(t['hp'],440)
 def test_committed_mine_route_stops_before_destination(self):
  b,a,t=self.fixture();a.update(x=1,y=2,zone_location=[1,2],engineer_location=[1,2]);b['engineer_hazards']=[{'id':'m','owner_id':a['id'],'team':'player','kind':'mine','x':3,'y':2}]
  a.update(x=4,y=2,movement_origin={'x':1,'y':2},movement_path=[{'x':x,'y':2,'cost':x-1} for x in (2,3,4)])
  c._record_movement(b,a,(1,2),[(2,2),(3,2),(4,2)])
  c._commit_player_movement(b,a);self.assertEqual((a['x'],a['y']),(2,2));self.assertTrue(a['engineer_interrupted'])
 def test_forced_route_mine_stops_animation_and_followup_attack(self):
  b,a,t=self.fixture();t.update(x=3,y=2);b['engineer_hazards']=[{'id':'m','owner_id':a['id'],'team':'player','kind':'mine','x':5,'y':2}]
  c._apply_displacement(b,a,t,{'mode':'push','distance':3,'ignore_resistance':True},20)
  self.assertEqual((t['x'],t['y']),(4,2));movement=next(v for v in b['animation_events'] if v['type']=='movement');self.assertEqual(movement['points'][-1],{'x':4,'y':2})
  with self.hit():self.assertFalse(c._perform_attack(b,t,a,'melee')[1])
 def test_mine_forecast_known_only(self):
  from backend.combat_hazard_preview import forecast
  b,a,t=self.fixture();h={'id':'m','owner_id':a['id'],'team':'player','kind':'mine','x':3,'y':2};b['engineer_hazards']=[h]
  path=[{'x':2,'y':2}];warning=forecast(b,a,path,c._combat_active,c._damage_before_barrier,c._living);self.assertIn('engineer_disruption',warning['effects'])
  h['team']='enemy';self.assertIsNone(forecast(b,a,path,c._combat_active,c._damage_before_barrier,c._living))
 def test_armor_piercing_and_burn_bypass_shell(self):
  b,a,t=self.fixture();u=self.machine(b,a);c._deal_damage(b,{**t,'attack':20},u,armor_pierce=40);self.assertFalse(u['alive'])
  u=self.machine(b,a);c.mage.burn(b,a,u);c._tick_dot_status(b,u,'burn');self.assertEqual(u['hp'],1)
 def test_scuttle_one_hp_floor_ejection_and_no_resistance(self):
  b,a,t=self.fixture();u=self.machine(b,a,'heavy_emplacement');self.cast(b,a,'man_the_guns',target_id=u['id']);a['hp']=2
  self.cast(b,a,'scuttle_protocol');self.assertFalse(u['alive']);self.assertNotIn('mounted_machine',a);self.assertEqual(a['hp'],1);self.assertNotEqual((a['x'],a['y']),(u['x'],u['y']))
 def test_command_api_rapid_then_build_and_mount(self):
  b,a,t=self.fixture();b['animation_events']=[]
  with patch('backend.combat._advance_to_player'):
   c.apply_player_command(b,{'action':'skill','skill_id':e.sid('rapid_assembly')})
   self.assertFalse(a.get('acted'));p=e.placement(b,a)[0]
   c.apply_player_command(b,{'action':'skill','skill_id':e.sid('sentry_turret'),**p})
   self.assertEqual(len(e.machines(b,a)),1)
 def test_dynamite_center_push_and_wall_collision(self):
  b,a,t=self.fixture();a.update(x=2,y=2);t.update(x=3,y=2)
  self.cast(b,a,'dynamite',x=3,y=2)
  b['terrain']=[{'id':'wall','x':4,'y':2,'kind':'wall','blocking':True}]
  a['ability_activation']=2
  with patch('backend.combat_mage.roll',return_value=100):e.start(b,a)
  self.assertTrue(any(v['type']=='collision_recoil' for v in b['animation_events']));self.assertTrue(conditions.has(t,'hobbled'))
 def test_preparing_mine_does_not_trigger_without_entry(self):
  b,a,t=self.fixture();a['engineer_location']=[a['x'],a['y']]
  p=e.placement(b,a)[0];self.cast(b,a,'proximity_charge',**p);a['acted']=False
  c._commit_player_movement(b,a);self.assertEqual(len(b['engineer_hazards']),1)
 def test_cancel_and_forced_displacement_release_construction(self):
  b,a,t=self.fixture();self.cast(b,a,'heavy_emplacement',**e.placement(b,a)[0]);a['acted']=False
  self.cast(b,a,'sentry_turret');self.assertNotIn('construction',a)
  a['acted']=False;self.cast(b,a,'sentry_turret',**e.placement(b,a)[0]);a['x']+=1;e.entry(b,a);self.assertNotIn('construction',a)
 def test_mine_interrupts_spell_before_cast_or_cooldown(self):
  b,a,t=self.fixture();s=deepcopy(jobs.SKILLS['job:mage:fireball'])
  a.update(x=4,y=2,zone_location=[1,2],engineer_location=[1,2],movement_origin={'x':1,'y':2},movement_path=[{'x':x,'y':2} for x in (2,3,4)])
  b['engineer_hazards']=[{'id':'m','owner_id':a['id'],'team':'player','kind':'mine','x':3,'y':2}]
  result=c.mage.execute(b,a,t,s)
  self.assertTrue(result['interrupted']);self.assertEqual((a['x'],a['y']),(2,2));self.assertEqual(t['hp'],500)
  self.assertNotIn(s['id'],a['ability_state']);self.assertFalse(b.get('zones'))
 def test_mine_forecast_stops_before_later_flames(self):
  from backend.combat_hazard_preview import forecast
  b,a,t=self.fixture();b['engineer_hazards']=[{'id':'m','owner_id':a['id'],'team':'player','kind':'mine','x':3,'y':2}]
  c.spaces.place_zone(b,t,{'zone':'scorched','turns':2},[{'x':4,'y':2}])
  result=forecast(b,a,[(2,2),(3,2),(4,2)],c._combat_active,c._damage_before_barrier,c._living)
  self.assertEqual(result['damage'],0);self.assertNotIn('burn',result['effects'])
 def test_view_read_only(self):
  b,a,t=self.fixture();self.machine(b,a);before=deepcopy(b);c.battle_view(b);c.battle_view(b);self.assertEqual(before,b)
if __name__=='__main__':unittest.main()
