"""Development art browser. Edits framing defaults, never portrait identities."""
from urllib.parse import quote
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .auth import IdentityDep
from .battle_lab import authorize
from .portraits import PORTRAIT_POOL_ROOT, CHAMPION_PORTRAIT_ROOT, SUPPORTED_EXTENSIONS
from .portrait_framing import defaults, clean_frame, save_default

router = APIRouter(prefix='/api/debug/portrait-lab')


def catalogue():
    rows = []
    for path in sorted(PORTRAIT_POOL_ROOT.glob('*/full/*')):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:continue
        pool = path.parent.parent.name
        key = '/api/portrait-pools/'+quote(pool)+'/full/'+quote(path.name)
        thumb = path.parent.parent/'thumb'/path.name
        rows.append({'key':key,'name':path.stem,'group':pool,'kind':'Generic',
                     'thumbnail':key.replace('/full/','/thumb/') if thumb.is_file() else key})
    for path in sorted(CHAMPION_PORTRAIT_ROOT.glob('**/full.webp')):
        relative = path.relative_to(CHAMPION_PORTRAIT_ROOT)
        key = '/api/champion-portraits/'+quote(relative.as_posix(),safe='/')
        rows.append({'key':key,'name':relative.parts[0].replace('_',' ').title(),
                     'group':relative.parts[0],'kind':'Champion',
                     'variant':'/'.join(relative.parts[1:-1]),
                     'thumbnail':key.replace('/full.webp','/thumb.webp') if path.with_name('thumb.webp').is_file() else key})
    frames = defaults()
    for row in rows:row['portrait_frame'] = clean_frame(frames.get(row['key']))
    return rows


class DefaultFrameRequest(BaseModel):
    key: str = Field(max_length=600)
    x: float = Field(default=.5,ge=0,le=1,allow_inf_nan=False)
    y: float = Field(default=.5,ge=0,le=1,allow_inf_nan=False)
    size: float = Field(default=1,ge=.25,le=2.5,allow_inf_nan=False)
    reset: bool = False
    image: Literal['square','original'] = 'square'


@router.get('')
async def list_portraits(identity: IdentityDep):
    authorize(identity)
    return {'portraits':catalogue()}


@router.post('/frame')
async def update_default(req: DefaultFrameRequest, identity: IdentityDep):
    authorize(identity)
    if req.key not in {row['key'] for row in catalogue()}:
        raise HTTPException(404,'Portrait not found in the art library')
    frame = save_default(req.key,None if req.reset else req.model_dump(include={'x','y','size','image'}))
    return {'portrait_frame':frame}
