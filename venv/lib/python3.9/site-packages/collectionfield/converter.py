# -*- coding: utf-8 -*-


class CollectionConverter(object):

    def __init__(self, collection_type, item_type, sort, unique_items,
                 delimiter):
        self.collection_type = collection_type
        self.item_type = item_type
        self.sort = sort
        self.unique_items = unique_items
        self.delimiter = delimiter

    def dump(self, value):
        value = value or ()
        value = self.collection_type(self.item_type(item) for item in value)
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
        return '{delimiter}{values}{delimiter}'.format(
            delimiter=self.delimiter,
            values=self.delimiter.join(str(item) for item in collection)
        )

    def load(self, value):
        value = value or ''
        n = len(self.delimiter)
        return self.collection_type(
            self.item_type(s) for s in value[n:-n].split(self.delimiter) if s
        )
