import base64
import datetime
import re
from uuid import uuid4

from django.conf import settings

from common.constants import BASE64_METADATA_REGEXP


def get_file_format_from_base64_metadata(metadata):
    return re.match(BASE64_METADATA_REGEXP, metadata).group(1)


def save_media_file(path, media_file, filename=None, file_format='.png'):
    if not filename:
        filename = f'{uuid4()}.{file_format}'

    file_path = settings.MEDIA_ROOT / path / filename

    with open(file_path, 'wb') as file:
        file.write(media_file)

    return f'{path}/{filename}'


def save_base64_encoded_file(encoded_file, saving_path):
    metadata, encoded_content = encoded_file.split(',')
    file_format = get_file_format_from_base64_metadata(metadata)
    return save_media_file(saving_path, base64.standard_b64decode(encoded_content), file_format=file_format)


def build_absolute_url_to_media_file(media_file_url):
    return f"{settings.BASE_URL}{settings.MEDIA_URL}{media_file_url}"


def get_start_of_date(date):
    return datetime.datetime.combine(date, datetime.time.min)


def get_end_of_date(date):
    return datetime.datetime.combine(date, datetime.time.max)
