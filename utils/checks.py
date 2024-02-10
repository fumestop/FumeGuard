from __future__ import annotations

import discord
from discord import app_commands


def afk_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.guild.me.guild_permissions.manage_nicknames:
        raise app_commands.CheckFailure(
            "I need the **Manage Nicknames** permission in this server "
            "to perform this action."
        )

    return True


def kick_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.guild.me.guild_permissions.kick_members:
        raise app_commands.CheckFailure(
            "I need the **Kick Members** permission in this server "
            "to perform this action."
        )

    if not ctx.user.guild_permissions.kick_members:
        raise app_commands.CheckFailure(
            "You need the **Kick Members** permission in this server "
            "to perform this action."
        )

    return True


def ban_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.guild.me.guild_permissions.ban_members:
        raise app_commands.CheckFailure(
            "I need the **Ban Members** permission in this server "
            "to perform this action."
        )

    if not ctx.user.guild_permissions.ban_members:
        raise app_commands.CheckFailure(
            "You need the **Ban Members** permission in this server "
            "to perform this action."
        )

    return True


def mute_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.guild.me.guild_permissions.moderate_members:
        raise app_commands.CheckFailure(
            "I need the **Moderate Members** permission in this server "
            "to perform this action."
        )

    if not ctx.user.guild_permissions.moderate_members:
        raise app_commands.CheckFailure(
            "You need the **Moderate Members** permission in this server "
            "to perform this action."
        )

    return True


def channel_mute_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.user.guild_permissions.moderate_members:
        raise app_commands.CheckFailure(
            "You need the **Moderate Members** permission in this server "
            "to perform this action."
        )

    return True


def warn_perms_check(ctx: discord.Interaction) -> bool:
    if (
        not ctx.user.guild_permissions.kick_members
        or not ctx.user.guild_permissions.ban_members
    ):
        raise app_commands.CheckFailure(
            "You need the **Kick Members** or **Ban Members** permission in this server "
            "to perform this action."
        )

    return True


def clear_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.guild.me.guild_permissions.manage_messages:
        raise app_commands.CheckFailure(
            "I need the **Manage Messages** permission in this server "
            "to perform this action."
        )

    if not ctx.user.guild_permissions.manage_messages:
        raise app_commands.CheckFailure(
            "You need the **Manage Messages** permission in this server "
            "to perform this action."
        )

    return True


def announce_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.user.guild_permissions.manage_guild:
        raise app_commands.CheckFailure(
            "You need the **Manage Server** permission in this server "
            "to perform this action."
        )

    return True


def roles_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.guild.me.guild_permissions.manage_roles:
        raise app_commands.CheckFailure(
            "I need the **Manage Roles** permission in this server "
            "to perform this action."
        )

    if not ctx.user.guild_permissions.manage_roles:
        raise app_commands.CheckFailure(
            "You need the **Manage Roles** permission in this server "
            "to perform this action."
        )

    return True


def settings_perms_check(ctx: discord.Interaction) -> bool:
    if not ctx.user.guild_permissions.manage_guild:
        raise app_commands.CheckFailure(
            "You need the **Manage Server** permission in this server "
            "to perform this action."
        )

    return True
