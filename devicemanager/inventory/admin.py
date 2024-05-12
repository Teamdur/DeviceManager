from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from devicemanager.inventory.forms import DeviceForm, QRCodeGenerationConfigForm
from devicemanager.inventory.models import (
    Building,
    Device,
    DeviceModel,
    DeviceType,
    Faculty,
    Manufacturer,
    QRCodeGenerationConfig,
    Room,
)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("short_name", "full_name")
    search_fields = ("short_name", "full_name")


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "faculty")
    search_fields = ("name", "faculty__short_name")
    list_filter = ("faculty__short_name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "building")
    search_fields = ("room_number", "building__name")
    list_filter = ("building__name",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name")
    search_fields = ("name", "short_name")


@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ("name", "device_type", "manufacturer")
    ordering = ("device_type",)
    search_fields = ("name", "device_type__short_name", "manufacturer__name")
    list_filter = ("device_type", "manufacturer")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "model", "serial_number", "inventory_number")
    ordering = ("model__name",)
    search_fields = ("uuid", "serial_number", "inventory_number")
    list_filter = ("model__device_type", "model__manufacturer")
    actions = ["generate_qr_codes"]

    form = DeviceForm

    @admin.action(description=_("Generate QR Codes"))
    def generate_qr_codes(self, request: HttpRequest, queryset: QuerySet):
        selected_ids = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(
            reverse("inventory:qr-generate") + f"?ids={','.join(str(id) for id in selected_ids)}"
        )


@admin.register(QRCodeGenerationConfig)
class QRCodeGenerationConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "active", "qr_code_size_cm", "qr_code_margin_mm")
    list_filter = ("active",)

    form = QRCodeGenerationConfigForm
