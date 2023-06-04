"""
Catering establishment views.
"""
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from catering_establishment import filters
from catering_establishment import models as ce_models
from catering_establishment.permissions import IsBookingAuthor, IsCateringEstablishmentOwner, IsVisible
from catering_establishment import serializers
from catering_establishment.services import (
    create_booking,
    create_catering_establishment_with_related_models,
    get_establishments_tables,
    get_establishments_work_hours,
)
from dish.models import CateringEstablishmentDish


class CateringEstablishmentViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    @action(detail=False, methods=('post',), url_path='create_new')
    def create_new(self, request, *args, **kwargs):
        data = request.data
        data['owner'] = request.user.id
        catering_establishment = create_catering_establishment_with_related_models(data)
        return Response({'id': catering_establishment.id})

    @action(detail=True, url_path='update_info')
    def retrieve_update_info(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, url_path='main_info')
    def retrieve_main_info(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        match self.action:
            case 'create_new':
                return (IsAuthenticated(),)
            case 'retrieve_main_info':
                return ((IsAuthenticated | IsVisible)(),)
            case _:
                return (IsAuthenticated(), IsCateringEstablishmentOwner())

    def get_serializer_class(self):
        if self.action == 'retrieve_main_info':
            return serializers.CateringEstablishmentMainInfoSerializer
        return serializers.CateringEstablishmentSerializer

    def get_queryset(self):
        if self.action == 'retrieve_main_info':
            return ce_models.CateringEstablishment.objects.main_info()
        return ce_models.CateringEstablishment.objects.all()


class UserCateringEstablishmentsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CateringEstablishmentRepresentationSerializer

    def get_queryset(self):
        return ce_models.CateringEstablishment.objects.filter(owner=self.request.user)


class CateringEstablishmentsRepresentationView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CateringEstablishmentRepresentationSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = ce_models.CateringEstablishment.objects.all()
        if establishments_ids := self.request.query_params.getlist('id'):
            queryset = queryset.filter(id__in=establishments_ids)
        return queryset


class CateringEstablishmentTablesListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CateringEstablishmentTableSerializer
    pagination_class = None

    def get_queryset(self):
        return ce_models.CateringEstablishmentTable.objects.filter(
            catering_establishment=self.request.query_params.get('catering_establishment')
        )


class CateringEstablishmentsTablesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = ce_models.CateringEstablishment.objects.with_tables_characteristics().filter(
            id__in=request.query_params.getlist('id')
        )
        return Response(get_establishments_tables(queryset))


class CateringEstablishmentWorkHoursView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = ce_models.WorkHours.objects.filter(catering_establishment__in=request.query_params.getlist('id'))
        return Response(get_establishments_work_hours(queryset))


class CateringEstablishmentCatalogView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CateringEstablishmentCatalogItemSerializer
    queryset = ce_models.CateringEstablishment.objects.catalog_filtration_related_data()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('name',)
    ordering_fields = ('name', 'rating')
    filterset_class = filters.CateringEstablishmentCatalogFilter


class CateringEstablishmentUserRatingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            {
                'rating': get_object_or_404(
                    ce_models.CateringEstablishmentRating,
                    catering_establishment=request.query_params.get('establishment'),
                    visitor=request.user,
                ).rating,
            }
        )

    def post(self, request):
        data = request.data
        data['visitor'] = request.user.id
        serializer_class = serializers.CateringEstablishmentUserRatingSerializer
        try:
            rating = ce_models.CateringEstablishmentRating.objects.get(
                catering_establishment=data.get('catering_establishment'),
                visitor=data['visitor'],
            )
            serializer = serializer_class(rating, data=data)
        except ce_models.CateringEstablishmentRating.DoesNotExist:
            serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        avg_rating = (
            ce_models.CateringEstablishment.objects.with_avg_rating()
            .get(id=serializer.validated_data['catering_establishment'].id)
            .rating
        )
        return Response({'avg_rating': avg_rating})


class CateringEstablishmentFeedbacksView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CateringEstablishmentFeedbackInfoSerializer

    def get_queryset(self):
        return ce_models.CateringEstablishmentFeedback.objects.filter(
            catering_establishment=self.request.query_params.get('catering_establishment')
        ).order_by('-created')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CateringEstablishmentFeedbackSerializer
        return serializers.CateringEstablishmentFeedbackInfoSerializer

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            kwargs['data']['visitor'] = self.request.user.id
        return super().get_serializer(*args, **kwargs)


class BookingViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.BookingFilter
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list_owned_by_user':
            queryset = (
                ce_models.Booking.objects.filter(client=self.request.user)
                .with_activeness_status()
                .with_payment_status()
            )
            if self.request.query_params.get('extended') == 'true':
                queryset = queryset.prefetch_related(
                    Prefetch(
                        'ordered_dishes__catering_establishment_dish',
                        queryset=CateringEstablishmentDish.objects.with_final_price(),
                    )
                )
            return queryset
        return ce_models.Booking.objects.all()

    def get_serializer_class(self):
        if self.action == 'list_owned_by_user' and self.request.query_params.get('extended') == 'true':
            return serializers.ExtendedBookingSerializer
        if self.action in ('create', 'update'):
            return serializers.BookingWriteSerializer
        return serializers.BookingReadSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data['client'] = request.user.id
        catering_establishment = create_booking(data)
        return Response(catering_establishment)

    def partial_update(self, request, *args, **kwargs):
        request.data['client'] = request.user.id
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, url_path='owned_by_user')
    def list_owned_by_user(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BookingPaymentCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, IsBookingAuthor)
    serializer_class = serializers.BookingPaymentSerializer


class BookingsStatisticsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.EstablishmentBookingsCountSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            ce_models.CateringEstablishment.objects.filter(
                owner=self.request.user,
                tables__bookings__start_datetime__gte=self.request.query_params.get('start_date'),
                tables__bookings__end_datetime__lte=self.request.query_params.get('end_date'),
            )
            .with_bookings_count()
            .order_by('-bookings_count')
        )
