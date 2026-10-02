import random
import unittest
from unittest.mock import patch

from backend.content import ITEMS, MISSION_TEMPLATES, GENERAL_LOOT_TABLE, EVENT_REWARD_TABLES, MISSION_RANKS
from backend.gear_expansion import CHAIN_RELICS
from backend.mission_loot import roll_item_pool, scene_reward_template
from backend.combat import _player_unit, _deal_damage, _current_unit, create_goblin_warcamp_battle, apply_player_command, _player_auto_turn
from backend.game import new_game


class GearExpansionTests(unittest.TestCase):
    def battle(self, iid):
        state = new_game({'name': 'Gear Tester', 'attributes': {'str': 10, 'vit': 10}})
        state['inventory'].append({'instance_id': 'test-weapon', 'item_id': iid})
        state['characters'][0]['equipment']['weapon'] = 'test-weapon'
        battle = create_goblin_warcamp_battle(state, ['player'], 'gear-test')
        battle['turn_order'] = ['player', 'gob_guard', 'gob_chief', 'gob_archer', 'gob_horn']
        battle['turn_index'] = 0
        return battle, battle['units']['player'], battle['units']['gob_guard']

    def test_capture_skill_is_nonlethal_in_manual_and_auto_combat(self):
        for auto in (False, True):
            battle, actor, enemy = self.battle('goblin_net_bow')
            actor.update(x=2, y=2, attack=100)
            enemy.update(x=3, y=2, hp=2)
            # Isolate the capture technique from boss-priority targeting.
            battle['units']['gob_chief'].update(x=7, y=0)
            battle['units']['gob_archer'].update(x=7, y=1)
            battle['units']['gob_horn'].update(x=7, y=2)
            with patch('backend.combat.random.Random') as rng:
                rng.return_value.randint.return_value=1
                if auto:
                    _player_auto_turn(battle, actor, 'aggressive')
                else:
                    apply_player_command(battle, {'action': 'attack', 'target_id': enemy['id']})
            self.assertEqual(enemy['condition'], 'unconscious')
            self.assertTrue(enemy['alive'])
            self.assertFalse(actor['special_used'])
            self.assertEqual(actor['combat_record']['total_damage'],0)

    def test_element_affinities_and_nonlethal_safety(self):
        battle, actor, enemy = self.battle('coalbrand_sabre')
        actor.update(attack=12, on_hit=None)
        enemy.update(hp=100, max_hp=100, armor=0, racial_weaknesses=['burn'])
        self.assertEqual(_deal_damage(battle, actor, enemy), 15)
        self.assertEqual(_deal_damage(battle, actor, enemy, intent='nonlethal'), 12)
        enemy['racial_weaknesses']=[];enemy['racial_resistances']=['burn']
        self.assertEqual(_deal_damage(battle, actor, enemy), 9)

    def test_status_ticks_once_per_activation_and_expires(self):
        battle, actor, enemy = self.battle('coalbrand_sabre')
        actor['statuses']=[{'id': 'burn', 'turns': 2}]
        actor.update(hp=60, max_hp=60, armor=99, guarding=True)
        _current_unit(battle)
        self.assertEqual(actor['hp'], 58)
        self.assertTrue(actor['guarding'])
        for _ in range(10):_current_unit(battle)
        self.assertEqual(actor['hp'], 58)
        battle['round']+=1
        _current_unit(battle)
        self.assertEqual(actor['hp'], 56)
        self.assertEqual(actor['statuses'], [])

    def test_poison_immune_races_and_subdue_never_proc(self):
        battle, actor, enemy = self.battle('venomthorn_bow')
        actor.update(attack=1, on_hit={'id':'poison','chance':100,'turns':2})
        enemy.update(hp=100, max_hp=100, racial_resistances=['poison'])
        _deal_damage(battle,actor,enemy)
        self.assertEqual(enemy['statuses'],[])
        enemy['racial_resistances']=[]
        _deal_damage(battle,actor,enemy,intent='nonlethal')
        self.assertEqual(enemy['statuses'],[])
        _deal_damage(battle,actor,enemy)
        self.assertEqual(enemy['statuses'][0]['id'],'poison')

    def test_event_caches_have_low_tiers_and_relics_never_enter_regular_pools(self):
        for event_id,event in EVENT_REWARD_TABLES.items():
            seen=set()
            for seed in range(180):
                iid,_,rarity=roll_item_pool({'event':event_id},'D',random.Random(seed),ITEMS,GENERAL_LOOT_TABLE,event,MISSION_RANKS,True)
                self.assertNotIn(iid,CHAIN_RELICS.values())
                seen.add(rarity)
            self.assertEqual(seen,{'common','uncommon'})

    def test_relic_checks_require_followup_and_have_real_drop_rates(self):
        for mid,iid in CHAIN_RELICS.items():
            raw=MISSION_TEMPLATES[mid]
            direct=scene_reward_template(raw,{})
            self.assertFalse(any(r.get('requires_chain_parent') for r in direct['reward_rolls']))
            followup=scene_reward_template(raw,{'chain_parent_id':'previous-contract'})
            roll=next(r for r in followup['reward_rolls'] if r.get('requires_chain_parent'))
            self.assertEqual(roll['reward']['item'],iid)
            self.assertEqual((roll['chance'],roll['critical_bonus']),(14,8))
            self.assertIn('mission_exclusive',ITEMS[iid]['tags'])

    def test_granted_offhand_skill_and_magic_rule(self):
        state=new_game({'name':'Caster'})
        state['inventory'].append({'instance_id':'storm','item_id':'bottled_storm'})
        state['characters'][0]['equipment']['accessory']='storm'
        unit=_player_unit(state,state['characters'][0],0,0)
        self.assertEqual(unit['special']['name'],'Storm Release')
        self.assertEqual(unit['special']['elevation_rule'],'ignore')
        before = unit['special']['attack']
        state['characters'][0]['attributes']['int'] += 8
        stronger = _player_unit(state,state['characters'][0],0,0)
        self.assertEqual(stronger['special']['attack'],before+4)
        self.assertEqual(stronger['attack'],unit['attack'])

    def test_burning_commander_triggers_victory_once(self):
        battle, actor, _ = self.battle('coalbrand_sabre')
        chief=battle['units']['gob_chief']
        chief.update(hp=1,statuses=[{'id':'burn','turns':2,'source_id':'player','source_name':actor['name']}])
        battle['turn_order']=['gob_chief','player']
        battle['round'] += 1
        self.assertIsNone(_current_unit(battle))
        self.assertEqual(chief['condition'],'dead')
        self.assertTrue(battle['decision_pending'])
        self.assertTrue(battle['battle_won'])
        events=len(battle.get('animation_events',[]))
        _current_unit(battle)
        self.assertEqual(len(battle.get('animation_events',[])),events)


if __name__=='__main__':unittest.main()
