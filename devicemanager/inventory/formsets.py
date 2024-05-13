from datetime import date

from django import forms


class DeviceRentalFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        rented_devices = set()
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            return_date = form.cleaned_data.get("return_date")
            is_pending_rental = return_date is None or return_date > date.today()
            if is_pending_rental:
                device = form.cleaned_data.get("device")
                if device in rented_devices:
                    raise forms.ValidationError("Device is already rented")
                rented_devices.add(device)
