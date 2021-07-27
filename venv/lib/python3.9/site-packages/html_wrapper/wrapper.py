from typing import Union, Dict, AnyStr, Any, Optional, \
    Iterable, Tuple, List
from functools import lru_cache
from abc import ABC

from lxml.html import HtmlElement, fromstring, tostring
from lxml.etree import XPath


NO_TEXT: str = ''
NO_ATTRS: Dict[str, str] = {}
SKIP_COMMA: int = -len(', ')

STR_ENCODING: str = 'unicode'
BS4_TYPES: Tuple[str] = "Tag", "BeautifulSoup"
COLLECTIONS: Tuple[type] = set, list, tuple


Attrs = Union[str, Dict[str, str]]
CssClassType = str


class BeautifulSoupMethods(ABC):
    """
    This is the subset of the BS4 API that is implemented
    """

    def __init__(self, html):
        pass

    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass

    def __getitem__(self, item: str) -> str:
        pass

    def __getattr__(self, item: str) -> Any:
        pass

    @property
    def text(self) -> str:
        pass

    @property
    def string(self) -> str:
        pass

    def name(self) -> str:
        pass

    def find(
        self,
        tag: str,
        attrs: Attrs = NO_ATTRS,
        *,
        class_: Optional[CssClassType] = None,
        **kwargs
    ) -> Optional['HtmlWrapper']:
        pass

    def find_all(
        self,
        tag: str,
        attrs: Attrs = NO_ATTRS,
        *,
        class_: Optional[CssClassType] = None,
        gen: bool = False,
        **kwargs
    ) -> 'Wrappers':
        pass


class HtmlWrapper(BeautifulSoupMethods):
    """
    An lxml adapter over a subset of the BeautifulSoup API
    """

    __slots__ = ['html']

    def __init__(self, html):
        if isinstance(html, (str, bytes)):
            self.html = fromstring(html)

        elif isinstance(html, HtmlWrapper):
            self.html = html.html

        elif isinstance(html, HtmlElement):
            self.html = html

        elif isinstance(html, BS4_TYPES):
            self.html = fromstring(str(html))

        else:
            name = str(type(html))
            msg = f"Object of type {name} not compatible with HtmlWrapper"

            raise TypeError(msg)

    def __repr__(self) -> str:
        return f'{self.__name__}: {repr(self.html)}'

    def __str__(self) -> str:
        string = tostring(self.html, encoding=STR_ENCODING)
        return string.strip()

    def __getitem__(self, item) -> str:
        items = self.html.attrib[item]

        if item == 'class':
            items = items.split(' ')

        return items

    def __getattr__(self, item) -> Any:
        val = self.find(item)

        if val is None:
            if hasattr(self.html, item):
                return getattr(self.html, item)

            else:
                return None

        else:
            return val

    @property
    def text(self) -> str:
        text = self.html.text_content()

        return text if text else NO_TEXT

    @property
    @lru_cache
    def string(self):
        return self.html.text.strip()

    def name(self) -> str:
        return self.html.tag

    def find(
        self,
        tag: str,
        attrs: Attrs = NO_ATTRS,
        *,
        class_: Optional[CssClassType] = None,
        **kwargs
    ) -> Optional['HtmlWrapper']:
        return find(self.html, tag, attrs, class_=class_, **kwargs)

    def find_all(
        self,
        tag: str,
        attrs: Attrs = NO_ATTRS,
        *,
        class_: Optional[CssClassType] = None,
        gen: bool = False,
        **kwargs
    ) -> 'Wrappers':
        return find_all(self.html, tag, attrs, class_=class_, gen=gen, **kwargs)


Wrappers = Union[Tuple[HtmlWrapper, ...], Iterable[HtmlWrapper]]


def find(
    html: HtmlElement,
    tag: str,
    attrs: Attrs = NO_ATTRS,
    class_: Optional[CssClassType] = None,
    **kwargs
) -> Optional[HtmlWrapper]:
    if isinstance(attrs, str):
        class_ = attrs
        attrs = NO_ATTRS

    elif isinstance(attrs, dict):
        kwargs.update(attrs)

    results = find_all(html, tag, attrs, class_, gen=True, **kwargs)

    return next(results) if results else None


def find_all(
    html: HtmlElement,
    tag: str,
    attrs: Attrs = NO_ATTRS,
    class_: Optional[CssClassType] = None,
    gen: bool = False,
    **kwargs
) -> Wrappers:
    if isinstance(attrs, str):
        class_ = attrs
        attrs = NO_ATTRS

    elif isinstance(attrs, dict):
        kwargs.update(attrs)

    xpath = get_xpath(tag, class_, **kwargs)
    elems = xpath(html)

    if not elems:
        return tuple()

    wrapper_map = map(HtmlWrapper, elems)  # returns an iterator

    return wrapper_map if gen else tuple(wrapper_map)


def get_xpath_str(tag: str, class_: CssClassType = None, **kwargs) -> str:
    tags: List[str] = [f'.//{tag}']

    if class_:
        kwargs['class'] = class_

    for attr, val in kwargs.items():
        tags.append('[')
        attr_xp = f'@{attr}'

        if isinstance(val, bool):
            if val:
                tags.append(attr_xp)

            else:
                tags.append(f'not({attr_xp})')

        elif isinstance(val, COLLECTIONS):
            for item in val:
                val_xp = f'"{item}", '

            val_xp = val_xp[:SKIP_COMMA] if val else NO_TEXT
            tags.append(f'contains({attr_xp}, {val_xp})')

        elif isinstance(val, str):
            tags.append(f'contains({attr_xp}, "{val}")')

        else:
            tags.append(f"{attr_xp}='{val}'")

        tags.append(']')

    return ''.join(tags)


@lru_cache(maxsize=None)
def get_xpath(tag: str, class_: CssClassType = None, **kwargs) -> XPath:
    xpath_str = get_xpath_str(tag, class_, **kwargs)

    return XPath(xpath_str)
