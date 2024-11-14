import json
import requests
from bs4 import BeautifulSoup

URL = "https://machinerymarketplace.net/eq"

TAXONOMY = 'taxonomy.json' # file that contains the machinery_marketplace  3-level taxonomy

with open("../../config.json", "r") as f:
    c = json.load(f)
    config = c["machinery_marketplace"]

def get_response():
    response = requests.get(URL)
    return response.text

def get_response_subcategories(id):

    url = "https://machinerymarketplace.net/Equipment/GetListSubCatByCat"

    payload = f"catList%5B%5D={id}"
    headers = {
        'accept': '*/*',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': config['cookie'],
        'origin': 'https://machinerymarketplace.net',
        'priority': 'u=1, i',
        'referer': 'https://machinerymarketplace.net/eq',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()["data"]



def get_complete_taxonomy(file_taxonomy):
    ''' Get the complete taxonomy of machinery marketplace '''
    categories = []
    soup = BeautifulSoup(get_response(), features="html.parser")
    first_level_tags = soup.select("#multiple-cat optgroup")

    for first_level_tag in first_level_tags:
        first_level_category = {"name" : first_level_tag["label"], "subcategories" : []}
        second_level_tags = first_level_tag.select("option")

        for second_level_tag in second_level_tags:

            second_level_category = {"name" : second_level_tag.text, "id": second_level_tag["value"], "subcategories" : []}
            third_level_tags = get_response_subcategories(second_level_category["id"])
            second_level_category["subcategories"] = [{"name" : third_level_tag["Name"], "id": third_level_tag["EquipSubCatId"], "parent_id" : third_level_tag["EquipCategoryId"]} for third_level_tag in third_level_tags]

            first_level_category["subcategories"].append(second_level_category)

        categories.append(first_level_category)


    with open(file_taxonomy, 'w') as outfile:
        json.dump(categories, outfile, indent=4)

def get_machinery_marketplace_taxonomy():

    get_complete_taxonomy(TAXONOMY)


if __name__ == '__main__':
    get_machinery_marketplace_taxonomy()

