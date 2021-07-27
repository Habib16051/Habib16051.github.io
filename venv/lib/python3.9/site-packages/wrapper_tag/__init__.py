from __future__ import unicode_literals, print_function, absolute_import
from wrapper_tag.arguments import Keyword, KeywordGroup, Event, Method, Hyperlink, Positional
from wrapper_tag.rendered import RenderedTag, SCRIPT_TAG
from wrapper_tag.tag import Tag
from wrapper_tag.utils import register_tag

__version__ = "0.1.17"


default_app_config = 'wrapper_tag.apps.WrapperTagConfig'

__all__ = (
    'Keyword', 'KeywordGroup', 'Event', 'Method', 'Hyperlink', 'Positional',
    'RenderedTag', 'SCRIPT_TAG',
    'Tag',
    'register_tag',
)
