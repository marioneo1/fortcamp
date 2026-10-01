import unittest
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from fastapi import HTTPException
from backend.db import Base,init_db
from backend.models import PlayerState
from backend.registration import set_registration,registered_count,require_registration
from backend.game import new_game

class RegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with self.engine.begin() as c:await c.run_sync(Base.metadata.create_all)
        self.sessions=async_sessionmaker(self.engine,expire_on_commit=False)
    async def asyncTearDown(self):await self.engine.dispose()
    async def test_registration_counts_opt_in_players_without_requiring_a_save(self):
        async with self.sessions() as s,s.begin():
            await set_registration(s,'friends','one','One');await set_registration(s,'friends','two','Two')
            await set_registration(s,'other','three','Three');await set_registration(s,'friends','one','One')
            self.assertEqual(await registered_count(s,'friends'),2)
            await require_registration(s,'friends','one')
            with self.assertRaises(HTTPException):await require_registration(s,'friends','nonplayer')
    async def test_unregister_preserves_progress_and_reregister_restores_participation(self):
        async with self.sessions() as s,s.begin():
            save=PlayerState(guild_id='friends',user_id='one',display_name='One',state=new_game({'name':'One'}),updated_at=1);s.add(save)
            await set_registration(s,'friends','one','One',False)
            self.assertEqual(await registered_count(s,'friends'),0)
            with self.assertRaises(HTTPException):await require_registration(s,'friends','one')
            self.assertIsNotNone(await s.get(PlayerState,('friends','one')))
            await set_registration(s,'friends','one','One');await require_registration(s,'friends','one')
            self.assertEqual(await registered_count(s,'friends'),1)
    async def test_legacy_backfill_does_not_reactivate_unregistered_players(self):
        async with self.sessions() as s,s.begin():
            for user in ['legacy','paused']:s.add(PlayerState(guild_id='friends',user_id=user,display_name=user,state=new_game({'name':user}),updated_at=1))
            await set_registration(s,'friends','paused','Paused',False)
        with patch('backend.db.engine',self.engine):await init_db();await init_db()
        async with self.sessions() as s:
            self.assertEqual(await registered_count(s,'friends'),1)
            with self.assertRaises(HTTPException):await require_registration(s,'friends','paused')
