from __future__ import annotations
import asyncio
import base64
import binascii
import io
import os
import re
import time
import uuid
from contextlib import asynccontextmanager
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select

from .auth import IdentityDep, create_session_token, exchange_discord_code, verify_discord_identity, session_namespace
from .web_auth import browser_router
from .content import MISSION_TEMPLATES
from .db import SessionLocal, init_db
from .game import (
    assign_character, equip_item, manage_prisoner, mission_rank, move_building, normalize_state,
    place_building, public_content, train_perk, upgrade_guild_hall,
)
from .portraits import CHAMPION_PORTRAIT_ROOT, PORTRAIT_POOL_ROOT
from .appearance import has_appearance, sanitize_appearance, tagged_appearance
from .models import GuildConfig, MissionInstance, PlayerState
from .services import (
    active_pool_slot, analyze_instance, available_chain_missions, claim_instance, create_player, debug_complete_instance,
    debug_resolve_now_instance,
    debug_start_battle, debug_start_goblin_battle, ensure_pool,
    force_pool_refresh, get_battle_instance, get_player, mission_summary, pool_event, pool_slot, resolve_due,
    spawn_private_contract, update_battle_instance,
)
from .notifications import dispatch_results
from .settings import settings
from .economy import camp_action, trade_view, purchase
from .services import reserve_instance, abandon_reservation, claim_budget
from .registration import require_registration, registered_count

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIST = ROOT / "frontend" / "dist"
PORTRAIT_ROOT = Path(os.getenv('FORTCAMP_UPLOAD_ROOT') or ROOT / "data" / "portraits")
PORTRAIT_POOL_ROOT.mkdir(parents=True, exist_ok=True)
CHAMPION_PORTRAIT_ROOT.mkdir(parents=True, exist_ok=True)
Image.MAX_IMAGE_PIXELS = 25_000_000
_bot_task: asyncio.Task | None = None
_scheduler_task: asyncio.Task | None = None
_bot = None
_notice_tasks: set[asyncio.Task] = set()


def request_notice_delivery(mission_ids):
    if not _bot or not _bot.is_ready():return
    async def send():
        try:await dispatch_results(_bot,mission_ids)
        except Exception as exc:print(f"notice delivery deferred: {type(exc).__name__}")
    task=asyncio.create_task(send());_notice_tasks.add(task)
    task.add_done_callback(_notice_tasks.discard)


async def scheduler_loop() -> None:
    while True:
        created_batches: list[tuple[str, list[MissionInstance]]] = []
        resolved_rows: list[MissionInstance] = []
        try:
            async with SessionLocal() as session:
                async with session.begin():
                    guild_ids = (await session.execute(select(GuildConfig.guild_id))).scalars().all()
                    for guild_id in guild_ids:
                        missions, created = await ensure_pool(session, guild_id)
                        if created:
                            created_batches.append((guild_id, list(missions)))
                    resolved_rows = await resolve_due(session)
            if _bot and _bot.is_ready():
                for guild_id, missions in created_batches:
                    await _bot.announce_pool(guild_id, missions)
                await dispatch_results(_bot)
        except Exception as exc:
            print(f"scheduler error: {exc}")
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bot_task, _scheduler_task, _bot
    await init_db()
    _scheduler_task = asyncio.create_task(scheduler_loop())
    if settings.bot_enabled and settings.discord_bot_token:
        from .bot import bot
        _bot = bot
        _bot_task = asyncio.create_task(bot.start(settings.discord_bot_token))

        def _report_bot_exit(task: asyncio.Task) -> None:
            if task.cancelled():
                return
            try:
                exc = task.exception()
            except asyncio.CancelledError:
                return
            if exc:
                print(f"Discord bot task stopped with error: {exc!r}")

        _bot_task.add_done_callback(_report_bot_exit)
    yield
    for task in list(_notice_tasks):task.cancel()
    if _scheduler_task:
        _scheduler_task.cancel()
    if _bot:
        await _bot.close()
    if _bot_task:
        _bot_task.cancel()


app = FastAPI(title="Fortcamp Alpha API", version="0.3.1", lifespan=lifespan)

def installed_web_guilds():
    if not _bot or not _bot.is_ready():
        raise HTTPException(503,'Fortcamp’s bot is connecting. Try again shortly.')
    return {str(g.id):{'name':g.name,'icon':str(g.icon.url) if g.icon else None} for g in _bot.guilds}

