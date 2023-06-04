from django.db.models.signals import post_delete
from django.dispatch import receiver

from dish import models as dish_models


@receiver(post_delete, sender=dish_models.CateringEstablishmentDish)
def delete_media_file(sender, instance, *args, **kwargs):
    try:
        # BUG: Deletion is not successful
        instance.photo.delete(save=False)
    except:
        pass
