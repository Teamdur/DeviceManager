from rest_framework import serializers

from devicemanager.utils.serializers import CharacterSeperatedField


class TestCharacterSeperatedField:
    class TestSerializer(serializers.Serializer):
        field = CharacterSeperatedField(child=serializers.IntegerField(), separator=",")

    def test_to_internal_value(self):
        serializer = self.TestSerializer(data={"field": "1,2,3"})
        assert serializer.is_valid()
        assert serializer.validated_data["field"] == [1, 2, 3]

    def test_to_representation(self):
        serializer = self.TestSerializer(instance={"field": [1, 2, 3]})
        assert serializer.data["field"] == "1,2,3"
