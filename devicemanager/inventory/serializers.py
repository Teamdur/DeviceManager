from typing import NotRequired, TypedDict

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from devicemanager.inventory.api_views import Faculty
from devicemanager.inventory.models import (
    Building,
    Device,
    DeviceModel,
    DeviceType,
    Manufacturer,
    QRCodeGenerationConfig,
    Room,
)
from devicemanager.users.models import User
from devicemanager.utils.serializers import CharacterSeperatedField


class QRCodeGenerateQueryData(TypedDict):
    ids: list[int]
    qr_code_size_cm: NotRequired[int]
    qr_code_margin_mm: NotRequired[int]
    fill_color: NotRequired[str]
    back_color: NotRequired[str]
    print_dpi: NotRequired[int]
    pdf_page_height_mm: NotRequired[int]
    pdf_page_width_mm: NotRequired[int]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Valid request example",
            summary="Valid request query parameters",
            value={
                "ids": "1,2,3",
                "qr_code_size_cm": 5,
                "qr_code_margin_mm": 5,
                "fill_color": "#000000",
                "back_color": "#FFFFFF",
            },
            request_only=True,
        )
    ]
)
class QRCodeGenerateQuerySerializer(serializers.ModelSerializer):
    ids = CharacterSeperatedField(required=True, separator=",", child=serializers.IntegerField())

    class Meta:
        model = QRCodeGenerationConfig
        fields = (
            "ids",
            "qr_code_size_cm",
            "qr_code_margin_mm",
            "fill_color",
            "back_color",
            "print_dpi",
            "pdf_page_height_mm",
            "pdf_page_width_mm",
        )

    @property
    def validated_data(self) -> QRCodeGenerateQueryData:
        return super().validated_data


class QRCodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "serial_number", "inventory_number"]


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ["id", "full_name", "short_name"]


class BuildingSerializer(serializers.ModelSerializer):
    faculty = serializers.PrimaryKeyRelatedField(many=False, queryset=Faculty.objects)

    class Meta:
        model = Building
        fields = ["id", "name", "faculty"]


class RoomSerializer(serializers.ModelSerializer):
    building = serializers.PrimaryKeyRelatedField(many=False, queryset=Building.objects)
    occupants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects)

    class Meta:
        model = Room
        fields = ["id", "room_number", "building", "description", "occupants"]


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["id", "name", "description"]


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ["id", "name", "short_name"]


class DeviceModelSerializer(serializers.ModelSerializer):
    device_type = serializers.PrimaryKeyRelatedField(many=False, queryset=DeviceType.objects)
    manufacturer = serializers.PrimaryKeyRelatedField(many=False, queryset=Manufacturer.objects)

    class Meta:
        model = DeviceModel
        fields = ["id", "device_type", "manufacturer", "name", "description"]


class DeviceSerializer(serializers.ModelSerializer):
    model = serializers.PrimaryKeyRelatedField(many=False, queryset=DeviceModel.objects)

    class Meta:
        model = Device
        fields = [
            "id",
            "model",
            "serial_number",
            "inventory_number",
        ]
