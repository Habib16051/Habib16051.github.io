from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from martor.models import MartorField
from mptt.models import MPTTModel, TreeForeignKey

from writing.mixins import SlugMixin
from writing.querysets import ArticleQuerySet


class Category(SlugMixin, MPTTModel):
    FORCE_SLUG_REGENERATION = True

    parent = TreeForeignKey('self', verbose_name=_('parent'), related_name='children', on_delete=models.CASCADE,
        db_index=True, blank=True, null=True)
    title = models.CharField(_('title'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=150, blank=True, db_index=True)
    # icon = models.CharField(_(u'icon'), max_length=255, blank=True)
    created = models.DateTimeField(_(u'created'), auto_now_add=True)
    modified = models.DateTimeField(_(u'modified'), auto_now=True)

    class Meta:
        verbose_name = _(u'category')
        verbose_name_plural = _(u'categories')
        ordering = ('title',)
        # order_insertion_by = ('title',)
        default_permissions = settings.DEFAULT_PERMISSIONS

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('writing:category_detail', kwargs={
            'slug': slugify(self.slug)
        })

    @cached_property
    def nested_article_set(self):
        descendants = self.get_descendants(include_self=True)
        return Article.objects \
            .filter(category__in=descendants) \
            .select_related('author', 'category')


class Article(SlugMixin, models.Model):
    FORCE_SLUG_REGENERATION = False  # To preserve SEO links

    category = models.ForeignKey(Category, verbose_name=_('category'), on_delete=models.PROTECT, blank=True, null=True, default=None)
    title = models.CharField(_('title'), max_length=100, unique=True, db_index=True)
    slug = models.SlugField(unique=True, max_length=150, blank=True, db_index=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), on_delete=models.PROTECT)
    is_highlighted = models.BooleanField(_('highlighted'), default=False)
    is_published = models.BooleanField(_('published'), default=True)
    seen = models.PositiveSmallIntegerField(_('seen'), db_index=True, default=0)
    excerpt = models.TextField(_('excerpt'), help_text=_('preview'))
    content = MartorField(_('content'))
    created = models.DateTimeField(_(u'created'), auto_now_add=True)
    modified = models.DateTimeField(_(u'modified'), auto_now=True)
    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = _(u'article')
        verbose_name_plural = _(u'articles')
        ordering = ['title']
        default_permissions = settings.DEFAULT_PERMISSIONS

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('writing:article_detail', kwargs={
            'slug': slugify(self.slug)
        })
