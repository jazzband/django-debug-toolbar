from django.conf import settings
from django.db import models


class NonAsciiRepr:
    def __repr__(self):
        return "nôt åscíì"


class Binary(models.Model):
    field = models.BinaryField()


class JSON(models.Model):
    field = models.JSONField()


if settings.USE_GIS:
    from django.contrib.gis.db import models as gismodels

    class Location(gismodels.Model):
        point = gismodels.PointField()
