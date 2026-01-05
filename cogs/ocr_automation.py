from discord.ext import commands
from modules.automation.runner import OCRAutomationRunner


class OCRAutomationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runner = OCRAutomationRunner()

    @commands.command(name="startOCRAutomation")
    async def start_automation(self, ctx):
        ok = self.runner.start()
        await ctx.send(
            "OCR automation started" if ok else "Automation already running"
        )

    @commands.command(name="stopOCRAutomation")
    async def stop_automation(self, ctx):
        ok = self.runner.stop()
        await ctx.send(
            "OCR automation stopped" if ok else "Automation not running"
        )
    