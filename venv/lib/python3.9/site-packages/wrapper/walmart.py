from .core import BaseWrapper


class WalmartAPIWrapper(BaseWrapper):
    """
    
    A wrapper around walmart API
    
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = 'http://api.walmartlabs.com/v1/'

    def _process_response(self, endpoint):
        return self._get_endpoint(endpoint)

    def search_item(self, term):
        """ search product by upc """
        endpoint = self.endpoint + 'search?format=json&facet=on&apiKey=%s&query=%s' % (self.api_key, term)
        return self._process_response(endpoint)

    def get_food_products(self, category_id='976759'):
        """ get products by id default is for food """
        endpoint = self.endpoint + "paginated/items?category=%sa&apiKey=%s&format=json" % category_id, self.api_key
        return self._process_response(endpoint)

    def product_recommendation(self, product_id):
        """ get recommednded products for the given product id """
        endpoint = self.endpoint + "nbp?apiKey=%s&itemId=%s&format=json" % (self.api_key, product_id)
        return self._process_response(endpoint)

    def product_history(self, product_id):
        """ get the history of products related to given product id """
        endpoint = self.endpoint + "postbrowse?apiKey=%s&itemId=%s&format=json" % (self.api_key, product_id)
        return self._process_response(endpoint)

    def get_item_review(self, product_id):
        """ get reviews for the given prodcuct """
        endpoint = self.endpoint + "reviews/%s?apiKey=%s&format=json" % (product_id, self.api_key)
        return self._process_response(endpoint)

    def get_best_sellers(self, category_id='976759'):
        """ get the best sellers in the category. default is food"""
        endpoint = self.endpoint + "feeds/bestsellers?apikey=%s&categoryId=%s" % self.api_key, category_id
        return self._process_response(endpoint)

    def get_rollback_items(self, category_id='976759'):
        """ get the roll back items in the given category. default is food """
        endpoint = self.endpoint + "feeds/rollback?apikey=%s&amp;categoryId=%s" % self.api_key, category_id
        return self._process_response(endpoint)

    def get_clearance_items(self, category_id='976759'):
        """ get clearane items for the given category. default is food """
        endpoint = self.endpoint + 'feeds/clearance?apikey=%s&amp;categoryId=%s' % self.api_key, category_id
        return self._process_response(endpoint)

    def store_locator(self, **kwargs):
        """ locates the closest store to the given location"""
        query = None
        cordinates = kwargs.get('cordinates', None)
        city = kwargs.get('city', None)
        zip = kwargs.get('zip', None)

        if cordinates:
            lat, lon = cordinates.split(',')
            if lat and lon:
                query = "lat=%s&lon=%s" % (lat, lon)
        if city:
            query = "city=%s" % city

        if zip:
            query = "zip=%s" % zip

        if not query:
            raise ValueError

        endpoint = self.endpoint + "stores?apiKey=%s&format=json&%s" % (self.api_key, query)
        return self._process_response(endpoint)
