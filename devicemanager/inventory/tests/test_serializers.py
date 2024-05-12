from devicemanager.inventory.serializers import QRCodeGenerateQuerySerializer


class TestQRCodeGenerateQuerySerializer:
    def test_ids_param_required(self):
        serializer = QRCodeGenerateQuerySerializer(data={})
        assert not serializer.is_valid()
        assert "ids" in serializer.errors

    def test_ids_can_be_provided_as_single_value(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1"})
        assert serializer.is_valid()
        assert serializer.validated_data["ids"] == [1]

    def test_ids_can_be_provided_as_list(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1,2,3"})
        assert serializer.is_valid()
        assert serializer.validated_data["ids"] == [1, 2, 3]

    def test_validates_ids_type(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1,2,3"})
        assert serializer.is_valid()

        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1,2,3,invalid"})
        assert not serializer.is_valid()
        assert "ids" in serializer.errors

    def test_serialize_qr_code_size_cm(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "qr_code_size_cm": 5})
        assert serializer.is_valid()
        assert serializer.validated_data["qr_code_size_cm"] == 5

    def test_serialize_qr_code_margin_mm(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "qr_code_margin_mm": 3})
        assert serializer.is_valid()
        assert serializer.validated_data["qr_code_margin_mm"] == 3

    def test_qr_code_size_cm_must_be_positive(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "qr_code_size_cm": 0})
        assert not serializer.is_valid()
        assert "qr_code_size_cm" in serializer.errors

    def test_qr_code_margin_mm_must_be_positive(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "qr_code_margin_mm": 0})
        assert not serializer.is_valid()
        assert "qr_code_margin_mm" in serializer.errors

    def test_fill_color(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "fill_color": "#FF0000"})
        assert serializer.is_valid()
        assert serializer.validated_data["fill_color"] == "#FF0000"

    def test_back_color(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "back_color": "#FF0000"})
        assert serializer.is_valid()
        assert serializer.validated_data["back_color"] == "#FF0000"

    def test_fill_color_invalid(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "fill_color": "invalid"})
        assert not serializer.is_valid()
        assert "fill_color" in serializer.errors

    def test_back_color_invalid(self):
        serializer = QRCodeGenerateQuerySerializer(data={"ids": "1", "back_color": "invalid"})
        assert not serializer.is_valid()
        assert "back_color" in serializer.errors
