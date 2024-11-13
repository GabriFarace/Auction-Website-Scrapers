import json
import requests


URL = "https://www.govdeals.com/"

TAXONOMY = 'taxonomy.json' # file that contains the gov_deals  3-level taxonomy

def get_response():
    url = "https://maestro.lqdt1.com/menus/categories"
    with open("../../config.json", "r") as f:
        c = json.load(f)
        config = c["gov_deals"]

    payload = json.dumps({
        "businessId": "GD",
        "accountIds": "",
        "menuType": "categories",
        "menuFacetValue": [
            "categoryName"
        ],
        "facetsFilter": [],
        "siteId": 1
    })
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': config["Ocp-Apim-Subscription-Key"],
        'Origin': 'https://www.govdeals.com',
        'Referer': 'https://www.govdeals.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-api-correlation-id': config["x-api-correlation-id"],
        'x-api-key': config["x-api-key"],
        'x-referer': 'https://www.govdeals.com/',
        'x-user-id': '-1',
        'x-user-timezone': 'Europe/Rome',
    }

    response = requests.request("POST", url, headers=headers, data=payload)


    return response.json()



def get_complete_taxonomy(file_taxonomy, url, response):
    ''' Get the complete taxonomy of gov deals '''

    first_level_categories = response["menus"]
    categories = []
    for first_level_category in first_level_categories:
        first_cat = {}
        first_cat["name"] = first_level_category["menuDescription"]
        first_cat["url"] = url + first_level_category["routePath"]
        first_cat["subcategories"] = []

        second_level_categories = first_level_category["children"]
        for second_level_category in second_level_categories:
            second_cat = {}
            second_cat["name"] = second_level_category["menuDescription"]
            second_cat["url"] = url + second_level_category["routePath"]
            second_cat["subcategories"] = []

            third_level_categories = second_level_category["children"]
            for third_level_category in third_level_categories:
                third_cat = {}
                third_cat["name"] = third_level_category["menuDescription"]

                third_cat["url"] = url + third_level_category["routePath"]


                second_cat["subcategories"].append(third_cat)

            first_cat["subcategories"].append(second_cat)

        categories.append(first_cat)

    with open(file_taxonomy, 'w') as outfile:
        json.dump(categories, outfile, indent=4)

def get_gov_deals_taxonomy():
    get_complete_taxonomy(TAXONOMY, URL, get_response())


if __name__ == '__main__':
    get_gov_deals_taxonomy()

