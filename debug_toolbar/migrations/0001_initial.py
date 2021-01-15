# Generated by Django 3.1.5 on 2021-01-09 17:02
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ToolbarStore",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("key", models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="PanelStore",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("panel", models.CharField(max_length=128)),
                ("data", models.TextField()),
                (
                    "toolbar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="debug_toolbar.toolbarstore",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="panelstore",
            constraint=models.UniqueConstraint(
                fields=("toolbar", "panel"), name="unique_toolbar_panel"
            ),
        ),
    ]
