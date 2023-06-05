from django.conf import settings
from django.db import models
from django.db.models import JSONField


class NonAsciiRepr:
    def __repr__(self):
        return "nôt åscíì"


class Binary(models.Model):
    field = models.BinaryField()

    def __str__(self):
        return ""


class PostgresJSON(models.Model):
    field = JSONField()

    def __str__(self):
        return ""


if settings.USE_GIS:
    from django.contrib.gis.db import models as gismodels

    class Location(gismodels.Model):
        point = gismodels.PointField()

        def __str__(self):
            return ""
