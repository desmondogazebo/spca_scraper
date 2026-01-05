import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

class PetBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.pet_search")
        # await self.tree.sync()

class OCRBot(commands.Bot):
    async def setup_hook(self):
        # await self.load_extension("cogs.automation")  # later
        await self.tree.sync()

def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = PetBot(command_prefix=commands.when_mentioned,intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} is online!")

    bot.run(DISCORD_TOKEN)
