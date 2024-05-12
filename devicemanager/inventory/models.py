import uuid

from django.db import models
from django.db.models import Index
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from devicemanager.users.models import User


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
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE, related_name="devices", verbose_name=_("Model"))
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
