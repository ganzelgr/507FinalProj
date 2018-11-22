import requests
import json
from bs4 import BeautifulSoup

CACHE_FNAME = 'cache_final.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def make_request_using_cache(url):
    if url in CACHE_DICTION:
        #print("Getting cached data...")
        return CACHE_DICTION[url]

    else:
        #print("Making a request for new data...")
        resp = requests.get(url)
        CACHE_DICTION[url] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[url]

#class Streamer():
#    def __init__(self, name, url):
#        self.name = name # name of streamer
#        self.url = url # url to get to the streamer's specific page

#        self.viewership = None # only there if they are in that list

#    def __str__(self):
#        return self.name

def scrape_twitch_metrics_page(page_url, name_url_dict):
    page_text = make_request_using_cache(page_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    streamer_table = page_soup.find(class_ = 'list-group')
    name_url = streamer_table.find_all(class_ = 'd-flex mb-2 flex-wrap')

    streamer_lst = []
    for streamer in name_url:
        name = streamer.find(class_ = 'mr-2 mb-0').text
        url = streamer.find('a')['href']
        # pull the game that they play and add that to the dict!!!!!!!

        streamer_lst.append(name)

        if name not in name_url_dict.keys():
            name_url_dict[name] = url

    return streamer_lst, name_url_dict

def scrape_streamer_page(page_url):
    page_text = make_request_using_cache(page_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    channel_details = page_soup.find_all(class_ = 'card mb-3')[6]
    info_lst = channel_details.find_all(class_ = 'col-6')

    date_joined = channel_details.find(class_ = 'with_zone').text
    follower_count = info_lst[9].text

    feat_snippet = channel_details.find_all('dl')[1]
    desc = feat_snippet.find('dd').text.strip()

    print(desc)

    # maybe add a function that takes each line of this and inserts into a table

# total viewership is the only thing you can't get from the streamer's page
#if page_url == 'https://www.twitchmetrics.net/channels/viewership?lang=en':
#    viewership_info = streamer_table.find_all(style = 'font-size: 1.1em')
#
#        count = 0
#        for streamer in viewership_info:
#            streamer_lst[count].viewership = streamer.text
#            count += 1

#--------------------------------------------------------------------

base_url = 'https://www.twitchmetrics.net'
name_url_dict = {}

# scrape most watched page
page_url = base_url + '/channels/viewership?lang=en'
viewership_lst, name_url_dict = scrape_twitch_metrics_page(page_url, name_url_dict)

# scrape fastest growing page
page_url = base_url + '/channels/growth?lang=en'
growth_lst, name_url_dict = scrape_twitch_metrics_page(page_url, name_url_dict)

# scrape highest peak viewership list
page_url = base_url + '/channels/peak?lang=en'
peak_lst, name_url_dict = scrape_twitch_metrics_page(page_url, name_url_dict)

# scrape most popular list
page_url = base_url + '/channels/popularity?lang=en'
popularity_lst, name_url_dict = scrape_twitch_metrics_page(page_url, name_url_dict)

# scrape most followed list
page_url = base_url + '/channels/follower?lang=en'
follower_lst, name_url_dict = scrape_twitch_metrics_page(page_url, name_url_dict)

#--------------------------------------------------------------------

page_url = base_url + name_url_dict['Ninja']
scrape_streamer_page(page_url)

print(name_url_dict)
