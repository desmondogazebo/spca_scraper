import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


class MainBot(commands.Bot):
    async def setup_hook(self):
        # Core features
        await self.load_extension("cogs.pet_search")

        # Automation / OCR
        await self.load_extension("cogs.automation")

        # Sync slash commands once on startup
        await self.tree.sync()


def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = MainBot(
        command_prefix=commands.when_mentioned,
        intents=intents,
    )

    @bot.event
    async def on_ready():
        print(f"{bot.user} is online!")

    bot.run(DISCORD_TOKEN)
