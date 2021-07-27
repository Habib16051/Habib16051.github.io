# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django import forms
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from collectionfield.validators import (
    MaxItemsValidator, ConvertedMaxLengthValidator
)


class choicelist(list):
    """List of choices prepared for usage with form widget"""
    pass


class CollectionFieldMixin(object):

    collection_field_compatible = True

    def __init__(self, collection_type=list,
                 item_type=str, sort=False, unique_items=False,
                 max_items=None, max_length=None, delimiter='|',
                 *args, **kwargs):
        self.collection_type = collection_type
        self.item_type = item_type
        self.sort = sort
        self.unique_items = unique_items
        self.max_items = max_items
        self.max_length = max_length
        self.delimiter = delimiter
        super(CollectionFieldMixin, self).__init__(*args, **kwargs)
        empty_collection = collection_type()
        if empty_collection not in self.empty_values:
            self.empty_values = self.empty_values[:] + [empty_collection]
        if max_items:
            self.validators.append(MaxItemsValidator(self.max_items))
        if max_length:
            self.validators.append(
                ConvertedMaxLengthValidator(
                    limit_value=self.max_length,
                    collection_type=self.collection_type,
                    item_type=self.item_type,
                    sort=self.sort,
                    unique_items=self.unique_items,
                    delimiter=self.delimiter
                )
            )


class CollectionField(CollectionFieldMixin, forms.Field):

    default_error_messages = {
        'invalid': _('Enter a list of valid values.'),
    }

    def __init__(self, separator=',', *args, **kwargs):
        self.separator = separator
        super(CollectionField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        """Converts value to string for widget usage"""
        if not isinstance(value, str):
            value = value or ()
            value = self.collection_type(
                self.item_type(item) for item in value
            )
            if isinstance(value, set) or not self.unique_items:
                collection = value
            else:
                collection = []
                # Remove the duplicates while keeping order:
                [
                    collection.append(item)
                    for item in value if item not in collection
                ]
            if self.sort:
                collection = sorted(collection)
            value = self.format_separator().join(
                str(item) for item in collection
            )
        return value

    def to_python(self, value):
        """Convert string value to proper collection for further validation"""
        if value in self.empty_values:
            return self.collection_type()  # None
        text_value = smart_text(value).strip()
        items = []
        for item in text_value.split(self.separator):
            item = item.strip()
            if item:
                items.append(item)
        for i, item in enumerate(items):
            try:
                items[i] = self.item_type(item)
            except Exception:
                raise forms.ValidationError(
                    self.error_messages['invalid'], code='invalid'
                )
        if isinstance(self.collection_type, set):
            collection = items
        else:
            if self.unique_items:
                collection = []
                # Remove the duplicates while keeping order:
                [
                    collection.append(item)
                    for item in items if item not in collection
                ]
            else:
                collection = items
            if self.sort:
                collection = sorted(collection)
        return self.collection_type(collection)

    def format_separator(self):
        separator = self.separator
        if re.match('\w+', separator):
            separator += ' '
        return separator


class CollectionChoiceField(CollectionFieldMixin, forms.MultipleChoiceField):

    default_error_messages = {
        'invalid': _('Enter a list of valid values.'),
    }

    def __init__(self, unique_items=True, *args, **kwargs):
        super(CollectionChoiceField, self).__init__(
            unique_items=unique_items, *args, **kwargs
        )

    def prepare_value(self, value):
        """Converts value to list of string for widget usage"""
        if not isinstance(value, choicelist):
            value = value or ()
            value = self.collection_type(
                self.item_type(item) for item in value
            )
            if isinstance(value, set) or not self.unique_items:
                collection = value
            else:
                collection = []
                # Remove the duplicates while keeping order:
                [
                    collection.append(item)
                    for item in value if item not in collection
                ]
            if self.sort:
                collection = sorted(collection)
            value = choicelist(
                str(item) for item in collection
            )
        return value

    def to_python(self, value):
        """Convert string value to proper collection for further validation"""
        if not value:
            return self.collection_type()  # []
        elif not isinstance(value, (list, tuple, self.collection_type)):
            raise forms.ValidationError(
                self.error_messages['invalid_list'], code='invalid_list'
            )
        else:
            items = [smart_text(item) for item in value]
            for i, item in enumerate(items):
                try:
                    items[i] = self.item_type(item)
                except Exception:
                    raise forms.ValidationError(
                        self.error_messages['invalid'], code='invalid'
                    )
            if isinstance(self.collection_type, set):
                collection = items
            else:
                if self.unique_items:
                    collection = []
                    # Remove the duplicates while keeping order:
                    [
                        collection.append(item)
                        for item in items if item not in collection
                    ]
                else:
                    collection = items
                if self.sort:
                    collection = sorted(collection)
            return self.collection_type(collection)
