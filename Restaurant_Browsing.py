class RestaurantBrowsing:
    """
    Browse restaurants based on cuisine, location, or rating.
    """
    def __init__(self, database):
        self.database = database

    def search_by_cuisine(self, cuisine_type):
        return [
            r for r in self.database.get_restaurants()
            if r["cuisine"].lower() == cuisine_type.lower()
        ]

    def search_by_location(self, location):
        return [
            r for r in self.database.get_restaurants()
            if r["location"].lower() == location.lower()
        ]

    def search_by_rating(self, min_rating):
        return [
            r for r in self.database.get_restaurants()
            if r["rating"] >= min_rating
        ]

    def search_by_filters(self, cuisine_type=None, location=None, min_rating=None):
        results = self.database.get_restaurants()
        if cuisine_type:
            results = [r for r in results if r["cuisine"].lower() == cuisine_type.lower()]
        if location:
            results = [r for r in results if r["location"].lower() == location.lower()]
        if min_rating:
            results = [r for r in results if r["rating"] >= min_rating]
        return results


class RestaurantDatabase:
    """
    Simple in-memory restaurant database.
    """
    def __init__(self):
        self.restaurants = [
            {"name": "Italian Bistro", "cuisine": "Italian", "location": "Downtown", "rating": 4.5, "price_range": "$$", "delivery": True},
            {"name": "Sushi House", "cuisine": "Japanese", "location": "Midtown", "rating": 4.8, "price_range": "$$$", "delivery": False},
            {"name": "Burger King", "cuisine": "Fast Food", "location": "Uptown", "rating": 4.0, "price_range": "$", "delivery": True},
            {"name": "Taco Town", "cuisine": "Mexican", "location": "Downtown", "rating": 4.2, "price_range": "$", "delivery": True},
            {"name": "Pizza Palace", "cuisine": "Italian", "location": "Uptown", "rating": 3.9, "price_range": "$$", "delivery": True},
        ]

    def get_restaurants(self):
        return self.restaurants


class RestaurantSearch:
    """
    User-facing search interface that wraps RestaurantBrowsing.
    """
    def __init__(self, browsing):
        self.browsing = browsing

    def search_restaurants(self, cuisine=None, location=None, rating=None):
        return self.browsing.search_by_filters(
            cuisine_type=cuisine, location=location, min_rating=rating
        )
