from django.contrib.auth.models import User
from django.template.loaders.app_directories import Loader


class LoaderWithSQL(Loader):
    def get_template(self, *args, **kwargs):
        # Force the template loader to run some SQL. Simulates a CMS.
        User.objects.all().count()
        return super().get_template(*args, **kwargs)
