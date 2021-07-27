from django.apps import AppConfig
from django.conf import settings
from logging import getLogger

try:
    # Django versions >= 1.9
    from django.utils.module_loading import import_module
except ImportError:
    # Django versions < 1.9
    from django.utils.importlib import import_module

import unipath


from wrapper_tag import utils


class WrapperTagConfig(AppConfig):
    name = 'wrapper_tag'
    verbose_name = 'wrapper tags'

    logger = getLogger('wrapper_tag')
    template_debug = utils.is_template_debug()

    def get_templatetag_libs(self):
        """
        Returns all templatetag libraries
        :return:
        """
        result = {}
        for installed_app in getattr(settings, 'INSTALLED_APPS', []):

            tt = '{}.templatetags'.format(installed_app)

            try:
                module = import_module(tt)
            except ImportError:
                continue

            for pf in unipath.Path(module.__file__).parent.listdir():
                if not (pf.isfile() and pf.ext.lower() == '.py' and not pf.name.startswith('_')):
                    continue
                ttfull = '{}.{}'.format(tt, pf.stem)

                try:
                    imported = import_module(ttfull)

                    register = getattr(imported, 'register', None)
                    if register:
                        result[str(pf.stem)] = register

                except ImportError:
                    continue

        return result