app.include_router(browser_router(installed_web_guilds))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"],
)
app.mount("/api/portrait-pools", StaticFiles(directory=PORTRAIT_POOL_ROOT), name="portrait-pools")
app.mount("/api/champion-portraits", StaticFiles(directory=CHAMPION_PORTRAIT_ROOT), name="champion-portraits")


class CharacterCreate(BaseModel):
    name: str = "Wanderer"
    race: str = "Human"
    series: str = "Player"
    specialty: str = "Survivor"
    traits: list[str] = []
    portrait: str = ""
    stats: dict[str, int] = {}
    attributes: dict[str, int] = {}
    perks: dict[str, str] = {}

    @field_validator('race')
    @classmethod
    def known_starting_race(cls, value):
        from .races import RACE_CATALOG
        if value not in RACE_CATALOG or RACE_CATALOG[value][0]=='Limited':
            raise ValueError('Choose a starting race from the race dropdown')
        return value


class NewGameRequest(BaseModel):
    character: CharacterCreate


class BuildRequest(BaseModel):
    blueprint_id: str
    x: int
    y: int


class MoveBuildingRequest(BaseModel):
    building_id: str
    x: int
    y: int


class AssignRequest(BaseModel):
    character_id: str
    building_id: str | None = None


class EquipRequest(BaseModel):
    character_id: str
    slot: str
    instance_id: str | None = None


class PrisonerActionRequest(BaseModel):
    action: str
    swap_prisoner_id: str | None = None


class PartyRequest(BaseModel):
    party_ids: list[str] = Field(default_factory=list)
    role_assignments: dict[str, str] | None = None
    bodyguard_ids: list[str] = Field(default_factory=list)


class TokenRequest(BaseModel):
    code: str


class DiscordSessionRequest(BaseModel):
    access_token: str
    guild_id: str


class DebugCompleteRequest(BaseModel):
    outcome: str
    party_ids: list[str] | None = None
    role_assignments: dict[str, str] | None = None


class PortraitRequest(BaseModel):
    portrait: str = ""


class PortraitUploadRequest(BaseModel):
    data_url: str


class AppearanceRequest(BaseModel):
    hair_color: str = ""
    hair_length: str = ""
    eye_color: str = ""
    skin_tone: str = ""
    build: str = ""
    distinctive_features: str = ""
    summary: str = ""


class TrainPerkRequest(BaseModel):
    character_id: str
    track: str
    teacher_id: str | None = None


class CampActionRequest(BaseModel):
    action: str
    data: dict = Field(default_factory=dict)


class TradeRequest(BaseModel):
    offer_id: str


class DebugPoolRefreshRequest(BaseModel):
    event_id: str = "general"


class CombatApproachPosition(BaseModel):
    x: int
    y: int


class CombatCommandRequest(BaseModel):
    action: str
    x: int | None = None
    y: int | None = None
    target_id: str | None = None
    move_to: CombatApproachPosition | None = None
    placement_id: str | None = None


class CombatAutoRequest(BaseModel):
    tactic: str = "balanced"
    resolve_all: bool = False


class MissionChoiceRequest(BaseModel):
    node_id: str
    revision: int
    choice_id: str


@app.get("/api/health")
async def health():
    return {"ok": True, "version": "0.3.1", "database": settings.database_url.split(":", 1)[0]}


@app.get("/api/config")
async def config():
    return {
        "discord_client_id": settings.discord_client_id,
        "dev_bypass_auth": settings.dev_bypass_auth,
        "version": "0.3.1",
        "mission_time_scale": settings.mission_time_scale,
        "debug_mode": settings.game_debug_mode,
        "environment": settings.environment,
        "session_namespace": session_namespace(),
        "web_origin": settings.web_origin,
        "web_login_enabled": bool(settings.web_origin and settings.discord_client_id and settings.discord_client_secret and settings.discord_bot_token),
    }


