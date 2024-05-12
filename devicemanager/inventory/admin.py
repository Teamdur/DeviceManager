from django.contrib import admin

from devicemanager.inventory.models import (
    Building,
    Device,
    DeviceModel,
    DeviceType,
    Faculty,
    Manufacturer,
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
    list_display = ("uuid", "model", "serial_number", "inventory_number")
    ordering = ("model__name",)
    search_fields = ("uuid", "serial_number", "inventory_number")
    list_filter = ("model__device_type", "model__manufacturer")
