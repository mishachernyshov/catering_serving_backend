from dish import models as dish_models


def delete_booking_related_ordered_dishes(booking_id):
    dish_models.OrderedDish.objects.filter(booking=booking_id).delete()


def bulk_create_ordered_dishes(booking, ordered_dishes_data):
    dish_models.OrderedDish.objects.bulk_create(
        [
            dish_models.OrderedDish(
                booking_id=booking,
                catering_establishment_dish_id=data_item['catering_establishment_dish'],
                weight=data_item['weight'],
            )
            for data_item in ordered_dishes_data
        ]
    )