@app.get("/api/portrait-proxy")
async def portrait_proxy(url: str):
    """Same-origin bridge for Google thumbnail URLs that can fail inside Activity frames."""
    if len(url) > 2000:
        raise HTTPException(400, "Portrait URL is too long")
    parsed = urlparse(url)
    allowed_host = bool(re.fullmatch(r"encrypted-tbn\d+\.gstatic\.com", (parsed.hostname or "").lower()))
    if parsed.scheme != "https" or not allowed_host:
        raise HTTPException(400, "Only encrypted Google thumbnail URLs use this proxy")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=12) as client:
            remote = await client.get(url, headers={"User-Agent": "Fortcamp/0.3.1", "Referer": "https://www.google.com/"})
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Portrait host could not be reached") from exc
    final_host = (urlparse(str(remote.url)).hostname or "").lower()
    content_type = remote.headers.get("content-type", "").split(";", 1)[0].lower()
    if remote.status_code >= 400 or not re.fullmatch(r"encrypted-tbn\d+\.gstatic\.com", final_host):
        raise HTTPException(502, "Portrait host rejected the image request")
    if not content_type.startswith("image/") or len(remote.content) > 5 * 1024 * 1024:
        raise HTTPException(400, "Portrait URL did not return a supported image")
    return Response(remote.content, media_type=content_type, headers={"Cache-Control": "public, max-age=86400"})


@app.post("/api/discord/token")
async def discord_token(req: TokenRequest):
    return {"access_token": await exchange_discord_code(req.code)}


@app.post("/api/discord/session")
async def discord_session(req: DiscordSessionRequest):
    identity = await verify_discord_identity(req.access_token, req.guild_id)
    return {"session_token": create_session_token(identity), "identity": identity.__dict__}


@app.get("/api/content")
async def content(identity: IdentityDep):
    return public_content()


@app.get("/api/state")
async def state(identity: IdentityDep):
    async with SessionLocal() as session:
        async with session.begin():
            if not settings.dev_bypass_auth:await require_registration(session,identity.guild_id,identity.user_id)
            row = await get_player(session, identity.guild_id, identity.user_id)
    return {"exists": row is not None, "state": row.state if row else None, "identity": identity.__dict__}


@app.post("/api/new-game")
async def new_game_endpoint(req: NewGameRequest, identity: IdentityDep):
    async with SessionLocal() as session:
        try:
            async with session.begin():
                if not settings.dev_bypass_auth:await require_registration(session,identity.guild_id,identity.user_id)
                row = await create_player(session, identity.guild_id, identity.user_id, identity.display_name, req.character.model_dump())
                await ensure_pool(session, identity.guild_id)
        except ValueError as exc:
            raise HTTPException(409, str(exc))
    return {"state": row.state}


async def locked_player(identity) -> tuple[Any, Any]:
    session = SessionLocal()
    await session.begin()
    row = (await session.execute(
        select(PlayerState).where(PlayerState.guild_id == identity.guild_id, PlayerState.user_id == identity.user_id).with_for_update()
    )).scalar_one_or_none()
    if not row:
        await session.rollback(); await session.close()
        raise HTTPException(404, "Create your character first")
    row.state = normalize_state(deepcopy(row.state))
    return session, row


@app.post("/api/camp")
async def camp_endpoint(req: CampActionRequest, identity: IdentityDep):
    session,row=await locked_player(identity)
    try:
        changed=deepcopy(row.state);camp_action(changed,req.action,**req.data)
        row.state=changed;row.updated_at=int(time.time());await session.commit()
        return {'state':changed}
    except ValueError as exc:
        await session.rollback();raise HTTPException(400,str(exc))
    finally:await session.close()


@app.get('/api/trade')
async def trade_endpoint(identity: IdentityDep):
    session,row=await locked_player(identity)
    try:
        changed=deepcopy(row.state);offers=trade_view(changed,f'{identity.guild_id}:{identity.user_id}')
        row.state=changed;await session.commit();return {'trade':offers,'state':changed}
    finally:await session.close()


@app.post('/api/trade')
async def buy_endpoint(req: TradeRequest,identity: IdentityDep):
    session,row=await locked_player(identity)
    try:
        changed=deepcopy(row.state);purchase(changed,f'{identity.guild_id}:{identity.user_id}',req.offer_id)
        row.state=changed;await session.commit();return {'state':changed}
    except ValueError as exc:
        await session.rollback();raise HTTPException(400,str(exc))
    finally:await session.close()


@app.post('/api/missions/{mission_id}/abandon')
async def abandon_endpoint(mission_id:str,identity:IdentityDep):
    async with SessionLocal() as session:
        try:
            async with session.begin():await abandon_reservation(session,identity.guild_id,identity.user_id,mission_id)
        except ValueError as exc:raise HTTPException(409,str(exc))
    return {'message':'Contract abandoned. Points are not refunded.'}


