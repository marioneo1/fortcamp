import time
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from backend.game import new_game, normalize_state, analyze_mission
from backend.mercenaries import market, prepare, betrayal, quote, recruit, settle, decorate_battle, betrayal_battle
from backend.combat import create_goblin_warcamp_battle, _check_end, _claim_victory
from backend.services import pool_event, POOL_SECONDS, claim_budget


class MercenaryTests(unittest.TestCase):
    def state(self):
        state=normalize_state(new_game({'name':'Owner','traits':['guard']}))
        state['resources']['gold']=5000
        market(state,'owner')
        return state

    def test_persistent_contacts_and_missing_only_replenishment(self):
        state=self.state();before=deepcopy(state['mercenaries'])
        self.assertEqual(market(state,'owner'),market(state,'owner'))
        state['mercenaries'].pop(1);market(state,'owner')
        self.assertEqual(len(state['mercenaries']),4)
        for offer in (before[0],before[2],before[3]):self.assertIn(offer,state['mercenaries'])

    def test_hire_validates_private_owner_crew_slots_gold_and_busy(self):
        for kind in ('public','wrong-owner','no-crew','no-slot','no-gold','busy','duplicate'):
            state=self.state();mid=state['mercenaries'][0]['id'];state['_mercenary_owner']='owner'
            mission=SimpleNamespace(id='job',claimed_by_user_id='owner')
            ids=[mid];party=['player',mid]
            if kind=='public':mission.claimed_by_user_id=None
            if kind=='wrong-owner':mission.claimed_by_user_id='other'
            if kind=='no-crew':party=[mid]
            if kind=='no-slot':party=['player']
            if kind=='no-gold':state['resources']['gold']=0
            if kind=='busy':state['mercenaries'][0]['busy_mission_id']='other-job'
            if kind=='duplicate':ids=[mid,mid]
            before=deepcopy(state)
            with self.assertRaises(ValueError):prepare(state,mission,ids,party,spend=True)
            self.assertEqual(state,before,kind)

    def test_hires_charge_once_are_weak_and_keep_solo_claim_bonus(self):
        state=self.state();mid=state['mercenaries'][0]['id'];state['_mercenary_owner']='owner'
        mission=SimpleNamespace(id='job',claimed_by_user_id='owner')
        prepare(state,mission,[mid],['player',mid],spend=True)
        self.assertEqual(state['resources']['gold'],4990)
        c=next(c for c in state['characters'] if c['id']==mid)
        self.assertTrue(c['temporary_mercenary'])
        self.assertTrue(any(i.get('mercenary_gear') for i in state['inventory']))
        with self.assertRaises(ValueError):prepare(state,mission,[mid],['player',mid],spend=True)
        self.assertEqual(claim_budget(state,POOL_SECONDS*100,POOL_SECONDS*100,POOL_SECONDS*100+121)['solo_bonus'],10)
        definition={'name':'Check','stat':'combat','rank':'D','difficulty':14,'party_size':2}
        hired=analyze_mission(state,definition,['player',mid])
        c['temporary_mercenary']=False
        crew=analyze_mission(state,definition,['player',mid])
        self.assertEqual(crew['criteria_bonus']-hired['criteria_bonus'],1)

    def test_private_followup_hires_before_claimed_by_is_set(self):
        state=self.state();state['_mercenary_owner']='owner';mid=state['mercenaries'][0]['id']
        mission=SimpleNamespace(id='chain',claimed_by_user_id=None,analysis={'chain_owner_user_id':'owner'})
        prepare(state,mission,[mid],['player',mid],spend=True)
        self.assertEqual(state['resources']['gold'],4990)

    def test_trust_discount_buyout_and_no_recruitment_without_relationship(self):
        state=self.state();o=state['mercenaries'][0];initial=quote(o)
        with self.assertRaises(ValueError):recruit(state,o['id'])
        o['relationship']=30
        self.assertLess(quote(o)['fee'],initial['fee'])
        self.assertLess(quote(o)['betrayal_chance'],initial['betrayal_chance'])
        c=recruit(state,o['id'])
        self.assertIn(c,state['characters'])
        self.assertNotIn(o,state['mercenaries'])
        self.assertFalse(c.get('temporary_mercenary'))
        self.assertEqual(state['resources']['gold'],4900)

    def test_group_betrayal_is_stable_and_loyal_holdout_never_alone(self):
        offers=self.state()['mercenaries'][:3]
        results=[betrayal(offers,str(i)) for i in range(1000)]
        self.assertTrue(any(len(r)==3 for r in results))
        self.assertTrue(any(len(r)==2 for r in results))
        self.assertFalse(any(len(r)==1 for r in results))
        self.assertLess(sum(bool(r) for r in results),160)
        self.assertEqual(betrayal(offers,'fixed'),betrayal(offers,'fixed'))
        for o in offers:o['relationship']=100
        self.assertFalse(betrayal(offers[:1],'trusted'))

    def test_death_removes_contact_and_fleeing_does_not(self):
        state=self.state();dead,escaped=state['mercenaries'][:2]
        battle={'units':{'dead':{'mercenary_id':dead['id'],'condition':'dead'},'escaped':{'mercenary_id':escaped['id'],'condition':'active','alive':False,'extracted':True}}}
        settle(state,{},'failure',battle,final=False)
        self.assertNotIn(dead,state['mercenaries']);self.assertIn(escaped,state['mercenaries'])

    def test_settlement_releases_hires_removes_loaned_gear_once(self):
        state=self.state();mid=state['mercenaries'][0]['id'];state['_mercenary_owner']='owner'
        prepare(state,SimpleNamespace(id='job',claimed_by_user_id='owner'),[mid],['player',mid],spend=True)
        analysis={'mercenary_ids':[mid]}
        settle(state,analysis,'success');settle(state,analysis,'success')
        self.assertEqual(len(state['characters']),1)
        self.assertFalse(any(i.get('mercenary_gear') for i in state['inventory']))
        self.assertEqual(state['mercenaries'][0]['relationship'],2)
        self.assertIsNone(state['mercenaries'][0]['busy_mission_id'])

    def test_rare_appearances_have_notifications_and_valid_positions(self):
        for kind in ('corpse','friendly','hostile'):
            state=self.state();analysis={}
            b=create_goblin_warcamp_battle(state,['player'],'placement',defer_start=True)
            decorate_battle(state,analysis,b,'placement',force=kind)
            guests=[u for u in b['units'].values() if u.get('mercenary_id')]
            self.assertEqual(len(guests),1,kind)
            u=guests[0]
            self.assertTrue(0<=u['x']<b['width'] and 0<=u['y']<b['height'])
            self.assertEqual(sum(v['x']==u['x'] and v['y']==u['y'] for v in b['units'].values()),1)
            self.assertIn('mercenary_notice',b)
            decorate_battle(state,analysis,b,'again',force=kind)
            self.assertEqual(len([u for u in b['units'].values() if u.get('mercenary_id')]),1)
            if kind=='corpse':self.assertNotIn(u['mercenary_id'],[o['id'] for o in state['mercenaries']])

    def test_hostile_blocks_victory_and_retreat_fails(self):
        state=self.state();b=create_goblin_warcamp_battle(state,['player'],'placement',defer_start=True)
        decorate_battle(state,{},b,'placement',force='hostile')
        b['units']['gob_chief'].update(alive=False,conscious=False,hp=0,condition='dead')
        _check_end(b);self.assertFalse(b['battle_won'])
        with self.assertRaises(ValueError):_claim_victory(b)
        b['units']['player'].update(alive=False,extracted=True)
        _check_end(b);self.assertEqual(b['outcome'],'failure')

    def test_betrayal_creates_named_fight_with_real_mercenary_equipment(self):
        state=self.state();mid=state['mercenaries'][0]['id'];state['_mercenary_owner']='owner'
        prepare(state,SimpleNamespace(id='job',claimed_by_user_id='owner'),[mid],['player',mid],spend=True)
        b=betrayal_battle(state,['player',mid],[mid],'test')
        self.assertTrue(b['mercenary_interlude'])
        self.assertEqual(b['units'][mid]['team'],'enemy')
        self.assertEqual(b['units'][mid]['name'],state['mercenaries'][0]['character']['name'])


