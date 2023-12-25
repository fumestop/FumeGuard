import json
import logging
import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from utils.core import load_cogs

with open("config.json") as json_file:
    data = json.load(json_file)

    token = data["bot_token"]

logging.basicConfig(
    level=logging.DEBUG,
    filename="logs/fumeguard.log",
    filemode="w",
    format="%(asctime)s - [%(levelname)s] %(message)s",
)


class FumeGuard(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = logging.getLogger("FumeGuard")


intents = discord.Intents.default()
intents.members = True

bot = FumeGuard(command_prefix=commands.when_mentioned_or("/"), intents=intents)

bot.launch_time = datetime.utcnow()
bot.remove_command("help")

bot.emoji1 = "\U0001F44D"
bot.emoji2 = "\u2705"
bot.emoji3 = "\u274C"
bot.emoji4 = "\U0001F44C"

bot.embed_colour = 0xE44C65


async def main():
    async with bot:
        await load_cogs(bot)
        await bot.start(token)


asyncio.run(main())
