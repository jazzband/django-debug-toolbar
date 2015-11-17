import django
from django.contrib.auth.models import User
from django.template.loaders.app_directories import Loader


class LoaderWithSQL(Loader):

    if django.VERSION[:2] >= (1, 9):
        def get_template(self, *args, **kwargs):
            # Force the template loader to run some SQL. Simulates a CMS.
            User.objects.all().count()
            return super(LoaderWithSQL, self).get_template(*args, **kwargs)
    else:
        def load_template(self, *args, **kwargs):
            # Force the template loader to run some SQL. Simulates a CMS.
            User.objects.all().count()
            return super(LoaderWithSQL, self).load_template(*args, **kwargs)
