import unittest
from final_proj import *

# testing data access
class TestScraping(unittest.TestCase):

    def test_page_scraping(self):
        base_url = 'https://www.twitchmetrics.net'
        total_streamers_lst = []

        # make sure that the scraping is returning the top 50 streamers on the viewership page
        page_url = base_url + '/channels/viewership?lang=en'
        viewership_lst, total_streamers_lst = scrape_viewership_page(page_url, total_streamers_lst)
        self.assertEqual(len(viewership_lst), 50)
        self.assertEqual(len(total_streamers_lst), 50)

        # make sure that the scraping is returning the top 50 streamers on another page (it uses a different function)
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
