from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from catering_establishment.models import Booking, CateringEstablishment


class IsCateringEstablishmentOwner(BasePermission):
    def has_permission(self, request, view):
        catering_establishment = get_object_or_404(CateringEstablishment, pk=request.parser_context['kwargs']['pk'])
        return catering_establishment.owner == request.user


class IsVisible(BasePermission):
    def has_permission(self, request, view):
        catering_establishment = get_object_or_404(CateringEstablishment, pk=request.parser_context['kwargs']['pk'])
        return catering_establishment.is_visible


class IsBookingAuthor(BasePermission):
    def has_permission(self, request, view):
        booking_id = request.query_params.get('booking') if request.method == 'GET' else request.data.get('booking')
        booking = get_object_or_404(Booking, pk=booking_id)
        return booking.client == request.user
