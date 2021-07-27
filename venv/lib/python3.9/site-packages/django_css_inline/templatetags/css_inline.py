import urllib
import gzip
import shutil
import logging
from html.parser import HTMLParser
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import format_html, mark_safe
from django.conf import settings

from django_css_inline.exceptions import LinkAttributeError

register = template.Library()

logger = logging.getLogger('django_css_inline')


class LinksHTMLParser(HTMLParser):
    style_content = ''
    external = ''

    def render_style_content(self):
        if self.style_content:
            return format_html(
                "<style type=\"text/css\">{}</style>{}",
                mark_safe(self.style_content),
                mark_safe(self.external)
            )
        return None

    def render_link(self, href):
        return "<link rel=\"stylesheet\" href=\"%s\">" % href

    def handle_starttag(self, tag, attrs):
        """
        :param tag : link, div...
        :param attrs : [('href', '/static/dist/css/cms-x.x.x.css'), ('rel', 'stylesheet')]
        """

        if tag == 'link':
            attrs_dict = dict(attrs)
            try:
                href = attrs_dict['href']
                rel = attrs_dict['rel']
            except NameError:
                raise LinkAttributeError()

            if rel == 'stylesheet':
                # External
                if href.startswith('https://') or href.startswith('//'):
                    try:
                        style_file = urllib.request.urlopen(href)
                        style_content = style_file.read()
                        try:
                            self.style_content += style_content.decode("utf-8")
                        except UnicodeDecodeError:
                            # Gzip file
                            self.style_content += gzip.decompress(style_content).decode("utf-8")
                    except urllib.error.HTTPError:
                        pass
                # Django Static
                elif href.startswith(settings.STATIC_URL):
                    style_path_static = href.replace(settings.STATIC_URL, '')
                    style_file = staticfiles_storage.open(style_path_static)
                    self.style_content += style_file.read().decode("utf-8")


class LinksNode(template.Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        if getattr(settings, 'DJANGO_CSS_INLINE_ENABLE', True):
            html = self.nodelist.render(context)
            parser = LinksHTMLParser()
            parser.feed(html)
            style_content = parser.render_style_content()
            logger.debug(style_content)
            if style_content:
                return style_content
            return self.nodelist.render(context)
        return self.nodelist.render(context)


@register.tag
def css_inline(parser, token):
    nodelist = parser.parse(('end_css_inline',))
    parser.delete_first_token()
    return LinksNode(nodelist=nodelist)
