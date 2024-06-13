from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.utils.translation import gettext_lazy as _


class DeviceIsRentedFilter(SimpleListFilter):
    title = _("Is rented")
    parameter_name = "is_rented"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(rental_count=Count("rentals"))
        if self.value() == "yes":
            return queryset.filter(is_rented=True)
        if self.value() == "no":
            return queryset.filter(is_rented=False)
        return queryset


class DeviceTypesForRentalFilter(SimpleListFilter):
    title = _("Device")
    parameter_name = "device_type"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        values = qs.values_list("device_manufacturer_model", flat=True).distinct()
        return [(value, value) for value in values]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(device_manufacturer_model=self.value())
        return queryset


class RentalIsRentedFilter(SimpleListFilter):
    title = _("Is rented")
    parameter_name = "is_rented"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_rented=True)
        if self.value() == "no":
            return queryset.filter(is_rented=False)
        return queryset
