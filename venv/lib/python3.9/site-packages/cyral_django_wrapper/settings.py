from django.conf import settings

USER_SETTINGS = getattr(settings, "CYRAL_DJANGO_WRAPPER", {})

# Defaults
REQUIRE_IDENTITY = False

for name, value in USER_SETTINGS.items():
    # we update the configuration global variable if it is set in USER_SETTINGS
    globals()[name] = value
