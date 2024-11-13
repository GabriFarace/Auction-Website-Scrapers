import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.exapro.com"

TAXONOMY = 'taxonomy.json' # file that contains the gov_deals  3-level taxonomy

def get_response():

    response = requests.get(URL)

    return response.text



def get_complete_taxonomy(file_taxonomy, url, response):
    ''' Get the complete taxonomy of exapro'''

    soup = BeautifulSoup(response, 'html.parser')
    categories_li = soup.select("div.menu--product-categories li.menu-item-has-children")
    categories = []

    for category_li in categories_li:
        category = {"name": category_li.find("a").text, "url": url + category_li.find("a")["href"]}
        print(category)
        sub_categories_li = category_li.select("div.mega-menu li")
        category["subcategories"] = [{"name" : sub_category_li.a.text, "url" : url + sub_category_li.a["href"]} for sub_category_li in sub_categories_li]

        categories.append(category)

    with open(file_taxonomy, 'w') as outfile:
        json.dump(categories, outfile, indent=4)

def get_exapro_taxonomy():
    get_complete_taxonomy(TAXONOMY, URL, get_response())


if __name__ == '__main__':
    get_exapro_taxonomy()

