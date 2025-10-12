import unittest
from Restaurant_Browsing import RestaurantDatabase, RestaurantBrowsing

class TestRestaurantFilters(unittest.TestCase):
    def setUp(self):
        self.db = RestaurantDatabase()
        self.browse = RestaurantBrowsing(self.db)

    # NEW TEST: combined filters
    def test_combined_filter(self):
        res = self.browse.search_by_filters(cuisine_type="Italian", location="Uptown")
        self.assertTrue(all(r["cuisine"] == "Italian" for r in res))

    # NEW TEST: no results
    def test_no_results(self):
        res = self.browse.search_by_filters(cuisine_type="Martian")
        self.assertEqual(res, [])
