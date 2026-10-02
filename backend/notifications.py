"""Durable result notices, independent of browser/Activity and reconnect timing."""
import time
from sqlalchemy import select, update, or_
from .db import SessionLocal
from .models import MissionInstance, MissionResultNotice

async def queue_result_notice(session, mission):
    if not await session.get(MissionResultNotice,mission.id):
        session.add(MissionResultNotice(mission_id=mission.id,status="pending",lease_until=0,attempts=0))

async def dispatch_results(bot, mission_ids=None):
    if not bot or not bot.is_ready():return 0
    now=int(time.time());sent=0
    eligible=or_(MissionResultNotice.status=="pending",(MissionResultNotice.status=="sending") & (MissionResultNotice.lease_until<=now))
    async with SessionLocal() as session:
        query=select(MissionResultNotice.mission_id).where(eligible,MissionResultNotice.lease_until<=now)
        if mission_ids is not None:query=query.where(MissionResultNotice.mission_id.in_(mission_ids))
        ids=list((await session.execute(query.limit(20))).scalars())
    for mission_id in ids:
        async with SessionLocal() as session:
            changed=await session.execute(update(MissionResultNotice).where(MissionResultNotice.mission_id==mission_id,eligible,MissionResultNotice.lease_until<=now).values(status="sending",lease_until=now+120,attempts=MissionResultNotice.attempts+1))
            await session.commit()
            if changed.rowcount!=1:continue
            mission=await session.get(MissionInstance,mission_id)
        success=False
        try:success=bool(mission and mission.status=="completed" and await bot.announce_result(mission))
        except Exception as exc:print(f"mission notice retry: {type(exc).__name__}")
        async with SessionLocal() as session:
            await session.execute(update(MissionResultNotice).where(MissionResultNotice.mission_id==mission_id).values(status="sent" if success else "pending",lease_until=0 if success else now+30))
            await session.commit()
        sent+=int(success)
    return sent
