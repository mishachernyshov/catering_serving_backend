"""
Common application configuration module.
"""
from django.apps import AppConfig


class CommonConfig(AppConfig):
    """
    Common application configuration.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
