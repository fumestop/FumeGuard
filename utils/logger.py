from __future__ import annotations

from typing import Optional

import discord
import aiomysql

from utils.db import (
    get_case_number,
    get_mod_log_channel,
    get_welcome_message,
    increment_case_number,
    get_member_log_channel,
)


async def log_mod_action(
    ctx: discord.Interaction,
    moderator: discord.Member,
    action: str,
    description: Optional[str] = None,
    member: Optional[discord.Member, discord.User] = None,
    channel: Optional[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.ForumChannel,
    ] = None,
    reason: Optional[str] = None,
    message_count: Optional[int] = None,
    color: Optional[str] = None,
) -> None:
    channel_id = await get_mod_log_channel(ctx.client.pool, ctx.guild.id)

    if not channel_id:
        return

    case_num = await get_case_number(ctx.client.pool, ctx.guild.id)

    _color = getattr(discord.Color, color) if color else None
    embed = discord.Embed(
        color=_color() or discord.Colour.from_str(ctx.client.config.EMBED_COLOR)
    )

    embed.title = f"{action} | Case {case_num}"

    if description:
        embed.description = description

    if member:
        embed.add_field(
            name="Name", value=f"**{member}** ({member.mention})", inline=False
        )
        embed.add_field(name="ID", value=member.id, inline=False)

    embed.add_field(
        name="Moderator",
        value=f"**{moderator}** ({moderator.mention})",
        inline=False,
    )

    if channel:
        embed.add_field(name="Channel", value=channel.mention, inline=False)

    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)

    if message_count:
        embed.add_field(name="Message Count", value=message_count, inline=False)

    await increment_case_number(ctx.client.pool, ctx.guild.id)

    channel = ctx.guild.get_channel(channel_id)

    if not channel:
        return

    await channel.send(embed=embed)


async def log_member(
    pool: aiomysql.Pool, member: discord.Member, join: Optional[bool] = True
) -> None:
    channel_id = await get_member_log_channel(pool, member.guild.id)

    if not channel_id:
        return

    else:
        channel_id = int(channel_id)

    embed = discord.Embed(
        colour=discord.Colour.green() if join else discord.Colour.red()
    )

    embed.title = "Member Joined" if join else "Member Left"

    embed.add_field(
        name="Name", value=f"**{member}** ({member.mention})", inline=False
    )
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(
        name="Member Count", value=member.guild.member_count, inline=False
    )

    channel = member.guild.get_channel(channel_id)

    if not channel:
        return

    await channel.send(embed=embed)


async def log_role_action(
    ctx: discord.Interaction,
    role: discord.Role,
    moderator: discord.Member,
    action: str,
    member: Optional[discord.Member] = None,
    reason: Optional[str] = None,
) -> None:
    channel_id = await get_mod_log_channel(ctx.client.pool, ctx.guild.id)

    if not channel_id:
        return

    embed = discord.Embed(color=role.color)

    embed.title = f"{action}"

    embed.add_field(
        name="Role Name", value=f"**{role}** ({role.mention})", inline=False
    )

    if member:
        embed.add_field(
            name="Member", value=f"**{member}** ({member.mention})", inline=False
        )

    embed.add_field(
        name="Moderator",
        value=f"**{moderator}** ({moderator.mention})",
        inline=False,
    )

    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)

    channel = ctx.guild.get_channel(channel_id)

    if not channel:
        return

    await channel.send(embed=embed)


async def welcome_member(pool: aiomysql.Pool, member: discord.Member) -> None:
    welcome_message = await get_welcome_message(pool, member.guild.id)

    if not welcome_message:
        return

    try:
        await member.send(welcome_message)

    except (discord.Forbidden, discord.errors.Forbidden):
        pass
