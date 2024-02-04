from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0
from utils.db import is_afk, get_afk_details, get_afk_members, set_afk, remove_afk

if TYPE_CHECKING:
    import aiomysql
    from bot import FumeGuard


@app_commands.guild_only()
class Afk(
    commands.GroupCog,
    group_name="afk",
    group_description="Various commands to manage your AFK status.",
):
    def __init__(self, bot: FumeGuard):
        self.bot: FumeGuard = bot

    @staticmethod
    async def _afk_perms(ctx: discord.Interaction):
        return ctx.guild.me.guild_permissions.manage_nicknames

    @staticmethod
    async def _process_mentions(pool: aiomysql.Pool, message: discord.Message):
        for member in message.mentions:
            if await is_afk(pool, user_id=member.id, guild_id=member.guild.id):
                afk_details = await get_afk_details(
                    pool, user_id=member.id, guild_id=member.guild.id
                )

                await message.reply(
                    content=f"{member.mention} is afk since <t:{int(datetime.timestamp(afk_details['start']))}:t>."
                    f"\n**Reason:** {afk_details['reason'] or 'Unspecified.'}",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.mentions:
            await self._process_mentions(self.bot.pool, message)

    @app_commands.command(name="set")
    @app_commands.check(_afk_perms)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _afk_set(self, ctx: discord.Interaction, reason: Optional[str] = None):
        """Sets your AFK status.

        Parameters
        ----------
        reason : Optional[str]
            The reason for being AFK.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await is_afk(
            self.bot.pool, user_id=ctx.user.id, guild_id=ctx.guild.id
        ):
            await set_afk(
                self.bot.pool,
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                reason=reason,
            )

            if not ctx.user.display_name.startswith("[AFK]"):
                try:
                    await ctx.user.edit(
                        nick=f"[AFK] {ctx.user.display_name}",
                        reason="AFK status set.",
                    )

                except (discord.Forbidden, discord.errors.Forbidden):
                    pass

            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content="**You are now AFK!**",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        else:
            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(content="You are already afk.")

    @app_commands.command(name="reset")
    @app_commands.check(_afk_perms)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _afk_reset(self, ctx: discord.Interaction):
        """Resets your AFK status."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if await is_afk(self.bot.pool, user_id=ctx.user.id, guild_id=ctx.guild.id):
            await remove_afk(
                self.bot.pool, user_id=ctx.user.id, guild_id=ctx.guild.id
            )

            if ctx.user.display_name.startswith("[AFK]"):
                try:
                    await ctx.user.edit(
                        nick=ctx.user.display_name[5:], reason="AFK status removed."
                    )

                except (discord.Forbidden, discord.errors.Forbidden):
                    pass

            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content="**Welcome back!** Your AFK status has been removed."
            )

        else:
            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(content="You are not afk.")

    @app_commands.command(name="check")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _afk_check(self, ctx: discord.Interaction, member: discord.Member):
        """Checks if a member is afk."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if await is_afk(self.bot.pool, user_id=member.id, guild_id=ctx.guild.id):
            afk_details = await get_afk_details(
                self.bot.pool, user_id=member.id, guild_id=ctx.guild.id
            )

            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content=f"{member.mention} is afk since <t:{int(datetime.timestamp(afk_details['start']))}:t>."
                f"\n**Reason:** {afk_details['reason'] or 'Unspecified.'}",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        else:
            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content=f"{member.mention} is not afk.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

    @app_commands.command(name="list")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _afk_list(self, ctx: discord.Interaction):
        """Shows a list of members who are afk."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        _afk_members = await get_afk_members(self.bot.pool, ctx.guild.id)

        if _afk_members:
            afk_members = list()

            for index, _member in enumerate(_afk_members, 1):
                member = ctx.guild.get_member(_member[0])

                afk_details = await get_afk_details(
                    self.bot.pool, user_id=member.id, guild_id=ctx.guild.id
                )

                afk_members.append(
                    f"`{index}.` {member.mention} - "
                    f"since <t:{int(datetime.timestamp(afk_details['start']))}:t> - "
                    f"**Reason:** {afk_details['reason'] or 'Unspecified.'}"
                )

            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content="\n".join(afk_members),
                allowed_mentions=discord.AllowedMentions.none(),
            )

        else:
            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(content="No members are afk.")

    @_afk_set.error
    @_afk_reset.error
    async def _afk_perms_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                "I need the **Manage Nicknames** permission in this server "
                "to set your AFK status.",
                ephemeral=True,
            )


async def setup(bot: FumeGuard):
    await bot.add_cog(Afk(bot))
