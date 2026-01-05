from playwright.async_api import async_playwright
import asyncio

ASD_URL = "https://www.asdsingapore.com/dogs-for-adoption"
ASD_BASE = "https://www.asdsingapore.com"

OPTIONS_MAP = {
    "HDB Approved": True,
    "HDB Not Approved": False,
    "Any": None,
}

GENDERS_MAP = {
    "Male": "Male",
    "Female": "Female",
    "Any": None,          # treat Any as None internally
}

def validate_search(option: str | None, gender: str | None) -> bool:
    return (option in OPTIONS_MAP) and (gender in GENDERS_MAP)

async def check_hdb(page, hdb: bool | None):
    yes_label = page.locator("label", has_text="Yes")
    no_label  = page.locator("label", has_text="No")

    if hdb is True:
        await yes_label.locator("input[type='checkbox']").check()
    elif hdb is False:
        await no_label.locator("input[type='checkbox']").check()
    else:
        # Any: explicitly select both
        await yes_label.locator("input[type='checkbox']").check()
        await no_label.locator("input[type='checkbox']").check()

async def check_gender(page, gender: str | None):
    male_label   = page.locator("input[type='checkbox'][name='gender'][value='M']")
    female_label = page.locator("input[type='checkbox'][name='gender'][value='F']")

    if gender == "Male":
        await male_label.check()
    elif gender == "Female":
        await female_label.check()
    else:
        # Any: explicitly select both
        await male_label.check()
        await female_label.check()

async def search_asd_pets(hdb: str | None, gender: str | None) -> list[tuple[str, str]]:
    """
    Input is SPCA-style labels:
      hdb: "HDB Approved" | "HDB Not Approved" | "Any"
      gender: "Male" | "Female" | "Any"

    Returns: [(name, url), ...]
    """
    if not validate_search(hdb, gender):
        return []

    hdb_val = OPTIONS_MAP[hdb]          # bool|None
    gender_val = GENDERS_MAP[gender]    # "Male"/"Female"/None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        async def block(route):
            if route.request.resource_type in ("image", "font", "stylesheet"):
                await route.abort()
            else:
                await route.continue_()

        await context.route("**/*", block)

        page = await context.new_page()
        page.set_default_timeout(60_000)  # ASD is slow
        await page.goto(ASD_URL, wait_until="domcontentloaded")

        await check_hdb(page, hdb_val)
        await check_gender(page, gender_val)

        await page.click("button:has-text('Search')")

        # Brutal but reliable
        await asyncio.sleep(3)

        links = await page.query_selector_all("h3.adopt-grid-name a")

        pets: list[tuple[str, str]] = []
        for link in links:
            name = (await link.inner_text() or "").strip()
            url = (await link.get_attribute("href") or "").strip()

            if not name or not url:
                continue

            # normalize to absolute
            if url.startswith("/"):
                url = ASD_BASE + url

            pets.append((name, url))

        await browser.close()

        # dedupe + sort
        return sorted(set(pets), key=lambda x: x[0].lower())
