from __future__ import print_function, unicode_literals

import six
from django.core.management.base import BaseCommand

from wrapper_tag import utils


class Command(BaseCommand):
    help = "Show documentation to tags"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('tags', nargs='*')

    def handle(self, *args, **options):
        libs = utils.get_config().get_templatetag_libs()

        for name, lib in six.iteritems(libs):
            for tag_name, compilation_func in six.iteritems(lib.tags):
                if tag_name in options['tags']:
                    print("\n{}".format(tag_name))
                    print("-" * len(tag_name))
                    print("To use this tag, put {{% load {} %}} in your template before using the tag.\n".format(name))
                    print(compilation_func.__doc__)