@app.post("/api/build")
async def build(req: BuildRequest, identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        building = place_building(state, req.blueprint_id, req.x, req.y)
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"building": building, "state": state}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(400, str(exc))
    finally:
        await session.close()


@app.post("/api/move-building")
async def move_building_endpoint(req: MoveBuildingRequest, identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        building = move_building(state, req.building_id, req.x, req.y)
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"building": building, "state": state}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(400, str(exc))
    finally:
        await session.close()


@app.post("/api/assign")
async def assign(req: AssignRequest, identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        assign_character(state, req.character_id, req.building_id)
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"state": state}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(400, str(exc))
    finally:
        await session.close()


@app.post("/api/equip")
async def equip(req: EquipRequest, identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        equip_item(state, req.character_id, req.instance_id, req.slot)
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"state": state}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(400, str(exc))
    finally:
        await session.close()


class RelationshipRequest(BaseModel):
    action: str = "talk"
    topic: str = "recent"
    meal: str | None = None


@app.post("/api/characters/{character_id}/conversation")
async def character_conversation(character_id: str,req: RelationshipRequest,identity: IdentityDep):
    from .relationships import conversation
    from .services import _player_locks
    lock=_player_locks.setdefault((identity.guild_id,identity.user_id),asyncio.Lock())
    async with lock:
        session,row=await locked_player(identity)
        try:
            state=normalize_state(deepcopy(row.state))
            reply=conversation(state,character_id,req.action,req.topic,req.meal)
            row.state=state;row.updated_at=int(time.time())
            await session.commit()
            return {"state":state,"reply":reply}
        except ValueError as exc:
            await session.rollback();raise HTTPException(400,str(exc))
        finally:await session.close()

@app.post("/api/prisoners/{prisoner_id}/action")
async def prisoner_action(prisoner_id: str, req: PrisonerActionRequest, identity: IdentityDep):
    from .services import _player_locks, spawn_prisoner_contract
    async with _player_locks.setdefault((identity.guild_id,identity.user_id),asyncio.Lock()):
        session, row = await locked_player(identity)
        try:
            state = normalize_state(deepcopy(row.state))
            if req.action == 'quest':
                prisoner=next((p for p in state.get('prisoners',[]) if p['id']==prisoner_id),None)
                if not prisoner:raise ValueError('Prisoner not found or no longer in custody')
                mission=await spawn_prisoner_contract(session,identity.guild_id,identity.user_id,prisoner)
                result={'text':'Allegiance contract added to Private Contracts.','mission_id':mission.id,'mission':mission_summary(mission)}
            else:
                result = manage_prisoner(state, prisoner_id, req.action, req.swap_prisoner_id)
            row.state = state; row.updated_at = int(time.time())
            await session.commit()
            return {"result": result, "state": state}
        except ValueError as exc:
            await session.rollback(); raise HTTPException(400, str(exc))
        finally:
            await session.close()


@app.post("/api/train-perk")
async def train_character_perk(req: TrainPerkRequest, identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        training = train_perk(state, req.character_id, req.track, req.teacher_id)
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"training": training, "state": state}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(400, str(exc))
    finally:
        await session.close()


@app.post("/api/player-character/portrait")
async def update_player_portrait(req: PortraitRequest, identity: IdentityDep):
    from .game import normalize_portrait_url
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        player = next((c for c in state.get("characters", []) if c.get("is_player")), None)
        if not player:
            raise ValueError("Player character not found")
        player["portrait"] = normalize_portrait_url(req.portrait)
        player["portrait_thumbnail"] = player["portrait"]
        player["portrait_source"] = "override" if player["portrait"] else "none"
        player["portrait_metadata_available"] = False
        if player.get("appearance_source") == "portrait":
            player["appearance"] = sanitize_appearance({})
            player["appearance_source"] = "none"
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"state": state}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(400, str(exc))
    finally:
        await session.close()


def _decode_portrait(data_url: str) -> tuple[bytes, str]:
    if len(data_url) > 6_000_000:
        raise ValueError("Portrait upload is too large")
    payload = data_url.split(",", 1)[1] if data_url.startswith("data:") and "," in data_url else data_url
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Portrait upload was not valid base64 data") from exc
    if not raw or len(raw) > 4 * 1024 * 1024:
        raise ValueError("Portrait uploads must be 4 MB or smaller")
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        extension = "png"
    elif raw.startswith(b"\xff\xd8\xff"):
        extension = "jpg"
    elif raw[:6] in {b"GIF87a", b"GIF89a"}:
        extension = "gif"
    elif len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        extension = "webp"
    else:
        raise ValueError("Upload a PNG, JPEG, GIF, or WebP image")
    return raw, extension


