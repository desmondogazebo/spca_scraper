import time

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


def search_asd_pets(hdb, gender):
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
    driver.get("https://www.asdsingapore.com/dogs-for-adoption")

    # Find and click the HDB approved checkbox based on user input
    if hdb == "hdb approved":
        hdb_yes_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='hdb' and @value='1']")
        hdb_yes_checkbox.click()
    elif hdb == "hdb not approved":
        hdb_no_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='hdb' and @value='0']")
        hdb_no_checkbox.click()
    # Find and click the Gender checkbox based on user input
    if gender == "male":
        gender_male_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='gender' and @value='M']")
        gender_male_checkbox.click()
    elif gender == "female":
        gender_female_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='gender' and @value='F']")
        gender_female_checkbox.click()

    # Click the "Search" button to display all dogs on the same page
    search_button = driver.find_element(By.XPATH, "//button[contains(text(),'Search')]")
    search_button.click()

    # Give the page some time to load dynamically loaded content
    time.sleep(3)  # Adjust time according to your needs

    # Now scrape the content using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract data - look for the container with the 'adopt-grid-name' class
    dog_elements = soup.find_all('h3', class_='adopt-grid-name')

    # Close the WebDriver
    driver.quit()

    # Process the scraped data
    dog_data = []
    for element in dog_elements:
        a_tag = element.find('a')
        if a_tag:
            dog_data.append(str(a_tag))

    sorted_dog_links = sorted(dog_data, key=sort_key)
    return sorted_dog_links


# Define a custom sorting key to sort the dog links by the dog's name
def sort_key(dog_link):
    # Extract the text within the <a> tag and remove any leading/trailing whitespace
    dog_name = dog_link.split('>', 1)[1].rsplit('<', 1)[0].strip()
    return dog_name
