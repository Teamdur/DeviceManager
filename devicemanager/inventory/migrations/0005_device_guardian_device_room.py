# Generated by Django 5.0.4 on 2024-05-20 17:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0004_devicerental"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="guardian",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="devices",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Guardian",
            ),
        ),
        migrations.AddField(
            model_name="device",
            name="room",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="devices",
                to="inventory.room",
                verbose_name="Room",
            ),
        ),
    ]