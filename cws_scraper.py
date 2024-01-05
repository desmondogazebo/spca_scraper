from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests


def search_cws_pets():
    # Configure Selenium to use Chrome in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/87.0.4280.88 Safari/537.36 ")

    chrome_path = ChromeDriverManager().install()
    chrome_service = Service(chrome_path)
    # pass the defined options and service objects to initialize the web driver
    driver = Chrome(options=options, service=chrome_service)

    # Navigate to the ASD adoption page
    base_page = "https://www.catwelfare.org/wcbcategories/adopt/"
    # Find and return the maximum number of pages
    cat_data = []
    curr_page = 1
    max_page = find_max_pages(driver, base_page)

    while curr_page <= max_page:
        url = f"{base_page}?page={curr_page}"
        page_results = requests.get(url)
        soup = BeautifulSoup(page_results.content, "html.parser")
        listings = soup.find('div', {'id': "wpc-products"})
        pet_results = listings.find_all("p", {"class": "wpc-title"})
        for pet_result in pet_results:
            a_tag = pet_result.find("a")
            if a_tag:
                cat_data.append(str(a_tag))
        curr_page += 1

    sorted_cat_links = sorted(cat_data, key=sort_key)
    return sorted_cat_links


# Define a custom sorting key to sort the dog links by the dog's name
def sort_key(cat_link):
    # Extract the text within the <a> tag and remove any leading/trailing whitespace
    cat_name = cat_link.split('>', 1)[1].rsplit('<', 1)[0].strip()
    return cat_name


def find_max_pages(driver, basepage):
    driver.get(basepage)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    pagination = soup.find("div", class_="wpc-paginations")

    page_nos = []
    for page in pagination.find_all("a", href=True):
        page_no = page.text
        if page_no.isnumeric():
            page_nos.append(int(page_no))

    if page_nos:
        return max(page_nos)
    else:
        return 1  # Default to 1 page if no pagination is found
