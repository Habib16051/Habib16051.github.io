from django.views.generic import DetailView, ListView

from writing.models import Article, Category


class ArticleDetailView(DetailView):
    model = Article

    def dispatch(self, request, *args, **kwargs):
        article = self.get_object()

        # TODO: check cookie
        # update "seen"
        article.seen += 1
        article.save(update_fields=['seen'])

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().select_related('author')


class ArticleListView(ListView):
    model = Article
    paginate_by = 10
    # filter_class = ArticleFilter

    def dispatch(self, request, *args, **kwargs):
        # self.filter = self.filter_class(request.GET, queryset=self.get_whole_queryset())
        return super().dispatch(request, *args, **kwargs)

    def get_whole_queryset(self):
        return self.model.objects.published() \
            .select_related('author', 'category') \
            .order_by('-created')

    def get_queryset(self):
        # return self.sort_queryset(self.filter.qs)
        return self.get_whole_queryset()

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['categories'] = Category.objects.filter(parent=None)
        # context_data['filter'] = self.filter
        return context_data
