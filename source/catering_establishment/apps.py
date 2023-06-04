"""
Catering establishment application configuration module.
"""
from django.apps import AppConfig


class CateringEstablishmentConfig(AppConfig):
    """
    Catering establishment application configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "catering_establishment"

    def ready(self):
        import catering_establishment.handlers
