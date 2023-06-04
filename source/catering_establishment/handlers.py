from django.db.models.signals import post_delete
from django.dispatch import receiver

from catering_establishment import models as ce_models


@receiver(post_delete, sender=ce_models.CateringEstablishmentPhoto)
def delete_media_file(sender, instance, *args, **kwargs):
    try:
        instance.photo.delete(save=False)
    except:
        pass
