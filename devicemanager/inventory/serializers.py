from rest_framework import serializers

from devicemanager.inventory.models import Device


class QRCodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "serial_number", "inventory_number"]
