from __future__ import annotations

from typing import TYPE_CHECKING

import re

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0
from utils.db import (
    automod_enable,
    automod_status,
    automod_disable,
    automod_get_allowed_link_roles,
    automod_get_allowed_embed_roles,
    automod_update_allowed_link_roles,
    automod_update_allowed_embed_roles,
)
from utils.checks import automod_perms_check

if TYPE_CHECKING:
    import aiomysql

    from bot import FumeGuard


URL_REGEX = r"\b((?:https?|ftp):\/\/|www\.|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:[^\s]*)\b"


@app_commands.guild_only()
class AutoMod(
    commands.GroupCog,
    group_name="automod",
    group_description="Various automatic moderation configuration commands.",
):
    def __init__(self, bot: FumeGuard):
        self.bot: FumeGuard = bot

    @staticmethod
    async def _process_message(pool: aiomysql.Pool, message: discord.Message):
        if await automod_get_allowed_link_roles(pool, message.guild.id):
            for role_id in await automod_get_allowed_link_roles(
                pool, message.guild.id
            ):
                role = message.guild.get_role(int(role_id))
                if role in message.author.roles:
                    return

            else:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, you are not allowed to send links in this server."
                )

        if await automod_get_allowed_embed_roles(pool, message.guild.id):
            for role_id in await automod_get_allowed_embed_roles(
                pool, message.guild.id
            ):
                role = message.guild.get_role(int(role_id))
                if role in message.author.roles:
                    return

            else:
                await message.edit(suppress=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if await automod_status(self.bot.pool, message.guild.id) and re.search(
            URL_REGEX, message.content
        ):
            await self._process_message(self.bot.pool, message)

    @app_commands.command(name="enable")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_enable(self, ctx: discord.Interaction):
        """Enable the automatic moderation system."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await automod_status(self.bot.pool, ctx.guild.id):
            await automod_enable(self.bot.pool, ctx.guild.id)
            await ctx.edit_original_response(
                content="Automatic moderation system has been enabled."
            )

        else:
            await ctx.edit_original_response(
                content="Automatic moderation system is already enabled."
            )

    @app_commands.command(name="disable")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_disable(self, ctx: discord.Interaction):
        """Disable the automatic moderation system."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if await automod_status(self.bot.pool, ctx.guild.id):
            await automod_disable(self.bot.pool, ctx.guild.id)
            await ctx.edit_original_response(
                content="Automatic moderation system has been disabled."
            )

        else:
            await ctx.edit_original_response(
                content="Automatic moderation system is already disabled."
            )

    @app_commands.command(name="show_link_send")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_show_link_send(self, ctx: discord.Interaction):
        """Show the roles who are allowed to send links in the server."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        allowed_link_roles = await automod_get_allowed_link_roles(
            self.bot.pool, ctx.guild.id
        )

        if allowed_link_roles:
            roles = [
                ctx.guild.get_role(int(role_id)).mention
                for role_id in allowed_link_roles
            ]
            await ctx.edit_original_response(
                content=f"Roles allowed to send links in the server are: {', '.join(roles)}."
            )

        else:
            await ctx.edit_original_response(
                content="No roles are allowed to send links in the server."
            )

    @app_commands.command(name="allow_link_send")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_allow_link_send(
        self, ctx: discord.Interaction, role: discord.Role
    ):
        """Set the roles who are allowed to send links in the server.

        Parameters
        ----------
        role : str
            The role to allow to send links.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if role.id not in await automod_get_allowed_link_roles(
            self.bot.pool, ctx.guild.id
        ):
            await automod_update_allowed_link_roles(
                self.bot.pool, ctx.guild.id, str(role.id)
            )
            await ctx.edit_original_response(
                content=f"Role {role.mention} is now allowed to send links in the server."
            )

        else:
            await ctx.edit_original_response(
                content=f"Role {role.mention} is already allowed to send links in the server."
            )

    @app_commands.command(name="disallow_link_send")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_disallow_link(
        self, ctx: discord.Interaction, role: discord.Role
    ):
        """Set the roles who are not allowed to send links in the server.

        Parameters
        ----------
        role : str
            The role to disallow to send links.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if role.id in await automod_get_allowed_link_roles(
            self.bot.pool, ctx.guild.id
        ):
            await automod_update_allowed_link_roles(
                self.bot.pool, ctx.guild.id, str(role.id)
            )
            await ctx.edit_original_response(
                content=f"Role {role.mention} is now disallowed to send links in the server."
            )

        else:
            await ctx.edit_original_response(
                content=f"Role {role.mention} is already disallowed to send links in the server."
            )

    @app_commands.command(name="show_link_embed")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_show_embed_send(self, ctx: discord.Interaction):
        """Show the roles who are allowed to send embeds in the server."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        allowed_embed_roles = await automod_get_allowed_embed_roles(
            self.bot.pool, ctx.guild.id
        )

        if allowed_embed_roles:
            roles = [
                ctx.guild.get_role(int(role_id)).mention
                for role_id in allowed_embed_roles
            ]
            await ctx.edit_original_response(
                content=f"Roles allowed to send embeds in the server are: {', '.join(roles)}."
            )

        else:
            await ctx.edit_original_response(
                content="No roles are allowed to send embeds in the server."
            )

    @app_commands.command(name="allow_link_embed")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_allow_embed(
        self, ctx: discord.Interaction, role: discord.Role
    ):
        """Set the roles who are allowed to send embeds in the server.

        Parameters
        ----------
        role : str
            The role to allow to send embeds.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if role.id not in await automod_get_allowed_embed_roles(
            self.bot.pool, ctx.guild.id
        ):
            await automod_update_allowed_embed_roles(
                self.bot.pool, ctx.guild.id, str(role.id)
            )
            await ctx.edit_original_response(
                content=f"Role {role.mention} is now allowed to send embeds in the server."
            )

        else:
            await ctx.edit_original_response(
                content=f"Role {role.mention} is already allowed to send embeds in the server."
            )

    @app_commands.command(name="disallow_link_embed")
    @app_commands.check(automod_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _automod_disallow_embed(
        self, ctx: discord.Interaction, role: discord.Role
    ):
        """Set the roles who are not allowed to send embeds in the server.

        Parameters
        ----------
        role : str
            The role to disallow to send embeds.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if role.id in await automod_get_allowed_embed_roles(
            self.bot.pool, ctx.guild.id
        ):
            await automod_update_allowed_embed_roles(
                self.bot.pool, ctx.guild.id, str(role.id)
            )
            await ctx.edit_original_response(
                content=f"Role {role.mention} is now disallowed to send embeds in the server."
            )

        else:
            await ctx.edit_original_response(
                content=f"Role {role.mention} is already disallowed to send embeds in the server."
            )


async def setup(bot: FumeGuard):
    await bot.add_cog(AutoMod(bot))
