class CMSError(Exception):
    pass


class LinkAttributeError(CMSError):
    def __init__(self, code=None, params=None):
        super().__init__(
            "You need to put inside css_start something static like this :"
            "<link rel='stylesheet' href='/static/django_css_inline/test-1.css'>"
            "or external like this : "
            "<link rel='stylesheet' href='https://exemple.com/test-1.css'>",
            500,
            params
        )
