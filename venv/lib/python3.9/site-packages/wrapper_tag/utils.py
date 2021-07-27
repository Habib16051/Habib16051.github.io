"""
Various helper utilities for wrapper tag
"""
from __future__ import absolute_import, print_function, unicode_literals

import random
import re

from django import get_version
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, RequestContext, Template
from django.template import TemplateSyntaxError
from django.template.base import token_kwargs
from django.template.context import BaseContext
from django.template.loader import get_template

from distutils.version import LooseVersion

from django.utils import inspect
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible

from logging import getLogger

logger = getLogger("wrapper_tag")


DJANGO_1_9_OR_HIGHER = (
    LooseVersion(get_version()) >= LooseVersion('1.9')
)

# pattern for camel_to_separated
CAMEL_TO_SEPARATED = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

# regex type for isinstance
REGEX_TYPE = type(re.compile(''))

# max rand value to generate id
ID_RAND_MAX = 2 ** 32


class NULL:
    """
    Internal type
    """


def camel_to_separated(s, separator='.'):
    """
    Returns dotted_case from CamelCase
    :param separator: separator to join multiple parts of name
    :param s: string to convert
    :return:
    """
    return CAMEL_TO_SEPARATED.sub(separator + r'\1', s).lower()


def flatten_context(context):
    def do_flatten(context):
        flat = {}
        for d in context.dicts:
            if isinstance(d, (Context, RequestContext)):
                flat.update(do_flatten(d))
            else:
                flat.update(d)
        return flat

    if callable(getattr(context, 'flatten', None)) and DJANGO_1_9_OR_HIGHER:
        return context.flatten()
    elif isinstance(context, BaseContext):
        return do_flatten(context)
    return context


def get_config():
    """
    Return wrapper tag config
    :return wrapper_tag.apps.WrapperTagConfig:
    """
    return apps.get_app_config('wrapper_tag')


def parse_bits(parser, bits, name):
    """
    Taken from django code and enhanced (params accept also wildcard on the end of string

    Parses bits for template tag helpers (simple_tag, include_tag and
    assignment_tag), in particular by detecting syntax errors and by
    extracting positional and keyword arguments.
    :param name:
    :param bits:
    :param parser:
    """
    args = []
    kwargs = {}
    for bit in bits:
        # First we try to extract a potential kwarg from the bit
        kwarg = token_kwargs([bit], parser)
        if kwarg:
            # The kwarg was successfully extracted
            param, value = list(six.iteritems(kwarg))[0]
            if param in kwargs:
                # The keyword argument has already been supplied once
                raise TemplateSyntaxError(
                    "'%s' received multiple values for keyword argument '%s'" %
                    (name, param))
            else:
                # All good, record the keyword argument
                kwargs[str(param)] = value
        else:
            if kwargs:
                raise TemplateSyntaxError(
                    "'%s' received some positional argument(s) after some "
                    "keyword argument(s)" % name)
            else:
                # Record the positional argument
                args.append(parser.compile_filter(bit))

    return args, kwargs


class TemplateMixin(object):

    template_errors = {
        'no_template': 'Please provide template or template_name',
    }

    def __init__(self, template=None, template_name=None):
        self._template = template
        self._template_name = template_name

    @property
    def template(self):
        if self._template:
            return Template(self._template)
        elif self._template_name:
            return get_template(self._template_name)


def get_sub_logger(logger, *names):
    """
    Return sub logger
    :param logger:
    :param name:
    :return:
    """
    if not names:
        return logger
    return getLogger('{}.{}'.format(logger.name, '.'.join(names)))


def is_seq(iterable):
    """
    Returns whether iterable is list|tuple
    :param iterable:
    :return:
    """
    return isinstance(iterable, (list, tuple))


def is_template_debug():
    """
    Returns whether template debug is enabled
    :return:
    """
    return bool(getattr(settings, 'TEMPLATE_DEBUG', False))


def is_rendered_tag(value, tag):
    """
    Returns whether it was stored with "as" attribute
    :param value:
    :param tag:
    :return:
    """
    from wrapper_tag import RenderedTag
    if not isinstance(value, RenderedTag):
        return False

    return tag == value.tag


