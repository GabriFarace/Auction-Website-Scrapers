import json
from bs4 import BeautifulSoup, Tag
import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.bid-on-equipment.com"

TAXONOMY = 'taxonomy.json' # file that contains the taxonomy

class BidOnEquipmentTaxonomyScraper:
    ''' Taxonomy scraper of the bid on equipment website'''
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
        with open("../../config.json", "r") as f:
            c = json.load(f)
            self.config = c["bid_on_equipment"]

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

    def get_first_level_categories(self):
        first_level_categories = []
        try:
            self.driver.get(URL)
            time.sleep(10)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            first_categories_tags = soup.select("#GlobalCategorySearchItems ul li a")

            first_level_categories = [{"name" : first_category_tag.text, "url" : URL + first_category_tag["href"], "subcategories" : []} for first_category_tag in first_categories_tags[2:]]
            for first_level_category in first_level_categories:
                first_level_category["subcategories"] = self.get_recursive_subcategories(first_level_category)
        except Exception as e:
            raise Exception(e)
        finally:
            return first_level_categories


    def get_recursive_subcategories(self, category):
        response = self.get_response(category["url"])
        subcategories = [{"name" : cat["Name"], "url" : URL + cat["Hyper"], "subcategories" : [] } for cat in response["Result"]]
        for subcategory in subcategories:
            subcategory["subcategories"] = self.get_recursive_subcategories(subcategory)

        return subcategories

    def value_has_changed(self, driver):
        current_value = driver.execute_script("return document.getElementById('searchGuid').value;")
        return current_value != "00000000-0000-0000-0000-000000000000"


    def get_response(self, url):
        # Open the target URL
        self.driver.get(url)

        # Wait for the main content to load (e.g., the `ul` element)

        # Wait until a specific element or the body tag is visible
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#form1"))
        )
        search_string = form.get_attribute("action")
        input_tag = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#searchGuid"))
        )

        WebDriverWait(self.driver, 20).until(self.value_has_changed)

        # Get the payload values
        guid = input_tag.get_attribute("value")
        category_id = int(re.search(r'\d+', search_string).group())

        # Make the API call
        url_api = "https://www.bid-on-equipment.com/SearchHelper.asmx/SideBar?scrptvrsn=1"

        payload = "{categoryId:"+ str(category_id) +", isClearanceOnly:false, guid:'"+ guid +"'}"

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': self.config["cookie"],
            'Origin': 'https://www.bid-on-equipment.com',
            'Referer': 'https://www.bid-on-equipment.com/capsule-equipment',
            'Request-Context': 'appId=cid-v1:3232bd7b-e46b-4687-8132-b927dc8b20a7',
            'Request-Id': '|HHcsT.ZruCT',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

        response = requests.request("POST", url_api, headers=headers, data=payload)
        response_json = response.json()
        return response_json["d"]

    def get_first_level_categories_from(self, url):
        categories = []
        try:
            self.driver.get(URL)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            flag = False
            first_categories_tags = soup.select("#GlobalCategorySearchItems ul li a")
            categories = []
            for first_category_tag in first_categories_tags:
                if flag or first_category_tag["href"] == url:
                    flag = True
                    first_level_category ={"name": first_category_tag.text, "url": URL + first_category_tag["href"],"subcategories": []}
                    first_level_category["subcategories"] = self.get_recursive_subcategories(first_level_category)
                    categories.append(first_level_category)
        except Exception as e:
            print(e)
            raise Exception(e)

        finally:
            return categories

    def get_bid_on_equipment_taxonomy_from(self, file_taxonomy, url):
        

        with open(TAXONOMY, 'r') as outfile:
            categories_1 = json.load(outfile)

        categories = []
        for category in categories_1:
            categories.append(category)
            if category["url"] == URL + url:
                categories.pop()
                break

        categories.extend(self.get_first_level_categories_from(url))

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)

    def get_bid_on_equipment_taxonomy(self, file_taxonomy):
        ''' Get the complete taxonomy of bid on equipment'''

        categories = self.get_first_level_categories()

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)



if __name__ == '__main__':
    scraper = BidOnEquipmentTaxonomyScraper()
    try:
        scraper.get_bid_on_equipment_taxonomy(TAXONOMY)
        #scraper.get_bid_on_equipment_taxonomy_from("taxonomy2.json", "/disposal-equipment")
    except Exception as e:
        print(e)
    finally:
        scraper.quit()



