from typing import NotRequired, TypedDict

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from devicemanager.inventory.models import Device, QRCodeGenerationConfig
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
