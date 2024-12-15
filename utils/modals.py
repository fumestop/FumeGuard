from __future__ import annotations

from typing import Optional

import discord
from discord import ui


class EvalModal(ui.Modal, title="Evaluate Code"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 5 * 60

    code = ui.TextInput(
        label="Code",
        placeholder="Enter the code to evaluate",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )


class ExecModal(ui.Modal, title="Execute Shell Commands"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 5 * 60

    sh_commands = ui.TextInput(
        label="Command(s)",
        placeholder="Enter the command(s) to execute",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )


class AnnouncementModal(ui.Modal, title="Create an Announcement"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 5 * 60

    message = ui.TextInput(
        label="Message",
        placeholder="Enter the message to announce (max. 1800 characters)",
        style=discord.TextStyle.paragraph,
        min_length=1,
        max_length=1800,
        required=True,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )


class RoleColorModal(ui.Modal, title="Role Color"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 5 * 60

    color = ui.TextInput(
        label="Color",
        placeholder="Enter the color to set (hex code)",
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )


class WelcomeMessageModal(ui.Modal, title="Welcome Message"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 5 * 60

    message = ui.TextInput(
        label="Message",
        placeholder="Enter the welcome message to set (max. 1800 characters)",
        style=discord.TextStyle.paragraph,
        min_length=1,
        max_length=1800,
        required=False,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )
