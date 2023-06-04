from django_filters import rest_framework as filters


class CateringEstablishmentMenuFilter(filters.FilterSet):
    catering_establishment = filters.NumberFilter()
    has_discount = filters.BooleanFilter(field_name='discount', method='filter_has_discount')
    final_price_min = filters.NumberFilter(field_name='final_price', lookup_expr='gte')
    final_price_max = filters.NumberFilter(field_name='final_price', lookup_expr='lte')
    category = filters.NumberFilter(field_name='dish__subcategory__category')
    subcategory = filters.NumberFilter(field_name='dish__subcategory')
    food = filters.NumberFilter(field_name='dish__food')

    def filter_has_discount(self, queryset, *args):
        return queryset.with_active_discount()
