#You must write unit tests to show that the data access, storage, and processing
#components of your project are working correctly. You must create at least 3
#test cases and use at least 15 assertions or calls to ‘fail( )’. Your tests should
#show that you are able to access data from all of your sources, that your
#database is correctly constructed and can satisfy queries that are necessary
# for your program, and that your data processing produces the results and data
#structures you need for presentation.


import unittest
from final_proj import *

# testing data access
class TestScraping(unittest.TestCase):

    def test_page_scraping(self):
        base_url = 'https://www.twitchmetrics.net'
        total_streamers_lst = []

        page_url = base_url + '/channels/viewership?lang=en'
        viewership_lst, total_streamers_lst = scrape_viewership_page(page_url, total_streamers_lst)
        self.assertEqual(len(viewership_lst), 50)
        self.assertEqual(len(total_streamers_lst), 50)


        total_streamers_lst = []
        page_url = base_url + '/channels/growth?lang=en'
        growth_lst, total_streamers_lst = scrape_twitch_metrics_page(page_url, total_streamers_lst)
        self.assertEqual(len(growth_lst), 50)
        self.assertEqual(len(growth_lst), 50)

# testing storage
class TestDatabase(unittest.TestCase):

    def test_categories_table(self):
        conn = sqlite.connect('twitch.db')
        cur = conn.cursor()

        sql = 'SELECT Name FROM Categories'
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertIn(('Most Watched',), result_list)
        self.assertEqual(len(result_list), 5)

        conn.close()

    def test_games_table(self):
        conn = sqlite.connect('twitch.db')
        cur = conn.cursor()

        sql = '''
            SELECT Name
            FROM Games
            WHERE Id = '13'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertIn(('ASMR',), result_list)
        self.assertEqual(len(result_list), 1)

        conn.close()

    def test_streamers_table(self):
        conn = sqlite.connect('twitch.db')
        cur = conn.cursor()

        sql = '''
            SELECT Username, HoursLive
            FROM Streamers
            WHERE Id = '1'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertEqual('Ninja', result_list[0][0])
        self.assertEqual(68, result_list[0][1])
        self.assertEqual(len(result_list), 1)

        conn.close()

    def test_joins(self):
        conn = sqlite.connect('twitch.db')
        cur = conn.cursor()

        sql = '''
            SELECT Username
            FROM Streamers
                JOIN Rankings
                ON Rankings.StreamerId=Streamers.Id
            WHERE CategoryId=1
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertIn(('Ninja',), result_list)
        self.assertEqual(len(result_list), 50)

        conn.close()

# testing processing and displays
class TestDisplay(unittest.TestCase):

    def test_display_rankings(self):
        try:
            display_rankings('viewership')
            display_rankings('popularity')
        except:
            self.fail()

    def test_display_streamer(self):
        try:
            display_streamer('Ninja')
            display_streamer('imaqtpie')
        except:
            self.fail()

    def test_plot(self):

        try:
            category = 'viewership'

            conn = sqlite.connect('twitch.db')
            cur = conn.cursor()

            statement = 'SELECT Streamers.Username, Streamers.ViewerHours '
            statement += 'FROM Streamers JOIN Rankings ON Streamers.Id = Rankings.StreamerId '
            statement += 'WHERE Rankings.CategoryId = 1'

            cur.execute(statement)

            plot_dict = {}
            plot_dict['column'] = "Weekly Viewer Hours"

            for row in cur:
                plot_dict[row[0]] = row[1]

            plot_rankings(category, plot_dict)
            conn.close()

        except:
                self.fail()

    def test_pie(self):
        try:
            plot_pie()
        except:
            self.fail()

if __name__ == '__main__':
    unittest.main()
