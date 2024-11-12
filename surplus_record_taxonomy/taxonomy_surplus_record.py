import json
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://surplusrecord.com"

TAXONOMY = 'taxonomy.json' # file that contains the surplus record taxonomy

class SurplusRecordTaxonomyScraper:
    ''' Abstract taxonomy scraper of the surplus record website'''
    def __init__(self):
        self.website = URL

    def get_response(self, url):
        pass

    def quit(self):
        pass

    def get_categories(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        categories_links = soup.select("#surplus-main-categories span.name a")
        categories = [{"name": category.text, "url": category["href"]} for category in categories_links]
        return categories

    def get_subcategories(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        sub_categories_links = soup.select("#sub-categories span.name a")
        if len(sub_categories_links) == 0:
            return None
        else:
            sub_categories = [{"name": sub_category.text, "url": sub_category["href"]} for sub_category in
                              sub_categories_links]
            return sub_categories

    def get_subcategories_recursive(self, sub_categories):
        if sub_categories is None:
            return None
        result = []
        for sub_category in sub_categories:
            sub_sub_cat = self.get_subcategories(self.get_response(URL + sub_category["url"]))
            if sub_sub_cat is None:
                result.append(sub_category)
            else:
                sub_category["sub_categories"] = self.get_subcategories_recursive(sub_sub_cat)
                result.append(sub_category)
        return result

    def get_surplus_record_taxonomy(self, file_taxonomy):
        ''' Get the complete taxonomy of surplus record website'''
        first_level_categories = self.get_categories(self.get_response(URL + "/machinery-equipment/"))
        categories = []
        for first_level_category in first_level_categories:
            first_cat = {}
            first_cat["name"] = first_level_category["name"]
            first_cat["url"] = first_level_category["url"]
            first_cat["subcategories"] = self.get_subcategories_recursive(self.get_subcategories(
                self.get_response(URL + first_cat["url"])))

            categories.append(first_cat)

        with open(file_taxonomy, 'w') as outfile:
            json.dump(categories, outfile, indent=4)



class SurplusRecordCategoriesBrowserScraper(SurplusRecordTaxonomyScraper):
    ''' Scraper of categories in the surplus record auction website that use an automated browser'''
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
                EC.presence_of_element_located((By.ID, "top-search"))
            )

        except Exception as e:
            print(f"Error waiting for page to load: {e}")
            raise Exception("Error waiting for page to load")

        # Get the html
        html_text = self.driver.page_source


        return html_text

class SurplusRecordCategoriesRequestsScraper(SurplusRecordTaxonomyScraper):
    ''' Scraper of categories in the surplus record auction website'''
    def __init__(self):
        pass

    def quit(self):
        pass
    def get_response(self, url):
        payload = {}
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'it,it-IT;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'cookie': '_cfuvid=jE.XlWD.SEkJF.gKv74LQj3qaJ_SL4nXvYEd_e0_htc-1731332854579-0.0.1.1-604800000; _gcl_au=1.1.1141188557.1731332854; referrer=bing|https://surplusrecord.com/; sr_session=cwdt5gexffecwdt5gexffe; _ga=GA1.1.660081338.1731332855; _fbp=fb.1.1731332855219.938662776640895210; cf_clearance=5B1wlS4LRGAAhggzbwl1xIwqdAYiR.P6uVaiS4Q2jB4-1731332855-1.2.1.1-fYRkdgxPm4KrahArVhCEdiNyvh2TxfK0wrrJ.1hdVE2ABu5L0mzNcg5O1umHTlJIC0Titcl7VcHVYWGGX6R211qBZMFHp3kIkrIiPkk9XXbd9H88FuCxDWn8eTOIPXcUkFHaW3QY2QGH8EdcAU2XS3QVLhfeKtc4k.wKYlAGFZAvG8FNIDi4IPMjU7k3gkO0x4Ljpu.Sn.g1nMKivZfY4hmxsHkIS8PloKOXe_XUtnROo43PTzP76esF0KCdlzrFL1E498QxYy46E959zGDUvTY065QDmIs58_RkIvQNftCWTaMbN.wtF4sc2jlErb6fAYqxEwWRwFNg4QvxA7AxtgpTpMVahi5qOkRuufsd937tYmx1KhheS.HHMi_qT_YYaoOlIinUfq9yDLsFn9MR3Q; dicbo_id=%7B%22dicbo_fetch%22%3A1731332855617%7D; OTZ=7817148_52_52_123900_48_436380; recaptcha-ca-e=AY4aWDtYP-RFN1jMEl5O2w_Co2kpHT_DWKCu2CzwQVOd6Z-dTDpwXmXdnpADdP_T21-kNbCd9Yr7CojQvUzNp-LakcHpAInRztaJvFsleNtSZQL0AConrd0UZ3fw9jjgqXngGPBUh_dkR0ZmSdP4jLyQINbrg7C0sSTPpKYRCEUh:U=94d41a4f36000000; _ga_K48D4H48Z6=GS1.1.1731332855.1.1.1731332864.0.0.0; _uetsid=81b9a970a03311efaa50b7cce5b250a0; _uetvid=81b9b690a03311ef91a3670c8423d260; recaptcha-ca-t=AY4aWDtHfZhqug-YxTu-H3lQkK8v0doCMXNKY4jOh28rhfKbDClIppkHLmm0f4FGdTbMBixztxjqCj1Ju5__Deu5xHpYy0nbMiWKg2tGJyXd2J2da6OPRIFpkAFp-6TJxW0zKwSzGJByNlKEwkCFlOpM07egHZk714q3CFTzvViE:U=e5d7144f36000000',
            'priority': 'u=0, i',
            'referer': 'https://surplusrecord.com/',
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version': '"130.0.2849.80"',
            'sec-ch-ua-full-version-list': '"Chromium";v="130.0.6723.117", "Microsoft Edge";v="130.0.2849.80", "Not?A_Brand";v="99.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.text


if __name__ == '__main__':
    scraper = SurplusRecordCategoriesBrowserScraper()
    try:
        scraper.get_surplus_record_taxonomy(TAXONOMY)
    except Exception as e:
        print(e)
    finally:
        scraper.quit()
