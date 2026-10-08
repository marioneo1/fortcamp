import unittest
from copy import deepcopy
from backend import combat, combat_spaces as spaces, combat_conditions as conditions
from backend.combat_hazard_preview import forecast
from tests.test_combat_abilities import AbilityFoundationTests

class HazardPreviewTests(unittest.TestCase):
    def fixture(self):
        return AbilityFoundationTests().fixture()
    def preview(self,b,a,path):
        return forecast(b,a,path,combat._combat_active,combat._damage_before_barrier,combat._living)
    def test_burn_preview_matches_entry_damage_with_barrier_and_resistance_without_mutating(self):
        b,a,t=self.fixture();a['status_resistances']={'burn':50}
        conditions.barrier(a,2,2,t)
        spaces.place_zone(b,t,{'zone':'scorched','turns':2},[{'x':2,'y':3},{'x':2,'y':4}])
        before=deepcopy(b);path=[(2,3),(2,4)]
        result=self.preview(b,a,path)
        self.assertEqual(b,before);self.assertEqual(result['effects']['burn']['stacks'],2)
        actual=deepcopy(b);probe=actual['units'][a['id']];probe.update(x=2,y=4)
        combat._apply_zone_route(actual,probe,path)
        self.assertEqual(result['damage'],100-probe['hp'])
    def test_caltrops_warn_of_delayed_bleed_and_hobble_without_immediate_damage(self):
        b,a,t=self.fixture();spaces.place_zone(b,t,{'zone':'caltrops','turns':2},[{'x':2,'y':3},{'x':2,'y':4}])
        result=self.preview(b,a,[(2,3),(2,4)])
        self.assertEqual(result['damage'],0);self.assertEqual(result['effects']['bleed']['stacks'],2)
        self.assertEqual(result['effects']['hobbled']['stacks'],2)
        a['passives'].append({'id':'job:rogue:trap_expert'})
        self.assertIsNone(self.preview(b,a,[(2,3),(2,4)]))
    def test_overlapping_flames_do_not_multiply_entry_and_immunity_is_explicit(self):
        b,a,t=self.fixture();spaces.place_zone(b,t,{'zone':'scorched','turns':2},[{'x':2,'y':3}])
        b['zones'].append({**deepcopy(b['zones'][0]),'id':'zone_2'})
        result=self.preview(b,a,[(2,3)]);self.assertEqual(result['damage'],2);self.assertEqual(result['effects']['burn']['stacks'],1)
        a['status_resistances']={'bleed':100};b['zones']=[];spaces.place_zone(b,t,{'zone':'caltrops','turns':2},[{'x':2,'y':3}])
        result=self.preview(b,a,[(2,3)]);self.assertNotIn('bleed',result['effects']);self.assertIn('hobbled',result['effects'])
    def test_movement_tree_contains_forecasts_for_final_path_not_discarded_preview(self):
        b,a,t=self.fixture();spaces.place_zone(b,t,{'zone':'scorched','turns':2},[{'x':2,'y':3},{'x':2,'y':4}])
        before=deepcopy(b);view=combat.battle_view(b);self.assertEqual(b,before)
        node=next(n for n in view['movement_tree'] if (n['x'],n['y'])==(2,4))
        self.assertEqual(node['hazard_forecast']['damage'],6)
        origin=next(n for n in view['movement_tree'] if (n['x'],n['y'])==(2,2))
        self.assertNotIn('hazard_forecast',origin)
    def test_resisted_stack_attempts_are_not_reported_as_guaranteed(self):
        b,a,t=self.fixture();a['status_resistances']={'bleed':50}
        spaces.place_zone(b,t,{'zone':'caltrops','turns':2},[{'x':2,'y':3}])
        result=self.preview(b,a,[(2,3)])
        self.assertTrue(result['uncertain']);self.assertEqual(result['effects']['bleed']['chance'],50)

    def test_delayed_mage_zones_are_not_entry_hazards(self):
        b,a,t=self.fixture();b['zones']=[{'id':'freeze','kind':'flash_freeze_armed','owner_id':t['id'],'cells':[{'x':2,'y':3}]}]
        self.assertIsNone(self.preview(b,a,[(2,3)]))
