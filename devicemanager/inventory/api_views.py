from django.http import FileResponse
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
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
from devicemanager.inventory.qr_code import QRCodePDFGenerator
from devicemanager.inventory.serializers import (
    BuildingSerializer,
    DeviceModelSerializer,
    DeviceRentalSerializer,
    DeviceSerializer,
    DeviceTypeSerializer,
    FacultySerializer,
    ManufacturerSerializer,
    QRCodeDataSerializer,
    QRCodeGenerateQuerySerializer,
    RoomSerializer,
)


class QRCodeGenerateView(GenericAPIView):
    queryset = Device.objects.all()
    lookup_field = "ids"
    serializer_class = QRCodeDataSerializer

    def get_queryset(self):
        filter_params = self.search_params["ids"]
        qs = self.queryset.filter(pk__in=filter_params)
        return qs

    @cached_property
    def search_params(self):
        params = self.request.query_params
        serializer = QRCodeGenerateQuerySerializer(data=params)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @cached_property
    def qr_generation_config(self):
        stored_config = QRCodeGenerationConfig.get_active_configuration()

        for key, value in self.search_params.items():
            setattr(stored_config, key, value)

        return stored_config

    @extend_schema(parameters=[QRCodeGenerateQuerySerializer])
    def get(self, request, *args, **kwargs):
        devices = self.get_queryset()
        pdf = QRCodePDFGenerator(devices, QRCodeDataSerializer, self.qr_generation_config).run()

        return FileResponse(pdf, content_type="application/pdf")


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
