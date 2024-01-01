import json

from discord.ext import commands
from discord.ext.ipc import Server
from discord.ext.ipc.objects import ClientPayload

from utils.db import (
    get_mod_log_channel,
    update_mod_log_channel,
    get_member_log_channel,
    update_member_log_channel,
)


class IPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("config.json") as json_file:
            data = json.load(json_file)
            self.secret_key = data["secret_key"]
            self.standard_port = data["standard_port"]
            self.multicast_port = data["multicast_port"]

        if not hasattr(bot, "ipc"):
            bot.ipc = Server(
                self.bot,
                secret_key=self.secret_key,
                standard_port=self.standard_port,
                multicast_port=self.multicast_port,
            )

    async def cog_load(self):
        await self.bot.ipc.start()

    async def cog_unload(self):
        await self.bot.ipc.stop()
        # self.bot.ipc = None

    # noinspection PyUnusedLocal
    @Server.route(name="get_guild_count")
    async def _get_guild_count(self, data: ClientPayload):
        return {"count": len(self.bot.guilds)}

    # noinspection PyUnusedLocal
    @Server.route(name="get_user_count")
    async def _get_user_count(self, data: ClientPayload):
        return {"count": len(self.bot.users)}

    # noinspection PyUnusedLocal
    @Server.route(name="get_command_count")
    async def _get_command_count(self, data: ClientPayload):
        cmds = await self.bot.tree.fetch_commands()
        return {"count": len(cmds)}

    @Server.route(name="get_channel_list")
    async def _get_channel_list(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        channels = list()

        for channel in guild.text_channels:
            if not channel.permissions_for(guild.me).send_messages:
                continue

            else:
                channels.append({"id": channel.id, "name": channel.name})

        return {"channels": channels}

    @Server.route(name="get_mutual_guilds")
    async def _get_mutual_guilds(self, data: ClientPayload):
        user = self.bot.get_user(data.user_id)

        if not user:
            return {"error": {"code": 404, "message": "User not found."}}

        return {"guilds": [guild.id for guild in user.mutual_guilds]}

    @Server.route(name="get_mod_log_channel")
    async def _get_mod_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        channel_id = await get_mod_log_channel(guild.id)

        if channel_id:
            channel = guild.get_channel(channel_id)
            return {"id": channel.id, "name": channel.name}

        else:
            return {"error": {"code": 404, "message": "Moderation logging disabled."}}

    @Server.route(name="update_mod_log_channel")
    async def _update_mod_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        await update_mod_log_channel(guild.id, data.channel_id)

        return {"status": 200, "message": "Success"}

    @Server.route(name="get_member_log_channel")
    async def _get_member_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        channel_id = await get_member_log_channel(guild.id)

        if channel_id:
            channel = guild.get_channel(channel_id)
            return {"id": channel.id, "name": channel.name}

        else:
            return {"error": {"code": 404, "message": "Member logging disabled."}}

    @Server.route(name="update_member_log_channel")
    async def _update_member_log_channel(self, data: ClientPayload):
        guild = self.bot.get_guild(data.guild_id)

        if not guild:
            return {"error": {"code": 404, "message": "Guild not found."}}

        await update_member_log_channel(guild.id, data.channel_id)

        return {"status": 200, "message": "Success"}


async def setup(bot):
    await bot.add_cog(IPC(bot))
