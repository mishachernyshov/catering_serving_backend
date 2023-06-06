"""
Dish application configuration module.
"""
from django.apps import AppConfig


class DishConfig(AppConfig):
    """
    Dish application configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "dish"
    verbose_name = "dish"

    def ready(self):
        from dish import handlers
