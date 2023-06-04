"""
Catering establishment models.
"""
from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Avg, ExpressionWrapper, F, Q
from django.db.models.functions import Coalesce
from django_extensions.db.models import TimeStampedModel

from catering_establishment.constants import CATERING_ESTABLISHMENTS_NAME_MAX_LENGTH
from common.models import TimeRangedModel
from location.models import Address


class WorkHours(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.start_time} - {self.end_time}'


class CateringEstablishmentQuerySet(models.QuerySet):
    def visible_only(self):
        return super().filter(is_visible=True)

    def with_avg_rating(self):
        return super().prefetch_related('ratings').annotate(rating=Coalesce(Avg('ratings__rating'), 0.0))

    def with_photos(self):
        return super().prefetch_related('photos')

    def with_location_data(self):
        return (
            super()
            .select_related('address')
            .annotate(settlement=F('address__settlement'))
            .select_related('address__settlement')
            .annotate(region=F('address__settlement__region'))
            .select_related('address__settlement__region')
            .annotate(country=F('address__settlement__region__country'))
        )

    def with_tables_characteristics(self):
        return super().prefetch_related('tables')


class CateringEstablishmentManager(models.Manager):
    def get_queryset(self):
        return CateringEstablishmentQuerySet(self.model, using=self._db)

    def visible_only(self):
        return self.get_queryset().visible_only()

    def with_avg_rating(self):
        return self.get_queryset().with_avg_rating()

    def with_location_data(self):
        return self.get_queryset().with_location_data()

    def catalog_filtration_related_data(self):
        return (
            self.get_queryset()
            .only(
                'id',
                'name',
                'address__name',
                'address__settlement',
                'address__settlement__region',
                'address__settlement__region__country',
            )
            .visible_only()
            .with_avg_rating()
            .with_location_data()
        )

    def main_info(self):
        return (
            self.get_queryset()
            .only(
                'name',
                'description',
                'address__name',
                'address__settlement',
                'address__settlement__region',
                'address__settlement__region__country',
                'address__settlement__name',
                'address__settlement__region__name',
                'address__settlement__region__country__name',
            )
            .with_photos()
            .with_avg_rating()
            .with_location_data()
        )

    def with_tables_characteristics(self):
        return self.get_queryset().with_tables_characteristics()


class CateringEstablishment(models.Model):
    """
    Catering establishment model.
    """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=CATERING_ESTABLISHMENTS_NAME_MAX_LENGTH)
    description = models.TextField()
    balance = models.FloatField(editable=False, default=0)
    is_visible = models.BooleanField(default=True)
    last_payment_datetime = models.DateTimeField(null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    work_hours = models.OneToOneField(WorkHours, on_delete=models.CASCADE, related_name='catering_establishment')

    objects = CateringEstablishmentManager()

    def __str__(self):
        return self.name


class CateringEstablishmentPhoto(models.Model):
    """
    Catering establishment image model.
    """

    photo = models.ImageField(upload_to='catering_establishment/photos/')
    catering_establishment = models.ForeignKey(CateringEstablishment, on_delete=models.CASCADE, related_name='photos')

    def __str__(self):
        return self.photo.name


class CateringEstablishmentRating(models.Model):
    """
    Catering establishment rating by visitor.
    """

    catering_establishment = models.ForeignKey(CateringEstablishment, on_delete=models.CASCADE, related_name='ratings')
    visitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.catering_establishment} - {self.visitor}'

    class Meta:
        unique_together = ('catering_establishment', 'rating')


class CateringEstablishmentFeedback(TimeStampedModel):
    """
    Visitor's feedback about a catering establishment.
    """

    catering_establishment = models.ForeignKey(
        CateringEstablishment,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    visitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    feedback = models.TextField()

    def __str__(self):
        return f'{self.catering_establishment} - {self.visitor}'

    class Meta:
        unique_together = ('catering_establishment', 'feedback')


class CateringEstablishmentTable(models.Model):
    """
    A table in a catering establishment.
    """

    catering_establishment = models.ForeignKey(CateringEstablishment, on_delete=models.CASCADE, related_name='tables')
    number = models.IntegerField()
    serving_clients_number = models.IntegerField()

    def __str__(self):
        return f'{self.catering_establishment}: {self.number}'


class BookingQuerySet(models.QuerySet):
    def with_activeness_status(self):
        return super().annotate(
            is_active=ExpressionWrapper(
                Q(end_datetime__gte=datetime.now()),
                output_field=models.BooleanField(),
            )
        )

    def active_only(self):
        return self.with_activeness_status().filter(is_active=True)

    def with_payment_status(self):
        return super().annotate(
            is_paid=ExpressionWrapper(
                Q(booking_payment__isnull=False),
                output_field=models.BooleanField(),
            )
        )


class BookingManager(models.Manager):
    def get_queryset(self):
        return BookingQuerySet(self.model, using=self._db)

    def with_activeness_status(self):
        return self.get_queryset().with_activeness_status()

    def active_only(self):
        return self.get_queryset().with_activeness_status().active_only()

    def with_payment_status(self):
        return self.get_queryset().with_payment_status()


class Booking(TimeRangedModel):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    catering_establishment_table = models.ForeignKey(
        CateringEstablishmentTable,
        on_delete=models.CASCADE,
        related_name='bookings',
    )

    objects = BookingManager()

    def __str__(self):
        return f'{self.catering_establishment_table.catering_establishment} - {self.client}'


class BookingPayment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='booking_payment')
    amount = models.FloatField()
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.booking} ({self.datetime})'


class BookingConditions(models.Model):
    id = models.CharField(max_length=12, primary_key=True, editable=False)
    catering_establishment = models.ManyToManyField(CateringEstablishment)

    def __str__(self):
        return self.catering_establishment


class SpecialOffer(models.Model):
    id = models.CharField(max_length=12, primary_key=True, editable=False)
    catering_establishments = models.ManyToManyField(
        CateringEstablishment,
        through='CateringEstablishmentSpecialOffer',
        related_name='special_offers',
    )

    def __str__(self):
        return self.id


class CateringEstablishmentSpecialOffer(models.Model):
    catering_establishment = models.ForeignKey(CateringEstablishment, on_delete=models.CASCADE)
    special_offer = models.ForeignKey(SpecialOffer, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.catering_establishment} - {self.special_offer}'


class SpecialOfferParticipation(models.Model):
    catering_establishment_special_offer = models.ForeignKey(
        CateringEstablishmentSpecialOffer,
        on_delete=models.CASCADE,
    )
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datetime = models.DateTimeField()

    def __str__(self):
        return f'{self.catering_establishment_special_offer} ({self.participant})'


class CateringEstablishmentBalanceChange(models.Model):
    catering_establishment = models.ForeignKey(
        CateringEstablishment,
        on_delete=models.CASCADE,
        related_name='balance_changes',
    )
    amount = models.FloatField()
    transaction_datetime = models.DateTimeField()

    def __str__(self):
        return f'{self.catering_establishment} ({self.transaction_datetime})'
