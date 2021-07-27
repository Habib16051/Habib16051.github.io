from .core import BaseWrapper


class ZomatoAPIWrapper(BaseWrapper):

    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = 'https://developers.zomato.com/api/v2.1/'
        self._endpoint = None
        self.headers = {'user-key': self.api_key}

    def get_categories(self):
        """ get categories """
        endpoint = self.endpoint + 'categories'
        return self._get_endpoint(endpoint)

    @staticmethod
    def parse_request(**kwargs):
        latitude = None
        longitude = None
        city_name = kwargs.get('city_name', None)
        city_id = kwargs.get('city_id', None)
        cordinates = kwargs.get('cordinates', None)
        if city_name:
            city_name = city_name

        if cordinates:
            if 'latitude' and 'longitude' in cordinates:
                latitude = cordinates['latitude']
                longitude = cordinates['longitude']
        return city_name, city_id, latitude, longitude

    def get_city(self, **kwargs):
        """ get details about the city"""
        city_name, _, latitude, longitude = self.parse_request(**kwargs)
        if city_name:
            self._endpoint = 'cities?q=%s' % city_name
        if latitude and longitude:
            self._endpoint = 'cities?lat=%s&lon=%s' % (latitude, longitude)

        if not self._endpoint:
            raise ValueError('no endpoint')

        endpoint = self.endpoint + self._endpoint
        return self._get_endpoint(endpoint)

    def get_collections(self, **kwargs):
        """ get collections is the given city """
        _, city_id, latitude, longitude = self.parse_request(**kwargs)
        if city_id:
            self._endpoint = 'collections?city_id=%s' % city_id
        if latitude and longitude:
            self._endpoint = 'collections?lat=%s&lon=%s' % (latitude, longitude)

        if not self._endpoint:
            raise ValueError('no endpoint')

        endpoint = self.endpoint + self._endpoint + '&count=100'
        return self._get_endpoint(endpoint)

    def get_cuisines(self, **kwargs):
        """ get cusisines available at the given locaton """
        _, city_id, latitude, longitude = self.parse_request(**kwargs)
        if city_id:
            self._endpoint = 'cuisines?city_id=%s' % city_id
        if latitude and longitude:
            self._endpoint = 'cuisines?lat=%s&lon=%s' % (latitude, longitude)

        if not self._endpoint:
            raise ValueError('no endpoint')

        endpoint = self.endpoint + self._endpoint
        return self._get_endpoint(endpoint)

    def get_restaurant_types(self, **kwargs):
        """ gets the restaurant types in given city """
        _, city_id, latitude, longitude = self.parse_request(**kwargs)
        if city_id:
            self._endpoint = 'establishments?city_id=%s' % city_id
        if latitude and longitude:
            self._endpoint = 'establishments?lat=%s&lon=%s' % (latitude, longitude)

        if not self._endpoint:
            raise ValueError('no endpoint')

        endpoint = self.endpoint + self._endpoint
        return self._get_endpoint(endpoint)

    def search(self, **kwargs):
        """ vets tje restaturants in the given city """
        _, city_id, latitude, longitude = self.parse_request(**kwargs)
        query = kwargs.get('query', None)
        if latitude and longitude:
            self._endpoint = 'establishments?lat=%s&lon=%s' % (latitude, longitude)
        if not self._endpoint or not query:
            raise ValueError('no endpoint')

        endpoint = self.endpoint + 'search?q=%s&lat=%s&lon=%s&radius=50000' % (query, latitude, longitude)
        return self._get_endpoint(endpoint)

    def get_top_restaurants(self, location_id, entity_type='city'):
        """ get the top restaurants in the given city """
        endpoint = self.endpoint + 'location_details?entity_id=%s&entity_type=%s' % (location_id, entity_type)
        return self._get_endpoint(endpoint)

    def get_daily_menu(self, restaurant_id):
        """" get the daily menu for the given restaurant if available """
        endpoint = self.endpoint + '/dailymenu?res_id=%s' % restaurant_id
        return self._get_endpoint(endpoint)

    def geocode(self, latlon):
        """ geocode the given location """
        lat, lon = latlon.split(',')
        endpoint = self.endpoint + "geocode?lat=%s&lon=%s" % (lat, lon)
        return self._get_endpoint(endpoint)

    def get_restaurant_details(self, restaurant_id):
        """ gets the details of the restaurant for the given restaurant id """
        endpoint = self.endpoint + '/restaurant?res_id=%s' % restaurant_id
        return self._get_endpoint(endpoint)

    def get_restaurant_review(self, restaurant_id):
        """ gets the reviews for the restaurant of the given restaurant id """
        endpoint = self.endpoint + 'reviews?res_id=%s' % restaurant_id
        return self._get_endpoint(endpoint)
