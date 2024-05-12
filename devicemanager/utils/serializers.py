from django.utils.translation import gettext as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


@extend_schema_field(OpenApiTypes.STR)
class CharacterSeperatedField(serializers.ListField):
    def __init__(self, separator, *args, **kwargs):
        self.separator = separator
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        # I do not know why but sometimes data is a list
        # this is most likely django fault as it is as list in request.search_params
        if isinstance(data, list):
            data = self.separator.join(str(el) for el in data)
        if not isinstance(data, str):
            msg = _("Incorrect type. Expected a string, but got %s")
            raise serializers.ValidationError(msg % type(data).__name__)

        data = data.split(self.separator)
        return super().to_internal_value(data)

    def to_representation(self, obj):
        obj = super().to_representation(obj)
        return self.separator.join(str(el) for el in obj)
