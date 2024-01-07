import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.logger import log_mod_action
from utils.tools import cooldown_level_0


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _kick_perms_check(ctx: discord.Interaction):
        return ctx.guild.me.guild_permissions.kick_members

    @staticmethod
    def _ban_perms_check(ctx: discord.Interaction):
        return ctx.guild.me.guild_permissions.ban_members

    @staticmethod
    def _clear_perms_check(ctx: discord.Interaction):
        return ctx.guild.me.guild_permissions.manage_messages

    @staticmethod
    def _moderate_members_perms_check(ctx: discord.Interaction):
        return ctx.guild.me.guild_permissions.moderate_members

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.check(_kick_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _kick(
        self, ctx: discord.Interaction, member: discord.Member, reason: str = None
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.kick_members:
            return await ctx.edit_original_response(
                content="You need the **Kick Members** permission in this server "
                "to execute this action."
            )

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

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.check(_ban_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _ban(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        delete_message_days: int = None,
        reason: str = None,
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.ban_members:
            return await ctx.edit_original_response(
                content="You need the **Ban Members** permission in this server "
                "to execute this action."
            )

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

    @app_commands.command(
        name="unban", description="Unban a previously banned member in the server."
    )
    @app_commands.check(_ban_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _unban(self, ctx: discord.Interaction, member: str, reason: str = None):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.ban_members:
            return await ctx.edit_original_response(
                content="You need the **Ban Members** permission in this server "
                "to execute this action."
            )

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

    @app_commands.command(name="mute", description="Timeout a member in the server.")
    @app_commands.check(_moderate_members_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _mute(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        minutes: int = None,
        hours: int = None,
        days: int = None,
        reason: str = None,
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.moderate_members:
            return await ctx.edit_original_response(
                content="You need the **Moderate Members** permission "
                "in this server to execute this action."
            )

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot mute **{member}**. Make sure you have a role "
                f"higher than the person you are trying to timeout."
            )

        await member.timeout(
            datetime.timedelta(minutes=minutes, hours=hours, days=days), reason=reason
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

    @app_commands.command(
        name="unmute", description="Remove the timeout for a member in the server."
    )
    @app_commands.check(_moderate_members_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _unmute(
        self, ctx: discord.Interaction, member: discord.Member, reason: str = None
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.moderate_members:
            return await ctx.edit_original_response(
                content="You need the **Moderate Members** permission "
                "in this server to execute this action."
            )

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

    @app_commands.command(
        name="channel_mute", description="Mute a member in the channel."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _channel_mute(
        self, ctx: discord.Interaction, member: discord.Member, reason: str = None
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.moderate_members:
            return await ctx.edit_original_response(
                content="You need the **Moderate Members** permission "
                "in this server to execute this action."
            )

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot mute **{member}**. "
                f"Make sure you have a role higher than the member "
                f"you are trying to mute."
            )

        if not ctx.channel.permissions_for(member).send_messages:
            return await ctx.edit_original_response(
                content=f"****{member}**** is already muted in this channel."
            )

        try:
            await ctx.message.channel.set_permissions(
                member, read_messages=True, send_messages=False
            )

        except (discord.Forbidden, discord.errors.Forbidden):
            return await ctx.edit_original_response(
                content="I do not have the permission to manage permissions "
                "for this channel. "
            )

        await ctx.edit_original_response(
            content=f"**{member}** has been muted in this channel!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Channel Muted",
            reason=reason,
            channel=ctx.channel,
            color="red",
        )

    @app_commands.command(
        name="channel_unmute", description="Unmute a member in the channel"
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _channel_unmute(
        self, ctx: discord.Interaction, member: discord.Member, reason: str = None
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.moderate_members:
            return await ctx.edit_original_response(
                content="You need the **Moderate Members** permission "
                "in this server to execute this action."
            )

        if ctx.channel.permissions_for(member).send_messages:
            return await ctx.edit_original_response(
                content=f"****{member}**** is not muted in this channel yet."
            )

        try:
            await ctx.message.channel.set_permissions(member, overwrite=None)

        except (discord.Forbidden, discord.errors.Forbidden):
            return await ctx.edit_original_response(
                content="I do not have the permission to manage permissions "
                "for this channel. "
            )

        await ctx.edit_original_response(
            content=f"**{member}** has been unmuted in this channel!"
        )
        await log_mod_action(
            ctx=ctx,
            member=member,
            moderator=ctx.user,
            action="Member Channel Unmuted",
            reason=reason,
            channel=ctx.channel,
            color="green",
        )

    @app_commands.command(name="warn", description="Issue a warning to a member.")
    @app_commands.check(_kick_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _warn(
        self, ctx: discord.Interaction, member: discord.Member, reason: str = None
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user == ctx.guild.owner and member.top_role > ctx.user.top_role:
            return await ctx.edit_original_response(
                content=f"You cannot warn **{member}**. "
                f"Make sure you have a role higher than the member "
                f"you are trying to warn."
            )

        try:
            await member.create_dm()
            await member.send(
                f"{member.mention} You have been warned by {ctx.user} with reason {reason}!"
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

    @app_commands.command(
        name="clear",
        description="Clear messages from the channel (maximum 100)",
    )
    @app_commands.check(_clear_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _clear(self, ctx: discord.Interaction, amount: int):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if amount in list(range(1, 101)):
            try:
                await ctx.delete_original_response()
                await ctx.channel.purge(
                    limit=amount, reason=f"{amount} messages cleared by {ctx.user}"
                )

            except (discord.Forbidden, discord.errors.Forbidden):
                return await ctx.edit_original_response(
                    content="I do not have permission to delete messages "
                    "in this channel. Please look for any channel-specific "
                    "overwrites and try again."
                )

            await ctx.channel.send("\U00002705", delete_after=5)

            await log_mod_action(
                ctx=ctx,
                moderator=ctx.user,
                action="Messages Cleared",
                reason=f"{amount} messages cleared",
                color="red",
            )

        else:
            return await ctx.edit_original_response(
                content=f"The number of messages can be between 1 and 100 only."
            )

    @app_commands.command(
        name="announce", description="Make an announcement in a channel."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _announce(
        self,
        ctx: discord.Interaction,
        channel: discord.TextChannel,
        mention: str,
        message: str,
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.user.guild_permissions.manage_guild:
            return await ctx.edit_original_response(
                content="You need the **Manage Server** permission in this server "
                "to execute this action."
            )

        if channel.permissions_for(ctx.guild.me).send_messages:
            if mention == "everyone":
                message = "@everyone " + message

            elif mention == "here":
                message = "@here " + message

            else:
                message = mention + " " + message

            await channel.send(message)
            await ctx.delete_original_response()

        else:
            await ctx.edit_original_response(
                content="I am missing the **Send Messages** permission "
                "in the channel you are trying to announce. "
                "Please give me the requisite permission and try again."
            )

    @_kick.error
    @_warn.error
    async def _kick_perms_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                "I need the **Kick Members** permission in this server "
                "to execute this action."
            )

    @_ban.error
    @_unban.error
    async def _ban_perms_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                "I need the **Ban Members** permission in this server "
                "to execute this action."
            )

    @_clear.error
    async def _clear_perms_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                "I need the **Manage Messages** permission in this server "
                "to execute this action."
            )

    @_mute.error
    @_unmute.error
    @_channel_mute.error
    @_channel_unmute.error
    async def _moderate_perms_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                "I need the **Moderate Members** permission in this server "
                "to execute this action."
            )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
