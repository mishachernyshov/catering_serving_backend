"""
User module models.
"""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserProfile(models.Model):
    """
    Additional data about a user.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()
    balance = models.FloatField()

    def __str__(self):
        return self.user.username  # pylint: disable=no-member


class UserBalanceChange(models.Model):
    """
    User balance changing values.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    transaction_datetime = models.DateTimeField()

    def __str__(self):
        return f'{self.user.username}: {self.amount} ({self.transaction_datetime})'  # pylint: disable=no-member
