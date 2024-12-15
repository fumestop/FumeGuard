from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0
from utils.checks import roles_perms_check
from utils.logger import log_role_action
from utils.modals import RoleColorModal

if TYPE_CHECKING:
    from bot import FumeGuard


@app_commands.guild_only()
class Roles(
    commands.GroupCog,
    group_name="role",
    group_description="Various commands to manage roles in the server.",
):
    def __init__(self, bot: FumeGuard):
        self.bot: FumeGuard = bot

    @app_commands.command(name="create")
    @app_commands.check(roles_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.choices(
        color=[
            app_commands.Choice(name="Default", value="default"),
            app_commands.Choice(name="Random", value="random"),
            app_commands.Choice(name="Custom", value="custom"),
            app_commands.Choice(name="Red", value="red"),
            app_commands.Choice(name="Dark Red", value="dark_red"),
            app_commands.Choice(name="Blue", value="blue"),
            app_commands.Choice(name="Dark Blue", value="dark_blue"),
            app_commands.Choice(name="Green", value="green"),
            app_commands.Choice(name="Dark Green", value="dark_green"),
            app_commands.Choice(name="Yellow", value="yellow"),
            app_commands.Choice(name="Orange", value="orange"),
            app_commands.Choice(name="Pink", value="pink"),
            app_commands.Choice(name="Purple", value="purple"),
            app_commands.Choice(name="Light Grey", value="light_grey"),
            app_commands.Choice(name="Dark Grey", value="dark_grey"),
            app_commands.Choice(name="Magenta", value="magenta"),
            app_commands.Choice(name="Gold", value="gold"),
            app_commands.Choice(name="Teal", value="teal"),
            app_commands.Choice(name="Fuchsia", value="fuchsia"),
            app_commands.Choice(name="OG Blurple", value="og_blurple"),
            app_commands.Choice(name="Blurple", value="blurple"),
            app_commands.Choice(name="Greyple", value="greyple"),
        ]
    )
    async def _role_create(
        self,
        ctx: discord.Interaction,
        name: str,
        color: app_commands.Choice[str],
        hoist: Optional[bool] = False,
        mentionable: Optional[bool] = False,
        reason: Optional[str] = None,
    ):
        """Create a new role in the server.

        Parameters
        ----------
        name : str
            The name of the role.
        color : app_commands.Choice[str]
            The color of the role. Can be either a default color or a custom hex code.
        hoist : Optional[bool]
            Whether to display the role separately from other members.
        mentionable : Optional[bool]
            Whether the role should be mentionable.
        reason : Optional[str]
            The reason for creating the role.

        """
        if color.value == "custom":
            modal = RoleColorModal()
            modal.ctx = ctx

            # noinspection PyUnresolvedReferences
            await ctx.response.send_modal(modal)
            await modal.wait()

            try:
                color = discord.Colour.from_str(modal.color.value)

            except ValueError:
                return await modal.interaction.edit_original_response(
                    content="Invalid hexadecimal color code."
                )

        else:
            _color = getattr(discord.Color, color.value)
            color = _color()

        role = await ctx.guild.create_role(
            name=name,
            color=color,
            hoist=hoist,
            mentionable=mentionable,
            reason=reason,
        )

        # noinspection PyUnresolvedReferences
        if ctx.response.is_done():
            # noinspection PyUnboundLocalVariable
            await modal.interaction.edit_original_response(
                content="The role has been created."
            )

        else:
            # noinspection PyUnresolvedReferences
            await ctx.response.send_message(content="The role has been created.")

        await log_role_action(
            ctx=ctx,
            role=role,
            moderator=ctx.user,
            action="Role Created",
            reason=reason,
        )

    @app_commands.command(name="add")
    @app_commands.check(roles_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _role_add(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
        reason: Optional[str] = None,
    ):
        """Add a role to a member.

        Parameters
        ----------
        member : discord.Member
            The member to add the role to.
        role : discord.Role
            The role to add to the member.
        reason : Optional[str]
            The reason for adding the role.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if role in member.roles:
            return await ctx.edit_original_response(
                content=f"{member.mention} already has the role {role.mention}.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        try:
            await member.add_roles(role, reason=reason)

        except (discord.errors.Forbidden, discord.Forbidden):
            return await ctx.edit_original_response(
                content=f"I do not have permission to add {role.mention} to {member.mention}.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        await ctx.edit_original_response(
            content=f"{role.mention} has been added to {member.mention}.",
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await log_role_action(
            ctx=ctx,
            role=role,
            moderator=ctx.user,
            action="Role Added",
            member=member,
            reason=reason,
        )

    @app_commands.command(name="remove")
    @app_commands.check(roles_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _role_remove(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
        reason: Optional[str] = None,
    ):
        """Remove a role from a member.

        Parameters
        ----------
        member : discord.Member
            The member to remove the role from.
        role : discord.Role
            The role to remove from the member.
        reason : Optional[str]
            The reason for removing the role.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if role not in member.roles:
            return await ctx.edit_original_response(
                content=f"{member.mention} does not have the role {role.mention}.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        try:
            await member.remove_roles(role, reason=reason)

        except (discord.HTTPException, discord.errors.HTTPException):
            return await ctx.edit_original_response(
                content=f"I do not have permission to remove that role.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        except (discord.errors.Forbidden, discord.Forbidden):
            return await ctx.edit_original_response(
                content=f"I do not have permission to remove {role.mention} from {member.mention}.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        await ctx.edit_original_response(
            content=f"{role.mention} has been removed from {member.mention}."
        )
        await log_role_action(
            ctx=ctx,
            role=role,
            moderator=ctx.user,
            action="Role Removed",
            member=member,
            reason=reason,
        )

    @app_commands.command(name="delete")
    @app_commands.check(roles_perms_check)
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _role_delete(
        self,
        ctx: discord.Interaction,
        role: discord.Role,
        reason: Optional[str] = None,
    ):
        """Delete an existing role from the server.

        Parameters
        ----------
        role : discord.Role
            The role to delete.
        reason : Optional[str]
            The reason for deleting the role.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        try:
            await role.delete()

        except (discord.HTTPException, discord.errors.HTTPException):
            return await ctx.edit_original_response(
                content="I cannot delete that role."
            )

        except (discord.errors.Forbidden, discord.Forbidden):
            return await ctx.edit_original_response(
                content="I do not have permission to delete that role."
            )

        await ctx.edit_original_response(
            content=f"The role **{role}** has been deleted."
        )
        await log_role_action(
            ctx=ctx,
            role=role,
            moderator=ctx.user,
            action="Role Deleted",
            reason=reason,
        )


async def setup(bot: FumeGuard):
    await bot.add_cog(Roles(bot))
