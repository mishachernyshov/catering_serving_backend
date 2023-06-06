"""
Dish models.
"""
from datetime import datetime

from django.db import models
from django.db.models import Case, When, F, Q
from django.utils.translation import gettext_lazy as _

from catering_establishment.models import Booking, CateringEstablishment
from common.models import TimeRangedModel


class DishCategory(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Dish category")
        verbose_name_plural = _("Dish categories")


class DishSubcategory(models.Model):
    name = models.CharField(max_length=32)
    category = models.ForeignKey(DishCategory, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Dish subcategory")
        verbose_name_plural = _("Dish subcategories")


class Food(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Food")
        verbose_name_plural = _("Foods")


class DishQuerySet(models.QuerySet):
    def with_ordering_count(self):
        return super().annotate(orders_count=models.Count('catering_establishment_dishes__ordered_dishes'))


class DishManager(models.Manager):
    def get_queryset(self):
        return DishQuerySet(self.model, using=self._db)

    def with_ordering_count(self):
        return self.get_queryset().with_ordering_count()


class Dish(models.Model):
    name = models.CharField(max_length=64)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(DishSubcategory, on_delete=models.CASCADE, related_name='dishes')

    objects = DishManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Dish")
        verbose_name_plural = _("Dishes")


class CateringEstablishmentDishQuerySet(models.QuerySet):
    def with_final_price(self):
        now = datetime.now()
        return super().annotate(
            final_price=Case(
                When(
                    Q(discount__type=Discount.PERCENT)
                    & Q(discount__start_datetime__lte=now)
                    & Q(discount__end_datetime__gte=now),
                    then=F('price') - (F('price') * F('discount__amount') / 100),
                ),
                When(
                    Q(discount__type=Discount.CASH_VALUE)
                    & Q(discount__start_datetime__lte=now)
                    & Q(discount__end_datetime__gte=now),
                    then=F('price') - F('discount__amount'),
                ),
                default='price',
            )
        )

    def with_active_discount(self):
        now = datetime.now()
        return super().filter(discount__start_datetime__lte=now, discount__end_datetime__gte=now)


class CateringEstablishmentDishManager(models.Manager):
    def get_queryset(self):
        return CateringEstablishmentDishQuerySet(self.model, using=self._db)

    def with_final_price(self):
        return self.get_queryset().with_final_price()

    def with_active_discount(self):
        return self.get_queryset().with_active_discount()


class CateringEstablishmentDish(models.Model):
    catering_establishment = models.ForeignKey(
        CateringEstablishment,
        on_delete=models.CASCADE,
        related_name='catering_establishment_dishes',
    )
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='catering_establishment_dishes')
    description = models.TextField()
    photo = models.ImageField(upload_to='dish/photos/')
    price = models.FloatField()

    objects = CateringEstablishmentDishManager()

    def __str__(self):
        return f'{self.dish} - {self.catering_establishment}'


class Discount(TimeRangedModel):
    PERCENT = 'percent'
    CASH_VALUE = 'cash_value'
    TYPE_CHOICES = (
        (PERCENT, _('Percent')),
        (CASH_VALUE, _('Cash value')),
    )

    catering_establishment_dish = models.OneToOneField(CateringEstablishmentDish, on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    amount = models.FloatField()

    def __str__(self):
        return str(self.catering_establishment_dish)


class OrderedDish(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='ordered_dishes')
    catering_establishment_dish = models.ForeignKey(
        CateringEstablishmentDish,
        on_delete=models.CASCADE,
        related_name='ordered_dishes',
    )
    weight = models.FloatField()

    def __str__(self):
        return f'{self.booking} - {self.catering_establishment_dish.dish.name}'
