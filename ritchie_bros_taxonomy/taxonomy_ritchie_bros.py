from selenium import webdriver
from selenium.webdriver.common.by import By
import unicodedata
import json


URL = "https://www.rbauction.com"
URL_ITA = "https://www.rbauction.it"# ritchie bros italian website URL

RESPONSE_JSON = 'response.json' # response from ritchie bros on loading the websites obtained by inspection. It contains the taxonomy
RESPONSE_ITA_JSON = 'response_ita.json' # response from ritchie bros on loading the websites obtained by inspection. It contains the italian taxonomy

TAXONOMY = 'taxonomy.json' # file that contains the ritchie bros 3-level taxonomy
TAXONOMY_ITA = 'taxonomy_ita.json' # file that contains the ritchie bros 3-level taxonomy in italian

def refactor_response(file_response):
    ''' Refactor the sniffed response and create a new more readable file'''
    with open(file_response) as file:
        response = json.load(file)
        new_response = {"buckets": []}

        aggregations = response["results"]["aggregations"]
        for aggregation in aggregations:
            if aggregation["field"] == "industries":
                new_response["buckets"] = aggregation["buckets"]
        return new_response

def remove_accents(input_str):
    # Normalize Unicode characters to their decomposed form
    normalized = unicodedata.normalize('NFD', input_str)
    # Filter out combining characters (accents)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents

def get_complete_taxonomy(file_taxonomy, url, response):
    ''' Get the complete taxonomy of ritchie bros using the refactored json file sniffed by inspection in the website'''

    first_level_categories = response["buckets"]
    categories = []
    for first_level_category in first_level_categories:
        first_cat = {}
        first_cat["name"] = first_level_category["displayName"]
        first_cat["subcategories"] = []

        second_level_categories = first_level_category["buckets"][0]["buckets"]
        for second_level_category in second_level_categories:
            second_cat = {}
            second_cat["name"] = second_level_category["displayName"]
            second_cat["subcategories"] = []

            third_level_categories = second_level_category["buckets"][0]["buckets"]
            for third_level_category in third_level_categories:
                third_cat = {}
                third_cat["name"] = third_level_category["displayName"]

                third_cat["url"] = url + "/cp/" + third_level_category["seoValue"]

                third_cat["docCount"] = third_level_category["docCount"]
                if "imageLurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageLurl"]
                elif "imageMurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageMurl"]
                elif "imageSurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageSurl"]
                elif "imageTurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageTurl"]
                else:
                    third_cat["image_url"] = "NO IMAGE URL"


                second_cat["subcategories"].append(third_cat)

            first_cat["subcategories"].append(second_cat)

        categories.append(first_cat)

    with open(file_taxonomy, 'w') as outfile:
        json.dump(categories, outfile, indent=4)

def get_ritchie_bros_taxonomy():
    get_complete_taxonomy(TAXONOMY, URL, refactor_response(RESPONSE_JSON))
    get_complete_taxonomy(TAXONOMY_ITA, URL_ITA, refactor_response(RESPONSE_ITA_JSON))
    #get_json_from_website()
    #get_first_second_level_categories()


if __name__ == '__main__':
    get_ritchie_bros_taxonomy()



'''
JSON_CATEGORIES_EXTRACTED = "data_ritchie_bros.json" # json extracted from website by automated browser
FIRST_SECOND_LEVEL_CATEGORIES = 'first_second_categories.json' # first and second level categories json file

def get_json_from_website():
    #Get the script data in the dom of the ritchie bros website that contains the first and second level categories
    try:
        # Initialize WebDriver
        driver = webdriver.Chrome()

        # URL of the page with the dropdown
        driver.get(URL)

        # Get the script tag's content
        script_tag  = driver.find_element(By.ID, '__NEXT_DATA__')
        script_content = script_tag.get_attribute('textContent')

        # Parse the JSON content
        json_data = json.loads(script_content)

        with open(JSON_CATEGORIES_EXTRACTED, "w") as file:
            json.dump(json_data, file, indent=4)
    except Exception as e:
        print(e)
    finally:
        # Close the browser
        driver.quit()



def get_first_second_level_categories():
     # Get the first and second level categories from the data extracted by the automated browser
    with open(JSON_CATEGORIES_EXTRACTED) as file:
        json_data = json.load(file)
        cat_menu = json_data["props"]["pageProps"]["categoryMenu"]["menu"]
        categories = {}
        for cat1 in cat_menu:
            category_name = cat1["displayText"]
            categories2_list = cat1["menu"]
            categories[category_name] = []
            for cat2 in categories2_list:
                categories[category_name].append({"name" : cat2["displayText"], "url" : cat2["url"]})

        with open(FIRST_SECOND_LEVEL_CATEGORIES, 'w') as outfile:
            json.dump(categories, outfile, indent=4)


'''