from django.db import models


class NonAsciiRepr:
    def __repr__(self):
        return "nôt åscíì"


class Binary(models.Model):
    field = models.BinaryField()


try:
    from django.db.models import JSONField
except ImportError:  # Django<3.1
    from django.contrib.postgres.fields import JSONField


class PostgresJSON(models.Model):
    field = JSONField()
