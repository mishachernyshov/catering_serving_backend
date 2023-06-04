from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")


class Region(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')

    def __str__(self):
        return f'{self.country}, {self.name}'

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class Settlement(models.Model):
    name = models.CharField(max_length=64)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='settlements')

    def __str__(self):
        return f'{self.region}, {self.name}'

    class Meta:
        verbose_name = _("Settlement")
        verbose_name_plural = _("Settlements")


class Address(models.Model):
    name = models.CharField(max_length=256)
    settlement = models.ForeignKey(Settlement, on_delete=models.CASCADE, related_name='addresses')

    def __str__(self):
        return f'{self.settlement}, {self.name}'

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
