import json
from bs4 import BeautifulSoup, Tag
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.surplex.com"

TAXONOMY = 'taxonomy3.json' # file that contains the  3-level taxonomy

class SurplexTaxonomyScraper:
    ''' Taxonomy scraper of the surplex website'''
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


    def get_response(self):
        url = "https://www.surplex.com/en/machines.html"
        # Open the target URL
        time.sleep(1)
        self.driver.get(url)

        # Wait for the main content to load (e.g., the `ul` element)

        # Wait until a specific element or the body tag is visible
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.btn.btn--tertiary.btn--iconLeft.btn--iconLarge[role='button']"))
        )
        self.driver.execute_script("arguments[0].click();", button)

        time.sleep(5)

        # Get the html
        html_text = self.driver.page_source

        return html_text

    def get_recursive_subcategories(self, soup, selector):
        if selector == "#category-menu > ul":
            nav = soup.select(selector)
            categories_ul = nav[1]
        else:
            categories_ul = soup.select_one(selector)

        categories = []
        if categories_ul is None:
            return categories

        categories_li = categories_ul.children
        for category_li in categories_li:
            if isinstance(category_li, Tag):
                url = ""
                if category_li.find("a"):
                    name = category_li.find("a").text
                    url = category_li.find("a")["href"]
                else:
                    name = category_li.find("span").text
                category = {"name": name, "url": URL + url,
                            "subcategories": self.get_recursive_subcategories(category_li, "ul")}
                categories.append(category)

        return categories

    def get_surplex_taxonomy(self, file_taxonomy):
        ''' Get the complete taxonomy of surplex'''
        response = self.get_response()
        soup = BeautifulSoup(response, 'html.parser')
        categories = self.get_recursive_subcategories(soup, "#category-menu > ul")

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)



if __name__ == '__main__':
    scraper = SurplexTaxonomyScraper()
    try:
        scraper.get_surplex_taxonomy(TAXONOMY)
    except Exception as e:
        print(e)
    finally:
        scraper.quit()



