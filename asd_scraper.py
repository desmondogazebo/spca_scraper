import asyncio
from playwright.async_api import async_playwright

ASD_URL = "https://www.asdsingapore.com/dogs-for-adoption"

async def search_asd_pets(hdb: str, gender: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # Block images, fonts, and stylesheets
        async def route_intercept(route):
            if route.request.resource_type in ["image", "stylesheet", "font"]:
                await route.abort()
            else:
                await route.continue_()
        await context.route("**/*", route_intercept)

        page = await context.new_page()
        await page.goto(ASD_URL, wait_until="domcontentloaded")

        # Apply HDB filter
        if hdb.lower() == "hdb approved":
            await page.check("input[name='hdb'][value='1']")
        elif hdb.lower() == "hdb not approved":
            await page.check("input[name='hdb'][value='0']")

        # Apply gender filter
        if gender.lower() == "male":
            await page.check("input[name='gender'][value='M']")
        elif gender.lower() == "female":
            await page.check("input[name='gender'][value='F']")

        # Click Search
        await page.click("button:has-text('Search')")
        await asyncio.sleep(5)
        await page.wait_for_selector("div.adopt-grid-border")

        pets = []

        # Wait for results to load
        await page.wait_for_selector("div.adopt-grid-border h3.adopt-grid-name a")  

        # Grab all dogs
        dog_divs = await page.query_selector_all("div.adopt-grid-border h3.adopt-grid-name a")
        pets = []
        for dog in dog_divs:
            name = (await dog.inner_text()).strip()
            href = await dog.get_attribute("href")
            pets.append({"name": name, "url": href})

        await browser.close()
        return sorted(pets, key=lambda x: x["name"].lower())
