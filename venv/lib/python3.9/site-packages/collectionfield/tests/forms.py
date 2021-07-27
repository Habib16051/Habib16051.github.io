# -*- coding: utf-8 -*-

from decimal import Decimal

from django import forms

from collectionfield.forms import CollectionField, CollectionChoiceField


class StringSetForm(forms.Form):

    values = CollectionField(collection_type=set)


class OptionalStringSetForm(forms.Form):

    values = CollectionField(collection_type=set, required=False)


class IntegerListForm(forms.Form):

    values = CollectionField(collection_type=list, item_type=int)


class DecimalTupleForm(forms.Form):

    values = CollectionField(collection_type=tuple, item_type=Decimal)


class SortedStringListForm(forms.Form):

    values = CollectionField(collection_type=list, sort=True)


class UniqueStringListForm(forms.Form):

    values = CollectionField(collection_type=list, unique_items=True)


class SpaceSeparatedIntegerListForm(forms.Form):

    values = CollectionField(
        collection_type=list, item_type=int, separator=' '
    )


class Max3StringSetForm(forms.Form):

    values = CollectionField(collection_type=set, max_items=3)


class Max10CharsStringListForm(forms.Form):

    values = CollectionField(max_length=10)


class ChoiceStringListForm(forms.Form):

    values = CollectionChoiceField(
        choices=(
            ('a', "A"),
            ('b', "B"),
            ('c', "C"),
            ('d', "D")
        )
    )


class GroupedChoiceStringListForm(forms.Form):

    values = CollectionChoiceField(
        choices=(
            (
                'Group A', (
                    ('a-1', "A-1"),
                    ('a-2', "A-2"),
                ),
            ),
            (
                'Group B', (
                    ('b-1', "B-1"),
                    ('b-2', "B-2"),
                ),
            ),
        )
    )


class ChoiceIntegerSetForm(forms.Form):

    values = CollectionChoiceField(
        item_type=int, collection_type=set,
        choices=(
            (1, "One"),
            (2, "Two"),
            (3, "Three"),
            (4, "Four")
        )
    )


class GroupedChoiceIntegerSetForm(forms.Form):

    values = CollectionChoiceField(
        item_type=int, collection_type=set,
        choices=(
            (
                'Group 1', (
                    (11, "1-1"),
                    (12, "1-2"),
                ),
            ),
            (
                'Group 2', (
                    (21, "2-1"),
                    (22, "2-2"),
                ),
            ),
        )
    )


class ChoiceDecimalTupleForm(forms.Form):

    values = CollectionChoiceField(
        item_type=Decimal, collection_type=tuple,
        choices=(
            (Decimal('1.0'), "One"),
            (Decimal('1.5'), "One and half"),
            (Decimal('2.0'), "Two"),
            (Decimal('2.5'), "Two and half")
        )
    )


class GroupedChoiceDecimalTupleForm(forms.Form):

    values = CollectionChoiceField(
        item_type=Decimal, collection_type=tuple,
        choices=(
            (
                'Group 1', (
                    (Decimal('1.1'), "1-1"),
                    (Decimal('1.2'), "1-2"),
                ),
            ),
            (
                'Group 2', (
                    (Decimal('2.1'), "2-1"),
                    (Decimal('2.2'), "2-2"),
                ),
            ),
        )
    )


class ChoiceMax2StringSetForm(forms.Form):

    values = CollectionChoiceField(
        collection_type=set,
        choices=(
            ('a', "A"),
            ('b', "B"),
            ('c', "C"),
            ('d', "D")
        ),
        max_items=2
    )


class ChoiceSortedIntegerListForm(forms.Form):

    values = CollectionChoiceField(
        item_type=int,
        choices=(
            (1, "One"),
            (2, "Two"),
            (3, "Three"),
            (4, "Four")
        ),
        sort=True
    )


class ChoiceOptionalDecimalSetForm(forms.Form):

    values = CollectionChoiceField(
        item_type=Decimal, collection_type=set,
        choices=(
            (Decimal('1.0'), "One"),
            (Decimal('2.0'), "Two"),
            (Decimal('3.0'), "Three"),
            (Decimal('4.0'), "Four")
        ),
        required=False
    )
