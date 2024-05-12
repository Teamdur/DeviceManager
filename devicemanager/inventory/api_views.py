from django.http import FileResponse
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from devicemanager.inventory.models import Device, QRCodeGenerationConfig
from devicemanager.inventory.qr_code import QRCodePDFGenerator
from devicemanager.inventory.serializers import (
    QRCodeDataSerializer,
    QRCodeGenerateQuerySerializer,
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


qr_code_generate_view = QRCodeGenerateView.as_view()
