# modules/freeSteam/free_steam_scraper.py
from __future__ import annotations

import re
import requests
from bs4 import BeautifulSoup

STEAM_FREE_URL = (
    "https://store.steampowered.com/search/?sort_by=Price_ASC&maxprice=free&supportedlang=english&specials=1&ndl=1"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def extract_app_id(href: str) -> str | None:
    match = re.search(r"/app/(\d+)/", href)
    return match.group(1) if match else None


def search_free_steam_games() -> list[dict]:
    resp = requests.get(STEAM_FREE_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    games: list[dict] = []

    for row in soup.select("a.search_result_row"):
        href = row.get("href", "").strip()
        if not href:
            continue

        app_id = extract_app_id(href)
        if not app_id:
            continue

        title_el = row.select_one("span.title")
        title = title_el.get_text(strip=True) if title_el else None
        if not title:
            continue

        games.append({
            "id": app_id,
            "name": title,
            "url": href.split("?")[0],
        })

    # dedupe by app id
    unique = {g["id"]: g for g in games}
    return sorted(unique.values(), key=lambda x: x["name"].lower())