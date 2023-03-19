"""
Models used in different project applications.
"""
from django.db import models


class TimeRangedModel(models.Model):
    """
    A model that has start date and end date characteristics.
    """

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
