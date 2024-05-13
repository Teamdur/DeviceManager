from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from devicemanager.inventory.models import Device, DeviceRental
from devicemanager.utils.widgets import ActionLink


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        exclude = ("id",)

    def get_action_links(self) -> list[ActionLink]:
        if self.instance and self.instance.pk:
            return self.get_action_data()
        return []

    def get_action_data(self) -> list[ActionLink]:
        return [
            {
                "url": reverse("inventory:qr-generate") + f"?ids={self.instance.pk}",
                "name": _("Generate QR code"),
            }
        ]


class DeviceRentalForm(forms.ModelForm):
    class Meta:
        model = DeviceRental
        exclude = ("id",)

    def clean(self):
        cleaned_data = super().clean()

        return_date = self.cleaned_data.get("return_date")
        device_pk = self.cleaned_data.get("device").pk
        other_rentals = DeviceRental.objects.filter(device=device_pk).exclude(pk=self.instance.pk)
        if return_date is None and other_rentals.exists():
            raise forms.ValidationError(_("Device is already rented"))

        return cleaned_data


class QRCodeGenerationConfigForm(forms.ModelForm):
    included_labels = forms.MultipleChoiceField(
        label=_("Included labels"),
        choices=Device.LABELS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Device
        exclude = ("id",)
