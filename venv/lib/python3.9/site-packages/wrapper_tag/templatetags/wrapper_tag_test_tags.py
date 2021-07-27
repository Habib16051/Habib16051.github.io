from __future__ import absolute_import, print_function, unicode_literals
from django import template
from django.utils.safestring import mark_safe

import wrapper_tag
from wrapper_tag import tag
from wrapper_tag import arguments

register = template.Library()


@wrapper_tag.register_tag(register)
class TestTag(tag.Tag):
    title = arguments.Keyword()
    name = arguments.Keyword()
    on_click = arguments.Event()

    class Meta:
        template = "<test{{ title__rendered }}>{{ content }}</test>"

    def render_title(self, argument, data, context):
        if argument.name not in data:
            return None
        return mark_safe(' title="{}"'.format(data[argument.name]))

    def render_name(self, argument, data, context):
        if argument.name not in data:
            return None
        return mark_safe(' name="{}"'.format(data[argument.name]))

    def render_on_click(self, argument, data, context):
        return "on_click"