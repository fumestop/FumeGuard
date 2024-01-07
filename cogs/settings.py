import discord
from discord import app_commands
from discord.ext import commands

from utils.tools import cooldown_level_1
from utils.logger import log_mod_action
from utils.db import (
    get_mod_log_channel,
    update_mod_log_channel,
    get_member_log_channel,
    update_member_log_channel,
    get_welcome_message,
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
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _set_mod_log(
        self, ctx: discord.Interaction, channel: discord.TextChannel
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        mod_log_channel = get_mod_log_channel(ctx.guild.id)

        if mod_log_channel and mod_log_channel == channel.id:
            return await ctx.edit_original_response(
                content=f"The moderation log channel for this server is already set to {channel.mention}."
            )

        await update_mod_log_channel(guild_id=ctx.guild.id, channel_id=channel.id)
        await log_mod_action(
            ctx=ctx,
            moderator=ctx.user,
            action=f"Moderation logging channel updated to {channel.mention}.",
            color="green",
        )

        await ctx.edit_original_response(
            content=f"The moderation log channel for this server has been set to {channel.mention}."
        )

    @app_commands.command(
        name="setmemberlog",
        description="Set the member join/leave logging channel for the server.",
    )
    @app_commands.check(_settings_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _set_member_log(
        self, ctx: discord.Interaction, channel: discord.TextChannel
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        member_log_channel = get_member_log_channel(ctx.guild.id)

        if member_log_channel and member_log_channel == channel.id:
            return await ctx.edit_original_response(
                content=f"The member logging channel for this server is already set to {channel.mention}."
            )

        await update_member_log_channel(guild_id=ctx.guild.id, channel_id=channel.id)
        await log_mod_action(
            ctx=ctx,
            moderator=ctx.user,
            action=f"Member logging channel updated to {channel.mention}.",
            color="green",
        )

        await ctx.edit_original_response(
            content=f"The member logging channel for this server has been set to {channel.mention}."
        )

    @app_commands.command(
        name="setwelcomemsg",
        description="Set the welcome message which will bd DMed to a member joining the server.",
    )
    @app_commands.check(_settings_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _set_welcome_msg(self, ctx: discord.Interaction, message: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        welcome_msg = get_welcome_message(ctx.guild.id)

        if welcome_msg and welcome_msg == message:
            return await ctx.edit_original_response(
                content=f"The welcome message for this server is already set to {message}."
            )

        if len(message) > 1500:
            await ctx.edit_original_response(
                content="Welcome message cannot be longer than 1500 characters!"
            )

        await update_welcome_message(guild_id=ctx.guild.id, message=message)
        await log_mod_action(
            ctx=ctx,
            moderator=ctx.user,
            action=f"Welcome message updated.",
            color="green",
        )

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
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(Settings(bot))
