"""
Documentation generator for WrapperTag
"""
import textwrap
from collections import OrderedDict
from operator import attrgetter

import six
from django.utils.encoding import force_text, smart_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class ArgumentsGroup(object):
    """
    ArgumentGroup groups classes of arguments in documentation


    Every custom argument class needs to provide `doc_group` attribute, so docgen knows how to group arguments in
    documentation.

    Example::

        class Event(Argument):
            doc_group = docgen.ArgumentsGroup(_('Events'), help_text=_('Event handlers that are available on rendered '
                                                               'tag `events` dictionary'), priority=0)

    This will ensure that all events are groupped in group 'Events' in tag documentation.
    """

    help_text = None
    priority = None
    title = None

    def __init__(self, title, help_text=None, priority=100):
        """

        :param title: title of arguments group
        :param help_text: short description
        :param priority: priority how to order groups
        """
        self.title = title
        self.help_text = help_text
        self.priority = priority

    def render(self, arguments):
        """
        render renders documentation for arguments
        :param arguments:
        :return:
        """
        doc = format_html("**{}**", self.title) + "\n\n"

        if self.help_text:
            doc += "*{}*\n\n".format(force_text(self.help_text))

        for argument in arguments:
            doc += "* {doc}\n".format(doc=smart_text(argument.gen_doc()))

        return mark_safe(doc)

    @classmethod
    def group_arguments(cls, tag_cls):
        """
        Group tag arguments by `doc_group` and return ordered dict where key is ArgumentsGroup instance
        :param tag_cls:
        :return:
        """
        groups = {}
        for _, argument in six.iteritems(tag_cls.arguments):
            if groups.get(argument.doc_group, None) is None:
                groups[argument.doc_group] = []

            groups[argument.doc_group].append(argument)

        result = OrderedDict()
        for key in sorted(groups.keys(), key=attrgetter('priority'), reverse=True):
            result[key] = sorted(groups[key], key=attrgetter('name'))

        return result


class ArgumentsGroupNaturalOrder(ArgumentsGroup):

    def render(self, arguments):
        """
        render renders documentation for arguments
        :param arguments:
        :return:
        """
        arguments = sorted(arguments, key=attrgetter('creation_counter'))
        return super(ArgumentsGroupNaturalOrder, self).render(arguments)


def generate(tag_cls):
    """
    generate generates documentation for given wrapper tag class
    :param tag_cls: wrapper_tag class
    :return:
    """

    doc = textwrap.dedent(tag_cls.__doc__ or '').strip()

    arguments_doc = ""

    for ag, arguments in six.iteritems(ArgumentsGroup.group_arguments(tag_cls)):
        filtered = filter(lambda x: not x.readonly, arguments)
        if not filtered:
            continue
        rendered_group = ag.render(filtered)
        arguments_doc += rendered_group + "\n"

    arguments_doc = arguments_doc.strip()

    # if {argumets} found in documentation it will be replaced with arguments documentation, otherwose it will
    # be appended to documentation
    if '{arguments}' in doc:
        doc = doc.replace('{arguments}', arguments_doc)
    else:
        doc = doc + "\n\n" + arguments_doc

    return doc
