import functools

from django.template.backends.jinja2 import Template as JinjaTemplate
from django.template.context import make_context
from django.test.signals import template_rendered


def patch_jinja_render():
    orig_render = JinjaTemplate.render

    @functools.wraps(orig_render)
    def wrapped_render(self, context=None, request=None):
        print(self.template.name)
        self.name = self.template.name
        template_rendered.send(
            sender=self, template=self, context=make_context(context, request)
        )
        return orig_render(self, context, request)

    if JinjaTemplate.render != wrapped_render:
        JinjaTemplate.original_render = JinjaTemplate.render
        JinjaTemplate.render = wrapped_render
