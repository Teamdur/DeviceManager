# Generated by Django 5.0.4 on 2024-05-12 20:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0002_qrcodegenerationconfig"),
    ]

    operations = [
        migrations.AddField(
            model_name="qrcodegenerationconfig",
            name="pdf_page_height_mm",
            field=models.PositiveIntegerField(
                default=297,
                validators=[django.core.validators.MinValueValidator(100)],
                verbose_name="PDF Page Height in mm",
            ),
        ),
        migrations.AddField(
            model_name="qrcodegenerationconfig",
            name="pdf_page_width_mm",
            field=models.PositiveIntegerField(
                default=210,
                validators=[django.core.validators.MinValueValidator(100)],
                verbose_name="PDF Page Width in mm",
            ),
        ),
        migrations.AddField(
            model_name="qrcodegenerationconfig",
            name="print_dpi",
            field=models.PositiveIntegerField(
                default=72, validators=[django.core.validators.MinValueValidator(1)], verbose_name="Print DPI"
            ),
        ),
        migrations.AlterField(
            model_name="qrcodegenerationconfig",
            name="qr_code_margin_mm",
            field=models.PositiveIntegerField(
                default=3, validators=[django.core.validators.MinValueValidator(1)], verbose_name="QR Code Margin"
            ),
        ),
        migrations.AlterField(
            model_name="qrcodegenerationconfig",
            name="qr_code_size_cm",
            field=models.PositiveIntegerField(
                default=5, validators=[django.core.validators.MinValueValidator(1)], verbose_name="QR Code Size in cm"
            ),
        ),
    ]
