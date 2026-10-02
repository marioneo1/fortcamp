import asyncio
import unittest
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from backend.db import Base
from backend.models import MissionInstance,MissionResultNotice
from backend.notifications import queue_result_notice,dispatch_results

class NoticesTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with self.engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
        self.sessions=async_sessionmaker(self.engine,expire_on_commit=False)
        self.patch=patch('backend.notifications.SessionLocal',self.sessions);self.patch.start()
        async with self.sessions() as session:
            row=MissionInstance(id='notice',guild_id='guild',template_id='wolves_fence',pool_slot=0,position=0,spawned_at=0,expires_at=1,duration_seconds=0,status='completed',claimed_by_user_id='user',result={'outcome':'success'})
            session.add(row);await queue_result_notice(session,row);await queue_result_notice(session,row);await session.commit()
    async def asyncTearDown(self):
        self.patch.stop();await self.engine.dispose()

    async def test_unready_bot_keeps_notice_and_success_is_not_repeated(self):
        class Bot:
            ready=False;calls=0
            def is_ready(self):return self.ready
            async def announce_result(self,row):self.calls+=1;return True
        bot=Bot();self.assertEqual(await dispatch_results(bot),0)
        bot.ready=True;self.assertEqual(await dispatch_results(bot),1)
        self.assertEqual(await dispatch_results(bot),0);self.assertEqual(bot.calls,1)
        async with self.sessions() as session:self.assertEqual((await session.get(MissionResultNotice,'notice')).status,'sent')

    async def test_missing_channel_or_failed_send_retries_without_losing_result(self):
        class Bot:
            def is_ready(self):return True
            async def announce_result(self,row):return False
        self.assertEqual(await dispatch_results(Bot()),0)
        async with self.sessions() as session:
            row=await session.get(MissionResultNotice,'notice')
            self.assertEqual(row.status,'pending');self.assertEqual(row.attempts,1);self.assertGreater(row.lease_until,0)
            mission=await session.get(MissionInstance,'notice');self.assertEqual(mission.result['outcome'],'success')

    async def test_http_completion_schedules_delivery_without_waiting_for_discord(self):
        import backend.main as main
        started=asyncio.Event();release=asyncio.Event()
        async def slow_send(bot,ids):started.set();await release.wait()
        class Bot:
            def is_ready(self):return True
        with patch.object(main,'_bot',Bot()),patch.object(main,'dispatch_results',slow_send):
            self.assertIsNone(main.request_notice_delivery(['notice']))
            await started.wait()
            tasks=list(main._notice_tasks)
            self.assertTrue(tasks);self.assertTrue(all(not task.done() for task in tasks))
            release.set();await asyncio.gather(*tasks)
