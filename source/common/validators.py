import base64
import binascii
import re

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from common.constants import BASE64_ENCODED_FILE_REGEXP


def validate_encoded_file(value):
    if not re.fullmatch(BASE64_ENCODED_FILE_REGEXP, value):
        raise ValidationError(_('Provided encoded data has incorrect format.'))
    try:
        base64.standard_b64decode(value.split(',')[1])
    except binascii.Error as ex:
        raise ValidationError(str(ex)) from ex
