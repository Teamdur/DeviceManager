from typing import Iterable, Optional

from colorfield.fields import ColorField
from distlib.util import cached_property
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
from devicemanager.utils.fields import ListJSONField
from devicemanager.utils.models import TimeTrackable
from devicemanager.utils.units import UnitConverter


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
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="rooms", verbose_name=_("Building"))
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
    name = models.CharField(max_length=256, verbose_name=_("Device Type Name"))
    short_name = models.CharField(max_length=60, verbose_name=_("Device short name"))

    class Meta:
        verbose_name = _("Device Type")
        verbose_name_plural = _("Device Types")
        indexes = [Index(Lower("short_name"), name="device_type_sname_lower_idx")]

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    id = models.AutoField(primary_key=True)
    device_type = models.ForeignKey(
        DeviceType, on_delete=models.CASCADE, related_name="models", verbose_name=_("Device Type")
    )
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, related_name="models", verbose_name=_("Manufacturer")
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
        DeviceModel, on_delete=models.CASCADE, related_name="devices", verbose_name=_("Model")
    )
    serial_number = models.CharField(
        max_length=512, null=True, blank=True, unique=True, db_index=True, verbose_name=_("Serial Number")
    )
    inventory_number = models.CharField(
        max_length=512, null=True, blank=True, unique=True, db_index=True, verbose_name=_("Inventory Number")
    )

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")

    def __str__(self):
        return f"{self.model} {self.inventory_number}"

    LABELS_CHOICES = (
        ("serial_number", _("Serial Number")),
        ("inventory_number", _("Inventory Number")),
        ("id", _("ID")),
    )

    @staticmethod
    def default_labels_include():
        return list(choice[0] for choice in Device.LABELS_CHOICES)

    def get_print_label(
        self, include_labels: Iterable[str] | None = None, config: Optional["QRCodeGenerationConfig"] = None
    ) -> str:
        qrcode_config = config or QRCodeGenerationConfig.get_active_configuration()
        if include_labels is None:
            include_labels = qrcode_config.included_labels

        labels = {
            "serial_number": (qrcode_config.serial_number_label, self.serial_number),
            "inventory_number": (qrcode_config.inventory_number_label, self.inventory_number),
            "id": (qrcode_config.id_label, self.id),
        }

        return "\n".join(
            f"{labels[label][0]}: {str(labels[label][1] or '')}" for label in include_labels if label in labels
        )


class QRCodeGenerationConfig(LifecycleModel):
    id = models.AutoField(primary_key=True, verbose_name=_("QR Code Generation Config ID"))
    qr_code_size_cm = models.PositiveIntegerField(
        verbose_name=_("QR Code Size in cm"), default=5, validators=[MinValueValidator(1)]
    )
    qr_code_margin_mm = models.PositiveIntegerField(
        verbose_name=_("QR Code Margin"), default=3, validators=[MinValueValidator(1)]
    )
    active = models.BooleanField(verbose_name=_("Configuration in use"), default=False)
    fill_color = ColorField(default="#000000", verbose_name=_("Fill Color"))
    back_color = ColorField(default="#FFFFFF", verbose_name=_("Background Color"))
    serial_number_label = models.CharField(max_length=15, default="SN", verbose_name=_("Serial Number Label"))
    inventory_number_label = models.CharField(max_length=15, default="IN", verbose_name=_("Inventory Number Label"))
    id_label = models.CharField(max_length=15, default="ID", verbose_name=_("ID Label"))
    included_labels = ListJSONField(verbose_name=_("Included Labels"), default=Device.default_labels_include)
    print_dpi = models.PositiveIntegerField(default=72, verbose_name=_("Print DPI"), validators=[MinValueValidator(1)])
    pdf_page_width_mm = models.PositiveIntegerField(
        default=210, verbose_name=_("PDF Page Width in mm"), validators=[MinValueValidator(100)]
    )
    pdf_page_height_mm = models.PositiveIntegerField(
        default=297, verbose_name=_("PDF Page Height in mm"), validators=[MinValueValidator(100)]
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
    def ensure_one_active_config_present(self):
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

    @cached_property
    def unit_converter(self):
        return UnitConverter(dpi=self.print_dpi)

    @cached_property
    def pdf_page_width_height_px(self):
        return (
            self.unit_converter.mm_to_px(self.pdf_page_width_mm),
            self.unit_converter.mm_to_px(self.pdf_page_height_mm),
        )


class DeviceRental(TimeTrackable, LifecycleModel):
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="rentals", verbose_name=_("Device"))
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rentals", verbose_name=_("Borrower"))
    rental_date = models.DateField(auto_now_add=True, verbose_name=_("Rental Date"))
    return_date = models.DateField(null=True, blank=True, verbose_name=_("Return Date"))

    class Meta:
        verbose_name = _("Device Rental")
        verbose_name_plural = _("Device Rentals")

    @hook(BEFORE_SAVE, condition=WhenFieldValueIs("return_date", None))
    def ensure_device_is_rented_once(self):
        other_device_rentals = DeviceRental.objects.filter(device=self.device, return_date=None).exclude(pk=self.pk)
        if other_device_rentals.exists():
            raise ValueError("Device is already rented")

    def __str__(self):
        return f"{self.device} - {self.borrower}"
