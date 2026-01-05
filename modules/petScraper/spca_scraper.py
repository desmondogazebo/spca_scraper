import requests
from bs4 import BeautifulSoup

BASE_URL = "https://spca.org.sg"
SEARCH_URL = f"{BASE_URL}/services/adoption/"

CATEGORY_MAP = {
        'Any': '',
        'Cat': 7,
        'Dog': 8,
        'Guinea Pig': 34,
        'Hamster': 19,
        'Other': 100,
        'Rabbit': 29,
        'Terrapin': 80
    }
AGE_MAP = {'Any': '', 'Adult': 14, 'Young': 12, 'Old': 13}
GENDER_MAP = {'Any': '', 'Male': 'male', 'Female': 'female'}

def validate_search(category: str, age: str, gender: str) -> bool:
    
    return (
        category in CATEGORY_MAP
        and age in AGE_MAP
        and gender in GENDER_MAP
    )

def find_max_pages(base_url: str, params: dict) -> int:
    r = requests.get(base_url, params=params, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # No results container → no pets
    if not soup.select_one("ul.search-result-listing"):
        return 0

    pagination = soup.select_one("ul.pagination")
    if not pagination:
        return 1  # only one page

    page_numbers = [
        int(a.text.strip())
        for a in pagination.select("a")
        if a.text.strip().isdigit()
    ]

    return max(page_numbers) if page_numbers else 1


def search_spca_pets(category: str, age: str, gender: str) -> list[dict]:
    params = {
        "animaltype": CATEGORY_MAP[category],
        "animalage": AGE_MAP[age],
        "animalgender": GENDER_MAP[gender],
    }

    max_page = find_max_pages(SEARCH_URL, params)
    if max_page == 0:
        return []

    pets: set[tuple[str, str]] = set()

    for page in range(1, max_page + 1):
        if page == 1:
            url = SEARCH_URL
        else:
            url = f"{SEARCH_URL}page/{page}/"

        resp = requests.get(
            url,
            params=params,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select("div.search-result-item-inner"):
            link = card.select_one("a[href]")
            name_el = card.select_one("h4")

            if not link or not name_el:
                continue

            name = name_el.get_text(strip=True)
            href = link["href"]

            if not href.startswith("http"):
                href = BASE_URL + href

            pets.add((name, href))

    # Deduplicate by URL, then sort by name
    return sorted(set(pets), key=lambda x: x[0].lower())