def _resize_portrait(raw: bytes) -> tuple[bytes, bytes]:
    try:
        with Image.open(io.BytesIO(raw)) as source:
            if source.width * source.height > 25_000_000:
                raise ValueError("Portrait dimensions are too large; use at most 25 megapixels")
            source.seek(0)
            image = ImageOps.exif_transpose(source).convert("RGBA" if source.mode in {"RGBA", "LA"} else "RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Portrait image could not be decoded safely") from exc
    full = image.copy()
    full.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
    thumb = ImageOps.fit(image, (192, 192), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    full_buffer, thumb_buffer = io.BytesIO(), io.BytesIO()
    full.save(full_buffer, format="WEBP", quality=90, method=6)
    thumb.save(thumb_buffer, format="WEBP", quality=84, method=6)
    return full_buffer.getvalue(), thumb_buffer.getvalue()


@app.get("/api/portraits/{asset_name}")
async def uploaded_portrait(asset_name: str):
    if not re.fullmatch(r"[0-9a-f]{32}(?:\.thumb)?\.(?:png|jpg|gif|webp)", asset_name):
        raise HTTPException(404, "Portrait not found")
    path = PORTRAIT_ROOT / asset_name
    if not path.is_file():
        raise HTTPException(404, "Portrait not found")
    return FileResponse(path, headers={"Cache-Control": "public, max-age=31536000, immutable"})


@app.post("/api/characters/{character_id}/portrait-upload")
async def upload_character_portrait(character_id: str, req: PortraitUploadRequest, identity: IdentityDep):
    try:
        raw, _ = _decode_portrait(req.data_url)
        full_bytes, thumb_bytes = _resize_portrait(raw)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    session, row = await locked_player(identity)
    PORTRAIT_ROOT.mkdir(parents=True, exist_ok=True)
    asset_id = uuid.uuid4().hex
    asset_name = f"{asset_id}.webp"
    thumb_name = f"{asset_id}.thumb.webp"
    path = PORTRAIT_ROOT / asset_name
    thumb_path = PORTRAIT_ROOT / thumb_name
    old_managed_paths: list[Path] = []
    try:
        path.write_bytes(full_bytes)
        thumb_path.write_bytes(thumb_bytes)
        state = deepcopy(row.state)
        character = next((char for char in state.get("characters", []) if char.get("id") == character_id), None)
        if not character:
            raise ValueError("Character not found")
        old_portrait = character.get("portrait", "")
        old_name = old_portrait.removeprefix("/api/portraits/") if old_portrait.startswith("/api/portraits/") else ""
        if re.fullmatch(r"[0-9a-f]{32}\.(?:png|jpg|gif|webp)", old_name):
            old_managed_paths.append(PORTRAIT_ROOT / old_name)
            old_managed_paths.append(PORTRAIT_ROOT / re.sub(r"\.[^.]+$", ".thumb.webp", old_name))
        character["portrait"] = f"/api/portraits/{asset_name}"
        character["portrait_thumbnail"] = f"/api/portraits/{thumb_name}"
        character["portrait_source"] = "override"
        character["portrait_locked"] = True
        character["portrait_metadata_available"] = False
        if character.get("appearance_source") == "portrait":
            character["appearance"] = sanitize_appearance({})
            character["appearance_source"] = "none"
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        for old_managed_path in old_managed_paths:
            if old_managed_path not in {path, thumb_path}:
                old_managed_path.unlink(missing_ok=True)
        return {"state": state, "portrait": character["portrait"], "portrait_thumbnail": character["portrait_thumbnail"]}
    except ValueError as exc:
        await session.rollback()
        path.unlink(missing_ok=True)
        thumb_path.unlink(missing_ok=True)
        raise HTTPException(404, str(exc))
    except Exception:
        await session.rollback()
        path.unlink(missing_ok=True)
        thumb_path.unlink(missing_ok=True)
        raise
    finally:
        await session.close()


@app.post("/api/characters/{character_id}/appearance")
async def update_character_appearance(character_id: str, req: AppearanceRequest, identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        character = next((char for char in state.get("characters", []) if char.get("id") == character_id), None)
        if not character:
            raise ValueError("Character not found")
        character["appearance"] = sanitize_appearance(req.model_dump())
        character["appearance_source"] = "manual" if has_appearance(character["appearance"]) else "none"
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"state": state, "appearance": character["appearance"]}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(404, str(exc))
    finally:
        await session.close()


@app.post("/api/characters/{character_id}/appearance-from-portrait")
async def fill_character_appearance_from_portrait(character_id: str, identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        character = next((char for char in state.get("characters", []) if char.get("id") == character_id), None)
        if not character:
            raise ValueError("Character not found")
        appearance = tagged_appearance(character)
        if not has_appearance(appearance):
            raise ValueError("This portrait does not have appearance tags yet")
        character["appearance"] = appearance
        character["appearance_source"] = "portrait"
        character["portrait_metadata_available"] = True
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"state": state, "appearance": appearance}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(404, str(exc))
    finally:
        await session.close()


@app.post("/api/guild-hall/upgrade")
async def upgrade_guild_hall_endpoint(identity: IdentityDep):
    session, row = await locked_player(identity)
    try:
        state = deepcopy(row.state)
        rank = upgrade_guild_hall(state)
        row.state = state; row.updated_at = int(time.time())
        await session.commit()
        return {"rank": rank, "state": state}
    except ValueError as exc:
        await session.rollback(); raise HTTPException(400, str(exc))
    finally:
        await session.close()


@app.get("/api/missions/pool")
async def mission_pool(identity: IdentityDep):
    async with SessionLocal() as session:
        async with session.begin():
            missions, _ = await ensure_pool(session, identity.guild_id)
            player = await get_player(session, identity.guild_id, identity.user_id)
            viewer_rank = mission_rank(player.state) if player else "E"
            registered_players = await registered_count(session,identity.guild_id)
            active_players=registered_players
    current_slot = active_pool_slot(identity.guild_id)
    return {
        "pool_slot": current_slot, "next_refresh": missions[0].spawned_at+1800 if missions else pool_slot()+1800,
        "rank": viewer_rank, "registered_players": registered_players,
        "active_players":active_players,
        "budget":claim_budget(player.state if player else {},current_slot,missions[0].spawned_at if missions else pool_slot()),
        "event": pool_event(identity.guild_id, current_slot),
        "missions": [mission_summary(x, viewer_rank=viewer_rank) for x in missions if (x.analysis or {}).get('public_wave',1)==1 or int(time.time())>=x.spawned_at+60],
    }


@app.get("/api/private-contracts")
async def private_contracts(identity: IdentityDep):
    async with SessionLocal() as session:
        async with session.begin():
            missions = await available_chain_missions(session, identity.guild_id, identity.user_id)
            player = await get_player(session, identity.guild_id, identity.user_id)
            viewer_rank = mission_rank(player.state) if player else "E"
    return {"missions": [mission_summary(row, viewer_rank=viewer_rank) for row in missions]}


@app.post("/api/debug/missions/refresh")
async def debug_refresh_missions(req: DebugPoolRefreshRequest, identity: IdentityDep):
    if not settings.game_debug_mode:
        raise HTTPException(404, "Debug mode is disabled")
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, "Debug controls are limited to server admins")
    try:
        slot = force_pool_refresh(identity.guild_id, req.event_id)
        async with SessionLocal() as session:
            async with session.begin():
                missions, _ = await ensure_pool(session, identity.guild_id)
        if _bot and _bot.is_ready():
            try:
                await _bot.announce_pool(identity.guild_id, missions)
            except Exception as exc:
                print(f"debug pool announcement error: {exc}")
        return {"pool_slot": slot, "event": pool_event(identity.guild_id, slot), "mission_count": len(missions)}
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/debug/battles/goblin-warcamp")
async def debug_goblin_battle(identity: IdentityDep):
    if not settings.game_debug_mode:
        raise HTTPException(404, "Debug mode is disabled")
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, "Debug controls are limited to server admins")
    async with SessionLocal() as session:
        try:
            async with session.begin():
                mission = await debug_start_goblin_battle(
                    session, identity.guild_id, identity.user_id, identity.display_name,
                )
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    return {"mission": mission_summary(mission), "battle": (mission.analysis or {}).get("battle")}


