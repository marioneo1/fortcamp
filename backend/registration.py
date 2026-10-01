import time
from sqlalchemy import select,func
from .models import PlayerRegistration

async def set_registration(session,guild_id,user_id,name,active=True):
    row=await session.get(PlayerRegistration,(guild_id,user_id))
    if row is None:
        row=PlayerRegistration(guild_id=guild_id,user_id=user_id,display_name=name[:100],active=active,updated_at=int(time.time()))
        session.add(row)
    else:
        row.active=active;row.display_name=name[:100];row.updated_at=int(time.time())
    await session.flush()
    return row

async def registered_count(session,guild_id):
    return int((await session.execute(select(func.count()).select_from(PlayerRegistration).where(PlayerRegistration.guild_id==guild_id,PlayerRegistration.active.is_(True)))).scalar_one())

async def require_registration(session,guild_id,user_id):
    row=await session.get(PlayerRegistration,(guild_id,user_id))
    if row is None or not row.active:
        from fastapi import HTTPException
        raise HTTPException(403,'Run /register with the Fortcamp bot in this server, then retry here. Unregistering preserves your save.')
