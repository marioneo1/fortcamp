"""Browser Discord login. OAuth tokens never reach storage or the browser."""
import hashlib
import secrets
import time
from urllib.parse import urlencode, urlsplit

import httpx
import jwt
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, select

from .auth import Identity, create_session_token, exchange_discord_code, session_namespace
from .db import SessionLocal
from .models import WebLoginSession, PlayerRegistration
from .registration import require_registration
from .settings import settings


def web_origin():
    origin = settings.web_origin
    parsed = urlsplit(origin)
    local = parsed.hostname in {'127.0.0.1', 'localhost'}
    if not parsed.netloc or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment or (parsed.scheme != 'https' and not (local and parsed.scheme == 'http')):
        raise HTTPException(503, 'Browser login origin is not configured. Use the Fortcamp profile launcher.')
    return origin


def cookie_name(kind):
    return f'fortcamp_{kind}_{session_namespace()[:12]}'


def set_cookie(response, kind, value, age):
    response.set_cookie(cookie_name(kind), value, httponly=True, secure=web_origin().startswith('https:'), samesite='lax', max_age=age, path='/api/web')
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'


def same_origin(request):
    if request.headers.get('origin') != web_origin():
        raise HTTPException(403, 'Use this environment’s Fortcamp website.')


async def discord_account(access_token):
    """Retrieve identity and paginate guilds; only IDs/admin flags are saved."""
    headers = {'Authorization': f'Bearer {access_token}'}
    async with httpx.AsyncClient(timeout=15) as client:
        me = await client.get('https://discord.com/api/users/@me', headers=headers)
        if me.status_code != 200:
            raise HTTPException(401, 'Discord login expired. Sign in again.')
        guilds, after = [], None
        for _ in range(10):
            result = await client.get('https://discord.com/api/users/@me/guilds', headers=headers, params={'limit':200, **({'after':after} if after else {})})
            if result.status_code != 200:
                raise HTTPException(401, 'Discord server list could not be verified.')
            rows = result.json()
            guilds.extend(rows)
            if len(rows) < 200:
                break
            after = str(rows[-1]['id'])
        user = me.json()
    return user, [{'id':str(g['id']), 'admin':bool(g.get('owner') or int(g.get('permissions') or 0) & ((1 << 3) | (1 << 5)))} for g in guilds]


async def verify_member(guild_id, user_id):
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(f'https://discord.com/api/guilds/{guild_id}/members/{user_id}', headers={'Authorization':f'Bot {settings.discord_bot_token}'})
    if response.status_code in {403,404}:
        raise HTTPException(403, 'You are no longer a member, or Fortcamp is no longer installed in that server.')
    if response.status_code != 200:
        raise HTTPException(503, 'Discord could not verify server membership. Try again shortly.')
    if str(response.json().get('user',{}).get('id')) != user_id:
        raise HTTPException(403, 'Server membership could not be verified.')


async def account(request, session):
    token = request.cookies.get(cookie_name('account'), '')
    row = await session.get(WebLoginSession, hashlib.sha256(token.encode()).hexdigest()) if token else None
    if not row or row.namespace != session_namespace() or row.expires_at <= int(time.time()):
        raise HTTPException(401, 'Sign in with Discord to choose a server.')
    return row


class ServerSelection(BaseModel):
    guild_id: str = Field(min_length=1, max_length=32)


