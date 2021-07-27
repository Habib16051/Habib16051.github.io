from .core import BaseWrapper
import json


class LocuAPIWrapper(BaseWrapper):

    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = 'https://api.locu.com/v2/venue/search'

    def search_restaurant(self, **kwargs):
        """ search api v2 """
        locality = kwargs.get('locality', None)
        location = kwargs.get('location', None)
        locu_id = kwargs.get('locu_id', None)

        params = {

            "fields": [
                "name",
                "location",
                "categories",
                "description"
            ],
            "venue_queries": [
                {
                    "categories": {
                        "$contains_any": ["restaurant", "hotel"]
                    }
                }
            ],
            "api_key": self.api_key
        }

        if locality:
            params['venue_queries'][0]['location'] = {"locality": locality}
        if location:
            latitude, longitue = location.split(',')
            params['venue_queries'][0]['location'] = {"geo": {"$in_lat_lng_radius": [latitude, longitue, 5000]}}
        if locu_id:
            params['fields'].append('menus')
            params['venue_queries'][0]['locu_id'] = locu_id

        self.data = json.dumps(params)
        return self._post_endpoint(self.endpoint)

    def get_restaurant_details(self, venue_id):
        """ get the deatils of the given venu_id """
        endpoint = 'http://api.locu.com/v1_0/venue/%s/?api_key=%s' % (venue_id, self.api_key)
        return self._get_endpoint(endpoint)

    def get_restuarants_with_menu(self, query):
        """ get the list of restaurants with menuus that match the given query """
        endpoint = 'http://api.locu.com/v1_0/venue/search/?api_key=%s&has_menu=true&%s' % (self.api_key, query)
        return self._get_endpoint(endpoint)

