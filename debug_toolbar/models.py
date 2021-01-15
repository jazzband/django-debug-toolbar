from django.db import models


class ToolbarStore(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=64, unique=True)


class PanelStore(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    toolbar = models.ForeignKey(ToolbarStore, on_delete=models.CASCADE)
    panel = models.CharField(max_length=128)
    data = models.TextField()
