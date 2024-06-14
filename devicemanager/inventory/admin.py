from typing import Any

from django.contrib import admin
from django.db.models import (
    BooleanField,
    Case,
    Count,
    Prefetch,
    Q,
    QuerySet,
    Value,
    When,
)
from django.db.models.functions import Concat
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from devicemanager.inventory.filters import (
    DeviceIsRentedFilter,
    DeviceTypesForRentalFilter,
    RentalIsRentedFilter,
)
from devicemanager.inventory.forms import (
    DeviceForm,
    DeviceRentalForm,
    QRCodeGenerationConfigForm,
)
from devicemanager.inventory.formsets import DeviceRentalFormSet
from devicemanager.inventory.models import (
    Building,
    Device,
    DeviceModel,
    DeviceRental,
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


class DeviceRentalInline(admin.StackedInline):
    model = DeviceRental
    extra = 1
    formset = DeviceRentalFormSet


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_type",
        "manufacturer",
        "device_model",
        "get_room",
        "building",
        "guardian",
        "serial_number",
        "inventory_number",
        "current_rental",
        "date_rented",
        "is_rented",
    )
    ordering = ("device_model__name",)
    search_fields = (
        "id",
        "serial_number",
        "inventory_number",
        "device_model__device_type__short_name",
        "device_model__device_type__name",
        "device_model__manufacturer__name",
        "device_manufacturer_model",
        "room__room_number",
        "room__building__name",
        "guardian__username",
    )
    list_filter = (
        "device_model__device_type",
        "device_model__manufacturer",
        "device_model",
        "room",
        "guardian",
        "serial_number",
        "inventory_number",
        DeviceIsRentedFilter,
    )
    actions = ["generate_qr_codes"]
    inlines = [DeviceRentalInline]

    form = DeviceForm

    @admin.action(description=_("Generate QR Codes"))
    def generate_qr_codes(self, request: HttpRequest, queryset: QuerySet):
        selected_ids = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(
            reverse("inventory:qr-generate") + f"?ids={','.join(str(id) for id in selected_ids)}"
        )

    @admin.display(description=_("Current Rental"))
    def current_rental(self, obj: Device) -> str:
        rental = obj.rentals.filter(return_date=None).first()
        return rental.borrower if rental else "-"

    @admin.display(ordering="device_model__device_type__short_name", description=_("Device Type"))
    def device_type(self, obj: Device) -> str:
        return obj.device_model.device_type.name

    @admin.display(ordering="device_model__manufacturer__name", description=_("Manufacturer"))
    def manufacturer(self, obj: Device) -> str:
        return obj.device_model.manufacturer.name

    @admin.display(ordering="room__room_number", description=_("Room"))
    def get_room(self, obj: Device) -> str:
        try:
            return obj.room.room_number
        except AttributeError:
            return "-"

    @admin.display(ordering="room__building__name", description=_("Building"))
    def building(self, obj: Device) -> str:
        try:
            return obj.room.building.name
        except AttributeError:
            return "-"

    @admin.display(description=_("Date rented"))
    def date_rented(self, obj: Device) -> str:
        rental = obj.rentals.filter(return_date=None).first()
        return rental.rental_date if rental else "-"

    @admin.display(description=_("Is rented"), boolean=True)
    def is_rented(self, obj: Device) -> bool:
        return obj.is_rented

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        qs = qs.select_related(
            "room__building",
            "device_model__manufacturer",
            "device_model__device_type",
            "device_model",
            "room__building",
            "room",
            "guardian",
        ).prefetch_related(Prefetch("rentals", queryset=DeviceRental.objects.select_related("borrower")))
        qs = qs.annotate(
            device_manufacturer_model=Concat(
                "device_model__manufacturer__name",
                Value(" "),
                "device_model__name",
            )
        )
        qs = qs.annotate(
            rental_count=Count("rentals", distinct=True),
        )
        qs = qs.annotate(
            is_rented=Case(
                When(Q(rentals__return_date__isnull=True) & Q(rental_count__gt=0), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        return qs


@admin.register(QRCodeGenerationConfig)
class QRCodeGenerationConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "active", "qr_code_size_cm", "qr_code_margin_mm")
    list_filter = ("active",)

    fieldsets = (
        (
            _("QR Code Params"),
            {"fields": ("active", "qr_code_size_cm", "qr_code_margin_mm")},
        ),
        (
            _("PDF Settings"),
            {"fields": ("pdf_page_width_mm", "pdf_page_height_mm", "print_dpi")},
        ),
        (_("Colors"), {"fields": ("fill_color", "back_color")}),
        (
            _("QR Code Labels"),
            {
                "fields": (
                    "room_label",
                    "owner_label",
                    "inventory_number_label",
                    "device_model_label",
                    "serial_number_label",
                    "included_labels",
                )
            },
        ),
    )

    form = QRCodeGenerationConfigForm


@admin.register(DeviceRental)
class DeviceRentalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "is_rented",
        "borrower",
        "rental_date",
        "return_date",
    )
    list_filter = (DeviceTypesForRentalFilter, "borrower", RentalIsRentedFilter)
    search_fields = ("device_manufacturer_model", "borrower__username", "rental_date", "return_date")
    ordering = ("rental_date",)

    form = DeviceRentalForm

    @admin.display(description=_("Is rented"), boolean=True)
    def is_rented(self, obj: DeviceRental) -> bool:
        return obj.is_rented

    @admin.display(description=_("Device model"))
    def device_manufacturer_model(self, obj: DeviceRental) -> str:
        return obj.device.device_manufacturer_model

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            device_manufacturer_model=Concat(
                "device__device_model__manufacturer__name",
                Value(" "),
                "device__device_model__name",
            ),
            is_rented=Case(When(return_date=None, then=Value(True)), default=Value(False), output_field=BooleanField()),
        ).select_related("device__device_model__manufacturer", "device__device_model", "borrower")
        return qs
