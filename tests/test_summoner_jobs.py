import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat as c, combat_summoner as s, job_loadouts as jobs
from tests import test_mage_jobs as fixtures
from backend import combat_hazard_preview as hazards

class SummonerTests(unittest.TestCase):
 def fixture(self,rapid=False):
  b,a,t=fixtures.MageTests().fixture([])
  a.update(job_id='summoner',attack=20,intelligence=16,hp=80,max_hp=100,move=3,summon_capacity=3,skills=[deepcopy(v) for v in jobs.SKILLS.values() if v.get('summoner_kind')],passives=[deepcopy(jobs.SKILLS['job:summoner:rapid_conjuration'])] if rapid else [],ability_activation=1)
  t.update(x=5,y=2,hp=500,max_hp=500,armor=0)
  return b,a,t
 def cast(self,b,a,key,**cmd):
  return s.command(b,a,next(v for v in a['skills'] if v['summoner_kind']==key),cmd)
 def deploy(self,b,a,key='bound_companion',element='earth'):
  points=s.placement(b,a,key=='wisp_swarm')[:3 if key=='wisp_swarm' else 1]
  self.cast(b,a,key,positions=points,element=element)
  a['acted']=False
  return s.group(b,a,key)
 def test_pool_and_migration(self):
  self.assertEqual(len([k for k in jobs.SKILLS if k.startswith('job:summoner:')]),8)
  a={'job_id':'summoner','learned_skills':['job:summoner:wolf','job:summoner:wisps'],'equipped_skills':['job:summoner:wolf'],'job_practice':20}
  jobs.initialize(a);before=deepcopy(a);jobs.initialize(a);self.assertEqual(a,before);self.assertEqual(a['equipped_skills'],['job:summoner:bound_companion'])
 def test_protect_summoner_and_other_ally_receive_grass_healing(self):
  for recipient in ('owner','ally'):
   b,a,t=self.fixture();u=self.deploy(b,a,element='grass')[0];a['hp']=10
   ally={**deepcopy(a),'id':'ally','name':'Protected ally','x':4,'y':4,'hp':10};b['units']['ally']=ally
   ward=a if recipient=='owner' else ally
   s.order(b,a,{'order':'protect','entity_id':u['id'],'target_id':ward['id']})
   s.autonomous(b,a,u)
   self.assertEqual(ward['hp'],60);self.assertEqual(u['hp'],75)
   self.assertEqual((ally if ward is a else a)['hp'],10)
 def test_protect_group_affects_only_companion_and_rejects_invalid_targets_atomically(self):
  b,a,t=self.fixture();u=self.deploy(b,a)[0];wisps=self.deploy(b,a,'wisp_swarm')
  s.order(b,a,{'order':'stand_down','entity_id':'all'})
  s.order(b,a,{'order':'protect','entity_id':'all','target_id':a['id']})
  self.assertEqual(u['summon_order'],{'kind':'protect','target_id':a['id']})
  self.assertTrue(all(w['summon_order']['kind']=='stand_down' for w in wisps))
  for target,entity in [(t['id'],u['id']),(u['id'],u['id']),(a['id'],wisps[0]['id'])]:
   before=deepcopy(b)
   with self.assertRaises(ValueError):s.order(b,a,{'order':'protect','entity_id':entity,'target_id':target})
   self.assertEqual(b,before)
 def test_protect_invalidated_ally_falls_back_and_clear_restores_owner_healing(self):
  for clear in (False,True):
   b,a,t=self.fixture();u=self.deploy(b,a,element='grass')[0];a['hp']=10
   ally={**deepcopy(a),'id':'ally','name':'Ally','x':6,'y':4,'hp':10};b['units']['ally']=ally
   s.order(b,a,{'order':'protect','entity_id':u['id'],'target_id':ally['id']})
   if clear:s.order(b,a,{'order':'clear','entity_id':u['id']})
   else:ally.update(alive=False,conscious=False,hp=0)
   s.autonomous(b,a,u);self.assertEqual(a['hp'],60)
 def test_protect_prefers_threat_to_ally_over_low_hp_enemy_and_holds_near_ally(self):
  for element in ('earth','fire'):
   b,a,t=self.fixture();u=self.deploy(b,a,element=element)[0];u.update(x=3,y=3,move=0)
   a.update(x=2,y=2);t.update(x=3,y=2,hp=500,attack_range=1)
   decoy={**deepcopy(t),'id':'decoy','x':4,'y':3,'hp':200,'attack_range':1};b['units']['decoy']=decoy
   s.order(b,a,{'order':'protect','entity_id':u['id'],'target_id':a['id']})
   with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)),patch('backend.combat_summoner.roll',return_value=100):s.autonomous(b,a,u)
   self.assertLess(t['hp'],500);self.assertEqual(decoy['hp'],200)
   self.assertLessEqual(c._distance(u,a),2)
 def test_protect_routes_to_ally_and_grass_burst_centers_on_that_ally(self):
  b,a,t=self.fixture();u=self.deploy(b,a,element='grass')[0];u.update(x=1,y=1)
  ally={**deepcopy(a),'id':'ally','name':'Protected ally','x':5,'y':4,'hp':100};b['units']['ally']=ally
  t.update(x=6,y=4);s.order(b,a,{'order':'protect','entity_id':u['id'],'target_id':ally['id']})
  goal,_=s.destination(b,a,u,[t]);self.assertGreater(goal[0]+goal[1],2)
  u.update(x=4,y=4,move=0);s.autonomous(b,a,u)
  self.assertEqual((t['x'],t['y']),(7,4));self.assertEqual(a['hp'],80)
  effect=next(e for e in b['animation_events'] if e.get('skill')=='summoner_nature_burst')
  self.assertEqual((effect['x'],effect['y']),(5,4))
 def test_public_commands_leave_quick_actions_open_and_end_on_main(self):
  b,a,t=self.fixture(True);t.update(x=4,y=2,attack=1)
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   view=c.apply_player_command(b,{'action':'skill','skill_id':'job:summoner:wisp_swarm','positions':[{'x':3,'y':1},{'x':4,'y':1},{'x':4,'y':3}]})
   self.assertEqual(view['current_unit_id'],a['id']);self.assertFalse(a['acted'])
   c.apply_player_command(b,{'action':'summon_order','entity_id':'all','order':'stand_down'})
   self.assertTrue(all(u['summon_order']['kind']=='stand_down' for u in s.crew(b,a)))
   view=c.apply_player_command(b,{'action':'skill','skill_id':'job:summoner:spirit_projection','target_id':t['id']})
   self.assertEqual(view['current_unit_id'],a['id']);self.assertGreater(a['ability_activation'],1)
   self.assertLess(t['hp'],500);self.assertTrue(all(u['id'] not in b['turn_order'] for u in s.crew(b,a)))
 def test_rapid_conjure_then_projection_or_sacrifice_is_one_main_action(self):
  for payoff in ('spirit_projection','sacrifice'):
   b,a,t=self.fixture(True);t.update(x=4,y=2)
   self.assertFalse(self.cast(b,a,'wisp_swarm',positions=[{'x':3,'y':1},{'x':4,'y':1},{'x':4,'y':3}]))
   with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
    self.assertTrue(self.cast(b,a,payoff,**({'target_id':t['id']} if payoff=='spirit_projection' else {'x':4,'y':2})))
   self.assertTrue(a['acted']);self.assertLess(t['hp'],500)
 def test_creatures_wait_until_next_owner_turn_and_act_once_with_movement_events(self):
  b,a,t=self.fixture();u=self.deploy(b,a,element='fire')[0];t.update(x=7,y=2)
  hp=t['hp'];s.finish(b,a);self.assertEqual(t['hp'],hp)
  a['ability_activation']+=1;s.start(b,u)
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   s.finish(b,a);after=deepcopy(b);s.finish(b,a)
  self.assertEqual(b,after)
  self.assertTrue(any(e['type']=='movement' and e['unit_id']==u['id'] for e in b['animation_events']))
 def test_grass_offering_is_predictable_nonlethal_and_not_spammed(self):
  b,a,t=self.fixture();u=self.deploy(b,a,element='grass')[0];a['hp']=10
  s.autonomous(b,a,u);self.assertEqual((u['hp'],a['hp']),(75,60))
  s.autonomous(b,a,u);self.assertEqual(a['hp'],60)
 def test_grass_uses_full_hp_and_int_and_normal_attack_damage(self):
  b,a,t=self.fixture();u=self.deploy(b,a,element='grass')[0]
  self.assertEqual((u['max_hp'],u['intelligence'],u['attack']),(a['max_hp'],a['intelligence'],a['intelligence']))
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   s.attack(b,a,u,t)
  self.assertEqual(500-t['hp'],16)
 def test_innate_orders_appear_once_without_consuming_equipped_skills(self):
  b,a,t=self.fixture();before=deepcopy(a['skills'])
  for _ in range(2):
   view=c.battle_view(b);orders=[v for v in view['units'][a['id']]['skills'] if v['id']=='innate:summoner:orders']
   self.assertEqual(len(orders),1);self.assertFalse(orders[0]['availability']['available'])
  self.assertEqual(a['skills'],before);self.deploy(b,a)
  orders=next(v for v in c.battle_view(b)['units'][a['id']]['skills'] if v['id']=='innate:summoner:orders')
  self.assertTrue(orders['availability']['available']);self.assertTrue(orders['free_action'])
 def test_lethal_summon_attack_keeps_contact_and_death_events_after_cleanup(self):
  b,a,t=self.fixture();u=self.deploy(b,a,'wisp_swarm')[0];b['animation_events']=[]
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   c._perform_attack(b,{**t,'attack':50},u,'melee')
  c._check_end(b)
  self.assertEqual(u['condition'],'dismissed')
  events=b['animation_events'];death=next(e for e in events if e['type']=='martial_effect' and e.get('skill')=='summoner_dissolve' and e['unit_id']==u['id'])
  attack=next(e for e in events if e['type']=='melee_attack' and e['target_id']==u['id'])
  self.assertGreater(events.index(death),events.index(attack))
  damage=next(e for e in events if e['type']=='combat_feedback' and e['unit_id']==u['id'])
  self.assertEqual(damage['attack_packet'],attack['attack_packet'])
 def test_fire_wall_crossing_counts_each_cell_and_matches_route_warning(self):
  b,a,t=self.fixture();u=self.deploy(b,a,element='fire')[0];t.update(max_hp=100,hp=100,x=4,y=2)
  z=c.spaces.place_zone(b,u,{'zone':'fire_wall','turns':3},[{'x':4+i,'y':2} for i in range(3)]);z['entry_damage']=10
  path=[{'x':4+i,'y':2} for i in range(3)]
  forecast=hazards.forecast(b,t,path,c._combat_active,c._damage_before_barrier,c._living)
  for p in path:t.update(p);c._trigger_zones(b,t,'entry')
  self.assertEqual(len(next(v for v in t['statuses'] if v['id']=='burn')['layers']),3)
  self.assertEqual(100-t['hp'],forecast['damage'])
 def test_companion_death_starts_cooldown_and_owner_defeat_dismisses_all(self):
  b,a,t=self.fixture();u=self.deploy(b,a)[0]
  c._deal_damage(b,{**t,'attack':999},u);c._check_end(b)
  skill=next(v for v in a['skills'] if v['summoner_kind']=='bound_companion');self.assertEqual(c.abilities.availability(a,skill)['cooldown_remaining'],5)
  self.deploy(b,a,'wisp_swarm');a.update(hp=0,alive=False,conscious=False);c._check_end(b);self.assertFalse(s.crew(b,a))
 def test_hold_routes_around_wall_instead_of_greedy_distance_loop(self):
  b,a,t=self.fixture();u=self.deploy(b,a,element='fire')[0];u.update(x=1,y=1,move=2)
  b['terrain']=[{'id':f'block_{y}','kind':'tree','x':2,'y':y,'blocking':True} for y in range(4)]
  s.order(b,a,{'order':'hold','entity_id':u['id'],'x':4,'y':1})
  goal,_=s.destination(b,a,u,[t]);self.assertEqual(goal,(1,3))
 def test_one_hp_wisp_does_not_choose_a_route_through_fire(self):
  b,a,t=self.fixture();u=self.deploy(b,a,'wisp_swarm')[0];u.update(x=2,y=1,move=2)
  c.spaces.place_zone(b,a,{'zone':'scorched','turns':2},[{'x':3,'y':1}])
  s.order(b,a,{'order':'hold','entity_id':u['id'],'x':4,'y':1})
  goal,_=s.destination(b,a,u,[t]);self.assertNotEqual(goal,(4,1))
 def test_inheritance_capacity_and_no_initiative_turn(self):
  b,a,t=self.fixture();u=self.deploy(b,a)[0]
  self.assertEqual(u['max_hp'],100);self.assertEqual(u['attack'],10);self.assertNotIn(u['id'],b['turn_order']);self.assertEqual(c.entities.usage(b,a),0)
  w=self.deploy(b,a,'wisp_swarm');self.assertEqual(len(w),3);self.assertTrue(all(v['hp']==1 and v['movement_type']=='flying' for v in w));self.assertEqual(c.entities.usage(b,a),3)
 def test_group_cooldown_starts_only_after_last_death(self):
  b,a,t=self.fixture();w=self.deploy(b,a,'wisp_swarm');skill=next(v for v in a['skills'] if v['summoner_kind']=='wisp_swarm')
  a['ability_activation']=9;s.cleanup(b);self.assertTrue(c.abilities.availability(a,skill)['reclaim'])
  for u in w[:2]:s.die(b,u,'dies')
  self.assertEqual(c.entities.usage(b,a),1)
  s.cleanup(b);self.assertTrue(c.abilities.availability(a,skill)['reclaim'])
  s.die(b,w[-1],'dies');s.cleanup(b);self.assertEqual(c.abilities.availability(a,skill)['cooldown_remaining'],6)
 def test_reclaim_quick_and_rapid_actions(self):
  b,a,t=self.fixture(True);self.assertFalse(self.cast(b,a,'bound_companion',positions=s.placement(b,a)[:1],element='fire'));self.assertFalse(a['acted'])
  self.assertFalse(self.cast(b,a,'bound_companion'));self.assertFalse(a['acted']);self.assertFalse(s.crew(b,a))
 def test_placement_validation_is_atomic(self):
  b,a,t=self.fixture();before=deepcopy(b)
  with self.assertRaises(ValueError):self.cast(b,a,'wisp_swarm',positions=[{'x':0,'y':0}]*3)
  self.assertEqual(b,before)
 def test_overload_percent_and_once(self):
  b,a,t=self.fixture();u=self.deploy(b,a)[0];u['hp']=50
  self.cast(b,a,'overload',target_id=u['id']);self.assertEqual((u['hp'],u['max_hp'],u['attack']),(150,300,30));a['acted']=False
  with self.assertRaises(ValueError):self.cast(b,a,'overload',target_id=u['id'])
  a['ability_activation']+=3;s.start(b,u);s.cleanup(b);self.assertFalse(u['alive']);self.assertEqual(a['ability_state']['job:summoner:bound_companion']['ready_at'],a['ability_activation']+5)
 def test_life_pact_cost_and_no_suicide(self):
  b,a,t=self.fixture();u=self.deploy(b,a)[0];u['hp']=1;a['hp']=25
  with self.assertRaises(ValueError):self.cast(b,a,'life_pact',target_id=u['id'])
  a['hp']=26;self.cast(b,a,'life_pact',target_id=u['id']);self.assertEqual((a['hp'],u['hp']),(1,26))
 def test_stand_down_and_hold_do_not_attack_or_abandon_position(self):
  b,a,t=self.fixture();u=self.deploy(b,a)[0];u.update(x=4,y=2);a['ability_activation']+=1
  s.order(b,a,{'order':'stand_down','entity_id':'all'});s.finish(b,a);self.assertEqual(t['hp'],500);self.assertEqual((u['x'],u['y']),(4,2))
  a['ability_activation']+=1;s.order(b,a,{'order':'hold','entity_id':'all','x':4,'y':2})
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   s.finish(b,a)
  self.assertEqual((u['x'],u['y']),(4,2));self.assertLess(t['hp'],500)
 def test_projection_four_contributions_and_sacrifice_friendly_fire(self):
  b,a,t=self.fixture(True);u=self.deploy(b,a)[0];w=self.deploy(b,a,'wisp_swarm')
  for v,p in zip([u,*w],[(4,2),(5,1),(6,2),(5,3)]):v.update(x=p[0],y=p[1])
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   self.cast(b,a,'spirit_projection',target_id=t['id'])
  self.assertEqual(t['hp'],500-4*16)
  a.update(acted=False,x=4,y=3,hp=100)
  self.cast(b,a,'sacrifice',x=5,y=2)
  self.assertFalse(s.crew(b,a));self.assertLess(a['hp'],100);self.assertTrue(c.conditions.has(t,'blind'))
 def test_swap_checks_ownership_and_locks_movement(self):
  b,a,t=self.fixture();u=self.deploy(b,a)[0];pos=(u['x'],u['y']);start=(a['x'],a['y'])
  self.assertFalse(self.cast(b,a,'transposition',ally_id=a['id'],target_id=u['id']))
  self.assertEqual((a['x'],a['y']),pos);self.assertEqual((u['x'],u['y']),start);self.assertEqual(c._movement_limit(a),0)
 def test_projection_bolts_start_at_each_contributor_and_keep_separate_packets(self):
  b,a,t=self.fixture(True);units=self.deploy(b,a,'wisp_swarm')
  for u,p in zip(units,[(4,2),(5,1),(6,2)]):u.update(x=p[0],y=p[1])
  skill=next(v for v in a['skills'] if v['summoner_kind']=='spirit_projection')
  before=deepcopy(b);forecast=s.previews(b,a,skill)[t['id']];self.assertEqual(b,before)
  b['animation_events']=[]
  with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
   self.cast(b,a,'spirit_projection',target_id=t['id'])
  bolts=[e for e in b['animation_events'] if e['type']=='magic_projectile']
  self.assertEqual({e['attacker_id'] for e in bolts},{u['id'] for u in units})
  self.assertEqual(len({e['attack_packet'] for e in bolts}),3)
  self.assertEqual(forecast['damage_on_hit'],500-t['hp'])
 def test_view_does_not_mutate_and_shows_order(self):
  b,a,t=self.fixture();self.deploy(b,a);before=deepcopy(b);view=c.battle_view(b);self.assertEqual(b,before);self.assertTrue(view['summoner']['summons'])

if __name__=='__main__':unittest.main()
