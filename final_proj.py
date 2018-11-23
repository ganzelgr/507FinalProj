import sqlite3 as sqlite
import requests
import json
from bs4 import BeautifulSoup
import sys

#--------------------------------CACHING------------------------------------
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

#-----------------------------STREAMER CLASS--------------------------------
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

#--------------------FUNCTION TO SCRAPE THE RANKINGS------------------------
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

#--------------------FUNCTION TO SCRAPE THE STREAMER PAGES------------------
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

#----------------------PERFORM ALL OF THE SCRAPING------------------------

# scrape each ranking list
# first item returned is just a list of usernames for each ranking
# second item is a growing list that contains the union of all of these rankings
def reset_db():
    print('---Scraping the rankings from twitchmetrics.net: Step 1 of 3---')

    base_url = 'https://www.twitchmetrics.net'
    total_streamers_lst = []

    # scrape most watched page
    print('Scraping the most watched list...')
    page_url = base_url + '/channels/viewership?lang=en'
    viewership_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

    # scrape fastest growing page
    print('Scraping the fastest growing list...')
    page_url = base_url + '/channels/growth?lang=en'
    growth_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

    # scrape highest peak viewership list
    print('Scraping the peak viewership list...')
    page_url = base_url + '/channels/peak?lang=en'
    peak_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

    # scrape most popular list
    print('Scraping the most popular list...')
    page_url = base_url + '/channels/popularity?lang=en'
    popularity_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

    # scrape most followed list
    print('Scraping the most followed list...')
    page_url = base_url + '/channels/follower?lang=en'
    follower_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)

    # scrape the streamer pages
    print('\n---Obtaining information on each streamer: Step 2 of 3---')
    streamer_cnt = len(total_streamers_lst)
    count = 1
    for streamer in total_streamers_lst:
        print('Scraping page ' + str(count) + ' of ' + str(streamer_cnt))
        page_url = base_url + streamer.url
        scrape_streamer_page(page_url, streamer)
        count += 1

    # get a list of all of the games that are played to make the table
    total_games_lst = []
    for streamer in total_streamers_lst:
        if streamer.game not in total_games_lst and streamer.game != '':
            total_games_lst.append(streamer.game)

#---------------------------MAKING THE TABLES-----------------------------------

# make the games and categories tables first, these don't point to anything
# then make the streamers table, it will point to the games table
# finally make the rankings table, this will point to the streamers and categories tables

    print('\n---Recreating the database: Step 3 of 3---')
    conn = sqlite.connect('twitch.db')
    cur = conn.cursor()

    # Drop the tables if they already exist so they can be made again
    statement = '''
        DROP TABLE IF EXISTS 'Games';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Categories';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Streamers';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Rankings';
    '''
    cur.execute(statement)

    conn.commit()

    # Create the Games table
    statement = '''
        CREATE TABLE 'Games' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    # Create the Categories table
    statement = '''
        CREATE TABLE 'Categories' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    # Create the Streamers table
    statement = '''
        CREATE TABLE 'Streamers' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Username' TEXT NOT NULL,
            'GameId' INTEGER NULL,
            'FollowerCount' INTEGER NOT NULL,
            'FollowerChange' INTEGER NOT NULL,
            'AvgViewers' INTEGER NOT NULL,
            'PeakViewers' INTEGER NOT NULL,
            'HoursLive' INTEGER NOT NULL,
            'DateJoined' TEXT NOT NULL,
            'Description' TEXT NULL
        );
    '''
    cur.execute(statement)

    # Create the Rankings table
    statement = '''
        CREATE TABLE 'Rankings' (
            'CategoryId' INTEGER NOT NULL,
            'StreamerId' INTEGER NOT NULL,
            'StreamerRanking' INTEGER NOT NULL
        );
    '''
    cur.execute(statement)
    conn.commit()

    # Fill the Games table
    for game in total_games_lst:
        insertion = (None, game)
        statement = 'INSERT INTO Games VALUES (?, ?)'
        cur.execute(statement, insertion)

    conn.commit()

    # Fill the Categories table
    categories_lst = ['Most Watched', 'Fastest Growing', 'Highest Peak Viewership', \
                    'Most Popular', 'Most Followed']
    for category in categories_lst:
        insertion = (None, category)
        statement = 'INSERT INTO Categories VALUES (?, ?)'
        cur.execute(statement, insertion)

    conn.commit()

    # Fill the Streamers table
    for streamer in total_streamers_lst:
        try:
            game_id = cur.execute('SELECT Id FROM "Games" WHERE Name = "' + streamer.game + '"').fetchone()[0]
        except:
            game_id = None

        insertion = (None, streamer.username, game_id, streamer.follower_count, \
                    streamer.follower_change, streamer.avg_viewers, streamer.peak_viewers, \
                    streamer.hours_live, streamer.date_joined, streamer.description)
        statement = 'INSERT INTO Streamers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

    conn.commit()

    # Fill the Rankings table
    rankings_lst = [viewership_lst, growth_lst, peak_lst, popularity_lst, follower_lst]

    for i in range(5):
        index = 1
        for streamer in rankings_lst[i]:
            category_id = i + 1
            streamer_id = cur.execute('SELECT Id FROM "Streamers" WHERE Username = "' + streamer + '"').fetchone()[0]

            insertion = (category_id, streamer_id, index)
            statement = 'INSERT INTO Rankings VALUES (?, ?, ?)'
            cur.execute(statement, insertion)

            index += 1

    conn.commit()
    conn.close()

