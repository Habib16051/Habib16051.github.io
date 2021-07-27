from django.apps import AppConfig

from cyral_django_wrapper import install_wrapper


class CyralDjangoWrapperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cyral_django_wrapper"

    def ready(self):
        # if the app is added to INSTALLED_APPS, the wrapper will be installed by
        # default
        install_wrapper()