@app.post("/api/debug/battles/captive-cart")
async def debug_captive_cart_battle(identity: IdentityDep):
    if not settings.game_debug_mode:
        raise HTTPException(404, "Debug mode is disabled")
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, "Debug controls are limited to server admins")
    async with SessionLocal() as session:
        try:
            async with session.begin():
                mission = await debug_start_battle(
                    session, identity.guild_id, identity.user_id, identity.display_name, "goblin_captive_cart",
                )
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    return {"mission": mission_summary(mission), "battle": (mission.analysis or {}).get("battle")}


@app.post("/api/debug/battles/smoke-signals")
async def debug_smoke_signals_battle(identity: IdentityDep):
    if not settings.game_debug_mode:
        raise HTTPException(404, "Debug mode is disabled")
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, "Debug controls are limited to server admins")
    async with SessionLocal() as session:
        try:
            async with session.begin():
                mission = await debug_start_battle(
                    session, identity.guild_id, identity.user_id, identity.display_name, "goblin_smoke_signals",
                )
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    return {"mission": mission_summary(mission), "battle": (mission.analysis or {}).get("battle")}


@app.post("/api/debug/private-contracts/hedgerow-watch")
async def debug_hedgerow_watch_contract(identity: IdentityDep):
    if not settings.game_debug_mode:
        raise HTTPException(404, "Debug mode is disabled")
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, "Debug controls are limited to server admins")
    async with SessionLocal() as session:
        try:
            async with session.begin():
                mission = await spawn_private_contract(
                    session, identity.guild_id, identity.user_id, "hedgerow_watch_defense", "DEBUG: Keeper Mara Fen",
                )
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    return {"mission": mission_summary(mission)}


