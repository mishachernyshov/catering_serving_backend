from django.contrib import admin

from location import models


admin.site.register(
    (
        models.Country,
        models.Region,
        models.Settlement,
        models.Address,
    )
)
