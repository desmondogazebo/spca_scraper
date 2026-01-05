import discord
from math import ceil

PAGE_SIZE = 25


class PaginationView(discord.ui.View):
    def __init__(self, pets, title="Results", user_id: int | None = None, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.pets = pets  # [(name, url), ...]
        self.title = title
        self.user_id = user_id

        self.page = 0
        self.max_page = max(ceil(len(pets) / PAGE_SIZE) - 1, 0)

        # Disable buttons if only 1 page
        if self.max_page == 0:
            self.prev.disabled = True
            self.next.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Lock paging controls to the user who initiated the search
        return self.user_id is None or interaction.user.id == self.user_id

    def get_embed(self) -> discord.Embed:
        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = self.pets[start:end]

        embed = discord.Embed(
            title=f"{self.title} (Page {self.page + 1}/{self.max_page + 1})",
            description="\n".join(f"[{name}]({url})" for name, url in page_items) or "No results.",
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"Showing {len(self.pets)} pets")
        return embed

    async def update(self, interaction: discord.Interaction):
        # Keep buttons enabled/disabled correctly
        self.prev.disabled = (self.page <= 0)
        self.next.disabled = (self.page >= self.max_page)

        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        await self.update(interaction)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1
        await self.update(interaction)
