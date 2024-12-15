from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_1
from utils.db import (
    get_mod_log_channel,
    get_welcome_message,
    get_member_log_channel,
    update_mod_log_channel,
    update_welcome_message,
    update_member_log_channel,
)
from utils.checks import settings_perms_check
from utils.logger import log_mod_action
from utils.modals import WelcomeMessageModal

if TYPE_CHECKING:
    from bot import FumeGuard


@app_commands.guild_only()
class Settings(
    commands.GroupCog,
    group_name="set",
    group_description="Commands to manage server-specific settings for FumeGuard.",
):
    def __init__(self, bot: FumeGuard):
        self.bot: FumeGuard = bot

    @app_commands.command(name="mod_log")
    @app_commands.check(settings_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    async def _set_mod_log(
        self, ctx: discord.Interaction, channel: Optional[discord.TextChannel] = None
    ):
        """Set the moderation logging channel for the server.

        Parameters
        ----------
        channel : Optional[discord.TextChannel]
            The channel to set as the moderation logging channel. Leave blank to disable.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        mod_log_channel = await get_mod_log_channel(self.bot.pool, ctx.guild.id)

        if not channel and not mod_log_channel:
            return await ctx.edit_original_response(
                content="No moderation log channel is set for this server."
            )

        elif channel and mod_log_channel == channel.id:
            return await ctx.edit_original_response(
                content=f"The moderation log channel for this server is already set to {channel.mention}."
            )

        else:
            if not channel:
                await log_mod_action(
                    ctx=ctx,
                    moderator=ctx.user,
                    action="Logging Channel Disabled",
                    description="Moderation logging channel has been disabled.",
                    color="red",
                )

                await update_mod_log_channel(self.bot.pool, guild_id=ctx.guild.id)

                return await ctx.edit_original_response(
                    content="The moderation log channel for this server has been disabled."
                )

            else:
                if not channel.permissions_for(ctx.guild.me).send_messages:
                    return await ctx.edit_original_response(
                        content=f"I do not have permissions to send messages in {channel.mention}."
                    )

                await update_mod_log_channel(
                    self.bot.pool, guild_id=ctx.guild.id, channel_id=channel.id
                )

                await ctx.edit_original_response(
                    content=f"The moderation log channel for this server has been set to {channel.mention}."
                )
                return await log_mod_action(
                    ctx=ctx,
                    moderator=ctx.user,
                    action="Logging Channel Updated",
                    description=f"Moderation logging channel updated to {channel.mention}.",
                    color="green",
                )

    @app_commands.command(name="member_log")
    @app_commands.check(settings_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    async def _set_member_log(
        self, ctx: discord.Interaction, channel: Optional[discord.TextChannel] = None
    ):
        """Set the member join/leave logging channel for the server.

        Parameters
        ----------
        channel : Optional[discord.TextChannel]
            The channel to set as the member logging channel.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        member_log_channel = await get_member_log_channel(
            self.bot.pool, ctx.guild.id
        )

        if not channel and not member_log_channel:
            return await ctx.edit_original_response(
                content="No member log channel is set for this server."
            )

        elif channel and member_log_channel == channel.id:
            return await ctx.edit_original_response(
                content=f"The member logging channel for this server is already set to {channel.mention}."
            )

        else:
            if not channel:
                await update_member_log_channel(self.bot.pool, guild_id=ctx.guild.id)

                await ctx.edit_original_response(
                    content="The member logging channel for this server has been disabled."
                )
                return await log_mod_action(
                    ctx=ctx,
                    moderator=ctx.user,
                    action="Logging Channel Disabled",
                    description="Member logging channel has been disabled.",
                    color="red",
                )

            else:
                if not channel.permissions_for(ctx.guild.me).send_messages:
                    return await ctx.edit_original_response(
                        content=f"I do not have permissions to send messages in {channel.mention}."
                    )

                await update_member_log_channel(
                    self.bot.pool, guild_id=ctx.guild.id, channel_id=channel.id
                )

                await ctx.edit_original_response(
                    content=f"The member logging channel for this server has been set to {channel.mention}."
                )
                return await log_mod_action(
                    ctx=ctx,
                    moderator=ctx.user,
                    action="Logging Channel Updated",
                    description=f"Member logging channel updated to {channel.mention}.",
                    color="green",
                )

    @app_commands.command(
        name="welcome_message",
        description="Set the welcome message which will bd DMed to a member joining the server.",
    )
    @app_commands.check(settings_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    async def _set_welcome_message(self, ctx: discord.Interaction):
        """Set the welcome message for the server."""
        welcome_message = await get_welcome_message(self.bot.pool, ctx.guild.id)

        modal = WelcomeMessageModal()
        modal.ctx = ctx
        modal.message.default = welcome_message

        # noinspection PyUnresolvedReferences
        await ctx.response.send_modal(modal)
        await modal.wait()

        if not modal.message.value and not welcome_message:
            return await ctx.edit_original_response(
                content="No welcome message is set for this server."
            )

        elif modal.message.value and welcome_message == modal.message.value:
            return await ctx.edit_original_response(
                content=f"The welcome message for the server is already set to the message you entered."
            )

        else:
            if not modal.message.value:
                await update_welcome_message(self.bot.pool, guild_id=ctx.guild.id)

                await ctx.edit_original_response(
                    content="The welcome message for this server has been disabled."
                )
                return await log_mod_action(
                    ctx=ctx,
                    moderator=ctx.user,
                    action="Welcome Message Disabled",
                    description="Welcome message has been disabled.",
                    color="red",
                )

            else:
                await update_welcome_message(
                    self.bot.pool, guild_id=ctx.guild.id, message=modal.message.value
                )

                await ctx.edit_original_response(
                    content="The welcome message for this server has been set."
                )
                return await log_mod_action(
                    ctx=ctx,
                    moderator=ctx.user,
                    action="Welcome Message Updated",
                    description="Welcome message has been updated.",
                    color="green",
                )


async def setup(bot: FumeGuard):
    await bot.add_cog(Settings(bot))
