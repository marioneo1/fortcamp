from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from .settings import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    from . import models  # noqa: F401
    # Save a consistent SQLite snapshot before first resource migration, including WAL.
    if engine.url.get_backend_name()=='sqlite' and engine.url.database not in {None,':memory:'}:
        from pathlib import Path
        import sqlite3
        path=Path(engine.url.database).resolve()
        backup=path.parent/'backups'/(path.stem+'-before-economy-v10.sqlite')
        if path.is_file() and not backup.exists():
            backup.parent.mkdir(parents=True,exist_ok=True)
            with sqlite3.connect(str(path)) as source,sqlite3.connect(str(backup)) as target:source.backup(target)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
