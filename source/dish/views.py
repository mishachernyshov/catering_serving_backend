"""
Dish views.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from catering_establishment.permissions import IsBookingAuthor
from dish import models as dish_models
from dish import serializers as dish_serializers
from dish.filters import CateringEstablishmentMenuFilter
from dish.services import bulk_create_ordered_dishes, delete_booking_related_ordered_dishes


class DishesRelatedDataView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(
            {
                'dishes_names': dish_serializers.DishNameSerializer(
                    dish_models.Dish.objects.all().order_by('name'), many=True
                ).data,
                'categories': (
                    dish_serializers.DishCategorySerializer(dish_models.DishCategory.objects.all(), many=True).data
                ),
                'foods': dish_serializers.FoodSerializer(dish_models.Food.objects.all(), many=True).data,
            }
        )


class DishesNamesView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = dish_serializers.DishNameSerializer
    pagination_class = None

    def get_queryset(self):
        return dish_models.Dish.objects.filter(id__in=self.request.query_params.getlist('id'))


class CreateDishView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = dish_serializers.DishSerializer


class CateringEstablishmentMenuView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = dish_serializers.CateringEstablishmentMenuItemSerializer
    queryset = dish_models.CateringEstablishmentDish.objects.with_final_price()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('dish__name',)
    ordering_fields = ('dish__name', 'final_price')
    filterset_class = CateringEstablishmentMenuFilter


class OrderPopulationView(CreateAPIView):
    permission_classes = (IsAuthenticated, IsBookingAuthor)
    serializer_class = dish_serializers.OrderedDishWriteSerializer


class OrderUpdateView(APIView):
    permission_classes = (IsAuthenticated, IsBookingAuthor)

    def post(self, request, *args, **kwargs):
        serializer = dish_serializers.OrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        delete_booking_related_ordered_dishes(data['booking'])
        bulk_create_ordered_dishes(data['booking'], data['ordered_dishes'])
        return Response(status=status.HTTP_204_NO_CONTENT)
