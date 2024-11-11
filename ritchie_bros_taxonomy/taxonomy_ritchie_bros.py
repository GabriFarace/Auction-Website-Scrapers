import json
import requests


URL = "https://www.rbauction.com"
URL_ITA = "https://www.rbauction.it"# ritchie bros italian website URL

TAXONOMY = 'taxonomy.json' # file that contains the ritchie bros 3-level taxonomy
TAXONOMY_ITA = 'taxonomy_ita.json' # file that contains the ritchie bros 3-level taxonomy in italian

def get_response(url):

    url = url + "/api/advancedSearch"

    payload = json.dumps({
        "searchType": "upcomingAuction"
    })
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US',
        'content-type': 'application/json',
        'cookie': 'optimizelyEndUserId=oeu1730195788262r0.759501836595829; mdLogger=false; kampyle_userid=7edb-5b76-2560-7d99-2956-4dbe-f17d-5671; __stripe_mid=66099525-bbab-4551-a9e9-7051c57cdcb0ec89e2; notice_preferences=0:; notice_gdpr_prefs=0:; cmapi_gtm_bl=ga-ms-ua-ta-asp-bzi-sp-awct-cts-csm-img-flc-fls-mpm-mpr-m6d-tc-tdc; cmapi_cookie_privacy=permit 1 required; _hjSessionUser_1340161=eyJpZCI6ImRkN2FkZmQ0LTlmOGUtNWYzZi04MTZjLWFlYjNlN2I3NjMzYyIsImNyZWF0ZWQiOjE3MzAxOTU3OTExMTUsImV4aXN0aW5nIjp0cnVlfQ==; ajs_user_id=86d9f480-89e9-461e-b890-0731ae7158ca; ajs_anonymous_id=2ab399dd-70bd-401f-8dfa-d8ca4fb6ffb2; kampylePageLoadedTimestamp=1731055926995; LAST_INVITATION_VIEW=1731055938237; DECLINED_DATE=1731055978044; _hjSession_1340161=eyJpZCI6ImM5MDAwOTQzLTdjZGYtNDQwNy04MjhkLTdkMDRlYjc3YjkwMCIsImMiOjE3MzEyMjYxMTUwOTIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; clockOffset=-60; TAsessionID=711076d7-0220-4903-aa8e-c0953d36bbd2|EXISTING; notice_behavior=implied,eu; __stripe_sid=bda9ca5c-106d-4b3f-8a8e-3dde8c07738d707504; kampyleUserSession=1731226632919; kampyleUserSessionsCount=19; kampyleSessionPageCounter=1; _dd_s=rum=1&id=52b83969-a1d9-4efa-a3aa-57831f0a21c4&created=1731226115047&expire=1731227539560',
        'origin': 'https://www.rbauction.com',
        'priority': 'u=1, i',
        'referer': 'https://www.rbauction.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


def refactor_response(response):
    ''' Refactor the sniffed response and create a new more readable file'''
    new_response = {"buckets": []}
    aggregations = response["results"]["aggregations"]
    for aggregation in aggregations:
        if aggregation["field"] == "industries":
            new_response["buckets"] = aggregation["buckets"]
    return new_response



def get_complete_taxonomy(file_taxonomy, url, response):
    ''' Get the complete taxonomy of ritchie bros using the refactored json file sniffed by inspection in the website'''

    first_level_categories = response["buckets"]
    categories = []
    for first_level_category in first_level_categories:
        first_cat = {}
        first_cat["name"] = first_level_category["displayName"]
        first_cat["subcategories"] = []

        second_level_categories = first_level_category["buckets"][0]["buckets"]
        for second_level_category in second_level_categories:
            second_cat = {}
            second_cat["name"] = second_level_category["displayName"]
            second_cat["subcategories"] = []

            third_level_categories = second_level_category["buckets"][0]["buckets"]
            for third_level_category in third_level_categories:
                third_cat = {}
                third_cat["name"] = third_level_category["displayName"]

                third_cat["url"] = url + "/cp/" + third_level_category["seoValue"]

                if "imageLurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageLurl"]
                elif "imageMurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageMurl"]
                elif "imageSurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageSurl"]
                elif "imageTurl" in third_level_category:
                    third_cat["image_url"] = third_level_category["imageTurl"]
                else:
                    third_cat["image_url"] = "NO IMAGE URL"


                second_cat["subcategories"].append(third_cat)

            first_cat["subcategories"].append(second_cat)

        categories.append(first_cat)

    with open(file_taxonomy, 'w') as outfile:
        json.dump(categories, outfile, indent=4)

def get_ritchie_bros_taxonomy():
    get_complete_taxonomy(TAXONOMY, URL, refactor_response(get_response(URL)))
    get_complete_taxonomy(TAXONOMY_ITA, URL_ITA, refactor_response(get_response(URL_ITA)))


if __name__ == '__main__':
    get_ritchie_bros_taxonomy()

