from django.core.validators import EMPTY_VALUES
from django.utils.text import slugify


class SlugMixin(object):  # TODO: move to django-pragmatic
    MAX_SLUG_LENGTH = 150
    FORCE_SLUG_REGENERATION = True
    SLUG_FIELD = 'title'

    def save(self, **kwargs):
        if self.slug in EMPTY_VALUES or self.FORCE_SLUG_REGENERATION:
            slug = slugify(getattr(self, self.SLUG_FIELD))
            self.slug = slug
            index = 1

            # Ensure uniqueness
            while self.__class__.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{slug}-{index}'
                index += 1

        return super().save(**kwargs)
