import asyncio
from playwright.async_api import async_playwright
import json
import random

URL = "https://surplusrecord.com"

TAXONOMY = 'taxonomy.json' # file that contains the surplus record taxonomy


class WebScraper:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def initialize_browser(self, playwright):
        # Start Playwright browser and open a new page.
        self.browser = await playwright.chromium.launch(headless=False)  # Headful mode
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        self.page = await self.context.new_page()

    async def get_links(self, url):
        # Navigate to the given URL
        await asyncio.sleep(2)
        await self.page.goto(url)
        content = await self.page.content()
        await asyncio.sleep(5)
        try:
            # Wait for the captcha to appear (you can change the selector to match the captcha's)
            await self.page.wait_for_selector('div.grecaptcha-logo', timeout=5000)  # Adjust timeout as needed

            # If the captcha appears, we stop the execution for manual solving
            print("Captcha detected, pausing the execution. Please solve the captcha manually.")
            input("Press Enter after solving the captcha...")
            await asyncio.sleep(2)
        except Exception as e:
            # If captcha does not appear within the timeout, we continue normally
            print("No captcha detected, proceeding with page scraping.")
        # Scrape all the links and their text from the page
        links = await self.page.eval_on_selector_all('#surplus-main-categories span.name a',
                                                     'elements => elements.map(e => ({ text: e.innerText, href: e.href }))')

        return links

    async def scrape_content_recursive(self, links, current_page):
        if len(links) == 0:
            return links

        results = []
        for link in links:
            await current_page.mouse.wheel(0, random.randint(150, 300))
            await asyncio.sleep(10)
            await current_page.mouse.wheel(0, random.randint(150, 300))
            new_context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            new_tab = await new_context.new_page()
            await new_tab.goto(link['href'])
            await asyncio.sleep(1)
            try:
                # Wait for the captcha to appear (you can change the selector to match the captcha's)
                await new_tab.wait_for_selector('div.grecaptcha-logo', timeout=5000)  # Adjust timeout as needed

                # If the captcha appears, we stop the execution for manual solving
                print("Captcha detected, pausing the execution. Please solve the captcha manually.")
                input("Press Enter after solving the captcha...")
                await asyncio.sleep(2)
            except Exception as e:
                # If captcha does not appear within the timeout, we continue normally
                print("No captcha detected, proceeding with page scraping.")



            # Scrape content from the new tab
            result = await new_tab.eval_on_selector_all('#sub-categories span.name a',
                                                         'elements => elements.map(e => ({ text: e.innerText, href: e.href }))')  # You can adjust the selector based on what you need
            result = await self.scrape_content_recursive(result, new_tab)
            await new_context.close()
            results.append({
                'link': link['href'],
                'text': link['text'],
                'subcategories': result
            })
        return results



    async def scrape(self, url):
        try:

            # Get all the links from the main page
            links = await self.get_links(url)
            print(links)

            results = await self.scrape_content_recursive(links, self.page)

            return results
            # After scraping all pages, close the browser
        except Exception as e:
            print(e)
        finally:
            await self.browser.close()

    '''async def scrape_content_recursive2(self, previous_link):
        categories = await self.page.query_selector_all('#sub-categories span.name a, #surplus-main-categories span.name a')
        if len(categories) == 0:
            await self.page.go_back()
            return []
        num_categories = len(categories)
        results = []
        current_url = self.page.url

        for i in range(num_categories):
            text = await categories[i].text_content()
            href = await categories[i].get_attribute('href')
            results.append({"text": text, "href": href})

        for i in range(num_categories):
            await self.page.mouse.wheel(0, random.randint(150, 300))
            await asyncio.sleep(1)
            await self.page.mouse.wheel(0, random.randint(150, 300))

            fresh_categories = await self.page.query_selector_all('#sub-categories span.name a, #surplus-main-categories span.name a')
            await fresh_categories[i].click()
            await asyncio.sleep(2)

            result = await self.scrape_content_recursive2(current_url)
            results[i]["subcategories"] = result

        await self.page.goto(previous_link)
        return results

    async def scrape2(self, url):
        try:

            # Get all the links from the main page
            #await self.page.goto(URL)
            await self.page.goto(url)

            results = await self.scrape_content_recursive2(url)

            return results
            # After scraping all pages, close the browser
        except Exception as e:
            print(e)
        finally:
            await self.browser.close()'''

# Main execution flow
async def main():
    async with async_playwright() as p:
        scraper = WebScraper()
        url = "/machinery-equipment/"  # Replace with the URL you want to scrape
        # Initialize the browser
        await scraper.initialize_browser(p)
        scraped_data = await scraper.scrape(URL + url)

        with open(TAXONOMY, 'w') as outfile:
            json.dump(scraped_data, outfile, indent=4)


# Run the scraping script
if __name__ == "__main__":
    asyncio.run(main())
