from django.urls import path
from rest_framework import routers

from devicemanager.inventory.api_views import (
    BuildingViewSet,
    DeviceModelViewSet,
    DeviceRentalViewSet,
    DeviceTypeViewSet,
    DeviceViewSet,
    FacultyViewSet,
    ManufacturerViewSet,
    QRCodeGenerateView,
    RoomViewSet,
)

app_name = "inventory"

qr_code_generate_view = QRCodeGenerateView.as_view()

router = routers.SimpleRouter()
router.register(r"faculties", FacultyViewSet)
router.register(r"buildings", BuildingViewSet)
router.register(r"rooms", RoomViewSet)
router.register(r"manufacturers", ManufacturerViewSet)
router.register(r"device-types", DeviceTypeViewSet)
router.register(r"device-models", DeviceModelViewSet)
router.register(r"device-rentals", DeviceRentalViewSet)
router.register(r"devices", DeviceViewSet)

urlpatterns = [path("qr-generate/", qr_code_generate_view, name="qr-generate"), *router.urls]
