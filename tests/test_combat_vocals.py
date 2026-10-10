import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_vocals
from backend.game import new_game
from backend.battle_lab import layout_presets
from backend.prison_recruitment import initialize_prisoner

class CombatVocalsTests(unittest.TestCase):
    def test_only_supported_audited_humanoids_are_assigned(self):
        for race in ('Human','Goblin'):
            for gender in ('male','female'):
                for personality in combat_vocals.PERSONALITIES:
                    u=dict(race=race,gender=gender,personality_id=personality,recruitable_snapshot={'job_id':'rogue'})
                    combat_vocals.assign(u)
                    self.assertEqual(u['combat_voice_key'],f'{race.lower()}_{gender}_{personality}')
                    self.assertEqual(u['combat_voice_key'],u['recruitable_snapshot']['combat_voice_key'])
        for extras in ({'race':'Elf'},{'gender':''},{'personality_id':'unknown'},{'creature':True},{'species_profile':'store_rat'}):
            u=dict(race='Goblin',gender='male',personality_id='guardian',recruitable_snapshot={'job_id':'rogue'})
            u.update(extras);combat_vocals.assign(u);self.assertNotIn('combat_voice_key',u)

    def test_audited_layouts_keep_their_authored_identity(self):
        observed=set()
        for mission in ('roadside_toll','goblin_pickpockets','ruined_well','supply_watch','timber_creek','tool_shed','herbs_wall','prison_rival_e','prison_former_e','prison_proof_e'):
            for preset in layout_presets('contract:'+mission):
                b=combat.create_contract_battle(new_game({'name':'QA'}),['player'],preset['seed'],mission,True)
                for u in combat._living(b,'enemy'):
                    key=combat_vocals.voice_key(u)
                    self.assertEqual(u['combat_voice_key'],key)
                    self.assertEqual(u['recruitable_snapshot']['combat_voice_key'],key)
                    observed.add(key)
        self.assertGreaterEqual(len(observed),12)

    def test_captured_voice_survives_recruitment_and_battle_entry(self):
        u={'id':'c','name':'QA','race':'Goblin','gender':'female','personality_id':'survivor',
           'recruitable_snapshot':{'job_id':'ranger','personality_id':'survivor'}}
        combat_vocals.assign(u)
        initialize_prisoner(u,now=0)
        c=u['recruitment']['candidate']
        self.assertEqual(c['combat_voice_key'],'goblin_female_survivor')
        state=new_game({'name':'QA'})
        before=deepcopy(c)
        b=combat._player_unit(state,c,1,1)
        self.assertEqual(b['combat_voice_key'],before['combat_voice_key'])
        initialize_prisoner(u,now=1)
        self.assertEqual(u['recruitment']['candidate']['combat_voice_key'],before['combat_voice_key'])

    def test_regular_players_and_animals_do_not_gain_a_humanoid_voice(self):
        state=new_game({'name':'QA'})
        self.assertIsNone(combat._player_unit(state,state['characters'][0],1,1).get('combat_voice_key'))
        for mission in ('rats_storehouse','wolves_fence'):
            b=combat.create_contract_battle(state,['player'],'layout-1',mission,True)
            self.assertTrue(all(not u.get('combat_voice_key') for u in combat._living(b,'enemy')))

    def test_slinger_event_identifies_attacker_without_moving_its_target_anchor(self):
        state=new_game({'name':'QA'})
        b=combat.create_contract_battle(state,['player'],'layout-1','goblin_pickpockets',True)
        a=combat._living(b,'enemy')[0];t=b['units']['player']
        b.update(terrain=[],animation_events=[],zones=[],objects={})
        b['units']={a['id']:a,t['id']:t}
        a.update(x=5,y=5,attack_range=3);t.update(x=6,y=5)
        with patch.object(combat,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            combat._perform_attack(b,a,t,'ballistic',ability={'npc_kind':'goliath_shot','elevation_rule':'ballistic'})
        e=next(e for e in b['animation_events'] if e.get('skill')=='specialty_stone')
        self.assertEqual(e['unit_id'],t['id'])
        self.assertEqual(e['attacker_id'],a['id'])
        self.assertTrue(e['attack_event'])
