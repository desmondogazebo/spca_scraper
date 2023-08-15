import telebot, os, time
from dotenv import load_dotenv  # Import load_dotenv function from dotenv module.
from spca_scraper import search_pets, validate_search
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
    # handle error checking here?
    if validate_search(category, age, gender):
        start = time.time()
        searching_intro = f"Searching for: category = [{category.lower()}] age = [{age.lower()}] gender = [{gender.lower()}]"
        result_list = search_pets(category.lower(), age.lower(), gender.lower())
        found_intro = f"Found {len(result_list)} results!"

        print(f"Chat {message.chat.id} @ {datetime.now()}:\n\t{searching_intro}\n\t{found_intro}")
        if len(result_list) != 0:
            fullstring = ''
            for index, item in enumerate(result_list):
                fullstring += f"\n{index + 1}) {item}"
            bot.send_message(message.chat.id, f"{searching_intro}\n{fullstring}", disable_web_page_preview=True, parse_mode='HTML')
            print(fullstring)
        else:
            bot.send_message(message.chat.id, f"{searching_intro}\n{found_intro}")
        print(f"Took {round(time.time() - start, 3)}s to run")
    else:
        print(f"Chat {message.chat.id} entered invalid input")
        bot.send_message(message.chat.id, f"One of your inputs was invalid. Please try again.")

bot.infinity_polling()
