BASE64_METADATA_REGEXP = r'data:\w+/(\w+);base64'
BASE64_ENCODED_FILE_REGEXP = rf'^{BASE64_METADATA_REGEXP},.*$'
DATETIME_DESERIALIZATION_FORMAT = '%Y-%m-%dT%H:%M'
