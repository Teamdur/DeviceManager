from django.utils.translation import gettext as _
from rest_framework.exceptions import NotAcceptable, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from devicemanager.inventory.models import Device


class QueryParamFilterMixin(APIView):
    lookup_field: str

    def get_filter_params(self):
        raw_query_params = self.request.query_params.get(self.lookup_field)

        if not raw_query_params:
            raise NotAcceptable(_("Query parameter {} is required".format(self.lookup_field)))

        try:
            ids = [int(id) for id in raw_query_params.split(",")]
        except (ValueError, TypeError):
            raise ParseError(_("Invalid query parameter {} provided".format(self.lookup_field)))

        if len(ids) == 0:
            raise NotAcceptable(_("Query parameter {} is required".format(self.lookup_field)))

        return ids


class QRCodeGenerateView(QueryParamFilterMixin, GenericAPIView):
    queryset = Device.objects.all()
    lookup_field = "ids"

    def get_queryset(self):
        filter_params = self.get_filter_params()
        qs = self.queryset.filter(pk__in=filter_params)
        return qs

    def get(self, request, *args, **kwargs):
        devices = self.get_queryset()
        return Response({"message": "QR Code Generated Successfully", "number_of_devices": devices.count()})


qr_code_generate_view = QRCodeGenerateView.as_view()
