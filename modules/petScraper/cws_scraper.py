import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.catwelfare.org"
BASE_PAGE = f"{BASE_URL}/wcbcategories/adopt/"


def _find_max_pages(soup: BeautifulSoup) -> int:
    """
    Detect last page number from pagination.
    """
    pages = []

    pagination = soup.find("div", class_="wpc-paginations")
    if not pagination:
        return 1

    for a in pagination.find_all("a", href=True):
        text = a.get_text(strip=True)
        if text.isdigit():
            pages.append(int(text))

    return max(pages) if pages else 1


def search_cws_pets() -> list[tuple[str, str]]:
    """
    Returns: [(name, url), ...]
    """

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120 Safari/537.36"
        )
    })

    # First page – determine pagination
    r = session.get(BASE_PAGE, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    max_page = _find_max_pages(soup)

    pets: set[tuple[str, str]] = set()

    for page in range(1, max_page + 1):
        url = BASE_PAGE if page == 1 else f"{BASE_PAGE}?page={page}"
        resp = session.get(url, timeout=15)
        resp.raise_for_status()

        s = BeautifulSoup(resp.text, "html.parser")

        for p in s.select("p.wpc-title a[href]"):
            name = p.get_text(strip=True)
            href = urljoin(BASE_URL, p.get("href"))

            if name and href:
                pets.add((name, href))

    return sorted(pets, key=lambda x: x[0].lower())
