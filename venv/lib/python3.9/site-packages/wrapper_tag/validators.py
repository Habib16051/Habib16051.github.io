from __future__ import unicode_literals, print_function
from django.core.validators import *
from django.db import models
from django.utils.encoding import smart_text, python_2_unicode_compatible


def any(*validators):
    """
    shorthand for AnyValidator
    :param validators:
    :return:
    """
    return AnyValidator(*validators)


def model_instance(*models):
    """
    shorthand to ModelInstance validator
    :param models:
    :return:
    """
    return ModelInstance(*models)


def requires_tag(*tags):
    """
    shorthand for RequiresTagValidator
    :param tags:
    :return:
    """
    return RequiresTagValidator(*tags)


def string():
    """
    shorthand for StringValidator
    :return:
    """
    return StringValidator()


@python_2_unicode_compatible
class AnyValidator(object):

    validators = None

    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, value):
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError:
                continue
            else:
                return

    def __str__(self):
        return 'Any validator: {}'.format(self.validators)


@python_2_unicode_compatible
class RequiresTagValidator(object):

    tags = None

    def __init__(self, *tags):
        self.tags = tags

    def __call__(self, value):
        """
        raises ValidationError.
        """

        if not value:
            return

        try:
            tag = self.get_tag(value)
        except ValueError:
            raise ValidationError('value {} not a tag.'.format(value))

        if self.tags and tag not in self.tags:
            raise ValidationError('tag {} not in allowed list: {}.'.format(tag, self.tags))

    def get_tag(self, value):
        """
        Returns tag if value has one
        :param value:
        :return:
        """

        from wrapper_tag import Tag

        # first check if it's tag
        if value == Tag or isinstance(value, Tag):
            tag = value.options.start_tag
        else:
            tag = getattr(value, 'tag', None)

        if tag is None:
            raise ValueError('value {} not tag'.format(smart_text(value)))

        return tag

    def __str__(self):
        if len(self.tags) > 1:
            f = 'Required tag in: {}'
        else:
            f = 'Required tag: {}'
        return f.format(self.tags)


@python_2_unicode_compatible
class StringValidator(object):

    def __call__(self, value):
        if not isinstance(value, six.string_types):
            raise ValidationError('value is not string')

    def __str__(self):
        return 'value must be string'


@python_2_unicode_compatible
class ModelInstance(object):

    models = None

    def __init__(self, *models):
        self.models = models

    def __call__(self, value):
        if not isinstance(value, models.Model):
            raise ValidationError('value not model instance')

        if self.models:
            for model in self.models:
                if isinstance(value, model):
                    return True
            raise ValidationError('value not model instance')

    def __str__(self):
        return 'value must be instance of: %s'.format(self.models)