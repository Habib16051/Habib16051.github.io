from django.urls import path
from django.utils.translation import pgettext_lazy
from writing.views import ArticleListView, ArticleDetailView#, CategoryDetailView

app_name = 'writing'

urlpatterns = [
    # path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path(pgettext_lazy('url', 'articles/'), ArticleListView.as_view(), name='article_list'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
]
