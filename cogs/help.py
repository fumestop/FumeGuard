from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0

if TYPE_CHECKING:
    from bot import FumeGuard


class Help(commands.Cog):
    def __init__(self, bot: FumeGuard):
        self.bot: FumeGuard = bot

    @app_commands.command(name="help")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _help(self, ctx: discord.Interaction):
        """Shows a list of all the commands provided by FumeGuard."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Command List"
        embed.description = 'Here"s a list of available commands: '

        embed.add_field(
            name="General",
            value=f"`ping`, `web`, `invite`, `vote`, `review`, `community`",
            inline=False,
        )

        embed.add_field(
            name="Afk",
            value=f"`afk set`, `afk reset`, `afk check`, `afk list`",
            inline=False,
        )

        embed.add_field(
            name="Moderation",
            value=f"`kick`, `ban`, `unban`, `mute`, `unmute`, `channelmute`, "
            f"`channelunmute`, `warn`, `clear`, `announce`",
            inline=False,
        )

        embed.add_field(
            name="Roles",
            value=f"`role create`, `role add`, `role remove`, `role delete`",
            inline=False,
        )

        embed.add_field(
            name="Settings",
            value=f"`set mod_log`, `set member_log`, `set welcome_message`",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)


async def setup(bot: FumeGuard):
    await bot.add_cog(Help(bot))
