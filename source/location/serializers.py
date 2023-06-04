from rest_framework import serializers

from location import models as location_models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = location_models.Country
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = location_models.Region
        fields = '__all__'


class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = location_models.Settlement
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = location_models.Address
        fields = '__all__'
