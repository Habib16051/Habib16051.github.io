from __future__ import absolute_import, print_function, unicode_literals

import copy
import re

import six
from django.core.exceptions import ValidationError
from django.template import TemplateSyntaxError, Context
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from wrapper_tag import utils
from wrapper_tag import docgen
from wrapper_tag import validators
from wrapper_tag.rendered import RenderedTag, SCRIPT_TAG

# regex type for isinstance
REGEX_TYPE = type(re.compile(''))


RENDER_METHOD_TAG = 1
RENDER_METHOD_ARGUMENT = 2


class Argument(utils.TemplateMixin):

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    # name is provided by tag metaclass
    name = None

    # logger instance
    logger = None

    _choices = None
    _default = None

    help_text = None
    readonly = False
    _tag_render_method = None
    validators = None
    extra_data = None

    render_method_type = None

    # signals
    on_data = None

    # default doc_group
    doc_group = docgen.ArgumentsGroup(_('Arguments'), help_text=_('Group of generic arguments'))

    def __init__(self, help_text=None, on_data=None, readonly=False, default=None,
                 validators=None, extra_data=None, choices=None, tag_render_method=None, **kwargs):
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Argument.creation_counter
        Argument.creation_counter += 1

        self.on_data = on_data
        self.extra_data = extra_data or {}
        self.help_text = help_text
        self.readonly = readonly
        self._tag_render_method = tag_render_method
        self._default = default

        if validators and not utils.is_seq(validators):
            validators = [validators]

        self.validators = validators or []
        self._choices = choices

        super(Argument, self).__init__(**kwargs)

    def __repr__(self):
        """
        Representation of argument
        :return:
        """
        return '<argument:{}:{} at 0x{:x}>'.format(self.name, self.__class__.__name__, id(self))

    @property
    def tag_clean_method(self):
        return 'clean_{}'.format(self.name)

    @property
    def tag_render_method(self):
        if self._tag_render_method:
            return self._tag_render_method
        return 'render_{}'.format(self.name)

    @property
    def template_errors(self):
        return {
            'no_template': 'Argument `{}` doesn\'t provide template or template_name'.format(self.name),
        }

    @property
    def default(self):
        """
        Default must be copied.
        :return:
        """
        if callable(self._default):
            return copy.deepcopy(self._default(self))
        return copy.deepcopy(self._default)

    @default.setter
    def default(self, value):
        self._default = value

    @property
    def choices(self):
        if callable(self._choices):
            return self._choices(self)
        return self._choices

    @choices.setter
    def choices(self, value):
        self._choices = value

    @property
    def rendered_key(self):
        return '{}__rendered'.format(self.name)

    def contribute_to_class(self, tag_cls, name):
        """
        Contribute to class
        :param tag_cls:
        :param name:
        :return:
        """

        def _clean_argument_(tag, argument, value):
            """
            Dummy clean_<argument> method
            """
            return value

        # check if clean_<argument> method is defined on tag, if not create dummy one
        tcl = getattr(tag_cls, self.tag_clean_method, None)
        if tcl is None:
            setattr(tag_cls, self.tag_clean_method, _clean_argument_)

        # check if render_<argument> method is defined on tag, if not assign `render`
        # @TODO: check arguments of render method
        trm = getattr(tag_cls, self.tag_render_method, None)
        if trm is None:
            self.render_method_type = RENDER_METHOD_ARGUMENT
        else:
            self.render = trm
            self.render_method_type = RENDER_METHOD_TAG
            # verify data_callback signature
            if utils.is_template_debug():
                utils.verify_func_signature(trm, 'argument', 'data', 'context', exact_names=True,
                                            prefix="{}.{}, ".format(tag_cls.__name__, self.name))

        # on_data signal receiver
        if self.on_data:
            if callable(self.on_data):
                tag_cls.on_data.connect(self.on_data)
            else:
                on_data = getattr(tag_cls, self.on_data, None)
                if on_data and callable(on_data):
                    tag_cls.on_data.connect(on_data)

    def full_clean(self, tag, value):
        """
        Internal!

        Do not override this method, rather provide `clean` method
        """
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError:
                value = self.default
                break

        value = getattr(tag, self.tag_clean_method)(self, value)
        value = self.clean(tag, value)
        return value

    def get_tag_value(self, args, kwargs):
        """
        Get keyword value from args/kwargs
        :param args:
        :param kwargs:
        :return:
        """
        if self.readonly:
            return self.default
        result = kwargs.pop(self.name, self.default)

        # if __raw__<name> was provided we use it as raw value (probably inherited from parent)
        # be careful though and use this just in situations you want to pass all values from parent
        if self.raw_key in kwargs:
            result = kwargs.pop(self.raw_key)

        return result

    def clean(self, tag, value):
        """
        This method should be overridden
        :param value:
        :return:
        """
        return value

    def full_render(self, tag, data, context):
        """
        Internal!

        :param data:
        :return:
        """

        with context.push(extra_data=self.extra_data, argument=self):
            if self.render_method_type == RENDER_METHOD_TAG:
                return self.render(tag, self, data, context)
            elif self.render_method_type == RENDER_METHOD_ARGUMENT:
                return self.render(tag, data, context)

    def render(self, tag, data, context):
        """
        Rendering function
        :param data:
        :return:
        """
        template = self.template

        if not template:
            return utils.NULL

        with context.push(**data):
            return template.render(context)
            # return template.render(Context(data))

    def gen_doc(self):
        """
        Generate documentation for argument
        :return:
        """

        doc = '``{}``'.format(self.name)

        if self.help_text:
            doc = '{} - {}'.format(doc, self.help_text)

        return doc

    @property
    def raw_key(self):
        return '__raw__{}'.format(self.name)


