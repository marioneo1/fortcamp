import unittest
from copy import deepcopy
from unittest.mock import patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from fastapi import HTTPException
from backend.auth import Identity
from backend.db import Base
from backend.models import PlayerState
from backend.construction import empty_plan, validate_plan, wall_segments, blocked_prop_overlap
from backend import construction_api

CAT={'ground':{'grass':{'file':'grass.png'}},'props':{'crate':{'file':'crate.png'}}}


class ConstructionRulesTests(unittest.TestCase):
    def setUp(self):
        self.catalogue=patch('backend.construction.catalogue',return_value=CAT);self.catalogue.start();self.addCleanup(self.catalogue.stop)
        self.size={'w':8,'h':6}

    def prop(self,**kwargs):
        return dict(id='crate_1',asset='crate',x=2,y=2,w=2,h=1,rotation=0,offset_x=.25,offset_y=-.3,blocking=False,**kwargs)

    def wall(self,**kwargs):
        result=dict(id='wall_1',x=2,y=2,shape='tee',anchor='north',material='timber',rotation=0,posts='auto')
        result.update(kwargs);return result

    def test_native_pieces_have_full_corners_and_explicit_post_variants(self):
        plan=empty_plan();plan['walls']=[self.wall(piece='corner_north_west',anchor='center',shape='corner',posts='none')]
        saved=validate_plan(plan,self.size)['walls'][0]
        self.assertEqual(saved['piece'],'corner_north_west')
        for a,b in wall_segments(saved):
            self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]),1)
        for bad in [{'piece':'invented_asset'},{'rotation':90},{'x':0,'anchor':'west'}]:
            with self.subTest(bad=bad):
                item=deepcopy(plan['walls'][0]);item.update(bad)
                with self.assertRaises(ValueError):validate_plan({**plan,'walls':[item]},self.size)

    def test_layers_keep_offsets_footprints_rotation_and_gate_state(self):
        plan=empty_plan();plan['ground']['1,1']={'asset':'grass','rotation':90}
        plan['props']=[self.prop()];plan['walls']=[self.wall(shape='gate',open=True)]
        checked=validate_plan(plan,self.size)
        self.assertEqual(checked['props'][0]['offset_y'],-.3)
        self.assertEqual(checked['props'][0]['w'],2)
        self.assertTrue(checked['walls'][0]['open'])
        self.assertEqual(checked['ground']['1,1']['rotation'],90)

    def test_shared_edge_coordinates_and_rotated_junctions(self):
        north=wall_segments(self.wall(shape='straight'))
        south=wall_segments(self.wall(shape='straight',y=1,anchor='south'))
        self.assertEqual(north,south)
        self.assertEqual(len(wall_segments(self.wall(shape='cross',rotation=90))),4)
        self.assertEqual(wall_segments(self.wall(shape='half',rotation=90))[0][1],(2.5,2.5))

    def test_no_client_paths_unknown_shapes_or_injected_identifiers(self):
        for bad in [{'asset':'../../secret'},{'id':'x" onload="alert(1)'},{'offset_x':float('nan')},{'rotation':45}]:
            plan=empty_plan();prop=self.prop();prop.update(bad);plan['props']=[prop]
            with self.subTest(bad=bad),self.assertRaises(ValueError):validate_plan(plan,self.size)
        plan=empty_plan();plan['walls']=[self.wall(shape='unknown')]
        with self.assertRaises(ValueError):validate_plan(plan,self.size)

    def test_bounds_and_unique_ids_are_validated(self):
        plan=empty_plan();p=self.prop();p['x']=7;plan['props']=[p]
        with self.assertRaises(ValueError):validate_plan(plan,self.size)
        plan['props']=[self.prop(),self.prop()]
        with self.assertRaises(ValueError):validate_plan(plan,self.size)
        plan=empty_plan();plan['walls']=[self.wall(x=0,anchor='west')]
        with self.assertRaises(ValueError):validate_plan(plan,self.size)

    def test_reserved_props_obstruct_facilities_but_decorations_do_not(self):
        p=self.prop();state={'construction':{'props':[p]}}
        self.assertFalse(blocked_prop_overlap(state,2,2,2,2))
        p['blocking']=True
        self.assertTrue(blocked_prop_overlap(state,2,2,2,2))
        self.assertFalse(blocked_prop_overlap(state,4,2,2,2))
        plan=empty_plan();plan['props']=[p]
        with self.assertRaisesRegex(ValueError,'facility'):
            validate_plan(plan,self.size,[{'type':'tent','x':2,'y':2}])


class ConstructionPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with self.engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
        self.sessions=async_sessionmaker(self.engine,expire_on_commit=False)
        self.session_patch=patch.object(construction_api,'SessionLocal',self.sessions);self.session_patch.start()
        self.identity=Identity(guild_id='camp',user_id='owner',display_name='Owner',guild_admin=False)
        async with self.sessions.begin() as session:
            for user in ['owner','friend']:
                session.add(PlayerState(guild_id='camp',user_id=user,display_name=user,state={'resources':{'gold':42},'characters':[{'id':'player'}],'base_size':{'w':8,'h':6},'buildings':[]},updated_at=1))

    async def asyncTearDown(self):
        self.session_patch.stop();await self.engine.dispose()

    async def test_owner_save_survives_reload_without_changing_other_data(self):
        plan=empty_plan()
        plan['walls']=[dict(id='native',piece='horizontal_right_post_south',x=2,y=2,shape='straight',anchor='north',material='iron',rotation=0,posts='none'),
                       dict(id='legacy',x=4,y=2,shape='tee',anchor='center',material='timber',rotation=0,posts='auto'),
                       dict(id='retired_native',piece='cross_north',x=5,y=3,shape='cross',anchor='center',material='timber',rotation=0,posts='none')]
        saved=await construction_api.save_construction(construction_api.SaveConstruction(revision=0,plan=plan),self.identity)
        self.assertEqual(saved['plan']['revision'],1)
        read=await construction_api.get_construction(self.identity)
        self.assertEqual(read['plan'],saved['plan'])
        self.assertTrue(all(p['shape'] not in ('tee','cross','half') for p in read['catalogue']['wall_pieces'].values()))
        self.assertEqual(saved['state']['resources']['gold'],42)
        self.assertEqual(saved['state']['characters'],[{'id':'player'}])
        async with self.sessions() as session:
            friend=(await session.execute(select(PlayerState).where(PlayerState.user_id=='friend'))).scalar_one()
            self.assertNotIn('construction',friend.state)

    async def test_stale_saves_rejected_and_invalid_plan_not_persisted(self):
        req=construction_api.SaveConstruction(revision=0,plan=empty_plan())
        await construction_api.save_construction(req,self.identity)
        with self.assertRaises(HTTPException) as caught:await construction_api.save_construction(req,self.identity)
        self.assertEqual(caught.exception.status_code,409)
        bad=empty_plan();bad['walls']=[{'id':'x'}]
        with self.assertRaises(HTTPException) as caught:
            await construction_api.save_construction(construction_api.SaveConstruction(revision=1,plan=bad),self.identity)
        self.assertEqual(caught.exception.status_code,422)
        self.assertEqual((await construction_api.get_construction(self.identity))['plan']['revision'],1)

    async def test_cross_server_cannot_access_saved_camp(self):
        foreign=Identity(guild_id='other',user_id='owner',display_name='Owner',guild_admin=False)
        with self.assertRaises(HTTPException):await construction_api.get_construction(foreign)
        with self.assertRaises(HTTPException):await construction_api.save_construction(construction_api.SaveConstruction(revision=0,plan=empty_plan()),foreign)