def browser_router(installed_guilds):
    router = APIRouter(prefix='/api/web')

    @router.get('/login')
    async def login(request: Request):
        origin = web_origin()
        if request.url.netloc != urlsplit(origin).netloc:
            raise HTTPException(400, f'Open {origin} to sign in to this environment.')
        if not settings.discord_client_id or not settings.discord_client_secret or not settings.discord_bot_token:
            raise HTTPException(503, 'Configure this environment’s Discord application and bot first.')
        now = int(time.time())
        nonce = secrets.token_urlsafe(32)
        state = jwt.encode({'nonce':nonce,'iat':now,'exp':now+600,'aud':'oauth:'+session_namespace()}, settings.app_session_secret, algorithm='HS256')
        url = 'https://discord.com/oauth2/authorize?' + urlencode({'client_id':settings.discord_client_id,'response_type':'code','scope':'identify guilds','redirect_uri':origin+'/api/web/callback','state':state,'prompt':'none'})
        response = RedirectResponse(url, status_code=302)
        set_cookie(response,'state',state,600)
        return response

    @router.get('/callback')
    async def callback(request: Request, code: str = '', state: str = '', error: str = ''):
        origin = web_origin()
        response = RedirectResponse(origin+'/?choose_server=1', status_code=302)
        try:
            expected = request.cookies.get(cookie_name('state'), '')
            if error or not code or not state or not expected or not secrets.compare_digest(state,expected):
                raise HTTPException(400,'Login was cancelled or expired.')
            jwt.decode(state,settings.app_session_secret,algorithms=['HS256'],audience='oauth:'+session_namespace(),options={'require':['exp','nonce','aud']})
            access_token = await exchange_discord_code(code, origin+'/api/web/callback')
            user, guilds = await discord_account(access_token)
            token = secrets.token_urlsafe(48)
            async with SessionLocal() as session:
                async with session.begin():
                    await session.execute(delete(WebLoginSession).where(WebLoginSession.expires_at <= int(time.time())))
                    old = request.cookies.get(cookie_name('account'))
                    if old:
                        await session.execute(delete(WebLoginSession).where(WebLoginSession.id == hashlib.sha256(old.encode()).hexdigest()))
                    session.add(WebLoginSession(id=hashlib.sha256(token.encode()).hexdigest(),namespace=session_namespace(),user_id=str(user['id']),display_name=(user.get('global_name') or user.get('username') or 'Player')[:100],guilds=guilds,expires_at=int(time.time())+43200))
            set_cookie(response,'account',token,43200)
        except (HTTPException,jwt.PyJWTError,httpx.HTTPError):
            response = RedirectResponse(origin+'/?login_error=expired_or_failed', status_code=302)
        response.delete_cookie(cookie_name('state'),path='/api/web',secure=origin.startswith('https:'),httponly=True,samesite='lax')
        response.headers['Cache-Control']='no-store'
        response.headers['Referrer-Policy']='no-referrer'
        return response

    @router.get('/servers')
    async def servers(request: Request):
        async with SessionLocal() as session:
            row = await account(request,session)
            allowed = {g['id'] for g in row.guilds}
            installed = installed_guilds()
            registered = {r.guild_id for r in (await session.execute(select(PlayerRegistration).where(PlayerRegistration.user_id==row.user_id,PlayerRegistration.active.is_(True)))).scalars()}
            visible = [{'id':gid,'name':g['name'],'icon':g.get('icon'), 'registered':gid in registered} for gid,g in installed.items() if gid in allowed]
            return JSONResponse({'display_name':row.display_name,'servers':sorted(visible,key=lambda g:g['name'].casefold()),'environment':settings.environment},headers={'Cache-Control':'no-store'})

    @router.post('/select')
    async def select_server(req: ServerSelection, request: Request):
        same_origin(request)
        async with SessionLocal() as session:
            row = await account(request,session)
            guild = next((g for g in row.guilds if g['id']==req.guild_id),None)
            if not guild or req.guild_id not in installed_guilds():
                raise HTTPException(403,'Choose a server you belong to where this Fortcamp bot is installed.')
            await verify_member(req.guild_id,row.user_id)
            await require_registration(session,req.guild_id,row.user_id)
            identity=Identity(req.guild_id,row.user_id,row.display_name,guild['admin'])
            return JSONResponse({'session_token':create_session_token(identity),'identity':identity.__dict__},headers={'Cache-Control':'no-store'})

    @router.post('/logout')
    async def logout(request: Request):
        same_origin(request)
        async with SessionLocal() as session:
            token = request.cookies.get(cookie_name('account'), '')
            async with session.begin():
                if token:
                    await session.execute(delete(WebLoginSession).where(WebLoginSession.id==hashlib.sha256(token.encode()).hexdigest()))
        response = JSONResponse({'ok':True},headers={'Cache-Control':'no-store'})
        response.delete_cookie(cookie_name('account'),path='/api/web',secure=web_origin().startswith('https:'),httponly=True,samesite='lax')
        return response

    return router
