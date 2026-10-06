import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from backend import job_loadouts as jobs, combat_martial as martial, combat
from tests import test_martial_jobs as fixtures


class SkillOrderTests(unittest.TestCase):
    def test_order_is_presentation_only_and_allowed_during_combat(self):
        state={'characters':[{'id':'player','status':'mission','equipped_skills':['a','b'],'job_practice':9}]}
        before=deepcopy(state)
        self.assertEqual(jobs.save_skill_order(state,'player',['b','a']),['b','a'])
        self.assertEqual(state['characters'][0]['equipped_skills'],before['characters'][0]['equipped_skills'])
        for ids in (['a','a'],[''],['x'*161]):
            with self.assertRaises(ValueError):jobs.save_skill_order(state,'player',ids)
        with self.assertRaises(ValueError):jobs.save_skill_order(state,'someone-else',['a'])

    def test_cooldown_passives_in_view_do_not_mutate_real_state(self):
        b,a,t=fixtures.MartialJobTests().fixture(('bloodthirst','unstoppable','too_angry_to_fall'))
        a['martial_state']={'bloodthirst_ready':a['ability_activation']+3,'unstoppable_ready':a['ability_activation']+2}
        before=deepcopy(b);view=combat.battle_view(b)
        statuses=[s for s in view['units'][a['id']]['statuses'] if s['id']=='passive_readiness']
        self.assertEqual(len(statuses),3)
        self.assertEqual(b,before)
        self.assertEqual(martial.passive_availability(a,a['passives'][0])['cooldown_remaining'],3)


class SkillOrderApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_owned_character_order_commits_and_foreign_character_rolls_back(self):
        from backend.main import character_skill_order, SkillOrderRequest
        from fastapi import HTTPException
        session=SimpleNamespace(commit=AsyncMock(),rollback=AsyncMock(),close=AsyncMock())
        row=SimpleNamespace(state={'characters':[{'id':'owned','status':'mission'}]})
        identity=SimpleNamespace(guild_id='order-test',user_id='owner')
        with patch('backend.main.locked_player',new=AsyncMock(return_value=(session,row))):
            result=await character_skill_order('owned',SkillOrderRequest(skill_ids=['p','a']),identity)
            self.assertEqual(result,{'skill_order':['p','a']});session.commit.assert_awaited_once()
            with self.assertRaises(HTTPException):
                await character_skill_order('foreign',SkillOrderRequest(skill_ids=['a']),identity)
            session.rollback.assert_awaited_once()
        self.assertEqual(row.state['characters'][0]['combat_skill_order'],['p','a'])
