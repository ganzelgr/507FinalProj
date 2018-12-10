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

# testing storage
class TestDatabase(unittest.TestCase):

    def test_bar_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Company FROM Bars'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Sirene',), result_list)
        self.assertEqual(len(result_list), 1795)

        sql = '''
            SELECT Company, SpecificBeanBarName, CocoaPercent,
                   Rating
            FROM Bars
            WHERE Company="Woodblock"
            ORDER BY Rating DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 8)
        self.assertEqual(result_list[0][3], 4.0)

        conn.close()

    def test_country_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT EnglishName
            FROM Countries
            WHERE Region="Oceania"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Australia',), result_list)
        self.assertEqual(len(result_list), 27)

        sql = '''
            SELECT COUNT(*)
            FROM Countries
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 250 or count == 251)

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Alpha2
            FROM Bars
                JOIN Countries
                ON Bars.CompanyLocationId=Countries.Id
            WHERE SpecificBeanBarName="Hacienda Victoria"
                AND Company="Arete"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('US',), result_list)
        conn.close()

# testing processing
class TestMapping(unittest.TestCase):

    # we can't test to see if the maps are correct, but we can test that
    # the functions don't return an error!
    def test_show_state_map(self):
        try:
            plot_sites_for_state('mi')
            plot_sites_for_state('az')
        except:
            self.fail()

    def test_show_nearby_map(self):
        site1 = NationalSite('National Monument',
            'Sunset Crater Volcano', 'A volcano in a crater.')
        site2 = NationalSite('National Park',
            'Yellowstone', 'There is a big geyser there.')
        try:
            plot_nearby_for_site(site1)
            plot_nearby_for_site(site2)
        except:
            self.fail()

class TestCompanySearch(unittest.TestCase):

    def test_company_search(self):
        results = process_command('companies region=Europe ratings top=5')
        self.assertEqual(results[1][0], 'Idilio (Felchlin)')

        results = process_command('companies country=US bars_sold top=5')
        self.assertTrue(results[0][0] == 'Fresco' and results[0][2] == 26)

        results = process_command('companies cocoa top=5')
        self.assertEqual(results[0][0], 'Videri')
        self.assertGreater(results[0][2], 0.79)

if __name__ == '__main__':
    unittest.main()
