import discord
from discord import app_commands
from discord.ext import commands

from utils.tools import cooldown_level_0


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help", description="A list of all the commands provided by FumeGuard."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _help(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        embed = discord.Embed(colour=self.bot.embed_colour)

        embed.title = "Command List"

        embed.description = 'Here"s a list of available commands: '

        embed.add_field(
            name="General",
            value=f"`ping`, `web`, `invite`, `vote`, `community`",
            inline=False,
        )

        embed.add_field(
            name="Afk",
            value=f"`afk`, `afklist`",
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
            value=f"`newrole`, `addrole`, `removerole`, `deleterole`",
            inline=False,
        )

        embed.add_field(
            name="Settings",
            value=f"`setmodlog`, `setuserlog`, `setwelcomemsg`",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
