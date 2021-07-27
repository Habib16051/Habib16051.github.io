import logging
from django.test import TestCase
from django.template import Context, Template

logger = logging.getLogger('django_css_inline')


class DjangoCssInlineTest(TestCase):

    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_css_static(self):
        rendered = self.render_template(
            '{% load css_inline %}'
            '{% css_inline %}'
            '<link rel="stylesheet" href="/static/django_css_inline/test-1.css">'
            '<link rel="stylesheet" href="/static/django_css_inline/test-2.css">'
            '{% end_css_inline %}'
        )
        self.assertEqual(
            rendered,
            """<style type="text/css">/* Django static test 1 */\n\n.test-1 {\n    color: red;\n}\n/* Django static test 2 */\n\n.test-2 {\n    color: green;\n}\n</style>"""
        )

    def test_css_external(self):
        rendered = self.render_template(
            '{% load css_inline %}'
            '{% css_inline %}'
            '<link rel="stylesheet" href="https://static.snoweb.fr/django-css-inline/test-3.css">'
            '{% end_css_inline %}'
        )
        self.assertEqual(
            rendered,
            """<style type="text/css">/* External test 3 */\n\n.test-3 {\n    color: blue;\n}\n</style>"""
        )

    def test_css_gzip(self):
        rendered = self.render_template(
            '{% load css_inline %}'
            '{% css_inline %}'
            '<link rel="stylesheet" href="https://static.snoweb.fr/django-css-inline/test-3.css">'
            '<link rel="stylesheet" href="https://static.snoweb.fr/snowebsvg/dist/css/themes-0.0.24.css">'
            '{% end_css_inline %}'
        )
        self.assertEqual(
            rendered,
            """<style type="text/css">/* External test 3 */\n\n.test-3 {\n    color: blue;\n}\n:root{--svg-theme-light-primary: #14253A;--svg-theme-light-secondary: #E63946;--svg-theme-light-tertiary: #f7f7f7;--svg-theme-dark-primary: #F7F7F7;--svg-theme-dark-secondary: #E63946;--svg-theme-dark-tertiary: #112032}.svg-theme-dark .svg-fill-primary{fill:var(--svg-theme-dark-primary)}.svg-theme-light .svg-fill-primary{fill:var(--svg-theme-light-primary)}.svg-theme-dark .svg-fill-secondary{fill:var(--svg-theme-dark-secondary)}.svg-theme-light .svg-fill-secondary{fill:var(--svg-theme-light-secondary)}.svg-theme-dark .svg-fill-tertiary{fill:var(--svg-theme-dark-tertiary)}.svg-theme-light .svg-fill-tertiary{fill:var(--svg-theme-light-tertiary)}.svg-theme-dark .svg-stroke-primary{stroke:var(--svg-theme-dark-primary)}.svg-theme-light .svg-stroke-primary{stroke:var(--svg-theme-light-primary)}.svg-theme-dark .svg-stroke-secondary{stroke:var(--svg-theme-dark-secondary)}.svg-theme-light .svg-stroke-secondary{stroke:var(--svg-theme-light-secondary)}.svg-theme-dark .svg-stroke-tertiary{stroke:var(--svg-theme-dark-tertiary)}.svg-theme-light .svg-stroke-tertiary{stroke:var(--svg-theme-light-tertiary)}\n</style>"""
        )


    def test_not_found(self):
        rendered = self.render_template(
            '{% load css_inline %}'
            '{% css_inline %}'
            '<link rel="stylesheet" href="https://static.snoweb.fr/this-url-does-not-exist.css">'
            '{% end_css_inline %}'
        )
        self.assertEqual(
            rendered,
            """<link rel="stylesheet" href="https://static.snoweb.fr/this-url-does-not-exist.css">"""
        )
