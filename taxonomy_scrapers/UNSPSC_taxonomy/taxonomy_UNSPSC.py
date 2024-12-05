import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json


URL = "https://www.ungm.org/public/unspsc"

TAXONOMY = 'taxonomy.json' # file that contains the  3-level taxonomy

class UnitedNationsTaxonomyScraper:
    ''' Taxonomy scraper of the united nations'''
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
        # Open the target URL
        time.sleep(1)
        self.driver.get(URL)

        # Wait for the main content to load (e.g., the `ul` element)

        # Wait until a specific element or the body tag is visible
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.unspscTree"))
        )
        #self.driver.execute_script("arguments[0].click();", button)


    def get_recursive_subcategories(self, category_tags, level):

        categories = []
        for category_tag in category_tags:
            span_tag = category_tag.find_element(By.CSS_SELECTOR, "span.nodeName")
            category = {"name": span_tag.find_elements(By.TAG_NAME, "span")[2].text, "code" : span_tag.find_elements(By.TAG_NAME, "span")[0].text}
            self.driver.execute_script("arguments[0].click();", span_tag)
            time.sleep(1)
            subcategories_tag = category_tag.find_elements(By.CSS_SELECTOR, "div.unspscChildren > div.unspscNode")
            if len(subcategories_tag) > 0:
                category["subcategories"] = self.get_recursive_subcategories(subcategories_tag, level + 1)
            if level == 1:
                with open("taxonomy1.json", "r+") as file:
                    # Step 1: Read and parse the JSON content
                    data = json.load(file)

                    # Step 2: Process the data
                    # Example: Add a new key-value pair
                    data.append(category)

                    # Step 3: Move the pointer to the beginning of the file
                    file.seek(0)

                    # Step 4: Write the updated data back to the file
                    json.dump(data, file, indent=4)

                    # Step 5: Truncate the file to remove any leftover content
                    file.truncate()
            categories.append(category)

        return categories

    def get_taxonomy(self, file_taxonomy):
        ''' Get the complete taxonomy of United Nations'''
        self.get_response()
        first_level_category_tags = self.driver.find_elements(By.CSS_SELECTOR, "div.unspscTree > div")

        categories = self.get_recursive_subcategories(first_level_category_tags, 1)

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)


class ExcelScraper:
    def __init__(self, file_path):
        self.input_excel_path = file_path

    def get_taxonomy(self, output_json_path):

        def build_taxonomy_tree(data, parent_key=None):
            """Recursively build the taxonomy tree based on parent-child relationships."""
            tree = []
            if parent_key is not None:
                children = data[data['Parent key'] == parent_key]
            else:
                children = data[data["Code"].isin(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])]

            for _, row in children.iterrows():
                node = {
                    "title": row["Title"],
                    "code": row["Code"],
                    "subcategories": build_taxonomy_tree(data, row["Key"])
                }
                tree.append(node)

            return tree


        # Read the Excel file
        df = pd.read_excel(self.input_excel_path)
        print(df.keys())

        # Create the taxonomy tree starting from the root (parent_key=None)
        taxonomy_tree = build_taxonomy_tree(df)

        # Write the result to a JSON file
        with open(output_json_path, 'w') as json_file:
            json.dump(taxonomy_tree, json_file, indent=4)

    def quit(self):
        return



if __name__ == '__main__':
    scraper = ExcelScraper("website_UNSPSC.xlsx")
    try:
        scraper.get_taxonomy(TAXONOMY)
    except Exception as e:
        print(e)
    finally:
        scraper.quit()



