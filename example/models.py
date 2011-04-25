from django.db import models


class Sample(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name
