from django.test.signals import template_rendered
from django.template import Origin


def render_decorator(func, template):
    """
    Used to wrap a function and send a template_rendered
    signal out after being called.
    """
    def render(context=None):
        template_rendered.send(
            sender=template, template=template, context=context)
        return func(context)
    # Used to prevent decorator from being applied multiple times
    render._decorated = True
    return render


def load_template_decorator(func):
    """
    Used to wrap a function to set a decorator on the template in it
    it's returned value.
    """
    def load_template(self, template_name, template_dirs=None):
        result = func(self, template_name, template_dirs)

        if len(result) > 0 and hasattr(result[0], 'render'):
            template = result[0]
            if not getattr(template.render, '_decorated', False):
                # If the template instance doesn't have an origin
                # property set it.
                if not hasattr(template, 'origin'):
                    template_source = self.load_template_source(
                        template_name, template_dirs)[1]
                    template.origin = Origin(template_source)
                template.render = render_decorator(template.render, template)
        return result
    return load_template
