import telebot, os, time
from dotenv import load_dotenv  # Import load_dotenv function from dotenv module.
from spca_scraper import search_pets
from datetime import datetime

load_dotenv()
TELE_TOKEN = os.environ.get("TELE_TOKEN")
bot = telebot.TeleBot(TELE_TOKEN)

@bot.message_handler(commands=['search'])
def tele_search_pets(message):
    text = "Any category for the search? Examples are\n\tcat\n\tdog\n\tguinea pig\n\thamster\n\trabbit\n\tterrapin\n\tother\nsay 'none' to search all"
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, age_handler)

def age_handler(message):
    category = message.text
    text = "Any preferred age? Examples are\n\tyoung\n\tadult\n\told\nsay 'none' to search all"
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, gender_handler,category)

def gender_handler(message, category):
    age = message.text
    text = "Any preferred gender? Examples are\n\tmale\n\tfemale\nsay 'none' to search all"
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, pet_finder, age, category)

def pet_finder(message, age, category):
    gender = message.text
    start = time.time()
    result_list = search_pets(category, age, gender)
    searching_intro = f"Searching for: category = [{category}] age = [{age}] gender = [{gender}], found {len(result_list)} results!"

    print(f"Chat {message.chat.id} @ {datetime.now()} : {searching_intro}")
    if len(result_list) != 0:
        fullstring = ''
        for index, item in enumerate(result_list):
            fullstring += f"\n{index + 1}) {item}"
        bot.send_message(message.chat.id, f"{searching_intro}\n{fullstring}", disable_web_page_preview=True, parse_mode='HTML')
        print(fullstring)
    else:
        bot.send_message(message.chat.id, f"{searching_intro}")
    print(f"Took {round(time.time() - start, 3)}s to run")

bot.infinity_polling()