@app.post("/api/missions/{mission_id}/analysis")
async def mission_analysis(mission_id: str, req: PartyRequest, identity: IdentityDep):
    async with SessionLocal() as session:
        try:
            analysis = await analyze_instance(
                session, identity.guild_id, identity.user_id, mission_id, req.party_ids, req.role_assignments,
                req.bodyguard_ids,
            )
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    return {"analysis": analysis}


@app.post("/api/missions/{mission_id}/claim")
async def mission_claim(mission_id: str, req: PartyRequest, identity: IdentityDep):
    async with SessionLocal() as session:
        try:
            async with session.begin():
                if not settings.dev_bypass_auth:await require_registration(session,identity.guild_id,identity.user_id)
                if not req.party_ids:
                    mission=await reserve_instance(session,identity.guild_id,identity.user_id,identity.display_name,mission_id)
                else:
                    mission = await claim_instance(
                        session, identity.guild_id, identity.user_id, identity.display_name,
                        mission_id, req.party_ids, req.role_assignments, req.bodyguard_ids,
                    )
                if mission.status=='claimed':await resolve_due(session,identity.guild_id,identity.user_id)
                decision = None
                if mission.status == "decision":
                    from .services import get_decision_instance
                    decision = await get_decision_instance(session, identity.guild_id, identity.user_id, mission_id)
        except ValueError as exc:
            raise HTTPException(409, str(exc))
    request_notice_delivery([mission.id])
    return {"mission": mission_summary(mission,include_result=True), "decision": decision, "message": "Contract saved to Private Contracts." if mission.status=='reserved' else 'Expedition started.'}


@app.get("/api/missions/{mission_id}/decision")
async def mission_decision(mission_id: str, identity: IdentityDep):
    from .services import get_decision_instance
    async with SessionLocal() as session:
        try:
            decision=await get_decision_instance(session,identity.guild_id,identity.user_id,mission_id)
        except ValueError as exc:
            raise HTTPException(409,str(exc))
    return {'decision':decision}


@app.post("/api/missions/{mission_id}/decision")
async def mission_choose(mission_id: str, req: MissionChoiceRequest, identity: IdentityDep):
    from .services import choose_decision_instance
    async with SessionLocal() as session:
        try:
            async with session.begin():
                response=await choose_decision_instance(session,identity.guild_id,identity.user_id,mission_id,req.node_id,req.revision,req.choice_id)
        except ValueError as exc:
            raise HTTPException(409,str(exc))
    request_notice_delivery([mission_id])
    return response


@app.get("/api/missions/{mission_id}/battle")
async def battle_state(mission_id: str, identity: IdentityDep):
    async with SessionLocal() as session:
        try:
            battle = await get_battle_instance(session, identity.guild_id, identity.user_id, mission_id)
        except ValueError as exc:
            raise HTTPException(404, str(exc))
    return {"battle": battle}


