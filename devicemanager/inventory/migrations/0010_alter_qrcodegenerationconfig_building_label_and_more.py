# Generated by Django 5.0.4 on 2024-06-10 18:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0009_remove_qrcodegenerationconfig_id_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="qrcodegenerationconfig",
            name="building_label",
            field=models.CharField(default="", max_length=15, verbose_name="Building Label"),
        ),
        migrations.AlterField(
            model_name="qrcodegenerationconfig",
            name="inventory_number_label",
            field=models.CharField(default="IN", max_length=15, verbose_name="Inventory Number Label"),
        ),
        migrations.AlterField(
            model_name="qrcodegenerationconfig",
            name="owner_label",
            field=models.CharField(default="", max_length=15, verbose_name="Owner Label"),
        ),
        migrations.AlterField(
            model_name="qrcodegenerationconfig",
            name="room_label",
            field=models.CharField(default="", max_length=15, verbose_name="Room Label"),
        ),
        migrations.AlterField(
            model_name="qrcodegenerationconfig",
            name="serial_number_label",
            field=models.CharField(default="SN", max_length=15, verbose_name="Serial Number Label"),
        ),
    ]
