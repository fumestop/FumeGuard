from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.logger import log_mod_action
from utils.cd import cooldown_level_0
from utils.modals import AnnouncementModal
from utils.checks import (
    kick_perms_check,
    ban_perms_check,
    mute_perms_check,
    channel_mute_perms_check,
    warn_perms_check,
    clear_perms_check,
)

if TYPE_CHECKING:
    from bot import FumeGuard


class Moderation(commands.Cog):
    def __init__(self, bot: FumeGuard):
        self.bot: FumeGuard = bot

    @app_commands.command(name="kick")
    @app_commands.check(kick_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _kick(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = None,
    ):
        """Kick a member from the server.

        Parameters
        ----------
        member: discord.Member
            The member to kick from the server.
        reason: Optional[str]
            The reason for kicking the member.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot kick **{member}**. "
                f"Make sure you have a role higher than the member "
                f"you are trying to kick."
            )

        try:
            await member.kick(reason=reason)

        except (discord.Forbidden, discord.errors.Forbidden):
            return await ctx.edit_original_response(
                content="I do not have permission to kick that user. "
                "Please make sure I have a role higher than the member "
                "you are trying to kick."
            )

        await ctx.edit_original_response(
            content=f"**{member}** has been kicked from the server!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Kicked",
            reason=reason,
            color="red",
        )

    @app_commands.command(name="ban")
    @app_commands.check(ban_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _ban(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        delete_message_days: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        """Ban a member from the server.

        Parameters
        ----------
        member: discord.Member
            The member to ban from the server.
        delete_message_days: Optional[int]
            The number of days of messages to delete sent by the member.
        reason: Optional[str]
            The reason for banning the member.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot ban **{member}**. "
                f"Make sure you have a role higher than the member "
                f"you are trying to ban."
            )

        try:
            await member.ban(reason=reason, delete_message_days=delete_message_days)

        except (discord.Forbidden, discord.errors.Forbidden):
            return await ctx.edit_original_response(
                content="I do not have permission to ban that user. "
                "Please make sure I have a role higher than the member "
                "you are trying to ban."
            )

        await ctx.edit_original_response(
            content=f"**{member}** has been banned from the server!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Banned",
            reason=reason,
            color="red",
        )

    @app_commands.command(name="unban")
    @app_commands.check(ban_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _unban(
        self, ctx: discord.Interaction, member: str, reason: Optional[str] = None
    ):
        """Unban a previously banned member in the server.

        Parameters
        ----------
        member: str
            The name of the member to unban.
        reason: Optional[str]
            The reason for unbanning the member.

        """

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        try:
            member = int(member)

        except ValueError:
            pass

        async for ban_entry in ctx.guild.bans():
            user = ban_entry.user

            if isinstance(member, str):
                if user.name == member:
                    await ctx.guild.unban(user, reason=reason)

                    await ctx.edit_original_response(
                        content=f"**{member}** has been unbanned!"
                    )

                    return await log_mod_action(
                        ctx=ctx,
                        member=user,
                        moderator=ctx.user,
                        action="Member Unbanned",
                        reason=reason,
                    )

            elif isinstance(member, int):
                try:
                    member = await self.bot.fetch_user(member)

                except discord.errors.NotFound:
                    break

                if user == member:
                    await ctx.guild.unban(user, reason=reason)

                    await ctx.edit_original_response(
                        content=f"**{member}** has been unbanned!"
                    )
                    return await log_mod_action(
                        ctx=ctx,
                        member=user,
                        moderator=ctx.user,
                        action="Member Unbanned",
                        reason=reason,
                        color="green",
                    )

            else:
                continue

        else:
            await ctx.edit_original_response(content="No such banned user found.")

    @app_commands.command(name="mute")
    @app_commands.check(mute_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _mute(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        minutes: Optional[int] = None,
        hours: Optional[int] = None,
        days: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        """Timeout a member in the server.

        Parameters
        ----------
        member: discord.Member
            The member to timeout in the server.

        minutes: Optional[int]
            The number of minutes for which the member should be timed out.
        hours: Optional[int]
            The number of hours for which the member should be timed out.
        days: Optional[int]
            The number of days for which the member should be timed out.
        reason: Optional[str]
            The reason for timing out the member.
        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot mute **{member}**. Make sure you have a role "
                f"higher than the person you are trying to timeout."
            )

        await member.timeout(
            datetime.timedelta(minutes=minutes, hours=hours, days=days),
            reason=reason,
        )

        await ctx.edit_original_response(
            content=f"**{member}** has been timed out in the server!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Muted",
            reason=reason,
            color="red",
        )

    @app_commands.command(name="unmute")
    @app_commands.check(mute_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _unmute(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = None,
    ):
        """Remove the timeout for a member in the server.

        Parameters
        ----------
        member: discord.Member
            The member to remove the timeout for.
        reason: Optional[str]
            The reason for removing the timeout.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        await member.timeout(None, reason=reason)

        await ctx.edit_original_response(
            content=f"**{member}** has been unmuted in the server!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Unmuted",
            reason=reason,
            color="green",
        )

    @app_commands.command(name="channelmute")
    @app_commands.check(channel_mute_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _channel_mute(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        channel: Optional[discord.TextChannel] = None,
        reason: Optional[str] = None,
    ):
        """Mute a member in a channel.

        Parameters
        ----------
        member: discord.Member
            The member to mute in the channel.
        channel: Optional[discord.TextChannel]
            The channel to mute the member in. If not provided, the current channel is used.
        reason: Optional[str]
            The reason for muting the member.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot mute **{member}**. "
                f"Make sure you have a role higher than the member "
                f"you are trying to mute."
            )

        channel = channel or ctx.channel

        if not channel.permissions_for(member).send_messages:
            return await ctx.edit_original_response(
                content=f"****{member}**** is already muted in {channel.mention}."
            )

        try:
            await channel.set_permissions(
                member, read_messages=True, send_messages=False
            )

        except (discord.Forbidden, discord.errors.Forbidden):
            return await ctx.edit_original_response(
                content=f"I do not have the permission to "
                f"manage permissions for {channel.mention}."
            )

        await ctx.edit_original_response(
            content=f"**{member}** has been muted in {channel.mention}!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Channel Muted",
            reason=reason,
            channel=channel,
            color="red",
        )

    @app_commands.command(name="channelunmute")
    @app_commands.check(channel_mute_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _channel_unmute(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        channel: Optional[discord.TextChannel],
        reason: Optional[str] = None,
    ):
        """Unmute a member in a channel.

        Parameters
        ----------
        member: discord.Member
            The member to unmute in the channel.
        channel: Optional[discord.TextChannel]
            The channel to unmute the member in. If not provided, the current channel is used.
        reason: Optional[str]
            The reason for unmuting the member.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        channel = channel or ctx.channel

        if channel.permissions_for(member).send_messages:
            return await ctx.edit_original_response(
                content=f"****{member}**** is not muted in {channel.mention} yet."
            )

        try:
            await channel.set_permissions(member, overwrite=None)

        except (discord.Forbidden, discord.errors.Forbidden):
            return await ctx.edit_original_response(
                content=f"I do not have the permission to "
                f"manage permissions for {channel.mention}."
            )

        await ctx.edit_original_response(
            content=f"**{member}** has been unmuted in {channel.mention}!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Channel Unmuted",
            reason=reason,
            channel=channel,
            color="green",
        )

    @app_commands.command(name="warn")
    @app_commands.check(warn_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _warn(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = None,
    ):
        """Issue a warning to a member.

        Parameters
        ----------
        member: discord.Member
            The member to issue a warning to.
        reason: str
            The reason for issuing the warning.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot warn **{member}**. Make sure you have a role "
                f"higher than the member you are trying to warn."
            )

        try:
            await member.send(
                f"{member.mention} - You have been warned by **{ctx.user}** with reason *{reason}*!"
            )

        except (discord.errors.Forbidden, discord.Forbidden):
            pass

        await ctx.edit_original_response(content=f"**{member}** has been warned!")
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Warned",
            reason=reason,
            color="red",
        )

    @app_commands.command(name="clear")
    @app_commands.check(clear_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _clear(self, ctx: discord.Interaction, amount: int):
        """Clear messages from the channel.

        Parameters
        ----------
        amount: int
            The number of messages to clear from the channel (between 1 and 100).

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if 1 <= amount <= 100:
            try:
                await ctx.delete_original_response()
                await ctx.channel.purge(
                    limit=amount,
                    reason=f"{amount} messages cleared by {ctx.user.name}",
                )

            except (discord.Forbidden, discord.errors.Forbidden):
                return await ctx.edit_original_response(
                    content="I do not have permission to delete messages in this channel."
                )

            await ctx.channel.send(content="\U00002705", delete_after=5)
            await log_mod_action(
                ctx=ctx,
                moderator=ctx.user,
                channel=ctx.channel,
                action="Messages Cleared",
                message_count=amount,
                color="red",
            )

        else:
            return await ctx.edit_original_response(
                content=f"The number of messages can be between 1 and 100 only."
            )

    @app_commands.command(name="announce")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    @app_commands.choices(
        mention=[
            app_commands.Choice(name="everyone", value="everyone"),
            app_commands.Choice(name="here", value="here"),
            app_commands.Choice(name="none", value="none"),
        ]
    )
    async def _announce(
        self,
        ctx: discord.Interaction,
        channel: discord.TextChannel,
        mention: app_commands.Choice[str],
    ):
        if channel.permissions_for(ctx.guild.me).send_messages:
            modal = AnnouncementModal()
            modal.ctx = ctx

            # noinspection PyUnresolvedReferences
            await ctx.response.send_modal(modal)
            await modal.wait()

            if mention.value == "everyone":
                message = f"@everyone {modal.message.value}"

            elif mention.value == "here":
                message = f"@here {modal.message.value}"

            else:
                message = modal.message.value

            await channel.send(message)
            await modal.interaction.edit_original_response(
                content=f"The announcement has been made in {channel.mention}."
            )

        else:
            # noinspection PyUnresolvedReferences
            await ctx.response.send_message(
                content=f"I do not have permission to send messages in {channel.mention}."
            )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
