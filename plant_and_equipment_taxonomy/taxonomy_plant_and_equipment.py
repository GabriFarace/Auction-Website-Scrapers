import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


###TODO FIX URLS
URL = "https://www.plantandequipment.com"

TAXONOMY = 'taxonomy.json' # file that contains the plant and equipment taxonomy

class PlantAndEquipmentTaxonomyScraper:
    ''' Taxonomy scraper of the plant and equipment website'''
    def __init__(self):
        #self.driver = webdriver.Chrome()
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



    def get_response(self, url):

        # Open the target URL
        time.sleep(1)
        self.driver.get(url)

        # Wait for the main content to load (e.g., the `ul` element)
        try:
            # Wait until a specific element or the body tag is visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "collapseFind"))
            )

        except Exception as e:
            print(f"Error waiting for page to load: {e}")
            raise Exception("Error waiting for page to load")

        # Get the html
        html_text = self.driver.page_source


        return html_text

    def get_categories(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        categories_links = soup.select("#collapseFind a")[:-1]
        categories = [{"name": category.text, "url": category["href"]} for category in categories_links]
        return categories

    def get_subcategories(self, url):
        # Locate and click the button to reveal subcategories
        time.sleep(5)
        self.driver.get(url)

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#btnIndustryCategory"))
        )
        time.sleep(2)

        next_button = self.driver.find_element(By.CSS_SELECTOR, "#btnIndustryCategory")
        print(next_button.text)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        # Force click via JavaScript
        self.driver.execute_script("arguments[0].click();", next_button)

        time.sleep(5)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#nestedCategoryItems div.accordion"))
        )

        sub_categories_divs = self.driver.find_elements(By.CSS_SELECTOR, "#nestedCategoryItems div.accordion")
        sub_categories_ids_buttons = [(int(sub_category_element.get_attribute("id").replace("categoryAccordion","")), sub_category_element.find_element(By.CSS_SELECTOR, "button")) for sub_category_element in sub_categories_divs]

        result = []

        for ids,button in sub_categories_ids_buttons:
            second_level_category = {"name" : button.text, "url" : url + button.text}
            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(5)
            # Wait for the subcategories to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"#nestedSubCategoryItems{ids}"))
            )
            third_level_categories = self.driver.find_elements(By.CSS_SELECTOR, f"#nestedSubCategoryItems{ids} li div.left")
            second_level_category["subcategories"] = [{"name" : third_cat.text, "url" : second_level_category["url"] + third_cat.text} for third_cat in third_level_categories]
            result.append(second_level_category)

        return result


    def get_plant_and_equipment_taxonomy(self, file_taxonomy):
        ''' Get the complete taxonomy of surplus record website'''
        first_level_categories = self.get_categories(self.get_response(URL))
        categories = []

        for first_level_category in first_level_categories:
            first_cat = {"name": first_level_category["name"], "url": URL + first_level_category["url"]}
            first_cat["subcategories"] = self.get_subcategories(first_cat["url"])

            categories.append(first_cat)

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)





if __name__ == '__main__':
    scraper = PlantAndEquipmentTaxonomyScraper()
    try:
        scraper.get_plant_and_equipment_taxonomy(TAXONOMY)
    except Exception as e:
        print(e)
    finally:
        scraper.quit()
