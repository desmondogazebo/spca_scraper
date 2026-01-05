from playwright.async_api import async_playwright
import asyncio
from typing import List, Tuple, Optional

BASE_URL = "https://www.sosd.org.sg/adopt-a-dog/"

GENDER_MAP = {
    "Male": "Male",
    "Female": "Female",
    "Any": None,
}

HDB_MAP = {
    "Yes": "Yes",
    "No": "No",
    "Any": None,
}


def build_url(gender: Optional[str], hdb: Optional[str]) -> str:
    params = []

    if gender:
        params.append(f"_gender={gender}")
    if hdb:
        params.append(f"_hdb_approved={hdb}")

    if not params:
        return BASE_URL

    return BASE_URL + "?" + "&".join(params)


async def search_sosd_pets(
    gender: Optional[str],
    hdb: Optional[str],
) -> List[Tuple[str, str]]:
    """
    Returns: [(name, url), ...]
    """

    url = build_url(gender, hdb)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Block heavy assets
        async def block(route):
            if route.request.resource_type in ("image", "font", "stylesheet"):
                await route.abort()
            else:
                await route.continue_()

        await context.route("**/*", block)

        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        # JS-heavy site – allow render to settle
        await asyncio.sleep(3)

        pets: list[Tuple[str, str]] = []

        cards = await page.query_selector_all("a.dog-loop-inner")

        for card in cards:
            href = await card.get_attribute("href")
            name_el = await card.query_selector("h4.name")

            if not href or not name_el:
                continue

            name = (await name_el.inner_text()).strip()

            pets.append((name, href))

        await browser.close()

        # Deduplicate + deterministic order
        return sorted(set(pets), key=lambda x: x[0].lower())
