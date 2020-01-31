from django.db import models


class NonAsciiRepr:
    def __repr__(self):
        return "nôt åscíì"


class Binary(models.Model):
    field = models.BinaryField()


try:
    from django.contrib.postgres.fields import JSONField

    class PostgresJSON(models.Model):
        field = JSONField()


except ImportError:
    pass
