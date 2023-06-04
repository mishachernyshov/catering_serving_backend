"""
Catering establishment administration module.
"""
from django.contrib import admin

from catering_establishment import models


admin.site.register(
    (
        models.CateringEstablishment,
        models.CateringEstablishmentTable,
        models.CateringEstablishmentPhoto,
        models.CateringEstablishmentRating,
        models.CateringEstablishmentFeedback,
        models.WorkHours,
        models.Booking,
        models.BookingPayment,
    )
)
