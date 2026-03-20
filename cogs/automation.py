# cogs/automation.py
from __future__ import annotations

import json
from pathlib import Path

import discord
from discord.ext import commands, tasks

import datetime

from modules.freeSteam.free_steam_scraper import search_free_steam_games

SEEN_FILE = Path("data/free_steam_seen.json")
TARGET_CHANNEL_ID = 1437720250476134400  # replace this


class Automation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.free_steam_checker.start()

    def cog_unload(self):
        self.free_steam_checker.cancel()

    def load_seen_ids(self) -> set[str]:
        if not SEEN_FILE.exists():
            return set()
        try:
            data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
            return set(data)
        except Exception:
            return set()

    def save_seen_ids(self, ids: set[str]) -> None:
        SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        SEEN_FILE.write_text(
            json.dumps(sorted(ids), indent=2),
            encoding="utf-8",
        )

    @tasks.loop(time=datetime.time(hour=10, minute=0))
    async def free_steam_checker(self):
        channel = self.bot.get_channel(TARGET_CHANNEL_ID)
        if channel is None:
            return

        seen_ids = self.load_seen_ids()
        games = await self.bot.loop.run_in_executor(None, search_free_steam_games)

        new_games = [g for g in games if g["id"] not in seen_ids]
        if not new_games:
            return

        embed = discord.Embed(
            title="Free Steam games spotted",
            description="\n".join(
                f"[{g['name']}]({g['url']})" for g in new_games[:20]
            ),
            color=discord.Color.blue(),
        )

        if len(new_games) > 20:
            embed.set_footer(text=f"And {len(new_games) - 20} more.")

        await channel.send(embed=embed)

        seen_ids.update(g["id"] for g in new_games)
        self.save_seen_ids(seen_ids)

    @free_steam_checker.before_loop
    async def before_free_steam_checker(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Automation(bot))