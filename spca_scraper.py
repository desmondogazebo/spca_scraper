import requests
from bs4 import BeautifulSoup

base_page = "https://spca.org.sg/services/adoption/"
category_dict = {
    'none': '',
    'cat': 7,
    'dog': 8,
    'guinea_pig': 34,
    'hamster': 19,
    'other': 100,
    'rabbit': 29,
    'terrapin': 80
}
age_dict = {'none': '', 'adult': 14, 'young': 12, 'old': 13}
gender_dict = {'none': '', 'male': 'male', 'female': 'female'}

headers = {"User-Agent": "Mozilla/5.0"}

def find_max_pages(category, age, gender):
    """Detect the last page number for given filters."""
    url = (f"{base_page}?animal_keyword=&animaltype={category_dict[category]}"
           f"&animalage={age_dict[age]}&animalgender={gender_dict[gender]}")
    print(f"Accessing {url}")
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    # No results at all
    container = soup.find("ul", class_="search-result-listing")
    if not container:
        return 0

    # Check pagination
    pagination = soup.find("ul", class_="pagination")
    if not pagination:
        return 1  # Only one page exists

    page_numbers = []
    for li in pagination.find_all("li"):
        a = li.find("a", href=True)
        if a and a.text.strip().isdigit():
            page_numbers.append(int(a.text.strip()))

    return max(page_numbers) if page_numbers else 1


def search_spca_pets(category, age, gender):
    if category.lower() == "guinea pig":
        category = "guinea_pig"

    results = []
    max_page = find_max_pages(category, age, gender)
    if max_page == 0:
        return results

    for page in range(1, max_page + 1):
        if page == 1:
            url = f"{base_page}?animal_keyword=&animaltype={category_dict[category]}&animalage={age_dict[age]}&animalgender={gender_dict[gender]}"
        else:
            url = f"{base_page}page/{page}/?animal_keyword=&animaltype={category_dict[category]}&animalage={age_dict[age]}&animalgender={gender_dict[gender]}"

        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.content, "html.parser")

        listings = soup.find_all("div", class_="search-result-item-inner")
        for item in listings:
            link_tag = item.find("a", href=True)
            name_tag = item.find("div", class_="item-title h4") or item.find("div", class_="item-title")  # fallback
            img_tag = item.select_one(".search-result-pic-container figure img")
            if link_tag and name_tag:
                results.append({
                    "name": name_tag.get_text(strip=True),
                    "url": link_tag['href'],
                    "img": img_tag['src'] if img_tag else None
                })

    return results


def validate_search(category, age, gender):
    if category not in category_dict or age not in age_dict or gender not in gender_dict:
        return False
    return True
