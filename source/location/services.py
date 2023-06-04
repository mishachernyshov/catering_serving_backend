from location import models as location_models
from location import serializers as location_serializers


def get_locations_data():
    return {
        'countries': location_serializers.CountrySerializer(location_models.Country.objects.all(), many=True).data,
        'regions': location_serializers.RegionSerializer(location_models.Region.objects.all(), many=True).data,
        'settlements': location_serializers.SettlementSerializer(
            location_models.Settlement.objects.all(), many=True
        ).data,
        'addresses': location_serializers.AddressSerializer(location_models.Address.objects.all(), many=True).data,
    }
