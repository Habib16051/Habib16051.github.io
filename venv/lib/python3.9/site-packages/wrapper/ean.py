from .core import BaseWrapper
import barcodenumber


class EANDataAPIWrapper(BaseWrapper):
    """ 
    Use EANdata.com's API to parse Barcode data
    URL_EXAMPLE: http://eandata.com/feed/?v=3&keycode=<your key code >&mode=json&find=<ean code>
    """

    def __init__(self):
        self.api_key = '2224F10258F8617D'
        self.endpoint = 'http://eandata.com/feed/?v=3&keycode=%s&mode=json&find=' % self.api_key

    def get_barcode_data(self, barcode):
        """ get the product info from barcode """
        if not barcodenumber.check_code_ean13(barcode):
            if not barcodenumber.check_code_upca(barcode):
                raise ValueError('Invalid Barcode')
        endpoint = self.endpoint + barcode
        return self._get_endpoint(endpoint)

