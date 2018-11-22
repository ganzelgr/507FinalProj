import sqlite3 as sqlite
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

class Streamer():
    def __init__(self, name, game, url):
        self.username = name
        self.game = game
        self.url = url

        self.follower_count = 0
        self.follower_change = 0
        self.avg_viewers = 0
        self.peak_viewers = 0
        self.hours_live = 0
        self.date_joined = ''
        self.description = ''

    def __str__(self):
        streamer_str = "username: " + self.username + ", game: " + self.game\
            + ", follower count: " + str(self.follower_count) + ", follower change: "\
            + str(self.follower_change) + ", average viewers: " + str(self.avg_viewers) +\
            ", peak viewers: " + str(self.peak_viewers) + ", hours live: " + str(self.hours_live)\
            + ", date joined: " + self.date_joined + ", description: " + self.description
        return streamer_str

def scrape_twitch_metrics_page(page_url, total_streamers_lst):
    page_text = make_request_using_cache(page_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    # narrow results down to the portion of the page containing usernames and urls
    streamer_table = page_soup.find(class_ = 'list-group')
    name_url = streamer_table.find_all(class_ = 'd-flex mb-2 flex-wrap')

    # narrow results down to the portion of the page containing the game names
    games = streamer_table.find_all(class_ = 'mr-3')

    # create a list of all of the games being played in order as they appear on the list
    games_lst = []
    for game in games:
        game_name = game.text.strip()

        if game_name != 'EN':
            games_lst.append(game_name)

    counter = 0
    ranking_lst = []
    for streamer in name_url:
        # get the name, game, and url for each streamer
        name = streamer.find(class_ = 'mr-2 mb-0').text
        game = games_lst[counter]
        url = streamer.find('a')['href']

        # append the name to the list of rankings
        ranking_lst.append(name)

        # search through the list of all of the streamer instances
        # if the current streamer is already in there, do nothing
        # if the current streamer hasn't been added yet, make an instance and append to the list
        in_list = False
        for item in total_streamers_lst:
            if item.username == name:
                in_list = True

        if in_list == False:
            instance = Streamer(name, game, url)
            total_streamers_lst.append(instance)

        counter += 1

    return ranking_lst, total_streamers_lst

def scrape_streamer_page(page_url, streamer):
    result = []

    page_text = make_request_using_cache(page_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    try:
        channel_details = page_soup.find_all(class_ = 'card mb-3')[6]
        info_lst = channel_details.find_all(class_ = 'col-6')

        date_joined = channel_details.find(class_ = 'with_zone').text

    except:
        channel_details = page_soup.find_all(class_ = 'card mb-3')[5]
        info_lst = channel_details.find_all(class_ = 'col-6')

        date_joined = channel_details.find(class_ = 'with_zone').text

    streamer.date_joined = date_joined

    follower_count = info_lst[9].text.strip().replace(',', '')
    streamer.follower_count = follower_count

    try:
        feat_snippet = channel_details.find_all('dl')[1]
        desc = feat_snippet.find('dd').text.strip()
        streamer.description = desc
    except:
        None

    weekly_performance = page_soup.find_all(class_ = 'card mb-3')[0]
    stats = weekly_performance.find_all(class_ = 'd-flex justify-content-start justify-content-md-around')

    follower_change = int(stats[0].find('samp').text.strip().replace(',', ''))
    streamer.follower_change = follower_change

    avg_viewers = int(stats[1].find('samp').text.strip().replace(',', ''))
    streamer.avg_viewers = avg_viewers

    peak_viewers = int(stats[2].find('samp').text.strip().replace(',', ''))
    streamer.peak_viewers = peak_viewers

    hours_live = int(stats[3].find('samp').text.strip().replace(',', ''))
    streamer.hours_live = hours_live


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

# scrape each ranking list
# first item returned is just a list of usernames for each ranking
# second item is a growing list that contains the union of all of these rankings

base_url = 'https://www.twitchmetrics.net'
total_streamers_lst = []

# scrape most watched page
page_url = base_url + '/channels/viewership?lang=en'
viewership_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

# scrape fastest growing page
page_url = base_url + '/channels/growth?lang=en'
growth_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

# scrape highest peak viewership list
page_url = base_url + '/channels/peak?lang=en'
peak_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

# scrape most popular list
page_url = base_url + '/channels/popularity?lang=en'
popularity_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

# scrape most followed list
page_url = base_url + '/channels/follower?lang=en'
follower_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

#--------------------------------------------------------------------

count = 0
for streamer in total_streamers_lst:
    print(count)
    page_url = base_url + streamer.url
    print(streamer.username)

    scrape_streamer_page(page_url, streamer)

    print(streamer)
    print('\n')
    count += 1

#page_url = base_url + total_streamers_lst[61].url
#scrape_streamer_page(page_url, total_streamers_lst[61])
