from django.views.generic.simple import direct_to_template
from django.contrib.auth.models import User

from models import Sample


def update_object(request, template=''):
    # create  object
    obj = Sample.objects.create(name='test')
    obj = Sample.objects.all().order_by('?')[0]

    # update objec
    obj.name = 'test1'
    obj.save()

    # update objec
    obj.name = 'test2'
    obj.save()

    # delete object
    obj.delete()

    obj2 = Sample.objects.create(name='test2')

    user, created = User.objects.get_or_create(username='admin', defaults={
    'username': 'admin',
    'email': 'test@test.com',
    'first_name': 'admin',
    'last_name': 'admin',
    })
    user.last_name = 'test'
    user.save()
    return direct_to_template(request, template=template)
