from __future__ import annotations
import time
import discord
from discord import app_commands
from discord.ext import commands

from .content import MISSION_RANKS, MISSION_TEMPLATES
from .db import SessionLocal
from .game import mission_rank
from .models import GuildConfig, MissionInstance
from .services import available_chain_missions, ensure_guild_config, ensure_pool, get_player, mission_summary, pool_event
from .settings import settings


class FortcampBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.none()
        intents.guilds = True
        super().__init__(command_prefix="!fortcamp-unused-", intents=intents)
        self._synced_guild_ids: set[int] = set()

    async def setup_hook(self) -> None:
        # IMPORTANT: Do not call self.tree.sync() globally on an Activity-enabled app.
        # Discord automatically owns a global PRIMARY_ENTRY_POINT (Launch) command for
        # Activities. discord.py's bulk global sync payload does not include that special
        # command, so Discord rejects the overwrite with error 50240.
        #
        # Fortcamp therefore syncs its ordinary slash commands as guild commands after
        # the Gateway is ready. This is also ideal for development because guild command
        # updates appear immediately.
        return

    async def _sync_commands_to_guild(self, guild: discord.Guild) -> None:
        if guild.id in self._synced_guild_ids:
            return
        target = discord.Object(id=guild.id)
        self.tree.copy_global_to(guild=target)
        try:
            synced = await self.tree.sync(guild=target)
            self._synced_guild_ids.add(guild.id)
            print(f"Synced {len(synced)} Fortcamp command(s) to guild {guild.name} ({guild.id})")
        except discord.HTTPException as exc:
            print(f"Discord command sync failed for guild {guild.id}: {exc}")

    async def on_ready(self):
        # If DISCORD_TEST_GUILD_ID is set, restrict dev command syncing to that guild.
        # If blank, sync to every guild the bot is currently installed in.
        for guild in self.guilds:
            if settings.discord_test_guild_id and str(guild.id) != settings.discord_test_guild_id:
                continue
            await self._sync_commands_to_guild(guild)

        async with SessionLocal() as session:
            async with session.begin():
                for guild in self.guilds:
                    await ensure_guild_config(session, str(guild.id))
        print(f"Discord bot ready as {self.user} in {len(self.guilds)} guild(s)")

    async def on_guild_join(self, guild: discord.Guild):
        # Makes installs into another test server work without a global command sync.
        if not settings.discord_test_guild_id or str(guild.id) == settings.discord_test_guild_id:
            await self._sync_commands_to_guild(guild)
        async with SessionLocal() as session:
            async with session.begin():
                await ensure_guild_config(session, str(guild.id))

    async def announce_pool(self, guild_id: str, missions: list[MissionInstance]) -> None:
        async with SessionLocal() as session:
            config = await session.get(GuildConfig, guild_id)
        if not config or not config.announcement_channel_id:
            return
        channel = self.get_channel(int(config.announcement_channel_id))
        if not isinstance(channel, discord.abc.Messageable):
            return
        lines = []
        e_rank = [row for row in missions if (row.analysis or {}).get("public_wave",1)==1 and MISSION_TEMPLATES[row.template_id].get("rank", "E") == "E"]
        for row in e_rank[:8]:
            m = mission_summary(row)
            lines.append(f"**[E] {m['name']}** · {m['party_size']} char · play immediately")
        for rank in MISSION_RANKS[1:]:
            count = sum(1 for row in missions if MISSION_TEMPLATES[row.template_id].get("rank", "E") == rank)
            if count:
                lines.append(f"**{rank}-Rank missions available:** {count} · details hidden until unlocked")
        event = pool_event(guild_id, missions[0].pool_slot if missions else 0)
        title = "New Fortcamp mission pool" if event["id"] == "general" else f"EVENT · {event['name']}"
        description = event["splash"] + "\n\n" + "\n".join(lines)
        embed = discord.Embed(title=title, description=description, colour=0xD7B66A)
        embed.set_footer(text="New pool every 30 minutes. Five points per opening wave; wave two opens after one minute, free-for-all after two.")
        try:
            await channel.send(embed=embed)
        except discord.HTTPException as exc:
            print(f"Discord pool announcement failed for guild {guild_id}: {exc}")

    async def announce_result(self, row: MissionInstance) -> None:
        async with SessionLocal() as session:
            config = await session.get(GuildConfig, row.guild_id)
        if not config or not config.announcement_channel_id or not row.claimed_by_user_id or not row.result:
            return
        channel = self.get_channel(int(config.announcement_channel_id))
        if not isinstance(channel, discord.abc.Messageable):
            return
        outcome = row.result.get("outcome", "completed").replace("_", " ").title()
        try:
            await channel.send(f"<@{row.claimed_by_user_id}> **{row.result.get('mission', 'Mission')}** finished: **{outcome}**. Open Fortcamp for the full result.")
        except discord.HTTPException as exc:
            print(f"Discord result announcement failed for guild {row.guild_id}: {exc}")


