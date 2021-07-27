from django.db.models import QuerySet, Q


class ArticleQuerySet(QuerySet):
    def highlighted(self):
        return self.filter(is_highlighted=True)

    def published(self):
        return self.filter(is_published=True)

    def of_category(self, category):
        return self.filter(
            Q(category=category) |
            Q(category__parent=category)
        )
