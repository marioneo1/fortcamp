from copy import deepcopy
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from .auth import IdentityDep
from .db import SessionLocal
from .models import PlayerState
from .construction import catalogue, empty_plan, validate_plan

router=APIRouter(prefix='/api/construction')


class SaveConstruction(BaseModel):
    revision:int=Field(ge=0)
    plan:dict


@router.get('')
async def get_construction(identity:IdentityDep):
    async with SessionLocal() as session:
        row=(await session.execute(select(PlayerState).where(PlayerState.guild_id==identity.guild_id,PlayerState.user_id==identity.user_id))).scalar_one_or_none()
        if not row:raise HTTPException(404,'Create your character first')
        return {'catalogue':catalogue(),'plan':row.state.get('construction',empty_plan()),
                'size':row.state.get('base_size',{'w':12,'h':8}),'buildings':row.state.get('buildings',[])}


@router.put('')
async def save_construction(req:SaveConstruction,identity:IdentityDep):
    from .services import _player_locks, now_ts
    async with _player_locks.setdefault((identity.guild_id,identity.user_id),asyncio.Lock()):
        async with SessionLocal() as session:
            async with session.begin():
                row=(await session.execute(select(PlayerState).where(PlayerState.guild_id==identity.guild_id,PlayerState.user_id==identity.user_id).with_for_update())).scalar_one_or_none()
                if not row:raise HTTPException(404,'Create your character first')
                state=deepcopy(row.state)
                old=state.get('construction',empty_plan())
                if old['revision']!=req.revision:raise HTTPException(409,'Your camp changed in another window. Reopen construction before saving.')
                try:plan=validate_plan(req.plan,state.get('base_size',{'w':12,'h':8}),state.get('buildings',[]))
                except (ValueError,TypeError,AttributeError) as exc:raise HTTPException(422,str(exc))
                plan['revision']=req.revision+1
                state['construction']=plan
                changed=await session.execute(update(PlayerState).where(
                    PlayerState.guild_id==identity.guild_id,PlayerState.user_id==identity.user_id,
                    PlayerState.state==row.state).values(state=state,updated_at=now_ts()).execution_options(synchronize_session=False))
                if changed.rowcount!=1:raise HTTPException(409,'Your camp changed during this save. Reopen construction before saving.')
            return {'state':state,'plan':plan}
