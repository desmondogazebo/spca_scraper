import discord
from discord import app_commands
from discord.ext import commands

from modules.automation.runner import DOMAutomationRunner


class AutomationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runner = DOMAutomationRunner()

    # ---------- SLASH COMMANDS ----------

    @app_commands.command(name="start_automation", description="Start OCR-based desktop automation")
    async def start_automation(self, interaction: discord.Interaction):
        # ACK IMMEDIATELY
        await interaction.response.defer(ephemeral=True)

        ok = self.runner.start()

        await interaction.followup.send(
            "OCR automation started ✅"
            if ok
            else "OCR automation is already running",
            ephemeral=True
        )

    @app_commands.command(name="stop_automation", description="Stop OCR-based desktop automation")
    async def stop_automation(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        ok = self.runner.stop()

        await interaction.followup.send(
            "OCR automation stopped 🛑"
            if ok
            else "OCR automation is not running",
            ephemeral=True
        )


# ---------- SETUP ----------

async def setup(bot):
    await bot.add_cog(AutomationCog(bot))
