import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from modules.petScraper.pagination import PaginationView

from modules.petScraper.spca_scraper import search_spca_pets, validate_search
from modules.petScraper.asd_scraper import search_asd_pets
from modules.petScraper.cws_scraper import search_cws_pets



# ---------- BASE VIEW (USER-LOCKED) ----------

class LockedView(discord.ui.View):
    def __init__(self, cog, user_id: int, timeout=120):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self):
        self.cog.clear_state(self.user_id)


# ---------- COG ----------
class PetSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state: dict[int, dict] = {}

    def get_state(self, user_id: int) -> dict:
        return self.state.setdefault(user_id, {"source": None, "filters": {}})

    def clear_state(self, user_id: int):
        self.state.pop(user_id, None)

    async def run_sync(self, fn, *args):
        return await asyncio.to_thread(fn, *args)

    # ---------- SLASH COMMAND ENTRY ----------

    @app_commands.command(name="petsearch", description="Search pets from many pet portals")
    async def petsearch(self, interaction: discord.Interaction):
        self.clear_state(interaction.user.id)
        self.get_state(interaction.user.id)

        await interaction.response.send_message(
            "Choose a source:",
            view=SourceView(self, interaction.user.id),
            ephemeral=True
        )

    # ---------- FINAL RENDER ----------

    async def send_results(self, interaction, pets, footer: str):
        if not pets:
            await interaction.followup.send("No results found.", ephemeral=True)
            return

        view = PaginationView(
            pets=pets,
            title="Pets for Adoption",
            user_id=interaction.user.id
        )

        embed = view.get_embed()
        embed.set_footer(text=footer)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


# ---------- SOURCE SELECTION ----------

class SourceView(LockedView):
    def __init__(self, cog, user_id):
        super().__init__(cog, user_id)
        self.add_item(SourceSelect(cog, user_id))


class SourceSelect(discord.ui.Select):
    def __init__(self, cog, user_id):
        self.cog = cog
        self.user_id = user_id
        super().__init__(
            placeholder="Select source",
            options=[
                discord.SelectOption(label="SPCA", value="spca"),
                discord.SelectOption(label="ASD", value="asd"),
                discord.SelectOption(label="CWS", value="cws"),
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        state = self.cog.get_state(self.user_id)
        source = self.values[0]
        state["source"] = source

        await interaction.response.defer(ephemeral=True)

        if source == "spca":
            await interaction.followup.send(
                "Select category:",
                view=SPCACategoryView(self.cog, self.user_id),
                ephemeral=True
            )
        elif source == "asd":
            await interaction.followup.send(
                "Select HDB approval:",
                view=ASDHDBView(self.cog, self.user_id),
                ephemeral=True
            )
        elif source == "cws":
            pets = await self.cog.run_sync(search_cws_pets)
            await self.cog.send_results(
                interaction,
                pets,
                "CWS | All adoptable cats"
            )
            self.cog.clear_state(self.user_id)


# ---------- SPCA FLOW ----------

class SPCACategoryView(LockedView):
    CATEGORIES = ["Cat", "Dog", "Guinea Pig", "Hamster", "Other", "Rabbit", "Terrapin"]

    def __init__(self, cog, user_id):
        super().__init__(cog, user_id)
        for c in self.CATEGORIES:
            self.add_item(SPCACategoryButton(c, cog))

class SPCACategoryButton(discord.ui.Button):
    def __init__(self, category, cog):
        super().__init__(label=category.title())
        self.category = category
        self.cog = cog

    async def callback(self, interaction):
        state = self.cog.get_state(interaction.user.id)
        state["filters"]["category"] = self.category

        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "Select age:",
            view=SPCAAgeView(self.cog, interaction.user.id),
            ephemeral=True
        )

class SPCAAgeView(LockedView):
    AGES = ["Adult", "Young", "Old", "Any"]

    def __init__(self, cog, user_id):
        super().__init__(cog, user_id)
        for age in self.AGES:
            self.add_item(SPCAAgeButton(age, cog))


class SPCAAgeButton(discord.ui.Button):
    def __init__(self, value: str, cog):
        super().__init__(label=value)
        self.value = value
        self.cog = cog

    async def callback(self, interaction):
        state = self.cog.get_state(interaction.user.id)
        state["filters"]["age"] = self.value

        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "Select gender:",
            view=SPCAGenderView(self.cog, interaction.user.id),
            ephemeral=True
        )

class SPCAGenderView(LockedView):
    GENDERS = ["Male", "Female", "Any"]

    def __init__(self, cog, user_id):
        super().__init__(cog, user_id)
        for g in self.GENDERS:
            self.add_item(SPCAGenderButton(g, cog))


class SPCAGenderButton(discord.ui.Button):
    def __init__(self, value: str, cog):
        super().__init__(label=value)
        self.value = value
        self.cog = cog

    async def callback(self, interaction):
        user_id = interaction.user.id
        state = self.cog.get_state(user_id)["filters"]
        state["gender"] = self.value

        await interaction.response.defer(ephemeral=True)
        print(state.get("category"), state.get("age"), state.get("gender"))
        if not validate_search(state.get("category"), state.get("age"), state.get("gender")):
            await interaction.followup.send("Invalid search.", ephemeral=True)
            self.cog.clear_state(user_id)
            return

        pets = await self.cog.run_sync(
            search_spca_pets,
            state.get("category"),
            state.get("age"),
            state.get("gender")
        )

        await self.cog.send_results(interaction, pets, f"SPCA | {state}")
        self.cog.clear_state(user_id)


# ---------- ASD FLOW ----------

class ASDHDBView(LockedView):
    OPTIONS = ["HDB Approved", "HDB Not Approved", "Any"]

    def __init__(self, cog, user_id: int):
        super().__init__(cog, user_id)
        for label in self.OPTIONS:
            self.add_item(ASDHDBButton(label, cog))


class ASDHDBButton(discord.ui.Button):
    def __init__(self, value: str, cog):
        super().__init__(label=value)
        self.value = value
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        state = self.cog.get_state(user_id)
        state["filters"]["hdb"] = self.value

        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "Select gender:",
            view=ASDGenderView(self.cog, user_id),
            ephemeral=True
        )


class ASDGenderView(LockedView):
    GENDERS = ["Male", "Female", "Any"]

    def __init__(self, cog, user_id: int):
        super().__init__(cog, user_id)
        for g in self.GENDERS:
            self.add_item(ASDGenderButton(g, cog))


class ASDGenderButton(discord.ui.Button):
    def __init__(self, value: str, cog):
        super().__init__(label=value)
        self.value = value
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        state = self.cog.get_state(user_id)
        filters = state["filters"]
        filters["gender"] = self.value  # FIX: use self.value

        await interaction.response.defer(ephemeral=True)

        pets = await search_asd_pets(filters.get("hdb"), filters.get("gender"))
        await self.cog.send_results(interaction, pets, f"ASD | {filters}")

        self.cog.clear_state(user_id)




# ---------- SETUP ----------

async def setup(bot):
    await bot.add_cog(PetSearch(bot))
