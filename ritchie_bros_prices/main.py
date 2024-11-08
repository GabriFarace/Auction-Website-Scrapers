from ritchie_bros_prices.prices_ritchie_bros import RitchieBrosScraper
import time
import json

def find(scraper, num_pages):
    try:
        scraper.log_in()
        with open("../ritchie_bros_taxonomy/taxonomy.json", "r") as t:
            taxonomy = json.load(t)

        data = []

        for first_level_category in taxonomy:
            first_cat = {"name" : first_level_category["name"]}
            first_cat["subcategories"] = []

            for second_level_category in first_level_category["subcategories"]:
                second_cat = {"name" : second_level_category["name"]}
                second_cat["subcategories"] = []

                for third_level_category in second_level_category["subcategories"]:
                    third_cat = {"name" : third_level_category["name"]}
                    third_cat["url"] = third_level_category["url"]
                    third_cat["docCount"] = third_level_category["docCount"]
                    third_cat["price_elements"] = scraper.find_prices(third_cat["url"]+"?listingStatuses=Sold", num_pages)

                    second_cat["subcategories"].append(third_cat)


                first_cat["subcategories"].append(second_cat)
            data.append(first_cat)



        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)

    except Exception as e:
        print(e)
    finally:
        scraper.quit()

if __name__ == "__main__":
    # Initialize the Scraper
    scraper = RitchieBrosScraper()