@app.post("/api/missions/{mission_id}/battle/command")
async def battle_command(mission_id: str, req: CombatCommandRequest, identity: IdentityDep):
    completed_mission = None
    async with SessionLocal() as session:
        try:
            async with session.begin():
                battle, result = await update_battle_instance(
                    session, identity.guild_id, identity.user_id, mission_id,
                    command=req.model_dump(exclude_none=True),
                )
                if result:
                    completed_mission = await session.get(MissionInstance, mission_id)
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    if completed_mission and _bot and _bot.is_ready():
        try:
            request_notice_delivery([completed_mission.id])
        except Exception as exc:
            print(f"battle result announcement error: {exc}")
    return {"battle": battle, "result": result}


@app.post("/api/missions/{mission_id}/battle/auto")
async def battle_auto(mission_id: str, req: CombatAutoRequest, identity: IdentityDep):
    completed_mission = None
    async with SessionLocal() as session:
        try:
            async with session.begin():
                battle, result = await update_battle_instance(
                    session, identity.guild_id, identity.user_id, mission_id,
                    auto=req.tactic, resolve_all=req.resolve_all,
                )
                if result:
                    completed_mission = await session.get(MissionInstance, mission_id)
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    if completed_mission and _bot and _bot.is_ready():
        try:
            request_notice_delivery([completed_mission.id])
        except Exception as exc:
            print(f"battle result announcement error: {exc}")
    return {"battle": battle, "result": result}


@app.post("/api/debug/missions/{mission_id}/complete")
async def debug_complete_mission(mission_id: str, req: DebugCompleteRequest, identity: IdentityDep):
    if not settings.game_debug_mode:
        raise HTTPException(404, "Debug mode is disabled")
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, "Debug controls are limited to server admins")
    async with SessionLocal() as session:
        try:
            async with session.begin():
                mission = await debug_complete_instance(
                    session, identity.guild_id, identity.user_id, mission_id, req.outcome,
                    req.party_ids or [], req.role_assignments,
                )
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    if _bot and _bot.is_ready():
        try:
            request_notice_delivery([mission.id])
        except Exception as exc:
            print(f"debug result announcement error: {exc}")
    return {"mission": mission_summary(mission, include_result=True), "result": mission.result}


@app.post("/api/debug/missions/{mission_id}/resolve-now")
async def debug_resolve_mission_now(mission_id: str, identity: IdentityDep):
    if not settings.game_debug_mode:
        raise HTTPException(404, "Debug mode is disabled")
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, "Debug controls are limited to server admins")
    async with SessionLocal() as session:
        try:
            async with session.begin():
                mission = await debug_resolve_now_instance(
                    session, identity.guild_id, identity.user_id, mission_id,
                )
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    if mission.result and _bot and _bot.is_ready():
        try:
            request_notice_delivery([mission.id])
        except Exception as exc:
            print(f"debug result announcement error: {exc}")
    return {"mission": mission_summary(mission, include_result=True), "result": mission.result}


@app.get("/api/missions/active")
async def active_missions(identity: IdentityDep):
    async with SessionLocal() as session:
        async with session.begin():
            resolved_rows = await resolve_due(session, identity.guild_id, identity.user_id)
            rows = (await session.execute(
                select(MissionInstance)
                .where(MissionInstance.guild_id == identity.guild_id, MissionInstance.claimed_by_user_id == identity.user_id)
                .order_by(MissionInstance.claimed_at.desc()).limit(200)
            )).scalars().all()
    if _bot and _bot.is_ready():
        for row in resolved_rows:
            try:
                request_notice_delivery([row.id])
            except Exception as exc:
                print(f"mission result announcement error: {exc}")
    return {"missions": [mission_summary(x, include_result=True) for x in rows]}


@app.post("/api/reset")
async def reset(identity: IdentityDep):
    if not settings.dev_bypass_auth:
        raise HTTPException(403, "Reset endpoint is disabled outside development mode")
    async with SessionLocal() as session:
        async with session.begin():
            row = await get_player(session, identity.guild_id, identity.user_id)
            if row:
                await session.delete(row)
    return {"ok": True}


if FRONTEND_DIST.exists():
    assets = FRONTEND_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/")
    async def index():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{path:path}")
    async def spa(path: str):
        candidate = FRONTEND_DIST / path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
