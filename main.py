import requests
import time
from bs4 import BeautifulSoup

base_page = f"https://spca.org.sg/services/adoption/"
category_dict = {'': '', 'cat': 7, 'dog': 8, 'guinea_pig': 34, 'hamster': 19, 'other': 100, 'rabbit': 29, 'terrapin': 80}
age_dict = {'': '', 'adult': 14, 'young': 12, 'old': 13}


def find_max_pages(category, age, gender):
    new_url = f"{base_page}?animal_keyword=&animaltype={category_dict[category]}&animalage={age_dict[age]}&animalgender={gender}"
    print(f"Searching {new_url}\nYour conditions are:\n \tcategory= {category}\n\tage= {age}\n\tgender= {gender}")
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
            # print(pet_result.prettify())
            pet_url = pet_result.find("a", href=True)['href']
            pet_name = pet_result.find("div", {"class": "search-result-title"}).text
            end_results.append(f"\t{pet_name} {pet_url}")

        curr_page += 1

    return end_results


animal_category = input("Any category for the search? Examples are\n\tcat\n\tdog\n\tguinea_pig\n\thamster\n\trabbit\n\tterrapin\n\tother\nLeave blank to search all\n>>")
animal_age = input("Any preferred age? Examples are\n\tyoung\n\tadult\n\told\nLeave blank to search all\n>>")
animal_gender = input("Any preferred gender? Examples are\n\tmale\n\tfemale\nLeave blank to search all\n>>")

start = time.time()
result_list = search_pets(animal_category, animal_age, animal_gender)
print(f"{len(result_list)} results found:")
for i in result_list:
    print(i)
print(f"took {round(time.time() - start, 2)}s to run")
