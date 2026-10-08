import unittest,json
from copy import deepcopy
from unittest.mock import patch
from backend import combat,combat_conditions as conditions,combat_mage as mage,combat_dots as dots
from tests import test_mage_jobs as fixtures

class PercentageDotTests(unittest.TestCase):
 def fixture(self,hp=50):
  b,a,t=fixtures.MageTests().fixture();t.update(hp=hp,max_hp=hp,status_activation=[10,1]);t.pop('dot_finished_stamp',None);t.pop('status_finished_stamp',None);return b,a,t
 def stack(self,t,a,sid,n):
  for _ in range(n):conditions.add_stack(t,sid,2,a)
 def test_burn_example_five_to_four_to_three(self):
  b,a,t=self.fixture();self.stack(t,a,'burn',5)
  for turn,damage,left in [(10,5,4),(11,4,3),(12,3,2)]:
   t['status_activation']=[turn,1];hp=t['hp'];combat._tick_gear_statuses(b,t);conditions.finish_activation(t)
   self.assertEqual(hp-t['hp'],damage);self.assertEqual(next(s for s in t['statuses'] if s['id']=='burn')['stacks'],left)
 def test_burn_resistance_does_not_block_application_and_scales_damage_last(self):
  for resist,expected in [(0,5),(50,2),(100,0)]:
   with self.subTest(resistance=resist):
    b,a,t=self.fixture();t['status_resistances']={'burn':resist}
    with patch('backend.combat_mage.roll',return_value=100):mage.burn(b,a,t,5)
    self.assertEqual(dots.count(t['statuses'][0]),5);self.assertEqual(combat._tick_dot_status(b,t,'burn'),expected)
 def test_target_damage_modifiers_apply_after_percentage_before_resistance(self):
  b,a,t=self.fixture(100);self.stack(t,a,'burn',5);conditions.apply(t,'pestilence',3,a);t['status_resistances']={'burn':20}
  self.assertEqual(combat._tick_dot_status(b,t,'burn'),10)  # 10 base -> 12 rounded after +25% -> 9.6 -> 10 HP.
 def test_minimum_is_per_stack_before_resistance(self):
  b,a,t=self.fixture(10);self.stack(t,a,'burn',3);self.assertEqual(combat._tick_dot_status(b,t,'burn'),3)
 def test_percentage_is_not_rounded_per_stack(self):
  b,a,t=self.fixture(75);self.stack(t,a,'burn',3);self.assertEqual(combat._tick_dot_status(b,t,'burn'),4)
 def test_flame_entry_adds_and_triggers_without_decay_and_overlap_is_one(self):
  b,a,t=self.fixture(100);mage.scorch(b,a,t,2);other={**deepcopy(a),'id':'other'};b['units']['other']=other;mage.scorch(b,other,t,2)
  self.stack(t,a,'burn',4);combat._trigger_zones(b,t,'entry')
  self.assertEqual(t['hp'],90);self.assertEqual(dots.count(t['statuses'][0]),5)
  combat._trigger_zones(b,t,'entry');self.assertEqual(t['hp'],78);self.assertEqual(dots.count(t['statuses'][0]),6)
 def test_regular_damage_and_decay_are_once_at_turn_end_not_views_or_start(self):
  b,a,t=self.fixture(100);self.stack(t,a,'burn',3);b['turn_index']=1;b['round']=10;t['status_activation']=None
  combat._current_unit(b);combat.battle_view(b);self.assertEqual(t['hp'],100)
  combat._tick_gear_statuses(b,t);combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],94)
  conditions.finish_activation(t);conditions.finish_activation(t);self.assertEqual(dots.count(t['statuses'][0]),2)
 def test_poison_and_bleed_damage_even_if_unit_guards(self):
  b,a,t=self.fixture(100);self.stack(t,a,'poison',2);self.stack(t,a,'bleed',3);t.update(moved=False,physical_action=False,guarding=True)
  combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],75);conditions.finish_activation(t)
  self.assertEqual({s['id']:s['stacks'] for s in t['statuses']},{'poison':1,'bleed':2})
 def test_caltrops_only_apply_bleed_until_turn_end(self):
  b,a,t=self.fixture(100);combat.spaces.place_zone(b,a,{'zone':'caltrops','turns':2},[{'x':3,'y':2},{'x':4,'y':2}]);t['zone_location']=[0,0]
  with patch('backend.combat_conditions.status_chance',return_value=100):combat._apply_zone_route(b,t,[(3,2),(4,2),(3,2)])
  self.assertEqual(t['hp'],100);self.assertEqual(dots.count(next(s for s in t['statuses'] if s['id']=='bleed')),3)
  combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],85)
 def test_new_stack_in_current_turn_still_decays_at_end(self):
  b,a,t=self.fixture();self.stack(t,a,'burn',1);conditions.finish_activation(t);self.assertFalse(conditions.has(t,'burn'))
 def test_json_legacy_layers_preserve_count_and_ignore_old_damage_or_duration(self):
  b,a,t=self.fixture(100);t['statuses']=[{'id':'poison','turns':2,'layers':[{'turns':1,'tick_damage':999},{'turns':2,'tick_damage':999},{'turns':1,'tick_damage':999}]}]
  b=json.loads(json.dumps(b));t=b['units'][t['id']];combat._tick_gear_statuses(b,t);self.assertEqual(t['hp'],90);conditions.finish_activation(t);self.assertEqual(dots.count(t['statuses'][0]),2)
 def test_armor_does_not_reduce_dot_and_barrier_still_absorbs(self):
  b,a,t=self.fixture(100);t['armor']=1000;self.stack(t,a,'burn',5);conditions.barrier(t,6,2,a)
  self.assertEqual(combat._tick_dot_status(b,t,'burn'),4);self.assertEqual(t['hp'],96)
 def test_dash_preview_survives_unstoppable_cleanse_and_is_pure(self):
  b,a,t=self.fixture(100);mage.scorch(b,a,t,2);t['fury']=1;before=deepcopy(t)
  with patch('backend.combat_martial.has_passive',side_effect=lambda u,sid:sid=='unstoppable'):
   self.assertEqual(combat._dash_ground_damage(b,t,[(t['x'],t['y'])]),0)
  self.assertEqual(t,before)
 def test_spell_zone_created_event_uses_parent_landing_packet(self):
  b,a,t=self.fixture(500)
  with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0},1)):mage.impact(b,a,'meteor',{'x':3,'y':2})
  event=next(e for e in b['animation_events'] if e['type']=='zone_created');cast=next(e for e in b['animation_events'] if e['type']=='mage_cast')
  self.assertEqual(event['attack_packet'],cast['attack_packet']);self.assertEqual(event['zone_id'],b['zones'][0]['id'])


 def test_poison_stacks_extend_duration_with_constant_ten_percent_tick(self):
  b,a,t=self.fixture(100);self.stack(t,a,'poison',4)
  for index in range(4):
   t['status_activation']=[20+index,1];hp=t['hp'];combat._tick_gear_statuses(b,t)
   self.assertEqual(hp-t['hp'],10)
   combat._tick_gear_statuses(b,t);self.assertEqual(hp-t['hp'],10)
   conditions.finish_activation(t)
   self.assertEqual(sum(dots.count(s) for s in t['statuses'] if s['id']=='poison'),3-index)
  self.assertFalse(conditions.has(t,'poison'))

 def test_poison_cashout_is_linear_while_bleed_is_still_triangular(self):
  _,_,t=self.fixture(100)
  self.assertEqual(dots.potential(t,'poison',4),40)
  self.assertEqual(dots.potential(t,'bleed',4),50)
  self.assertEqual(dots.base_damage(t,'poison',0),0)

if __name__=='__main__':unittest.main()