bot = FortcampBot()


@bot.tree.command(name="register", description="Join Fortcamp in this server; keep your existing progress")
@app_commands.guild_only()
async def register(interaction: discord.Interaction):
    from .registration import set_registration,registered_count
    async with SessionLocal() as session:
        async with session.begin():
            await ensure_guild_config(session,str(interaction.guild_id))
            await set_registration(session,str(interaction.guild_id),str(interaction.user.id),interaction.user.display_name)
            count=await registered_count(session,str(interaction.guild_id))
    where=f'{settings.web_origin} or the Fortcamp Activity' if settings.web_origin else 'the Fortcamp Activity'
    await interaction.response.send_message(f"Registered! Open {where} to create or resume your character. {count} registered player(s) in this server.",ephemeral=True)


@bot.tree.command(name="unregister", description="Pause Fortcamp participation without deleting your characters or progress")
@app_commands.guild_only()
async def unregister(interaction: discord.Interaction):
    from .registration import set_registration
    async with SessionLocal() as session:
        async with session.begin():
            await set_registration(session,str(interaction.guild_id),str(interaction.user.id),interaction.user.display_name,False)
    await interaction.response.send_message("Unregistered. Your characters, items and progress are kept. You no longer count toward new mission pools or start new contracts. Existing expeditions may still finish. Use /register to return.",ephemeral=True)


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"


@bot.tree.command(name="fortcamp_setup", description="Use this channel for Fortcamp mission announcements")
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def fortcamp_setup(interaction: discord.Interaction):
    assert interaction.guild_id and interaction.channel_id
    async with SessionLocal() as session:
        async with session.begin():
            config = await ensure_guild_config(session, str(interaction.guild_id))
            config.announcement_channel_id = str(interaction.channel_id)
            missions, _ = await ensure_pool(session, str(interaction.guild_id))
    await interaction.response.send_message("Fortcamp mission-pool announcements will be posted in this channel.", ephemeral=True)
    await bot.announce_pool(str(interaction.guild_id), missions)


@bot.tree.command(name="fortcamp_pool", description="Show a short summary of the current shared mission pool")
@app_commands.guild_only()
async def fortcamp_pool(interaction: discord.Interaction):
    assert interaction.guild_id
    async with SessionLocal() as session:
        async with session.begin():
            missions, _ = await ensure_pool(session, str(interaction.guild_id))
            missions = list(missions) + await available_chain_missions(
                session, str(interaction.guild_id), str(interaction.user.id),
            )
            player = await get_player(session, str(interaction.guild_id), str(interaction.user.id))
            viewer_rank = mission_rank(player.state) if player else "E"
            event = pool_event(str(interaction.guild_id), missions[0].pool_slot if missions else 0)
    lines = []
    locked_counts = {rank: 0 for rank in MISSION_RANKS}
    for row in missions:
        if (row.analysis or {}).get("public_wave",1)==2 and int(time.time())<row.spawned_at+60:
            continue
        m = mission_summary(row, viewer_rank=viewer_rank)
        if m.get("locked"):
            if m["status"] == "available":
                locked_counts[m["rank"]] += 1
            continue
        owner = f" — claimed by **{m['claimed_by_name']}**" if m["claimed_by_name"] else ""
        lines.append(f"• **[{m['rank']}] {m['name']}** ({m['party_size']} chars, play immediately){owner}")
    for rank in MISSION_RANKS:
        if locked_counts[rank]:
            lines.append(f"• **{rank}-Rank missions available:** {locked_counts[rank]} · details locked")
    heading = f"**{event['name']}** · {event['splash']}\n\nYour Guild Hall visibility: **{viewer_rank}-Rank**\n"
    description = heading + ("\n".join(lines) or "No missions in the current pool.")
    if len(description) > 1950:
        description = description[:1900] + "\n…Open the Fortcamp Activity for the full pool."
    await interaction.response.send_message(description, ephemeral=True)
