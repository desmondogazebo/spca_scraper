import requests
from bs4 import BeautifulSoup

base_page = f"https://spca.org.sg/services/adoption/"
category_dict = {'none': '', 'cat': 7, 'dog': 8, 'guinea_pig': 34, 'hamster': 19, 'other': 100, 'rabbit': 29, 'terrapin': 80}
age_dict = {'none': '', 'adult': 14, 'young': 12, 'old': 13}
gender_dict = {'none': '', 'male': 'male', 'female': 'female'}
def find_max_pages(category, age, gender):
    new_url = f"{base_page}?animal_keyword=&animaltype={category_dict[category]}&animalage={age_dict[age]}&animalgender={gender_dict[gender]}"
    print(f"Accessing {new_url}")

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
            # find how many pages there are, skipping the foward and back buttons
        else:
            return 1
            # more than 0 pages, but only 1 page found.
    else:
        return 0
        # no results


def search_pets(category, age, gender):
    if category.lower() == "guinea pig": category = "guinea_pig"
    end_results = []
    curr_page = 1
    max_page = find_max_pages(category, age, gender)

    while curr_page <= max_page:
        url = f"{base_page}page/{curr_page}/?animal_keyword=&animaltype={category_dict[category]}&animalage={age_dict[age]}&animalgender={gender_dict[gender]}"
        page_results = requests.get(url)

        soup = BeautifulSoup(page_results.content, "html.parser")
        listings = soup.find('ul', {'class': "search-result-listing"})

        pet_results = listings.find_all("div", {"class": "search-result-item-inner"})

        for pet_result in pet_results:
            pet_url = pet_result.find("a", href=True)['href']
            pet_name = pet_result.find("div", {"class": "search-result-title"}).text
            end_results.append(f"<a href='{pet_url}'>{pet_name}</a>")

        curr_page += 1
    return end_results

def validate_search(category, age, gender):
    if category not in category_dict or age not in age_dict or gender not in gender_dict: return False
    return True
