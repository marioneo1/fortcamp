import json
import unittest
from copy import deepcopy
from unittest.mock import patch

from backend import combat, combat_stats
from backend.battle_lab import layout_presets
from backend.game import new_game, effective_attribute
from backend.prison_recruitment import initialize_prisoner
from backend.equipment_rules import equipped_skills
from backend.combat_encounter_profiles import MISSION_IDS


class SharedCombatStatTests(unittest.TestCase):
    def test_neutral_body_and_rank_bonuses_have_one_source(self):
        state=new_game({})
        character=state['characters'][0]
        character.update(attributes=dict.fromkeys(combat_stats.ATTRIBUTE_NAMES,6),
                         equipment={},traits=[],perks={},adventurer_rank='S')
        unit=combat._player_unit(state,character,0,0)
        self.assertEqual((unit['max_hp'],unit['attack'],unit['armor']),(72,9,5))
        character['traits']=['naturally_gifted']
        self.assertEqual(effective_attribute(state,character,'str'),16)
        self.assertIn('×2.5',unit['stat_sources']['Attack'])

    def test_capture_tool_does_not_replace_lethal_attack_and_uses_new_base(self):
        state=new_game({'starting_role':'captor'})
        actor=combat._player_unit(state,state['characters'][0],0,0)
        self.assertEqual(actor['attack'],combat_stats.attack(actor['strength']))
        self.assertTrue(actor['capture_weapon'])

    def test_equipment_technique_uses_same_weapon_formula(self):
        item={'name':'Probe','power':3,'combat_skill':{'id':'probe','scaling':'dex'}}
        skill=equipped_skills([item],lambda key:8,1)[0]
        self.assertEqual(skill['attack'],combat_stats.attack(8,3,1))

    def test_recruitment_preserves_body_and_rank_across_all_audited_variations(self):
        for mission in sorted(MISSION_IDS):
            prepared = mission in ('frontier_watch_defense', 'prison_rescue_e')
            for preset in layout_presets(mission if prepared else 'contract:'+mission):
                state=new_game({})
                if mission == 'frontier_watch_defense':
                    battle=combat.create_frontier_watch_defense_battle(state,['player'],preset['seed'])
                elif mission == 'prison_rescue_e':
                    battle=combat.create_prison_rescue_battle(state,['player'],preset['seed'],True)
                else:
                    battle=combat.create_contract_battle(state,['player'],preset['seed'],mission,True)
                for enemy in combat._living(battle,'enemy'):
                    if enemy.get('creature'):
                        continue
                    captive={'id':enemy['id'],'name':enemy['name'],'race':enemy['race'],
                             'recruitable_snapshot':deepcopy(enemy['recruitable_snapshot'])}
                    initialize_prisoner(captive,now=0)
                    candidate=json.loads(json.dumps(captive['recruitment']['candidate']))
                    gear=enemy['combat_equipment']
                    # Recruitment removes encounter gear. Compare the same weapon
                    # scaling/power; an unequipped Ranger legitimately uses STR.
                    weapon={'name':gear['name'],'weapon_type':gear['weapon_type'],
                            'weapon_scaling':gear['weapon_scaling'],'power':gear['weapon_power']}
                    with patch('backend.combat._equipped_weapon',return_value=weapon):
                        ally=combat._player_unit(state,candidate,0,0,battle_seed=preset['seed'])
                    with self.subTest(mission=mission,layout=preset['id'],unit=enemy['id']):
                        self.assertEqual(ally['max_hp'],enemy['max_hp'])
                        self.assertEqual(ally['attack'],enemy['attack'])
                        self.assertEqual(ally['armor']+enemy['combat_equipment']['armor'],enemy['armor'])
                        self.assertEqual(ally['attributes'],enemy['attributes'])
                        self.assertEqual(candidate['adventurer_rank'],enemy['adventurer_rank'])

    def test_legacy_ranked_attributes_are_not_inferred_and_multiplied_again(self):
        state=new_game({});candidate=state['characters'][0]
        candidate.update(attributes=dict.fromkeys(combat_stats.ATTRIBUTE_NAMES,8),equipment={},traits=[],perks={})
        self.assertEqual(effective_attribute(state,candidate,'vit'),8)
        self.assertEqual(combat._player_unit(state,candidate,0,0)['max_hp'],44)

    def test_animals_retain_their_species_profile(self):
        state=new_game({})
        for mission in ('rats_storehouse','wolves_fence'):
            preset=layout_presets('contract:'+mission)[0]
            battle=combat.create_contract_battle(state,['player'],preset['seed'],mission,True)
            for enemy in combat._living(battle,'enemy'):
                self.assertNotIn('recruitable_snapshot',enemy)
                self.assertTrue(enemy['species_profile'])


if __name__=='__main__':unittest.main()
