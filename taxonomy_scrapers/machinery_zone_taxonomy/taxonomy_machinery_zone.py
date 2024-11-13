import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



URL_CONSTRUCTION = "https://www.machineryzone.com"
URL_AGRICULTURE = "https://www.agriaffaires.us"
URL_MAP = {URL_CONSTRUCTION : "construction.html", URL_AGRICULTURE : "agriculture.html"}
TAXONOMY = 'taxonomy.json' # file that contains the machinery zone  3-level taxonomy


def get_response(url):
    file_name = URL_MAP[url]
    with open(file_name, "r", encoding="utf-8") as f:
        file_content = f.read()
    return file_content

'''def get_response(url):
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    content = ""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "#js-main-nav"))
        )
        content = driver.page_source

    except Exception as e:
        print(e)
    finally:
        driver.quit()
        return content'''



def get_subcategories(li, url_base, index):
    level_name_li = li.select_one(f"#menu_{index} a")
    if level_name_li is None:
        level_name_li = li.select_one("a")
        if level_name_li is None:
            return None
        level_name_span = level_name_li.select_one("span")
        if level_name_span is None:
            level_name = level_name_li.text.strip()
        else:
            level_name = level_name_span.text.strip()
    else:
        level_name = level_name_li.text.strip()

    url = url_base + level_name_li['href']
    category = {"name" : level_name, "url" : url, "subcategories" : []}
    sub_level_li_items = li.select(f"ul[aria-labelledby='menu_{index}'] > li")
    if len(sub_level_li_items) == 0:
        return category

    i = 1
    for sub_level_li in sub_level_li_items:
        print(f"{index} sub element ")
        print(sub_level_li)
        subs = get_subcategories(sub_level_li, url_base, index + "_" + str(i))
        if subs is not None:
            category["subcategories"].append(subs)
        i = i+1
    return category


def get_complete_taxonomy(url):
    ''' Get the complete taxonomy of machinery zone '''

    categories = []
    response = get_response(url)
    soup = BeautifulSoup(response, 'html.parser')

    li_items = soup.select("#js-main-nav > ul > li")
    i = 1
    for li in li_items:
        ul_inside = li.select_one("ul")
        if ul_inside:
            categories.append(get_subcategories(li, url, str(i)))
        i = i + 1

    return categories

def get_machinery_zone_taxonomy():
    categories = get_complete_taxonomy(URL_CONSTRUCTION)
    categories.extend(get_complete_taxonomy(URL_AGRICULTURE))

    with open(TAXONOMY, 'w') as outfile:
        json.dump(categories, outfile, indent=4)


if __name__ == '__main__':
    get_machinery_zone_taxonomy()

