import discord
from discord import app_commands
from discord.ext import commands

from utils.tools import dynamic_cooldown_x
from utils.db import (
    update_mod_log_channel,
    update_member_log_channel,
    update_welcome_message,
)


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _settings_perms_check(ctx: discord.Interaction):
        return ctx.user.guild_permissions.manage_guild

    @app_commands.command(
        name="setmodlog",
        description="Set the moderation logging channel for the server.",
    )
    @app_commands.check(_settings_perms_check)
    @app_commands.checks.dynamic_cooldown(dynamic_cooldown_x)
    @app_commands.guild_only()
    async def _set_mod_log(
        self, ctx: discord.Interaction, channel: discord.TextChannel
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        await update_mod_log_channel(ctx.guild.id, channel.id)

        await ctx.edit_original_response(
            content=f"The moderation log channel for this server has been set to {channel.mention}."
        )

    @app_commands.command(
        name="setmemberlog",
        description="Set the member join/leave logging channel for the server.",
    )
    @app_commands.check(_settings_perms_check)
    @app_commands.checks.dynamic_cooldown(dynamic_cooldown_x)
    @app_commands.guild_only()
    async def _set_member_log(
        self, ctx: discord.Interaction, channel: discord.TextChannel
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        await update_member_log_channel(ctx.guild.id, channel.id)

        await ctx.edit_original_response(
            content=f"The member join/leave log channel for this server has been set to {channel.mention}."
        )

    @app_commands.command(
        name="setwelcomemsg",
        description="Set the welcome message which will bd DMed to a member joining the server.",
    )
    @app_commands.check(_settings_perms_check)
    @app_commands.checks.dynamic_cooldown(dynamic_cooldown_x)
    @app_commands.guild_only()
    async def _set_welcome_msg(self, ctx: discord.Interaction, *, msg: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if len(msg) > 1500:
            await ctx.edit_original_response(
                content="Welcome message cannot be longer than 1500 characters!"
            )

        await update_welcome_message(ctx.guild.id, msg)

        await ctx.edit_original_response(
            content="The welcome message for this server has been set."
        )

    @_set_mod_log.error
    @_set_member_log.error
    @_set_welcome_msg.error
    async def _settings_perms_check_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                "You do not have permissions to execute this command."
                "\n **Required Permission** : *Manage Server*",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Settings(bot))
