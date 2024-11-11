import json
import requests
from bs4 import BeautifulSoup

URL = "https://surplusrecord.com"

TAXONOMY = 'taxonomy.json' # file that contains the ritchie bros 3-level taxonomy


def get_response(url):
    payload = {}
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': '_gcl_au=1.1.1086377985.1730368388; _ga=GA1.1.1710168499.1730368389; _fbp=fb.1.1730368388825.779777127995113008; _cfuvid=8yHQmPXfh.WZkInxCvz5ORtrgXKzhSYXnIew8G9efKA-1731320572525-0.0.1.1-604800000; referrer=https://chatgpt.com/; sr_session=6xpj140hn36xpj140hn3; last_banner_ad=banner-ad-506262; cf_clearance=xq5IGSflD4w_lHnXKQwKcA679tduWpS.pGy5Ei5Ko74-1731322554-1.2.1.1-LGHW710qwo55QT.davio_rA0o_FKNnwcudyPMqDdSnhcqnjaamiiH7uHKdYrHDb9cUq8HJdDlBXO3E.CFYuQgAWWimfigxgbC33kXX9bNAtK8ELZvkEyHK1eSqyoTFLm8ImiUGbmYzRFnzD.EyFZu5DSkaO7JP2lsu.CmHRcDfEIQtrP0GMV2lOsp5trg6CusIe.WM9qYwh1ET8Ix7hGgTN54.15ktrGDHLXYrqfZwvG.8vmTAnpuLwX6qttbwBWvksSeVZof.vuk.DP6Y.MzNXR_NTh0HUL4TpYFVoVlYdVm8GqvsoiYhPlpyyYPC0L2eFEvqxKkzlECWR4H23IGQsCznzMgqkvxfFW7NoHvFvUlWGx8EiSRhRWeWUdYBFC.DO0K0f0T0cVnpSw6atYP3_2KOJ4oIYoHBAf8RBwyJVozl6uCmPAnxRwsQCh5mva; dicbo_id=%7B%22dicbo_fetch%22%3A1731323240247%7D; _ga_K48D4H48Z6=GS1.1.1731320574.2.1.1731323253.0.0.0; _uetsid=e9c71490a01611efae89eb347709f52f; _uetvid=eee39880976d11efa2d539c9d3bf3629; recaptcha-ca-t=AY4aWDuI9IU8ZUgwVbTaWT2_xcSacz_npgVmvG4Dx7jP-ibFMPVh-xAtpZ5pPU4inN_DTjl8Ez0Z0fLHs9pYARLA0XU69POn8CoVANidQmZCKUPqOriJBmy1QOO_w8Yq5y1NEoxgb6gpOxpmJEm8EbZkpEvqSw02DIedPKSxh5IN:U=319d544f36000000',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"130.0.6723.117"',
        'sec-ch-ua-full-version-list': '"Chromium";v="130.0.6723.117", "Google Chrome";v="130.0.6723.117", "Not?A_Brand";v="99.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)


    return response.text



def get_categories(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    categories_links = soup.select("surplus-main-category-column span.name a")
    categories = [{"name" : category.text, "url" : category["href"]} for category in categories_links]
    return categories

def get_subcategories(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    sub_categories_links = soup.select("#sub-categories span.name a")
    if len(sub_categories_links) == 0:
        return None
    else:
        sub_categories = [{"name" : sub_category.text, "url" : sub_category["href"]} for sub_category in sub_categories_links]
        return sub_categories


def get_subcategories_recurvise(sub_categories):
    if sub_categories is None:
        return None

def get_complete_taxonomy(file_taxonomy):
    ''' Get the complete taxonomy of ritchie bros using the refactored json file sniffed by inspection in the website'''
    try:

        first_level_categories = get_categories(get_response(URL + "/machinery-equipment/"))
        categories = []
        for first_level_category in first_level_categories:
            first_cat = {}
            first_cat["name"] = first_level_category["name"]
            first_cat["url"] = first_level_category["url"]
            first_cat["subcategories"] = get_subcategories_recurvise(get_subcategories(get_response(URL + first_cat["url"])))


            categories.append(first_cat)

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)
    except Exception as e:
        print(e)

def get_surplus_record_taxonomy():
    get_complete_taxonomy(TAXONOMY)


if __name__ == '__main__':
    get_surplus_record_taxonomy()
