from ritchie_bros_prices.prices_ritchie_bros import RitchieBrosScraper
import time
import json

def find_all(scraper, data, num_pages):

    for first_level_category in data:
        for second_level_category in first_level_category["subcategories"]:
            for third_level_category in second_level_category["subcategories"]:
                third_level_category["price_elements"] = scraper.find_prices(third_level_category["url"]+"?listingStatuses=Sold", num_pages)

    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


def find_first_level(scraper, data, num_pages):

    for second_level_category in data["subcategories"]:
        for third_level_category in second_level_category["subcategories"]:
            third_level_category["price_elements"] = scraper.find_prices(third_level_category["url"]+"?listingStatuses=Sold", num_pages)

    with open(data["name"]+".json", "w") as file:
        json.dump(data, file, indent=4)



def find_second_level(scraper, data, num_pages):

    for third_level_category in data["subcategories"]:
        third_level_category["price_elements"] = scraper.find_prices(third_level_category["url"]+"?listingStatuses=Sold", num_pages)

    with open(data["name"]+".json", "w") as file:
        json.dump(data, file, indent=4)

def find_third_level(scraper, data, num_pages):

    data["price_elements"] = scraper.find_prices(data["url"]+"?listingStatuses=Sold", num_pages)

    with open(data["name"]+".json", "w") as file:
        json.dump(data, file, indent=4)


def find_main():
    # Initialize the Scraper web
    scraper = RitchieBrosScraper()
    try:

        scraper.log_in()
        with open("../ritchie_bros_taxonomy/taxonomy.json", "r") as t:
            taxonomy = json.load(t)

        keep_going = True
        while keep_going:
            category = input("What category are you looking for? : ")

            data = taxonomy.copy()
            done = False
            for first_level_category in data:
                if first_level_category["name"] == category:
                    find_first_level(scraper, first_level_category, 1)
                    done = True
                    break
                for second_level_category in first_level_category["subcategories"]:
                    if second_level_category["name"] == category:
                        find_second_level(scraper, second_level_category, 2)
                        done = True
                        break
                    for third_level_category in second_level_category["subcategories"]:
                        if third_level_category["name"] == category:
                            find_third_level(scraper, third_level_category, 3)
                            done = True
                            break
                    if done:
                        break
                if done:
                    break

            if not done:
                find_all(scraper, data, 1)

            choice = input("Would you like to continue? (y/n) : ")
            if choice == "n":
                keep_going = False

    except Exception as e:
        print(e)
    finally:
        scraper.quit()


if __name__ == "__main__":
    find_main()