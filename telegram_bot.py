import asyncio
import os

from dotenv import load_dotenv
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from spca_scraper import search_spca_pets, validate_search
from asd_scraper import search_asd_pets
from cws_scraper import search_cws_pets

load_dotenv()
API_TOKEN = os.environ.get("TELE_TOKEN")
bot = AsyncTeleBot(API_TOKEN)

# Global dictionary to hold user data
user_data = {}


# Function to create a custom keyboard
def make_keyboard(buttons_list):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for button in buttons_list:
        markup.add(types.KeyboardButton(button))
    return markup


# Handler for the /start command
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    markup = make_keyboard(['SPCA', 'ASD', 'CWS', 'Option 4'])
    await bot.reply_to(message, "Choose an option:", reply_markup=markup)


# Handler for regular messages to capture button responses
@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    user_id = message.chat.id
    user_state = user_data.get(user_id, {})

    if message.text in ["SPCA", "ASD", "CWS", "Option 4"]:
        user_data[user_id] = {'option': message.text, 'category': None, 'age': None, 'gender': None}
        if message.text == "SPCA":
            markup = make_keyboard(['Cat', 'Dog', 'Guinea Pig', 'Hamster', 'Other', 'Rabbit', 'Terrapin'])
            await bot.reply_to(message, "Select a category:", reply_markup=markup)
        elif message.text == "ASD":
            markup = make_keyboard(['HDB Approved', 'HDB Not Approved', 'None'])
            await bot.reply_to(message, "Select HDB approval:", reply_markup=markup)
        elif message.text == "CWS":
            search_results = search_cws_pets()
            result_count = len(search_results)
            max_display_results = 20  # Define the maximum number of results to display

            if result_count > 0:
                response_message = f"Found {result_count} results"
                if result_count <= max_display_results:
                    response_message += ":\n" + '\n'.join(search_results)
                else:
                    response_message += f"! Had {result_count} number of cats, too long to display, showing the first {max_display_results}:\n" + '\n'.join(search_results[:max_display_results])
            else:
                response_message = f"No results found."

            await bot.send_message(message.chat.id, response_message, parse_mode='HTML', disable_web_page_preview=True)
            del user_data[user_id]  # Clear user data after search

    elif user_state.get('option') == "SPCA":
        if user_state.get('category') is None:
            user_data[user_id]['category'] = message.text.lower()
            markup = make_keyboard(['Adult', 'Young', 'Old', 'None'])
            await bot.reply_to(message, "Select age group:", reply_markup=markup)
        elif user_state.get('age') is None:
            user_data[user_id]['age'] = message.text.lower()
            markup = make_keyboard(['Male', 'Female', 'None'])
            await bot.reply_to(message, "Select gender:", reply_markup=markup)
        elif user_state.get('gender') is None:
            user_data[user_id]['gender'] = message.text.lower()
            if validate_search(user_data[user_id]['category'], user_data[user_id]['age'], user_data[user_id]['gender']):
                search_results = search_spca_pets(user_data[user_id]['category'],
                                                  user_data[user_id]['age'],
                                                  user_data[user_id]['gender'])
                result_count = len(search_results)
                chosen_conditions = (f"Category: {user_data[user_id]['category'].capitalize()}, "
                                     f"Age: {user_data[user_id]['age'].capitalize()}, "
                                     f"Gender: {user_data[user_id]['gender'].capitalize()}")
                if result_count > 0:
                    response_message = f"Found {result_count} results for {chosen_conditions}:\n" + '\n'.join(
                        search_results)
                else:
                    response_message = f"No results found for {chosen_conditions}."
                await bot.send_message(message.chat.id, response_message, parse_mode='HTML',
                                       disable_web_page_preview=True)
            else:
                await bot.reply_to(message, "Invalid search criteria. Please start again.")
            del user_data[user_id]  # Clear user data after search
    # Implement handlers for other options (ASD, CWS, etc.)
    elif user_state.get('option') == "ASD":
        if user_state.get('hdb') is None:
            user_data[user_id]['hdb'] = message.text.lower()
            markup = make_keyboard(['Male', 'Female', 'None'])
            await bot.reply_to(message, "Select gender:", reply_markup=markup)
        elif user_state.get('gender') is None:
            user_data[user_id]['gender'] = message.text.lower()
            search_results = search_asd_pets(user_data[user_id]['hdb'],
                                             user_data[user_id]['gender'])
            result_count = len(search_results)
            chosen_conditions = (f"HDB Approval: {user_data[user_id]['hdb'].capitalize()}, "
                                 f"Gender: {user_data[user_id]['gender'].capitalize()}")
            if result_count > 0:
                response_message = f"Found {result_count} results for {chosen_conditions}:\n" + '\n'.join(
                    search_results)
            else:
                response_message = f"No results found for {chosen_conditions}."
            await bot.send_message(message.chat.id, response_message, parse_mode='HTML',
                                   disable_web_page_preview=True)
            del user_data[user_id]  # Clear user data after search


asyncio.run(bot.polling())
