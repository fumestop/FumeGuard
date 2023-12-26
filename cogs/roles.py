import discord
from discord import app_commands
from discord.ext import commands

from utils.logger import log_role_action
from utils.tools import dynamic_cooldown_x


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _roles_perms_check(ctx: discord.Interaction):
        return (
            ctx.user.guild_permissions.manage_roles
            and ctx.guild.me.guild_permissions.manage_roles
        )

    @app_commands.command(
        name="newrole", description="Create a new role in the server."
    )
    @app_commands.check(_roles_perms_check)
    @app_commands.checks.dynamic_cooldown(dynamic_cooldown_x)
    @app_commands.guild_only()
    @app_commands.choices(
        color=[
            app_commands.Choice(name="Default", value="default"),
            app_commands.Choice(name="Random", value="random"),
            app_commands.Choice(name="Custom", value="custom"),
            app_commands.Choice(name="Red", value="Red"),
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
    async def _new_role(
        self, ctx: discord.Interaction, name: str, color: app_commands.Choice[str]
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.edit_original_response(
                content="I do not have the permission to create roles."
            )

        if color == "custom":
            try:
                color = discord.Colour.from_str(color.value)

            except ValueError:
                return await ctx.edit_original_response(
                    content="Invalid hex color code."
                )

        else:
            _color = getattr(discord.Color, color.value)
            color = _color()

        role = await ctx.guild.create_role(name=name, color=color)

        await ctx.edit_original_response(content="The role has been created.")
        await log_role_action(
            ctx=ctx, role=role, moderator=ctx.user, action="Role Created"
        )

    @app_commands.command(name="addrole", description="Add a role to a member.")
    @app_commands.check(_roles_perms_check)
    @app_commands.checks.dynamic_cooldown(dynamic_cooldown_x)
    @app_commands.guild_only()
    async def _add_role(
        self, ctx: discord.Interaction, member: discord.Member, role: discord.Role
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.edit_original_response(
                content="I do not have the permission to create roles."
            )

        try:
            await member.add_roles(role)

        except (discord.errors.Forbidden, discord.Forbidden):
            return await ctx.edit_original_response(
                content=f"I do not have permission to add that role to **{member}**."
            )

        await ctx.edit_original_response(
            content=f"The role **{role}** has been added to **{member}**."
        )
        await log_role_action(
            ctx=ctx, role=role, moderator=ctx.user, action="Role Added", member=member
        )

    @app_commands.command(name="removerole", description="Remove a role from a member.")
    @app_commands.check(_roles_perms_check)
    @app_commands.checks.dynamic_cooldown(dynamic_cooldown_x)
    @app_commands.guild_only()
    async def _remove_role(
        self, ctx: discord.Interaction, member: discord.Member, role: discord.Role
    ):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.edit_original_response(
                content="I do not have the permission to create roles."
            )

        try:
            await member.remove_roles(role)

        except (discord.errors.Forbidden, discord.Forbidden):
            return await ctx.edit_original_response(
                content=f"I do not have permission to remove that role from **{member}**."
            )

        await ctx.edit_original_response(
            content=f"The role **{role}** has been removed from **{member}**."
        )
        await log_role_action(
            ctx=ctx, role=role, moderator=ctx.user, action="Role Removed", member=member
        )

    @app_commands.command(
        name="deleterole", description="Delete an existing role from the server."
    )
    @app_commands.check(_roles_perms_check)
    @app_commands.checks.dynamic_cooldown(dynamic_cooldown_x)
    @app_commands.guild_only()
    async def _del_role(self, ctx: discord.Interaction, role: discord.Role):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.edit_original_response(
                content="I do not have the permission to create roles."
            )

        try:
            await role.delete()
        except (discord.errors.Forbidden, discord.Forbidden):
            return await ctx.edit_original_response(
                content="I do not have permission to delete that role."
            )

        await ctx.edit_original_response(
            content=f"The role **{role}** has been deleted."
        )
        await log_role_action(
            ctx=ctx, role=role, moderator=ctx.user, action="Role Deleted"
        )

    @_new_role.error
    @_add_role.error
    @_remove_role.error
    @_del_role.error
    async def _roles_perms_check_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                "You do not have permissions to execute this command."
                "\n **Required Permission** : *Manage Roles*",
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(Roles(bot))
