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
    member: [discord.Member, discord.User],
    moderator: discord.Member,
    action: str,
    reason: str = None,
    channel=None,
):
    channel_id = await get_mod_log_channel(ctx.guild.id)

    if not channel_id:
        return

    else:
        channel_id = int(channel_id)

    case_num = await get_case_id(ctx.guild.id)

    embed = discord.Embed(
        colour=discord.Colour.green()
        if action.lower() in ["unban", "unmute", "channel unmute"]
        else discord.Colour.red()
    )

    embed.title = f"{action} | Case {case_num}"

    embed.add_field(name="Name", value=f"**{member}** ({member.mention})", inline=False)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(
        name="Moderator", value=f"**{moderator}** ({moderator.mention})", inline=False
    )

    if channel:
        embed.add_field(name="Channel", value=channel.mention, inline=False)

    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)

    await update_case_id(ctx.guild.id)

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