def verify_func_signature(func, *args, **kwargs):
    """
    verify signature of function
    :param func:
    :return:
    """
    spec = inspect.getargspec(func)
    need_star_kwargs = kwargs.pop('need_star_kwargs', False)
    exact_names = kwargs.pop('exact_names', False)
    prefix = kwargs.pop('prefix', '')
    enable_if = kwargs.pop('enable_if', True)
    enabled = enable_if() if callable(enable_if) else enable_if

    if not enabled:
        return

    if spec.args and spec.args[0] == 'self':
        spec_args = spec.args[1:]
    else:
        spec_args = spec.args

    func_name = func.__name__
    if need_star_kwargs and not spec.keywords:
        raise ImproperlyConfigured('{}function {}, does not accept **kwargs.'.format(prefix, func_name))

    if len(spec_args) != len(args):
        raise ImproperlyConfigured('{}function {}, signature does not match to: {}.'.format(prefix, func_name, args))

    if exact_names:
        for i in range(len(args)):
            if spec_args[i] != args[i]:
                raise ImproperlyConfigured('{}function {}, must have exact arg names: {}, got: {}.'.format(
                    prefix, func_name, args, spec_args))


def find_elements(item, iterable):
    """
    Finds elements with wildcard in iterable (list, tuple..)
    Both item and iterable can be wildcarded.

    :param item: item to be found
    :param iterable: list/tuple of elements to find in..
    :return: list of found
    """
    result = []

    if not isinstance(item, REGEX_TYPE):
        pattern = '^{}$'.format(item.replace('+', '.+').replace('*', '.*'))
        item = re.compile(pattern)

    for value in iterable:
        if item.match(value):
            result.append(value)

    return result


def register_tag(library, **kwargs):
    """
    Register WrapperTag class
    :param library:
    :param kwargs:
    :return:

    @TODO: Add support for aliases.
    @TODO: add support for signals
    @TODO: add support for class prepared
    """

    signals = {
        "on_data": kwargs.pop('on_data', None),
        "on_render_data": kwargs.pop('on_render_data', None),
        "on_render_tag": kwargs.pop('on_render_data', None),
        "on_register": kwargs.pop('on_register', None),
    }

    # def get_library_name(cls):
    #     """
    #     Returns library name
    #     :param cls:
    #     :return:
    #     """
    #     return repr(cls).split('.')[-2]

    def wrap(cls):

        from wrapper_tag import Tag
        if not issubclass(cls, Tag) and is_template_debug():
            raise ImproperlyConfigured("Class {} is not WrapperTag instance".format(cls))

        from wrapper_tag import docgen

        cls.__doc__ = docgen.generate(cls)

        # add main library tag
        library.tag(cls.options.start_tag, cls)

        # bind signals
        for signal, func in six.iteritems(signals):
            if not callable(func):
                continue
            s = getattr(cls, signal)
            s.connect(func, dispatch_uid=signal)

        # send on_register signal
        # @TODO: add this code also to aliases
        cls.on_register.send_robust(sender=cls)

        logger.debug("Registered `%s`=>`%s` wrapper tag.", cls.options.start_tag, cls.options.end_tag)

        # # set library_name
        # cls.options.library_name = get_library_name(cls)

        # aliases = []
        # for alias in cls.options.aliases:
        #     if is_seq(alias):
        #         start_tag, end_tag = alias[0], alias[1]
        #     else:
        #         start_tag, end_tag = alias, 'end:{}'.format(alias)
        #     aliases.append({
        #         'start_tag': start_tag,
        #         'end_tag': end_tag,
        #     })
        #
        # doc = cls.gen_doc(aliases=aliases)

        # # register_tag also aliases (if available)
        # for alias in aliases:
        #     new_wrapper_tag_class = type(str('Alias_{}_{}'.format(alias, cls.__name__)), cls.__bases__,
        #                                  dict(cls.__dict__))
        #     new_wrapper_tag_class.options.start_tag = alias['start_tag']
        #     new_wrapper_tag_class.options.end_tag = alias['end_tag']
        #
        #     new_doc = cls.gen_doc(alias_to=cls.options.start_tag)
        #     library.tag(alias['start_tag'], init_outer(new_wrapper_tag_class, doc=new_doc))


        return cls

    return wrap


@python_2_unicode_compatible
class StringSet(set):
    """
    StringSet is set that provides method to return string value.
    """

    def __str__(self):
        return " ".join(self)

    def __repr__(self):
        return "'{}'".format(str(self))

    def add(self, value):
        for v in value.split(" "):
            if not v:
                continue
            super(StringSet, self).add(v)


def generate_id(rand_max=ID_RAND_MAX, prefix="id_"):
    """
    Generate random identifier
    :return:
    """
    return '{}{}'.format(prefix, random.randint(0, rand_max))
