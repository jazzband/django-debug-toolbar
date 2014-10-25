from django.contrib.auth.models import User
from django.template.loaders.app_directories import Loader


class LoaderWithSQL(Loader):
    def load_template_source(self, template_name, template_dirs=None):
        # Force the template loader to run some SQL. Simulates a CMS.
        User.objects.all().count()
        return super(LoaderWithSQL, self).load_template_source(
            template_name, template_dirs=template_dirs)