class EventAndStarterTests(unittest.TestCase):
    def test_natural_events_are_rare_and_never_consecutive(self):
        events=[pool_event('balance-fixture',i*POOL_SECONDS)['id'] for i in range(1,10001)]
        rate=sum(e!='general' for e in events)/len(events)
        self.assertTrue(.09<rate<.12,rate)
        self.assertFalse(any(a!='general' and b!='general' for a,b in zip(events,events[1:])))

    def test_starter_equipment_matches_perk_without_upgrading_existing_saves(self):
        from backend.combat import _player_unit
        kits={'guard':('chipped_sword',1),'scout':('frayed_bow',4),'fire_magic':('cracked_wand',3),'medic':('knotted_staff',1),'engineer':('worn_mallet',1)}
        for perk,(weapon,reach) in kits.items():
            s=new_game({'traits':[perk]});c=s['characters'][0]
            iid=c['equipment']['weapon'];self.assertEqual(next(i['item_id'] for i in s['inventory'] if i['instance_id']==iid),weapon)
            self.assertEqual(_player_unit(s,c,0,0)['attack_range'],reach)
            if perk=='guard':self.assertIsNotNone(c['equipment']['offhand'])
        old=new_game({});before=deepcopy(old['inventory']);normalize_state(old)
        self.assertEqual(old['inventory'],before)


class MercenaryContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_betrayal_preserves_dialogue_and_original_combat(self):
        from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
        from backend.db import Base
        from backend.models import PlayerState,MissionInstance
        from backend.content import MISSION_TEMPLATES
        from backend.services import claim_instance,_finish_battle
        for form in ('decision','battle'):
            engine=create_async_engine('sqlite+aiosqlite:///:memory:')
            definition={'name':'Continuation fixture','rank':'D','stat':'combat','difficulty':12,'party_size':2,'rewards':{}}
            if form=='decision':definition['decision_scene']={'start':'opening','nodes':{'opening':{'title':'The original job','text':'The wagon is ready.','choices':{}}}}
            else:definition['combat_encounter']={'id':'contract:highway_ambush'}
            try:
                async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
                factory=async_sessionmaker(engine,expire_on_commit=False)
                s=normalize_state(new_game({'name':'Owner'}));s['mission_rank']='D';s['resources']['gold']=100;market(s,'owner')
                mid=s['mercenaries'][0]['id'];now=int(time.time())
                with patch.dict(MISSION_TEMPLATES,{'continuation-fixture':definition}):
                    async with factory() as session:
                        row=PlayerState(guild_id='continuation',user_id='owner',display_name='Owner',state=s,updated_at=now)
                        mission=MissionInstance(id='continuation-job',guild_id='continuation',template_id='continuation-fixture',pool_slot=0,position=0,spawned_at=now,expires_at=now+3600,duration_seconds=1,status='reserved',claimed_by_user_id='owner',analysis={})
                        session.add_all([row,mission]);await session.flush()
                        with patch('backend.mercenaries.betrayal',return_value=[mid]):
                            started=await claim_instance(session,'continuation','owner','Owner',mission.id,['player',mid],mercenary_ids=[mid])
                        interlude=started.analysis['battle'];interlude.update(status='complete',outcome='success')
                        interlude['units'][mid].update(condition='unconscious',conscious=False)
                        resumed=await _finish_battle(session,started,row,interlude)
                        self.assertEqual(resumed['resume_status'],form)
                        self.assertEqual(started.status,form)
                        self.assertIsNone(started.result)
                        self.assertEqual(row.state['resources']['gold'],85)
                        if form=='battle':
                            self.assertEqual(started.analysis['battle']['encounter_id'],'contract:highway_ambush')
                            self.assertNotIn(mid,started.analysis['battle']['units'])
                            self.assertNotIn(mid,started.analysis['battle']['turn_order'])
                        else:self.assertEqual(started.analysis['scene']['revision'],0)
            finally:await engine.dispose()

    async def test_hire_preview_accept_finish_and_betrayal_resume(self):
        from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
        from backend.db import Base
        from backend.models import PlayerState,MissionInstance
        from backend.content import MISSION_TEMPLATES
        from backend.services import analyze_instance,claim_instance,resolve_due,_finish_battle
        template={'name':'Hiring fixture','rank':'D','stat':'combat','difficulty':12,'party_size':2,'rewards':{},'critical_rewards':{},'duration':1}
        with patch.dict(MISSION_TEMPLATES,{'hiring-fixture':template}):
            for turncoat in (False,True):
                engine=create_async_engine('sqlite+aiosqlite:///:memory:')
                try:
                    async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
                    factory=async_sessionmaker(engine,expire_on_commit=False)
                    s=normalize_state(new_game({'name':'Owner'}));s['mission_rank']='D';s['resources']['gold']=100;market(s,'owner')
                    mid=s['mercenaries'][0]['id'];now=int(time.time())
                    async with factory() as session:
                        row=PlayerState(guild_id='hiring',user_id='owner',display_name='Owner',state=s,updated_at=now)
                        mission=MissionInstance(id='hiring-test',guild_id='hiring',template_id='hiring-fixture',pool_slot=0,position=0,spawned_at=now,expires_at=now+3600,duration_seconds=1,status='reserved',claimed_by_user_id='owner',analysis={})
                        session.add_all([row,mission]);await session.flush()
                        preview=await analyze_instance(session,'hiring','owner',mission.id,['player',mid],mercenary_ids=[mid])
                        self.assertTrue(preview['claimable']);self.assertEqual(preview['mercenary_fee'],15)
                        self.assertEqual(len(row.state['characters']),1)
                        with patch('backend.mercenaries.betrayal',return_value=[mid] if turncoat else []):
                            started=await claim_instance(session,'hiring','owner','Owner',mission.id,['player',mid],mercenary_ids=[mid])
                        self.assertEqual(row.state['resources']['gold'],85)
                        if turncoat:
                            b=started.analysis['battle'];b['status']='complete';b['outcome']='failure';b['units']['player'].update(extracted=True,alive=False)
                            resumed=await _finish_battle(session,started,row,b)
                            self.assertTrue(resumed['mercenary_interlude']);self.assertEqual(started.status,'claimed')
                            self.assertIsNone(started.result)
                            self.assertNotIn(mid,started.party_ids)
                        await resolve_due(session,'hiring','owner')
                        self.assertEqual(started.status,'completed',started.error_text)
                        self.assertEqual(len(row.state['characters']),1)
                        self.assertFalse(any(i.get('mercenary_gear') for i in row.state['inventory']))
                        self.assertIsNone(row.state['mercenaries'][0]['busy_mission_id'])
                finally:await engine.dispose()
