from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(os.getenv('FORTCAMP_ENV_FILE') or None)


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/fortcamp.db")
    discord_client_id: str = os.getenv("DISCORD_CLIENT_ID", "")
    discord_client_secret: str = os.getenv("DISCORD_CLIENT_SECRET", "")
    discord_bot_token: str = os.getenv("DISCORD_BOT_TOKEN", "")
    discord_test_guild_id: str = os.getenv("DISCORD_TEST_GUILD_ID", "")
    app_session_secret: str = os.getenv("APP_SESSION_SECRET", "dev-only-change-me")
    dev_bypass_auth: bool = _bool("DEV_BYPASS_AUTH", True)
    dev_guild_id: str = os.getenv("DEV_GUILD_ID", "local-guild")
    dev_user_id: str = os.getenv("DEV_USER_ID", "local-user")
    dev_user_name: str = os.getenv("DEV_USER_NAME", "Local Tester")
    bot_enabled: bool = _bool("BOT_ENABLED", False)
    mission_pool_size: int = max(8, min(24, int(os.getenv("MISSION_POOL_SIZE", "12"))))
    mission_time_scale: float = max(0.01, float(os.getenv("MISSION_TIME_SCALE", "1.0")))
    game_debug_mode: bool = _bool("GAME_DEBUG_MODE", False)


settings = Settings()
