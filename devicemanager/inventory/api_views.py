from django.http import FileResponse
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.viewsets import ModelViewSet

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
from devicemanager.inventory.qr_code import DeviceQRCodeGenerator
from devicemanager.inventory.serializers import (
    BuildingSerializer,
    DeviceModelSerializer,
    DeviceRentalSerializer,
    DeviceSerializer,
    DeviceTypeSerializer,
    FacultySerializer,
    ManufacturerSerializer,
    QRCodeGenerateQuerySerializer,
    RoomSerializer,
)


class QRCodeGenerateView(GenericAPIView):
    queryset = Device.objects.all()
    lookup_field = "ids"
    serializer_class = QRCodeGenerateQuerySerializer
    parser_classes = (FormParser, JSONParser)

    @cached_property
    def request_data(self):
        if self.request.method == "GET":
            return self.request.query_params
        return self.request.data

    @cached_property
    def qr_generation_config(self):
        config = QRCodeGenerationConfig.get_active_configuration()
        serializer = self.get_serializer(data=self.request_data, instance=config, partial=True)
        serializer.is_valid(raise_exception=True)
        for key, value in serializer.validated_data.items():
            setattr(config, key, value)
        return config

    @cached_property
    def device_ids(self):
        serializer = self.get_serializer(data=self.request_data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["ids"]

    @cached_property
    def qr_generator(self):
        return DeviceQRCodeGenerator(
            pdf_width_mm=self.qr_generation_config.label_width_mm,
            pdf_height_mm=self.qr_generation_config.label_height_mm,
            pdf_padding_mm=self.qr_generation_config.label_padding_mm,
            gap_x_mm=self.qr_generation_config.label_horizontal_spacing_mm,
            gap_y_mm=self.qr_generation_config.label_vertical_spacing_mm,
            title_gap_mm=self.qr_generation_config.label_title_gap_mm,
            dpi=self.qr_generation_config.dpi,
            inv_prefix=self.qr_generation_config.inv_prefix,
            sn_prefix=self.qr_generation_config.sn_prefix,
            font_size_small=self.qr_generation_config.font_size_small,
            font_size=self.qr_generation_config.font_size,
            font_size_large=self.qr_generation_config.font_size_large,
            fill_color=self.qr_generation_config.fill_color,
            background_color=self.qr_generation_config.background_color,
        )

    def get_device_queryset(self, ids: list[int]):
        return Device.objects.filter(pk__in=ids).select_related("room", "owner", "device_model")

    def get_context_data(self, *args, **kwargs):
        qs = self.get_device_queryset(self.device_ids)

        for device in qs:
            self.qr_generator.add_device(device)

        pdf = self.qr_generator.build_pdf()
        return pdf

    @extend_schema(parameters=[QRCodeGenerateQuerySerializer])
    def get(self, *args, **kwargs):
        pdf = self.get_context_data()

        return FileResponse(pdf, filename="device_labels.pdf", content_type="application/pdf")

    @extend_schema(parameters=[QRCodeGenerateQuerySerializer])
    def post(self, *args, **kwargs):
        pdf = self.get_context_data()

        return FileResponse(pdf, filename="device_labels.pdf", content_type="application/pdf")


class FacultyViewSet(ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class BuildingViewSet(ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class ManufacturerViewSet(ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class DeviceTypeViewSet(ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer


class DeviceModelViewSet(ModelViewSet):
    queryset = DeviceModel.objects.all()
    serializer_class = DeviceModelSerializer


class DeviceViewSet(ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class DeviceRentalViewSet(ModelViewSet):
    queryset = DeviceRental.objects.all()
    serializer_class = DeviceRentalSerializer
