import requests
import time
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv  # Import load_dotenv function from dotenv module.

load_dotenv()
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_DATA = requests.get(f"https://api.telegram.org/bot{TELE_TOKEN}/getUpdates").json()
def get_chat_ids():
    chat_ids_list = []
    print(CHAT_DATA['result'])
    for chatter in CHAT_DATA['result']:
        chat_ids_list.append(str(chatter['message']['chat']['id']))
    print(f"Had {len(chat_ids_list)} users, reduced to {len(list(set(chat_ids_list)))} due to duplicates.") # remove dupes
    return list(set(chat_ids_list))

CHAT_IDS = get_chat_ids()

base_page = f"https://spca.org.sg/services/adoption/"
category_dict = {'': '', 'cat': 7, 'dog': 8, 'guinea_pig': 34, 'hamster': 19, 'other': 100, 'rabbit': 29, 'terrapin': 80}
age_dict = {'': '', 'adult': 14, 'young': 12, 'old': 13}

def send_telegram(message):
    delay = 0.0
    if len(CHAT_IDS) > 30:
        delay = len(CHAT_IDS) * 0.035 # this is the lowest amount of time to wait
    for CHAT_ID in CHAT_IDS:
        time.sleep(delay)
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url)
def find_max_pages(category, age, gender):
    new_url = f"{base_page}?animal_keyword=&animaltype={category_dict[category]}&animalage={age_dict[age]}&animalgender={gender}"
    condition_text = f"Your conditions are:\n \tcategory= {category}\n\tage= {age}\n\tgender= {gender}"
    print(f"Searching {new_url}...\n{condition_text}")

    loaded = requests.get(new_url)
    soup = BeautifulSoup(loaded.content, "html.parser")

    # check if this page has any results at all...
    has_pet = soup.find("ul", {"class": "search-result-listing"})
    if has_pet is not None:
        # handle multipage
        pages = soup.find_all("li", {"class": "page-item"})

        if len(pages) > 0:
            page_nos = []
            for page in pages:
                page_no = page.find("a", href=True).text
                page_nos.append(page_no)
            return int(max([x for x in page_nos if x.isnumeric()]))
        else:
            return 1
    else:
        return 0


def search_pets(category, age, gender):
    end_results = []
    curr_page = 1
    max_page = find_max_pages(category, age, gender)

    while curr_page <= max_page:
        url = f"{base_page}page/{curr_page}/?animal_keyword=&animaltype={category_dict[category]}&animalage={age_dict[age]}&animalgender={gender}"
        page_results = requests.get(url)

        soup = BeautifulSoup(page_results.content, "html.parser")
        listings = soup.find('ul', {'class': "search-result-listing"})

        pet_results = listings.find_all("div", {"class": "search-result-item-inner"})

        for pet_result in pet_results:
            pet_url = pet_result.find("a", href=True)['href']
            pet_name = pet_result.find("div", {"class": "search-result-title"}).text
            end_results.append(f"{pet_name} {pet_url}")

        curr_page += 1
    send_telegram(f"Searching for: category = [{category}] age = [{age}] gender = [{gender}], found {len(end_results)} results!")
    return end_results

def print_results(result_list):
    if len(result_list) != 0:
        fullstring = ''
        for index, item in enumerate(result_list):
            fullstring += f"\n{index+1}) {item}"
        send_telegram(fullstring)
        print(fullstring)

# animal_category = input("Any category for the search? Examples are\n\tcat\n\tdog\n\tguinea_pig\n\thamster\n\trabbit\n\tterrapin\n\tother\nLeave blank to search all\n>>")
# animal_age = input("Any preferred age? Examples are\n\tyoung\n\tadult\n\told\nLeave blank to search all\n>>")
# animal_gender = input("Any preferred gender? Examples are\n\tmale\n\tfemale\nLeave blank to search all\n>>")

start = time.time()
animal_list = ['cat', 'dog']
for animal in animal_list:
    # result_list = search_pets(animal_category, animal_age, animal_gender)
    pet_list = search_pets(animal, "young", "")
    print_results(pet_list)

print(f"Sent messages to {len(CHAT_IDS)} users. Total run time = {round(time.time() - start, 2)}s")
