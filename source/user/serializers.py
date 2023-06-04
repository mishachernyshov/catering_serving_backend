from datetime import datetime

import pytz
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import get_default_password_validators
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


User = get_user_model()


class UserCreationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    birthday = serializers.DateField()
    password = serializers.CharField(max_length=128)

    def validate_username(self, value):
        if User.objects.filter(username=value):
            raise ValidationError(_('The user with such username already exists.'))
        return value

    def validate_birthday(self, value):
        current_timestamp = datetime.now(pytz.UTC)
        if value > current_timestamp.date():
            raise ValidationError(_('The specified date of birth is in the future.'))
        return value

    def validate_password(self, value):
        password_validators = get_default_password_validators()
        for validator in password_validators:
            validator.validate(value)
        return value
