# discord_bot_full.py
import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands

from spca_scraper import search_spca_pets, validate_search
from asd_scraper import search_asd_pets
from cws_scraper import search_cws_pets

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# User state tracking
user_data = {}

# Helper to run synchronous scrapers in async context
async def run_scraper(scraper_func, *args):
    return await asyncio.to_thread(scraper_func, *args)

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# Start command: asks for initial option
@bot.command(name="start")
async def start(ctx):
    options = ['SPCA', 'ASD', 'CWS', 'Option 4']

    class OptionSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Choose an option...",
                min_values=1,
                max_values=1,
                options=[discord.SelectOption(label=o) for o in options]
            )

        async def callback(self, interaction: discord.Interaction):
            user_id = interaction.user.id
            user_data[user_id] = {'option': self.values[0], 'category': None, 'age': None, 'gender': None}
            await interaction.response.defer()

            if self.values[0] == "SPCA":
                categories = ['Cat', 'Dog', 'Guinea Pig', 'Hamster', 'Other', 'Rabbit', 'Terrapin']
                await send_next_step(interaction, user_id, "Select a category:", categories, "category")
            elif self.values[0] == "ASD":
                hdb_options = ['HDB Approved', 'HDB Not Approved', 'None']
                await send_next_step(interaction, user_id, "Select HDB approval:", hdb_options, "hdb")
            elif self.values[0] == "CWS":
                results = await run_scraper(search_cws_pets)
                max_display = 20
                if results:
                    response = f"Found {len(results)} results"
                    if len(results) <= max_display:
                        response += ":\n" + '\n'.join(results)
                    else:
                        response += f"! Too many results, showing first {max_display}:\n" + '\n'.join(results[:max_display])
                else:
                    response = "No results found."
                await interaction.followup.send(response)
                user_data.pop(user_id, None)

    view = discord.ui.View()
    view.add_item(OptionSelect())
    await ctx.send("Choose an option:", view=view)


async def send_next_step(interaction, user_id, prompt, choices, field):
    class NextSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder=prompt,
                min_values=1,
                max_values=1,
                options=[discord.SelectOption(label=c) for c in choices]
            )

        async def callback(self, select_interaction: discord.Interaction):
            user_data[user_id][field] = self.values[0].lower()
            await select_interaction.response.defer()

            state = user_data[user_id]
            # SPCA multi-step logic
            if state['option'] == "SPCA":
                if field == "category":
                    ages = ['Adult', 'Young', 'Old', 'None']
                    await send_next_step(select_interaction, user_id, "Select age group:", ages, "age")
                elif field == "age":
                    genders = ['Male', 'Female', 'None']
                    await send_next_step(select_interaction, user_id, "Select gender:", genders, "gender")
                elif field == "gender":
                    # Perform search
                    if validate_search(state['category'], state['age'], state['gender']):
                        results = await run_scraper(search_spca_pets, state['category'], state['age'], state['gender'])
                        chosen_conditions = (f"Category: {state['category'].capitalize()}, "
                                             f"Age: {state['age'].capitalize()}, "
                                             f"Gender: {state['gender'].capitalize()}")
                        if results:
                            response = f"Found {len(results)} results for {chosen_conditions}:\n" + '\n'.join(results)
                        else:
                            response = f"No results found for {chosen_conditions}."
                        await select_interaction.followup.send(response)
                    else:
                        await select_interaction.followup.send("Invalid search criteria. Please start again.")
                    user_data.pop(user_id, None)
            # ASD multi-step logic
            elif state['option'] == "ASD":
                if field == "hdb":
                    genders = ['Male', 'Female', 'None']
                    await send_next_step(select_interaction, user_id, "Select gender:", genders, "gender")
                elif field == "gender":
                    results = await run_scraper(search_asd_pets, state['hdb'], state['gender'])
                    chosen_conditions = f"HDB Approval: {state['hdb'].capitalize()}, Gender: {state['gender'].capitalize()}"
                    if results:
                        response = f"Found {len(results)} results for {chosen_conditions}:\n" + '\n'.join(results)
                    else:
                        response = f"No results found for {chosen_conditions}."
                    await select_interaction.followup.send(response)
                    user_data.pop(user_id, None)

    view = discord.ui.View()
    view.add_item(NextSelect())
    await interaction.followup.send(prompt, view=view)