from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import requests

class RitchieBrosScraper:
    ''' Scraper of prices in the ritchie bros auction website'''
    def __init__(self):
        self.driver = webdriver.Chrome()
        with open("../config.json", "r") as f:
            c = json.load(f)
            self.config = c["ritchie_bros"]


    def log_in(self):
        ''' Deals with the login process. '''
        # Open login page
        self.driver.get(self.config["login_url"])

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "input-password-signin-password"))
        )

        # Login logic
        username = self.driver.find_element(By.ID, "email")
        password = self.driver.find_element(By.ID, "input-password-signin-password")
        login_button = self.driver.find_element(By.ID, "btn-login")

        username.send_keys(self.config["user"])
        password.send_keys(self.config["passw"])
        time.sleep(5)
        login_button.click()




    # After logging in
    def save_cookie(self):
        cookies = self.driver.get_cookies()
        with open("cookies.json", "w") as file:
            json.dump(cookies, file)

    # Before accessing a logged-in page
    def load_cookie(self):
        with open("cookies.json", "rb") as file:
            cookies = json.load(file)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.refresh()

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



    def find_prices(self, url, pages):
        ''' Find a number of pages of the prices of an asset defined by the url equals to the pages parameters'''
        data = []
        url = url+"?listingStatuses=Sold"
        # Open the target URL
        time.sleep(3)
        self.driver.get(url)

        # Wait for the main content to load (e.g., the `ul` element)
        wait = WebDriverWait(self.driver, 10)
        k = 0
        while k<pages:
            wait.until(EC.presence_of_element_located((By.ID, "searchResults")))
            # Extract data from the current page
            ul_element = self.driver.find_element(By.ID, "searchResults")

            # Find all li elements inside the ul
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")

            # Loop through each li and extract h5 and span text
            for li in li_elements:
                try:
                    # Find the name of the asset
                    name_div_element = li.find_element(By.CSS_SELECTOR, "div.MuiStack-root.muiltr-1w8dugu")

                    name_h4_element = name_div_element.find_element(By.CSS_SELECTOR, "h4.MuiTypography-root.MuiTypography-subtitle2.muiltr-1luqgnj")

                    name_a_element = name_h4_element.find_element(By.TAG_NAME, "a")

                    # Find the place and usage of the asset
                    place_usage_div_elements = li.find_elements(By.CSS_SELECTOR, "div.MuiStack-root.muiltr-u4p24i")
                    place_usage = []
                    for p in place_usage_div_elements:
                        place_usage_p_element = p.find_element(By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.muiltr-474m9o")
                        place_usage.append(place_usage_p_element.text)



                    # Find the date
                    date_element = li.find_element(By.TAG_NAME, "h5")

                    # Find the lot
                    lot_element = li.find_element(By.CSS_SELECTOR, "span.MuiChip-label.MuiChip-labelMedium.muiltr-9iedg7")

                    # Find the price
                    price_element = li.find_element(By.CSS_SELECTOR, 'span[data-testid="priceComponent"]')



                    # Extract the text
                    name = name_a_element.text
                    place = place_usage[0]
                    usage = place_usage[1] if len(place_usage)>1 else "NO USAGE DATA"
                    lot = lot_element.text
                    date_purchase = date_element.text
                    price = price_element.text

                    # Print the extracted text
                    element = {"Asset" : name, "Lot" : lot, "Location" : place, "Usage" : usage, "Date" : date_purchase, "Price" : price}
                    data.append(element)


                except Exception as e:
                    print(f"Error extracting data from element: {e}")

            print(f"Page {k+1} extracted")
            k = k+1
            # Check if the "Next" button exists and is clickable
            try:

                # Locate the "Next" button
                next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Go to next page"]')))

                # Scroll to the "Next" button to ensure it's in view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)

                # Wait briefly to ensure scrolling has completed
                time.sleep(1)

                # Use ActionChains to click the button (avoids click interception)
                action = ActionChains(self.driver)
                action.move_to_element(next_button).click().perform()
                time.sleep(3)  # Wait for the next page to load

            except Exception as e:
                print(f"No more pages or unable to click Next button for url{url}")
                break  # Exit the loop if no more pages

        print(f"Finished extracting all pages for url : {url}")
        return data

class RitchieBrosScraperAPI:
    ''' Scraper of prices in the ritchie bros auction website'''
    def __init__(self):
        with open("../config.json", "r") as f:
            c = json.load(f)
            self.config = c["ritchie_bros"]

    def log_in(self):
        pass



    # After logging in
    def save_cookie(self):
        pass

    # Before accessing a logged-in page
    def load_cookie(self):
        pass

    def quit(self):
        pass

    # R3cuzslrvdqhtrEb0yY4Z
    def find_prices(self, url, pages):
        ''' Find a number of pages of the prices of an asset defined by the url equals to the pages parameters'''
        data = []
        category = url.split("/")[-1]
        extracted = 0
        referer = f'https://www.rbauction.com/cp/{category}?listingStatuses=Sold'
        while extracted < pages:
            url = f"https://www.rbauction.com/_next/data/R3cuzslrvdqhtrEb0yY4Z/en-US/cp/{category}.json?listingStatuses=Sold&industries={category}&from={extracted * 30}"

            payload = {}
            headers = {
                'accept': '*/*',
                'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'cookie': self.config["cookie"],
                'priority': 'u=1, i',
                'referer': referer,
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'x-nextjs-data': '1'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            returned = response.json()["pageProps"]["data"]["results"]
            if returned["returnedAmount"] < 30:
                if returned == 0:
                    print(f"Page contains nothing for category: {category}")
                else:
                    data.extend(returned["records"])
                    print(f"Extracted page number:{extracted + 1} for category : {category}, Page contains less than 30 elements ")
                break

            data.extend(returned["records"])
            print(f"Extracted page number:{extracted + 1} for category : {category}")
            referer = url
            extracted += 1
        return data