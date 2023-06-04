from django_filters import rest_framework as filters

from common.filters import NumberInFilter
from common.utils import get_end_of_date, get_start_of_date


class CateringEstablishmentCatalogFilter(filters.FilterSet):
    rating_min = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    address__name = filters.CharFilter(lookup_expr='icontains')
    settlement = filters.NumberFilter()
    region = filters.NumberFilter()
    country = filters.NumberFilter()


class BookingFilter(filters.FilterSet):
    catering_establishment_table = filters.NumberFilter()
    date = filters.DateFilter(method='filter_date')
    catering_establishment = filters.NumberFilter(field_name='catering_establishment_table__catering_establishment')
    active_only = filters.BooleanFilter(method='filter_activeness')
    is_paid = filters.BooleanFilter()

    def filter_date(self, queryset, _, value):
        return queryset.filter(start_datetime__lte=get_end_of_date(value), end_datetime__gte=get_start_of_date(value))

    def filter_activeness(self, queryset, _, value):
        return queryset.active_only() if value else queryset
