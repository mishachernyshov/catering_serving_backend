"""
Dish administration module.
"""
from django.contrib import admin

from dish import models


admin.site.register(
    (
        models.Dish,
        models.DishCategory,
        models.DishSubcategory,
        models.Food,
        models.CateringEstablishmentDish,
        models.Discount,
        models.OrderedDish,
    )
)
