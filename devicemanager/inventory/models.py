from datetime import datetime

from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Index
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from django_lifecycle import (
    BEFORE_CREATE,
    BEFORE_SAVE,
    BEFORE_UPDATE,
    LifecycleModel,
    hook,
)
from django_lifecycle.conditions import WhenFieldValueChangesTo, WhenFieldValueIs

from devicemanager.users.models import User
from devicemanager.utils.models import TimeTrackable


class Faculty(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=512, unique=True, verbose_name=_("Faculty Full Name"))
    short_name = models.CharField(max_length=60, unique=True, verbose_name=_("Faculty  Name"))

    class Meta:
        verbose_name = _("Faculty")
        verbose_name_plural = _("Faculties")
        indexes = [Index(Lower("short_name"), name="faculty_name_lower_idx")]

    def __str__(self):
        return self.short_name


class Building(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60, verbose_name=_("Building Name"))
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="buildings")

    class Meta:
        verbose_name = _("Building")
        verbose_name_plural = _("Buildings")
        indexes = [Index(Lower("name"), name="building_name_lower_idx")]

    def __str__(self):
        return self.name


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=60, verbose_name=_("Room Number"))
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name=_("Building"),
    )
    description = models.TextField(blank=True)
    occupants = models.ManyToManyField(User, related_name="rooms", blank=True, verbose_name=_("Occupants"))

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")
        indexes = [Index(Lower("room_number"), name="room_number_lower_idx")]

    def __str__(self):
        return f"{self.building.name} - {self.room_number}"


class Manufacturer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True, verbose_name=_("Manufacturer Name"))
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Manufacturer")
        verbose_name_plural = _("Manufacturers")
        indexes = [Index(Lower("name"), name="manufacturer_name_lower_idx")]

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, verbose_name=_("Device Type"))
    short_name = models.CharField(max_length=60, verbose_name=_("Device Type short name"))

    class Meta:
        verbose_name = _("Device Type")
        verbose_name_plural = _("Device Types")
        indexes = [Index(Lower("short_name"), name="device_type_sname_lower_idx")]

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    id = models.AutoField(primary_key=True)
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.CASCADE,
        related_name="models",
        verbose_name=_("Device Type"),
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name="models",
        verbose_name=_("Manufacturer"),
    )
    name = models.CharField(max_length=256, verbose_name=_("Model Name"))
    description = models.TextField(blank=True, verbose_name=_("Device Description"))

    class Meta:
        verbose_name = _("Device Model")
        verbose_name_plural = _("Device Models")
        indexes = [Index(Lower("name"), name="device_model_name_lower_idx")]

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"


class Device(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=_("Device ID"))
    device_model = models.ForeignKey(
        DeviceModel,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name=_("Model"),
    )
    serial_number = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Serial Number"),
    )
    inventory_number = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Inventory Number"),
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        related_name="devices",
        verbose_name=_("Room"),
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="devices",
        verbose_name=_("Owner"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")

    def __str__(self):
        return f"{self.device_model} {self.inventory_number or ''}"

    LABELS_CHOICES = (
        ("room", _("Room")),
        ("owner", _("Owner")),
        ("inventory_number", _("Inventory Number")),
        ("device_model", _("Device Model")),
        ("serial_number", _("Serial Number")),
    )

    @staticmethod
    def default_labels_include():
        return list(choice[0] for choice in Device.LABELS_CHOICES)


class QRCodeGenerationConfig(LifecycleModel):
    id = models.AutoField(primary_key=True, verbose_name=_("QR Code Generation Config ID"))
    label_width_mm = models.PositiveIntegerField(
        verbose_name=_("Label Width in mm"),
        default=50,
        validators=[MinValueValidator(1)],
    )
    label_height_mm = models.PositiveIntegerField(
        verbose_name=_("Label Height in mm"),
        default=30,
        validators=[MinValueValidator(1)],
    )
    label_padding_mm = models.PositiveIntegerField(
        verbose_name=_("Label Padding in mm"),
        default=2,
    )
    label_horizontal_spacing_mm = models.PositiveIntegerField(
        verbose_name=_("Label Horizontal Spacing in mm"),
        default=2,
    )
    label_vertical_spacing_mm = models.PositiveIntegerField(
        verbose_name=_("Label Vertical Spacing in mm"),
        default=1,
    )
    label_title_gap_mm = models.PositiveIntegerField(
        verbose_name=_("Label gap between room and rest of the fields in mm"), default=2
    )
    dpi = models.PositiveIntegerField(
        verbose_name=_("DPI"),
        default=300,
        validators=[MinValueValidator(1)],
    )
    font_size_small = models.PositiveIntegerField(verbose_name=_("Small Font Size [pt]"), default=14)
    font_size = models.PositiveIntegerField(verbose_name=_("Font Size [pt]"), default=18)
    font_size_large = models.PositiveIntegerField(verbose_name=_("Large Font Size [pt]"), default=28)
    fill_color = ColorField(default="#000000", verbose_name=_("Fill Color"))
    background_color = ColorField(default="#FFFFFF", verbose_name=_("Background Color"))
    active = models.BooleanField(verbose_name=_("Configuration in use"), default=False)
    inv_prefix = models.CharField(
        max_length=15,
        default="inv:",
        verbose_name=_("Inventory Number Prefix"),
        null=True,
        blank=True,
    )
    sn_prefix = models.CharField(
        max_length=15,
        default="sn:",
        verbose_name=_("Serial Number Prefix"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("QR Code Generation Config")
        verbose_name_plural = _("QR Code Generation Configs")

    @hook(
        BEFORE_UPDATE,
        condition=WhenFieldValueChangesTo("active", True),
    )
    def update_disables_other_configs(self):
        QRCodeGenerationConfig.objects.filter(active=True).update(active=False)
        self.active = True

    @hook(
        BEFORE_CREATE,
    )
    def _ensure_one_active_config_present(self):
        active_config_count = QRCodeGenerationConfig.objects.filter(active=True).count()
        if active_config_count == 0:
            self.active = True
        elif self.active:
            QRCodeGenerationConfig.objects.filter(active=True).update(active=False)

    @staticmethod
    def get_active_configuration():
        return QRCodeGenerationConfig.objects.get_or_create(active=True)[0]

    def __str__(self):
        return f"QR Code Generation Config {self.id}"


class DeviceRental(TimeTrackable, LifecycleModel):
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="rentals",
        verbose_name=_("Device"),
    )
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rentals",
        verbose_name=_("Borrower"),
    )
    rental_date = models.DateField(default=datetime.now, verbose_name=_("Rental Date"))
    return_date = models.DateField(null=True, blank=True, verbose_name=_("Return Date"))

    class Meta:
        verbose_name = _("Device Rental")
        verbose_name_plural = _("Device Rentals")

    @hook(BEFORE_SAVE, condition=WhenFieldValueIs("return_date", None))
    def _ensure_device_is_rented_once(self):
        other_device_rentals = DeviceRental.objects.filter(device=self.device, return_date=None).exclude(pk=self.pk)
        if other_device_rentals.exists():
            raise ValueError("Device is already rented")

    def __str__(self):
        return f"{self.device} - {self.borrower}"
