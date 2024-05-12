from django.urls import path

from devicemanager.inventory.api_views import qr_code_generate_view

app_name = "inventory"

urlpatterns = [path("qr-generate/", qr_code_generate_view, name="qr-generate")]
