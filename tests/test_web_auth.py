from dataclasses import replace
import hashlib
import time
import unittest
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.auth import Identity, create_session_token, require_identity, session_namespace
from backend.db import Base
from backend.models import WebLoginSession, PlayerState
from backend.registration import set_registration
from backend.settings import settings
from backend.web_auth import browser_router, cookie_name, web_origin


class WebAuthTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.cfg=replace(settings,environment='dev',web_origin='https://dev.example.test',database_url='sqlite+aiosqlite:///:memory:',discord_client_id='dev-app',discord_client_secret='oauth-secret',discord_bot_token='bot-token',app_session_secret='shared-test-key-for-two-environments-123',dev_bypass_auth=False)
        self.engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        self.sessions=async_sessionmaker(self.engine,expire_on_commit=False)
        async with self.engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
        self.patches=[patch('backend.auth.settings',self.cfg),patch('backend.web_auth.settings',self.cfg),patch('backend.web_auth.SessionLocal',self.sessions)]
        for p in self.patches:p.start()
        self.installed={'10':{'name':'Friends'},'20':{'name':'Other server'}}
        app=FastAPI();app.include_router(browser_router(lambda:self.installed))
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url=self.cfg.web_origin)

    async def asyncTearDown(self):
        await self.client.aclose()
        for p in reversed(self.patches):p.stop()
        await self.engine.dispose()

    async def login(self):
        first=await self.client.get('/api/web/login')
        self.assertEqual(first.status_code,302)
        params=parse_qs(urlsplit(first.headers['location']).query)
        self.assertEqual(params['scope'],['identify guilds'])
        self.assertEqual(params['prompt'],['none'])
        self.assertEqual(params['redirect_uri'],[self.cfg.web_origin+'/api/web/callback'])
        self.assertIn('HttpOnly',first.headers['set-cookie'])
        self.assertIn('Secure',first.headers['set-cookie'])
        guilds=[{'id':'10','admin':False},{'id':'20','admin':True},{'id':'999','admin':True}]
        with patch('backend.web_auth.exchange_discord_code',AsyncMock(return_value='private-access-token')) as exchange,patch('backend.web_auth.discord_account',AsyncMock(return_value=({'id':'1','username':'Tester'},guilds))):
            result=await self.client.get('/api/web/callback',params={'code':'code','state':params['state'][0]})
        self.assertEqual(result.status_code,302)
        self.assertEqual(result.headers['location'],self.cfg.web_origin+'/?choose_server=1')
        exchange.assert_awaited_once_with('code',self.cfg.web_origin+'/api/web/callback')
        self.assertNotIn('private-access-token',result.text+str(result.headers))

    async def registered(self,guild='10'):
        async with self.sessions() as s:
            async with s.begin():await set_registration(s,guild,'1','Tester')

    async def select(self,guild='10',origin=None):
        return await self.client.post('/api/web/select',json={'guild_id':guild},headers={'Origin':origin or self.cfg.web_origin})

    async def test_picker_intersects_membership_and_installed_bot_servers(self):
        await self.login();await self.registered()
        result=await self.client.get('/api/web/servers')
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.headers['cache-control'],'no-store')
        self.assertEqual({g['id'] for g in result.json()['servers']},{'10','20'})
        self.assertTrue(next(g for g in result.json()['servers'] if g['id']=='10')['registered'])
        self.assertFalse(next(g for g in result.json()['servers'] if g['id']=='20')['registered'])

    async def test_select_rechecks_membership_and_binds_server_identity(self):
        await self.login();await self.registered()
        with patch('backend.web_auth.verify_member',AsyncMock()) as verify:
            result=await self.select()
        self.assertEqual(result.status_code,200);verify.assert_awaited_once_with('10','1')
        identity=await require_identity('Bearer '+result.json()['session_token'])
        self.assertEqual(identity.guild_id,'10');self.assertEqual(identity.user_id,'1');self.assertFalse(identity.guild_admin)
        await self.registered('20')
        with patch('backend.web_auth.verify_member',AsyncMock()):other=await self.select('20')
        second=await require_identity('Bearer '+other.json()['session_token'])
        self.assertEqual(second.guild_id,'20');self.assertTrue(second.guild_admin)
        # Same player has independent server rows; switching does not copy progress.
        async with self.sessions() as s:
            async with s.begin():
                for gid in ['10','20']:s.add(PlayerState(guild_id=gid,user_id='1',display_name='Tester',state={'camp':gid},updated_at=0))
            self.assertEqual((await s.get(PlayerState,(identity.guild_id,identity.user_id))).state,{'camp':'10'})
            self.assertEqual((await s.get(PlayerState,(second.guild_id,second.user_id))).state,{'camp':'20'})

    async def test_cannot_select_uninstalled_or_nonmember_server(self):
        await self.login()
        for gid in ['999','unlisted']:
            self.assertEqual((await self.select(gid)).status_code,403)
        self.installed.pop('10')
        self.assertEqual((await self.select()).status_code,403)

    async def test_removed_member_and_unregistered_player_cannot_enter(self):
        await self.login()
        with patch('backend.web_auth.verify_member',AsyncMock(side_effect=HTTPException(403,'Removed member'))):
            self.assertEqual((await self.select()).status_code,403)
        with patch('backend.web_auth.verify_member',AsyncMock()):
            result=await self.select()
        self.assertEqual(result.status_code,403);self.assertIn('/register',result.json()['detail'])

    async def test_state_cookie_mismatch_or_expiry_never_exchanges_code(self):
        first=await self.client.get('/api/web/login')
        state=parse_qs(urlsplit(first.headers['location']).query)['state'][0]
        with patch('backend.web_auth.exchange_discord_code',AsyncMock()) as exchange:
            result=await self.client.get('/api/web/callback',params={'code':'x','state':state+'tampered'})
        self.assertIn('login_error',result.headers['location']);exchange.assert_not_awaited()
        expired=jwt.encode({'exp':int(time.time())-1,'nonce':'n','aud':'oauth:'+session_namespace()},self.cfg.app_session_secret,algorithm='HS256')
        self.client.cookies.set(cookie_name('state'),expired,domain='dev.example.test',path='/api/web')
        with patch('backend.web_auth.exchange_discord_code',AsyncMock()) as exchange:
            result=await self.client.get('/api/web/callback',params={'code':'x','state':expired})
        self.assertIn('login_error',result.headers['location']);exchange.assert_not_awaited()

    async def test_account_persists_in_database_without_oauth_token(self):
        await self.login()
        token=self.client.cookies.get(cookie_name('account'))
        async with self.sessions() as s:
            row=await s.get(WebLoginSession,hashlib.sha256(token.encode()).hexdigest())
            self.assertEqual(row.user_id,'1');self.assertNotIn('access_token',row.__dict__)
        app=FastAPI();app.include_router(browser_router(lambda:self.installed))
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url=self.cfg.web_origin,cookies=self.client.cookies) as restarted:
            self.assertEqual((await restarted.get('/api/web/servers')).status_code,200)

    async def test_cross_origin_mutations_and_logout_revocation(self):
        await self.login()
        self.assertEqual((await self.select(origin='https://play.example.test')).status_code,403)
        bad=await self.client.post('/api/web/logout',headers={'Origin':'https://evil.example'})
        self.assertEqual(bad.status_code,403)
        good=await self.client.post('/api/web/logout',headers={'Origin':self.cfg.web_origin})
        self.assertEqual(good.status_code,200)
        self.assertEqual((await self.client.get('/api/web/servers')).status_code,401)

    async def test_dev_release_tokens_reject_even_with_shared_secret(self):
        token=create_session_token(Identity('10','1','Tester'))
        for cfg in [replace(self.cfg,environment='release'),replace(self.cfg,database_url='sqlite+aiosqlite:///other.db'),replace(self.cfg,discord_client_id='other-app')]:
            with patch('backend.auth.settings',cfg),self.assertRaises(HTTPException) as raised:
                await require_identity('Bearer '+token)
            self.assertEqual(raised.exception.status_code,401)
        legacy=jwt.encode({'sub':'1','guild_id':'10','exp':int(time.time())+100},self.cfg.app_session_secret,algorithm='HS256')
        with self.assertRaises(HTTPException):await require_identity('Bearer '+legacy)

    async def test_expired_account_cannot_select_and_wrong_origin_cannot_start(self):
        await self.login()
        token=self.client.cookies.get(cookie_name('account'))
        async with self.sessions() as s:
            async with s.begin():(await s.get(WebLoginSession,hashlib.sha256(token.encode()).hexdigest())).expires_at=0
        self.assertEqual((await self.client.get('/api/web/servers')).status_code,401)
        self.assertEqual((await self.client.get('https://play.example.test/api/web/login')).status_code,400)

    def test_web_origin_rejects_external_http_and_path_redirects(self):
        for value in ['http://example.test','https://example.test/path','https://user@example.test','https://example.test?x=1']:
            with patch('backend.web_auth.settings',replace(self.cfg,web_origin=value)),self.assertRaises(HTTPException):web_origin()
        with patch('backend.web_auth.settings',replace(self.cfg,web_origin='http://127.0.0.1:5174')):
            self.assertEqual(web_origin(),'http://127.0.0.1:5174')
