from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.tools import cooldown_level_0
from utils.db import is_afk, get_afk_details, get_afk_members, set_afk, remove_afk


class Afk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _afk_perms(ctx: discord.Interaction):
        return ctx.guild.me.guild_permissions.manage_nicknames

    @staticmethod
    async def _process_mentions(message: discord.Message):
        for member in message.mentions:
            if await is_afk(user_id=member.id, guild_id=member.guild.id):
                afk_details = await get_afk_details(
                    user_id=member.id, guild_id=member.guild.id
                )

                await message.reply(
                    content=f"{member.mention} is afk since <t:{int(datetime.timestamp(afk_details['start']))}:t>."
                    f"\n**Reason:** {afk_details['reason']}",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.mentions:
            await self._process_mentions(message)

    @app_commands.command(name="afk", description="Sets your afk message.")
    @app_commands.check(_afk_perms)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _afk(self, ctx: discord.Interaction, reason: str = None):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await is_afk(user_id=ctx.user.id, guild_id=ctx.guild.id):
            if reason and len(reason) > 100:
                # noinspection PyUnresolvedReferences
                return await ctx.edit_original_message(
                    content="Your AFK reason must be less than 100 characters."
                )

            try:
                await ctx.user.edit(
                    nick=f"[AFK] {ctx.user.display_name}", reason="AFK set."
                )

            except (discord.Forbidden, discord.errors.Forbidden):
                pass

            await set_afk(
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                reason=reason or "Unspecified.",
            )

            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content="Your AFK status has been set! "
                "**Use this command again to remove it.**"
            )

        else:
            await remove_afk(user_id=ctx.user.id, guild_id=ctx.guild.id)

            if ctx.user.display_name.startswith("[AFK]"):
                try:
                    await ctx.user.edit(
                        nick=ctx.user.display_name[5:], reason="AFK removed."
                    )

                except (discord.Forbidden, discord.errors.Forbidden):
                    pass

            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content="**Welcome back!** Your AFK status has been removed."
            )

    @app_commands.command(name="afklist", description="A list of members who are afk.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _afk_list(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        _afk_members = await get_afk_members(ctx.guild.id)

        if _afk_members:
            afk_members = list()

            for index, _member in enumerate(_afk_members, 1):
                member = ctx.guild.get_member(_member[0])

                afk_details = await get_afk_details(
                    user_id=member.id, guild_id=ctx.guild.id
                )

                afk_members.append(
                    f"`{index}.` {member.mention} - "
                    f"since <t:{int(datetime.timestamp(afk_details['start']))}:t> - "
                    f"**Reason:** {afk_details['reason']}"
                )

            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(
                content="\n".join(afk_members),
                allowed_mentions=discord.AllowedMentions.none(),
            )

        else:
            # noinspection PyUnresolvedReferences
            await ctx.edit_original_response(content="No members are afk.")

    @_afk.error
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


async def setup(bot):
    await bot.add_cog(Afk(bot))
