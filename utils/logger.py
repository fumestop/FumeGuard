import discord

from utils.db import (
    get_mod_log_channel,
    get_member_log_channel,
    get_case_id,
    update_case_id,
    get_welcome_message,
)


async def log_member(member: discord.Member, join: bool = True):
    channel_id = await get_member_log_channel(member.guild.id)

    if not channel_id:
        return

    else:
        channel_id = int(channel_id)

    embed = discord.Embed(
        colour=discord.Colour.green() if join else discord.Colour.red()
    )

    embed.title = "Member Joined" if join else "Member Left"

    embed.add_field(name="Name", value=f"**{member}** ({member.mention})", inline=False)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Member Count", value=member.guild.member_count, inline=False)

    channel = member.guild.get_channel(channel_id)

    if not channel:
        return

    await channel.send(embed=embed)


async def log_mod_action(
    ctx: discord.Interaction,
    moderator: discord.Member,
    action: str,
    member: [discord.Member, discord.User] = None,
    channel=None,
    reason: str = None,
    message_count: int = None,
    color: str = None,
):
    channel_id = await get_mod_log_channel(ctx.guild.id)

    if not channel_id:
        return

    case_num = await get_case_id(ctx.guild.id)

    _color = getattr(discord.Color, color) if color else None
    embed = discord.Embed(color=_color() or discord.Colour.blurple())

    embed.title = f"{action} | Case {case_num}"

    if member:
        embed.add_field(
            name="Name", value=f"**{member}** ({member.mention})", inline=False
        )
        embed.add_field(name="ID", value=member.id, inline=False)

    embed.add_field(
        name="Moderator", value=f"**{moderator}** ({moderator.mention})", inline=False
    )

    if channel:
        embed.add_field(name="Channel", value=channel.mention, inline=False)

    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)

    if message_count:
        embed.add_field(name="Message Count", value=message_count, inline=False)

    await update_case_id(ctx.guild.id)

    channel = ctx.guild.get_channel(channel_id)

    if not channel:
        return

    await channel.send(embed=embed)


async def log_role_action(
    ctx: discord.Interaction,
    role: discord.Role,
    moderator: discord.Member,
    action: str,
    member: discord.Member = None,
):
    channel_id = await get_mod_log_channel(ctx.guild.id)

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
        name="Moderator", value=f"**{moderator}** ({moderator.mention})", inline=False
    )

    channel = ctx.guild.get_channel(channel_id)

    if not channel:
        return

    await channel.send(embed=embed)


async def welcome_member(member: discord.Member):
    welcome_msg = await get_welcome_message(member.guild.id)

    if not welcome_msg:
        return

    try:
        await member.send(welcome_msg)

    except (discord.Forbidden, discord.errors.Forbidden):
        pass
