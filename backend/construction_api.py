from copy import deepcopy
import asyncio
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from .auth import IdentityDep
from .db import SessionLocal
from .models import PlayerState
from .construction import catalogue, empty_plan, validate_plan, ROOT, AVAILABLE_WALL_PIECES

from .settings import settings

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


wall_lab_router=APIRouter(prefix='/api/debug/construction')


def authorize_wall_lab(identity):
    if not settings.game_debug_mode or settings.environment.lower() in {'prod','production','release','stable'}:
        raise HTTPException(404,'Wall Kit Lab is only available in development debug mode')
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403,'Wall Kit Lab is limited to server admins')


def wall_test_plan():
    """All active variants plus a connected room, detached from player saves."""
    plan=empty_plan()
    for index,(piece,definition) in enumerate(AVAILABLE_WALL_PIECES.items()):
        plan['walls'].append({'id':f'sample_{index}','piece':piece,'shape':definition['shape'],'rotation':0,
                             'x':index%8*2+1,'y':index//8*2+1,'anchor':'center','material':'timber','posts':'none'})
    def add(piece,x,y,anchor='center'):
        plan['walls'].append({'id':f'room_{len(plan["walls"])}','piece':piece,'shape':AVAILABLE_WALL_PIECES[piece]['shape'],
                             'rotation':0,'x':x,'y':y,'anchor':anchor,'material':'timber','posts':'none'})
    add('corner_north_west',2,8);add('corner_north_east',8,8)
    add('corner_south_west',2,12);add('corner_south_east',8,12)
    for x in range(3,8):
        add('gate_horizontal' if x==5 else 'horizontal_plain',x,8,'north')
        add('horizontal_plain_south',x,12,'south')
    for y in range(9,12):
        add('vertical_plain_west',2,y,'west');add('vertical_plain',8,y,'east')
    return plan


@wall_lab_router.get('/wall-kits')
async def get_wall_kits(identity:IdentityDep):
    authorize_wall_lab(identity)
    manifest=json.loads((ROOT/'frontend/src/construction-wall-art.json').read_text())
    kits={'placeholder':{'name':'Geometry placeholders'}}
    asset_root=ROOT/'frontend/public/assets/combat-terrain'
    for ident,kit in manifest.items():
        if all((asset_root/source['file']).is_file() for source in kit['sources'].values()):kits[ident]={'name':kit['name']}
    return {'kits':kits,'catalogue':catalogue(),'plan':wall_test_plan(),'size':{'w':18,'h':15},'buildings':[]}
