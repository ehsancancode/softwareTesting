import unittest
from Restaurant_Browsing import RestaurantDatabase, RestaurantBrowsing

class TestRestaurantBrowsing(unittest.TestCase):
    """Unit tests for RestaurantBrowsing functionality."""

    def setUp(self):
        self.database = RestaurantDatabase()
        self.browsing = RestaurantBrowsing(self.database)

    def test_search_by_cuisine(self):
        """Should return all restaurants matching a cuisine."""
        results = self.browsing.search_by_cuisine("Italian")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["cuisine"] == "Italian" for r in results))

    def test_search_by_location(self):
        """Should return all restaurants in a specific location."""
        results = self.browsing.search_by_location("Downtown")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["location"] == "Downtown" for r in results))

    def test_search_by_rating(self):
        """Should return all restaurants above the given rating."""
        results = self.browsing.search_by_rating(4.0)
        self.assertEqual(len(results), 4)
        self.assertTrue(all(r["rating"] >= 4.0 for r in results))

    def test_search_by_filters(self):
        """Should combine multiple filters."""
        results = self.browsing.search_by_filters(
            cuisine_type="Italian", location="Downtown", min_rating=4.0
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Italian Bistro")

if __name__ == "__main__":
    unittest.main()
