import json
import requests


URL = "https://www.machinerytrader.com"

TAXONOMY = 'taxonomy.json' # file that contains the gov_deals  3-level taxonomy

def get_response():
    with open("../../config.json", "r") as f:
        c = json.load(f)
        config = c["machinery_trader"]


    url = "https://www.machinerytrader.com/ajaxcontent/getdrilldownsearch?lang=en-US&eListingType=1&eDrillDownField=1&isAttachmentSearch=false"

    payload = {}
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'cookie' : config["cookie"],
        'priority': 'u=1, i',
        'referer': 'https://www.machinerytrader.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-xsrf-token': config["x-xsrf-token"],
    }

    response = requests.request("GET", url, headers=headers, data=payload)


    return response.json()

def get_recursive_subcategories(all_categories, index, parent_value):
    result = []
    while index < len(all_categories) and all_categories[index]["ParentValue"] == parent_value:
        new_index, sub_categories = get_recursive_subcategories(all_categories, index + 1, all_categories[index]["Value"])
        category = { "name" : all_categories[index]["CleanName"],
                    "value" : all_categories[index]["Value"],
                      "url" : f"{URL}/listings/search?Category={all_categories[index]["Value"]}&ListingType=Auction%20Results&page=1"}

        if len(sub_categories) > 0:
            category["sub_categories"] = sub_categories

        result.append(category)

        index = new_index
    return index, result

def get_complete_taxonomy(file_taxonomy, response):
    ''' Get the complete taxonomy of machinery trader using the refactored json file sniffed by inspection in the website'''

    all_categories = response["Categories"][1:]
    index, categories = get_recursive_subcategories(all_categories, 0, "")
    print(index == len(all_categories))

    with open(file_taxonomy, 'w') as outfile:
        json.dump(categories, outfile, indent=4)

def get_machinery_trader_taxonomy():
    get_complete_taxonomy(TAXONOMY, get_response())


if __name__ == '__main__':
    get_machinery_trader_taxonomy()

