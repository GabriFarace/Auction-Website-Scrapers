import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.machinio.com"

TAXONOMY = 'taxonomy.json' # file that contains the taxonomy

class MachinioTaxonomyScraper:
    ''' Taxonomy scraper of the machinio website'''
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def quit(self):
        ''' Close the automated browser'''
        if self.driver:
            self.driver.quit()

    def __exit__(self, exc_type, exc_value, traceback):
        # Quit the WebDriver when exiting the context
        if self.driver:
            self.driver.quit()
        # Handle exceptions if necessary, or let them propagate
        return False

    def get_first_level_categories(self, response):
        soup = BeautifulSoup(response, "html.parser")
        first_categories_tags = soup.select("#hierarchy-nav > ul.h-nav__menu > li.h-nav__cat")

        first_level_categories = []
        for first_categories_tag in first_categories_tags:
            name = first_categories_tag.find("a.has-submenu").text
            url = first_categories_tag.find("a")["href"]
            first_level_category = {"name": name, "url": URL + url}
            second_category_tags = first_categories_tag.select("ul li")
            first_level_category["subcategories"] = [{"name" : second_category_tag.find("a").text, "url" : URL + second_category_tag.find("a")["href"]} for second_category_tag in second_category_tags]
            first_level_categories.append(first_level_category)
        return first_level_categories

    def get_response(self):
        # Open the target URL
        self.driver.get(URL)

        # Wait until a specific element or the body tag is visible
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#hierarchy-toggle"))
        )
        button.click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#hierarchy-nav ul.h-nav__menu"))
        )
        time.sleep(2)
        return self.driver.page_source

    def get_machinio_taxonomy(self, file_taxonomy):
        ''' Get the complete taxonomy of machinio'''

        response = self.get_response()
        categories = self.get_first_level_categories(response)

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)



if __name__ == '__main__':
    scraper = MachinioTaxonomyScraper()
    try:
        scraper.get_machinio_taxonomy(TAXONOMY)
    except Exception as e:
        print(e)
    finally:
        scraper.quit()



