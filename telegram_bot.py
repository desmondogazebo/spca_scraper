import os, time
from dotenv import load_dotenv  # Import load_dotenv function from dotenv module.

from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup

from spca_scraper import search_pets, validate_search
from datetime import datetime

load_dotenv()
TELE_TOKEN = os.environ.get("TELE_TOKEN")
state_storage = StateMemoryStorage() # init storage
# Now, you can pass storage to bot.
bot = AsyncTeleBot(TELE_TOKEN, state_storage=state_storage)

class MyStates(StatesGroup):
    s_category = State() # statesgroup should contain states
    s_age = State()
    s_gender = State()

@bot.message_handler(commands=['search'])
async def start_ex(message):
    text = "Any category for the search? Examples are\n\tcat\n\tdog\n\tguinea pig\n\thamster\n\trabbit\n\tterrapin\n\tother\nsay 'none' to search all"
    await bot.reply_to(message, text)
    await bot.set_state(message.from_user.id, MyStates.s_category)

@bot.message_handler(state="*", commands='cancel')
async def any_state(message):
    print(f"Chat {message.chat.id} cancelled input")
    await bot.send_message(message.chat.id, "Your state was cancelled.")
    await bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(state=MyStates.s_category)
async def category_handler(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['category'] = message.text
        await bot.set_state(message.from_user.id, MyStates.s_age)
        text = "Any preferred age? Examples are\n\tyoung\n\tadult\n\told\nsay 'none' to search all"
        await bot.reply_to(message, text)

@bot.message_handler(state=MyStates.s_age)
async def age_handler(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = message.text
        await bot.set_state(message.from_user.id, MyStates.s_gender)
        text = "Any preferred gender? Examples are\n\tmale\n\tfemale\nsay 'none' to search all"
        await bot.reply_to(message, text)

@bot.message_handler(state=MyStates.s_gender)
async def gender_handler(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['gender'] = message.text
        category = data['category'].strip().lower()
        age = data['age'].strip().lower()
        gender = data['gender'].strip().lower()
        if validate_search(category, age, gender):
            start = time.time()
            searching_intro = f"Searching for: category = [{category}] age = [{age}] gender = [{gender}]"
            result_list = search_pets(category, age, gender)
            found_intro = f"Found {len(result_list)} results!"

            print(f"Chat {message.chat.id} @ {datetime.now()}:\n\t{searching_intro}\n\t{found_intro}")
            if len(result_list) != 0:
                fullstring = ''
                for index, item in enumerate(result_list):
                    fullstring += f"\n{index + 1}) {item}"
                await bot.reply_to(message, f"{searching_intro}\n{found_intro}\n{fullstring}", disable_web_page_preview=True, parse_mode='HTML')
                print(fullstring)
            else:
                await bot.reply_to(message, f"{searching_intro}\n{found_intro}")
            print(f"Took {round(time.time() - start, 3)}s to run")
        else:
            print(f"Chat {message.chat.id} entered invalid input")
            await bot.reply_to(message, f"One of your inputs was invalid. Please try again.")
    await bot.delete_state(message.from_user.id, message.chat.id)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())

import asyncio
asyncio.run(bot.polling())
