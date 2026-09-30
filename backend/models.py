from __future__ import annotations
from sqlalchemy import JSON, BigInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class PlayerState(Base):
    __tablename__ = "player_states"
    guild_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), default="Player")
    state: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False)


class GuildConfig(Base):
    __tablename__ = "guild_configs"
    guild_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    announcement_channel_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)


class MissionInstance(Base):
    __tablename__ = "mission_instances"
    __table_args__ = (
        UniqueConstraint("guild_id", "pool_slot", "position", name="uq_guild_pool_position"),
    )

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    guild_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    template_id: Mapped[str] = mapped_column(String(80), nullable=False)
    pool_slot: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    spawned_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    expires_at: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(String(24), default="available", index=True)
    claimed_by_user_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    claimed_by_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    claimed_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    completes_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    party_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    party_snapshot: Mapped[list | None] = mapped_column(JSON, nullable=True)
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    resolved_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
