from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.ipc import Server
from discord.ext.ipc.objects import ClientPayload

from utils.db import (
    get_mod_log_channel,
    update_mod_log_channel,
    get_member_log_channel,
    update_member_log_channel,
    get_welcome_message,
    update_welcome_message,
    is_afk,
    set_afk,
    remove_afk,
    get_afk_details,
)

if TYPE_CHECKING:
    from bot import FumeGuard


class IPC(commands.Cog):
    def __init__(self, bot: FumeGuard):
        self.bot: FumeGuard = bot

    async def cog_load(self):
        await self.bot.ipc.start()

    async def cog_unload(self):
        await self.bot.ipc.stop()

    # noinspection PyUnusedLocal
    @Server.route(name="get_guild_count")
    async def _get_guild_count(self, data: ClientPayload):
        return {"status": 200, "count": len(self.bot.guilds)}

    # noinspection PyUnusedLocal
    @Server.route(name="get_user_count")
    async def _get_user_count(self, data: ClientPayload):
        return {"status": 200, "count": len(self.bot.users)}

    # noinspection PyUnusedLocal
    @Server.route(name="get_command_count")
    async def _get_command_count(self, data: ClientPayload):
        _commands = await self.bot.tree.fetch_commands()
        return {"status": 200, "count": len(_commands)}

    @Server.route(name="get_channel_list")
    async def _get_channel_list(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        channels = dict()

        for channel in guild.text_channels:
            if not channel.permissions_for(guild.me).send_messages:
                continue

            else:
                channels[channel.id] = channel.name

        return {"channels": channels}

    @Server.route(name="get_mutual_guilds")
    async def _get_mutual_guilds(self, data: ClientPayload):
        user = self.bot.get_user(data.user_id)

        if not user:
            return {"error": {"code": 404, "message": "User not found."}}

        guilds = dict()

        for guild in user.mutual_guilds:
            member = await guild.fetch_member(user.id)

            guilds[guild.id] = {
                "name": guild.name,
                "member_manage_guild": member.guild_permissions.manage_guild,
                "bot_manage_nicknames": guild.me.guild_permissions.manage_nicknames,
            }

        return {"guilds": guilds}

    @Server.route(name="get_mod_log_channel")
    async def _get_mod_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        channel_id = await get_mod_log_channel(self.bot.pool, guild.id)

        if channel_id:
            channel = guild.get_channel(channel_id)
            return {"id": channel.id, "name": channel.name}

        else:
            return {"id": 0, "name": "Logging disabled."}

    @Server.route(name="update_mod_log_channel")
    async def _update_mod_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        await update_mod_log_channel(self.bot.pool, guild.id, data.channel_id)

        return {"status": 200, "message": "Success."}

    @Server.route(name="get_member_log_channel")
    async def _get_member_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        channel_id = await get_member_log_channel(self.bot.pool, guild.id)

        if channel_id:
            channel = guild.get_channel(channel_id)
            return {"id": channel.id, "name": channel.name}

        else:
            return {"id": 0, "name": "Logging disabled."}

    @Server.route(name="update_member_log_channel")
    async def _update_member_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        await update_member_log_channel(self.bot.pool, guild.id, data.channel_id)

        return {"status": 200, "message": "Success."}

    @Server.route(name="get_welcome_message")
    async def _get_welcome_message(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        message = await get_welcome_message(self.bot.pool, guild.id)

        return {"message": message}

    @Server.route(name="update_welcome_message")
    async def _update_welcome_message(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        await update_welcome_message(self.bot.pool, guild.id, data.message)

        return {"status": 200, "message": "Success."}

    @Server.route(name="is_afk")
    async def _is_afk(self, data: ClientPayload):
        user = self.bot.get_user(data.user_id)

        if not user:
            return {"error": {"code": 404, "message": "User not found."}}

        guild = self.bot.get_guild(data.guild_id)
        member = await guild.fetch_member(user.id)

        if not member:
            return {"error": {"code": 404, "message": "Member not found."}}

        return {
            "afk": await is_afk(self.bot.pool, user_id=member.id, guild_id=guild.id)
        }

    @Server.route(name="get_afk_details")
    async def _get_afk_details(self, data: ClientPayload):
        user = self.bot.get_user(data.user_id)

        if not user:
            return {"error": {"code": 404, "message": "User not found."}}

        guild = self.bot.get_guild(data.guild_id)
        member = await guild.fetch_member(user.id)

        if not member:
            return {"error": {"code": 404, "message": "Member not found."}}

        if not await is_afk(self.bot.pool, user_id=member.id, guild_id=guild.id):
            return {"error": {"code": 400, "message": "User is not AFK."}}

        afk_details = await get_afk_details(
            self.bot.pool, user_id=member.id, guild_id=guild.id
        )

        afk_details["start"] = afk_details["start"].strftime("%d-%m-%Y %H:%M:%S")

        return {"details": afk_details}

    @Server.route(name="toggle_afk")
    async def _toggle_afk(self, data: ClientPayload):
        user = self.bot.get_user(data.user_id)

        if not user:
            return {"error": {"code": 404, "message": "User not found."}}

        guild = self.bot.get_guild(data.guild_id)
        member = await guild.fetch_member(user.id)

        if not member:
            return {"error": {"code": 404, "message": "Member not found."}}

        if not await is_afk(self.bot.pool, user_id=user.id, guild_id=guild.id):
            if data.reason and len(data.reason) > 100:
                return {"error": {"code": 400, "message": "AFK reason too long."}}

            try:
                await member.edit(
                    nick=f"[AFK] {user.display_name}", reason="AFK status set."
                )

            except (discord.Forbidden, discord.errors.Forbidden):
                pass

            await set_afk(
                self.bot.pool,
                user_id=member.id,
                guild_id=guild.id,
                reason=data.reason,
            )

        else:
            await remove_afk(self.bot.pool, user_id=member.id, guild_id=guild.id)

            if member.display_name.startswith("[AFK]"):
                try:
                    await member.edit(
                        nick=member.display_name[5:], reason="AFK status removed."
                    )

                except (discord.Forbidden, discord.errors.Forbidden):
                    pass

        return {"status": 200, "message": "Success."}


async def setup(bot: FumeGuard):
    await bot.add_cog(IPC(bot))