class Keyword(Argument):
    """
    Single keyword argument such as {% tag title="title" %}
    """

    # default doc_group
    doc_group = docgen.ArgumentsGroup(_('Keyword arguments'), priority=1000)

    def get_tag_value(self, args, kwargs):
        """
        Get keyword value from args/kwargs
        :param args:
        :param kwargs:
        :return:
        """
        value = super(Keyword, self).get_tag_value(args, kwargs)
        if self.choices and value not in self.choices:
            value = self.default
        return value

    def gen_doc(self):
        doc = super(Keyword, self).gen_doc()
        if self.choices:
            doc = '{}\n    * choices - {}'.format(doc, self.choices)
        if self.default:
            doc = '{}\n    * default - {}'.format(doc, self.default)
        return doc


class KeywordGroup(Argument):
    """
    Group of multiple keyword arguments.
    """

    source = None
    choices = None

    # default doc_group
    doc_group = docgen.ArgumentsGroup(_('Keyword arguments groups'),
                                      help_text=_('Group of keywords identified by "source". Source is a list of '
                                                  'regular expressions that keywords names match.'))

    def __init__(self, source=None, choices=None, **kwargs):
        kwargs['default'] = kwargs.pop('default', {})
        kwargs['choices'] = kwargs.pop('choices', {})
        super(KeywordGroup, self).__init__(**kwargs)

        # clean source
        self._set_source(source)

        self.choices = choices

        # check if sources are set
        if not self.readonly and not self.source and utils.get_config().template_debug:
            raise TemplateSyntaxError('keyword group must have source set.')

    def _set_source(self, source):
        """
        Clean source and convert to regular expression

        @TODO: probably source must be just simple list of strings (no flags) so user can add custom source.

        :return:
        """
        self.source = []
        if source is None:
            return

        if not utils.is_seq(source):
            source = [source]

        for item in source:
            self.source.append(item)

    @property
    def compiled_source(self):
        """
        Return list of regexes of sources.
        :return:
        """
        for item in self.source:
            yield re.compile('^{}$'.format(item.replace('+', '.+').replace('*', '.*')))

    def is_source(self, source):
        """
        Check if given source is one of sources
        :param source:
        :return:
        """
        for cs in self.compiled_source:
            if cs.match(source):
                return True
        return False

    def get_tag_value(self, args, kwargs):
        """
        Get keyword value from args/kwargs
        :param args:
        :param kwargs:
        :return:
        """
        result = self.default or {}

        if self.readonly:
            return result

        for key in kwargs.keys():
            for source in self.compiled_source:
                if source.match(key):
                    result[key] = kwargs.pop(key)

        return result

    def filter_data(self, data):
        """
        Filter data for sources
        :param data:
        :return:
        """
        result = {}
        cs = self.compiled_source
        for key in data.keys():
            for source in cs:
                if source.match(key):
                    result[key] = data[key]
        return result

    def gen_doc(self):
        doc = super(KeywordGroup, self).gen_doc()
        if self.source:
            doc = '{}\n    * source - {}'.format(doc, ", ".join(self.source))
        if self.choices:
            doc = '{}\n    * choices - {}'.format(doc, self.choices)
        if self.default:
            doc = '{}\n    * default:: ``{}``'.format(doc, self.default)
        return doc


