from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Annotated

import httpx
import jwt
from fastapi import Depends, Header, HTTPException

from .settings import settings


@dataclass
class Identity:
    guild_id: str
    user_id: str
    display_name: str
    guild_admin: bool = False


def create_session_token(identity: Identity) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": identity.user_id, "guild_id": identity.guild_id, "name": identity.display_name, "guild_admin": identity.guild_admin, "iat": now, "exp": now + 60 * 60 * 12},
        settings.app_session_secret,
        algorithm="HS256",
    )


async def exchange_discord_code(code: str) -> str:
    if not settings.discord_client_id or not settings.discord_client_secret:
        raise HTTPException(500, "Discord OAuth credentials are not configured")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": settings.discord_client_id,
                "client_secret": settings.discord_client_secret,
                "grant_type": "authorization_code",
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code >= 400:
        raise HTTPException(401, "Discord authorization code exchange failed")
    token = response.json().get("access_token")
    if not token:
        raise HTTPException(401, "Discord did not return an access token")
    return token


async def verify_discord_identity(access_token: str, guild_id: str) -> Identity:
    if not guild_id:
        raise HTTPException(400, "Launch this Activity from a Discord server")
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=15) as client:
        me_response, guilds_response = await client.get("https://discord.com/api/users/@me", headers=headers), await client.get("https://discord.com/api/users/@me/guilds", headers=headers)
    if me_response.status_code >= 400 or guilds_response.status_code >= 400:
        raise HTTPException(401, "Discord access token could not be verified")
    me = me_response.json()
    guilds = guilds_response.json()
    guild = next((g for g in guilds if str(g.get("id")) == str(guild_id)), None)
    if not guild:
        raise HTTPException(403, "This Discord account is not a member of that server")
    permissions = int(guild.get("permissions") or 0)
    guild_admin = bool(guild.get("owner") or (permissions & (1 << 3)) or (permissions & (1 << 5)))
    name = me.get("global_name") or me.get("username") or "Discord User"
    return Identity(guild_id=str(guild_id), user_id=str(me["id"]), display_name=name[:100], guild_admin=guild_admin)


async def require_identity(
    authorization: Annotated[str | None, Header()] = None,
    x_dev_guild: Annotated[str | None, Header()] = None,
    x_dev_user: Annotated[str | None, Header()] = None,
    x_dev_name: Annotated[str | None, Header()] = None,
) -> Identity:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, settings.app_session_secret, algorithms=["HS256"])
            return Identity(guild_id=str(payload["guild_id"]), user_id=str(payload["sub"]), display_name=str(payload.get("name") or "Player"), guild_admin=bool(payload.get("guild_admin", False)))
        except jwt.PyJWTError:
            raise HTTPException(401, "Invalid or expired game session")

    if settings.dev_bypass_auth:
        return Identity(
            guild_id=x_dev_guild or settings.dev_guild_id,
            user_id=x_dev_user or settings.dev_user_id,
            display_name=x_dev_name or settings.dev_user_name,
            guild_admin=True,
        )
    raise HTTPException(401, "Discord authentication required")


IdentityDep = Annotated[Identity, Depends(require_identity)]