#--------------------FUNCTION FOR DISPLAYING RANKINGS------------------
def display_rankings(category):
    conn = sqlite.connect('twitch.db')
    cur = conn.cursor()

    statement = 'SELECT Rankings.StreamerRanking, Streamers.Username, Games.Name, '

    #if category == 'viewership':
    #    statement += 'Streamers.AvgViewers '
    #    category_id = 1
    #    column_name = "Weekly Viewership"
    if category == 'growth':
        statement += 'Streamers.FollowerChange '
        category_id = 2
        column_name = "Weekly Follower Change"
    elif category == 'peak':
        statement += 'Streamers.PeakViewers '
        category_id = 3
        column_name = "Weekly Peak Viewers"
    elif category == 'popularity':
        category_id = 4
        statement += 'Streamers.AvgViewers '
        column_name = "Weekly Average Viewers"
    elif category == 'follower':
        category_id = 5
        statement += 'Streamers.FollowerCount '
        column_name = "Total Follower Count"

    statement += 'FROM Streamers JOIN Rankings ON Streamers.Id = Rankings.StreamerId '
    statement += 'JOIN Games ON Streamers.GameId = Games.Id '
    statement += 'WHERE Rankings.CategoryId = ' + str(category_id)

    cur.execute(statement)

    print("\n{:<7} {:<20s} {:<20s} {:<10}".format('Ranking', 'Username', 'Game', column_name))
    for row in cur:

        final_lst = []
        for word in row:
            if isinstance(word, str) and len(word) > 12:
                word = word[0:11] + '...'
            final_lst.append(word)

        print("{:<7} {:<20s} {:<20s} {:<10}".format(final_lst[0], final_lst[1], final_lst[2], final_lst[3]))

    conn.close()


#---------------------------MAIN CODE--------------------------------
# commands:
#       reset
#       rankings [category] - shows the ranking in table
#           streamer - gives info on a streamer on that list
#           plot - plots that list
#       plot [category/all] [variable] - plots given people by a given variable
#       game - returns list of streamers that play that game


# category = viewership, growth, peak, popularity, follower
# variable =

command = input("Enter a command (or enter 'help' for options): ")

while command.lower() != 'exit':
    command_str = command.lower().split()

    if command_str[0] == 'reset':
        reset_db()

    if command_str[0] == 'rankings':
        category = command_str[1]

        display_rankings(category)

    command = input("Enter a command (or enter 'help' for options): ")

print('Bye!')
