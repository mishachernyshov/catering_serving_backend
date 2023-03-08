"""
User application configuration module.
"""
from django.apps import AppConfig


class UserConfig(AppConfig):
    """
    User application configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "user"