class Positional(Argument):
    """
    Positional argument
    """

    varargs = False

    # default doc_group
    doc_group = docgen.ArgumentsGroupNaturalOrder(_('Positional arguments'),
                                                  help_text=_('Positional arguments support for tags'),
                                                  priority=9999)

    def __init__(self, varargs=False, *args, **kwargs):
        kwargs['default'] = kwargs.pop('default', [])
        super(Positional, self).__init__(*args, **kwargs)

        # is varargs?
        self.varargs = bool(varargs)

    def get_tag_value(self, args, kwargs):
        """
        Get keyword value from args/kwargs
        :param args:
        :param kwargs:
        :return:
        """
        result = self.default or []

        if self.varargs:
            while args:
                result.append(args.pop(0))
        else:
            if not args and utils.is_template_debug():
                raise TemplateSyntaxError('expected arg but no given')
            result.append(args.pop(0))

        return result

    def gen_doc(self):
        """
        Generate documentation for argument
        :return:
        """

        doc = super(Positional, self).gen_doc()

        if self.varargs:
            doc = '{}\n    * variable arguments count'.format(doc)

        return doc


class Event(Argument):
    """
    Event is shorthand for event arguments.

    Event has additional functionality to add `events` on RenderedTag.
    """

    # default doc_group
    doc_group = docgen.ArgumentsGroup(_('Events'), help_text=_('Event handlers that are available on rendered '
                                                               'tag `events` dictionary'), priority=0)

    def __init__(self, *args, **kwargs):
        kwargs['validators'] = kwargs.pop('validators', [])
        kwargs['validators'].append(validators.any(
            validators.requires_tag(SCRIPT_TAG),
            validators.string(),
        ))
        super(Event, self).__init__(*args, **kwargs)

    def contribute_to_class(self, tag_cls, name):
        """
        Patch render_wrapper_tag method on tag, to set 'events' on RenderedTag
        :param tag_cls: tag class
        :param name:
        :return:
        """
        super(Event, self).contribute_to_class(tag_cls, name)

        tag_cls.on_render_data.connect(self.on_render_data, dispatch_uid="events")

    def on_render_data(self, sender, data, context, **kwargs):
        """
        Add methods to rendered tag, to be accessible from template
        :param sender:
        :param data:
        :param context:
        :param kwargs:
        :return:
        """
        if 'events__' not in data:
            data['events__'] = {}

        for _, argument in six.iteritems(sender.arguments):
            if not isinstance(argument, Event):
                continue

            if argument.name in data and argument.rendered_key in data:
                data['events__'][argument.name] = data[argument.rendered_key]


class Method(Argument):

    # default doc_group
    doc_group = docgen.ArgumentsGroup(_('Methods'), help_text=_('Methods that are available on rendered '
                                                                'tag `methods` dictionary'), priority=0)

    def contribute_to_class(self, tag_cls, name):
        """
        Patch render_wrapper_tag method on tag, to set 'events' on RenderedTag
        :param tag_cls: tag class
        :param name:
        :return:
        """
        super(Method, self).contribute_to_class(tag_cls, name)

        tag_cls.on_render_tag.connect(self.on_render_tag, dispatch_uid="methods")

    def on_render_tag(self, sender, rendered_tag, data, context, **kwargs):
        """
        Add methods to rendered tag, to be accessible from template
        :param sender:
        :param rendered_tag:
        :param data:
        :param context:
        :param kwargs:
        :return:
        """
        if rendered_tag.get('methods', None) is None:
            rendered_tag['methods'] = {}

        for _, argument in six.iteritems(sender.arguments):
            if not isinstance(argument, Method):
                continue

            if argument.rendered_key in data:
                rendered_tag['methods'][argument.name] = RenderedTag(data[argument.rendered_key], SCRIPT_TAG)


class Hyperlink(KeywordGroup):
    """
    Hyperlink argument groups functionality for plain href and also for url reversing abilities
    """

    def __init__(self, *args, **kwargs):
        kwargs['source'] = ('href', 'url', 'url_kwarg_*', 'url_arg_*', 'url_query')
        kwargs['default'] = {
            'href': '#'
        }
        super(Hyperlink, self).__init__(*args, **kwargs)

    def render(self, argument, data, context):
        """
        Return rendered hyperlink
        :param data: tag data
        :param context: render context
        :return:
        """
        value = data[self.name]

        if 'url' in value:
            kwarg_keys = utils.find_elements('url_kwarg_*', value.keys())
            arg_keys = utils.find_elements('url_arg_*', sorted(value.keys()))
            url_kwargs = {k.lstrip('url_kwarg_'): v for k, v in six.iteritems(value) if k in kwarg_keys}
            url_args = [value[v] for v in arg_keys]

            rev = reverse(value['url'], args=url_args, kwargs=url_kwargs)
            if 'url_query' in value and value['url_query']:
                rev = '{}?{}'.format(rev, value['url_query'])
            return rev
        return value['href']
