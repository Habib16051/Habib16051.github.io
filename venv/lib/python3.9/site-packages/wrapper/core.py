import requests


class BaseWrapper(object):
    """
    Wraps requests methods header
    """
    headers = {}
    api_key = None
    endpoint = None
    data = None

    def _get_endpoint(self, url):
        return requests.get(url, headers=self.headers)

    def _post_endpoint(self, url):
        return requests.post(url, data=self.data, headers=self.headers)
