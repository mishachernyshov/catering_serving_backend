from django.db.models import prefetch_related_objects
from rest_framework import serializers

from catering_establishment import constants as ce_constants
from catering_establishment import models as ce_models
from common.constants import DATETIME_DESERIALIZATION_FORMAT
from common.utils import build_absolute_url_to_media_file, save_base64_encoded_file
from common.validators import validate_encoded_file
from dish import constants as dish_constants
from dish.models import CateringEstablishmentDish, Discount
from dish.serializers import CateringEstablishmentDishSerializer, OrderedDishWithFinalPriceSerializer
from location.models import Address, Settlement
from location.serializers import AddressSerializer


class CateringEstablishmentTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.CateringEstablishmentTable
        fields = '__all__'


class CateringEstablishmentTableCharacteristicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.CateringEstablishmentTable
        fields = ('number', 'serving_clients_number')


class CateringEstablishmentRepresentationSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField()

    class Meta:
        model = ce_models.CateringEstablishment
        fields = ('id', 'name', 'photo')

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'name': instance.name,
        }
        if first_photo := instance.photos.all().first():
            representation['photo'] = build_absolute_url_to_media_file(first_photo)
        return representation


class WorkHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.WorkHours
        exclude = ('id',)


class CateringEstablishmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=1, max_length=ce_constants.CATERING_ESTABLISHMENTS_NAME_MAX_LENGTH)
    address = AddressSerializer()
    work_hours = WorkHoursSerializer()
    photos = serializers.ListField(child=serializers.CharField(validators=[validate_encoded_file]))
    tables = serializers.ListField(child=CateringEstablishmentTableCharacteristicsSerializer())
    dishes = CateringEstablishmentDishSerializer(many=True)

    class Meta:
        model = ce_models.CateringEstablishment
        fields = '__all__'

    def create(self, validated_data):
        catering_establishment_data = self._get_catering_establishment_data(validated_data)
        catering_establishment_data['address'] = Address.objects.create(**validated_data['address'])
        catering_establishment_data['work_hours'] = ce_models.WorkHours.objects.create(**validated_data['work_hours'])

        catering_establishment = ce_models.CateringEstablishment.objects.create(**catering_establishment_data)

        self.create_catering_establishment_photos(validated_data['photos'], catering_establishment)
        self.create_tables(validated_data['tables'], catering_establishment)
        self.create_dishes(validated_data['dishes'], catering_establishment)

        return catering_establishment

    @staticmethod
    def _get_catering_establishment_data(validated_data):
        fields = ('name', 'description', 'owner', 'is_visible')
        data = {}

        for field in fields:
            if (field_value := validated_data.get(field)) is not None:
                data[field] = field_value

        return data

    @staticmethod
    def create_catering_establishment_photos(photos_data, catering_establishment):
        folder_media_path = f'{ce_constants.MEDIA_FOLDER_NAME}/{ce_constants.PHOTOS_FOLDER_NAME}'

        for photo_data in photos_data:
            file_path = save_base64_encoded_file(photo_data, folder_media_path)
            ce_models.CateringEstablishmentPhoto.objects.create(
                photo=file_path,
                catering_establishment=catering_establishment,
            )

    @staticmethod
    def create_tables(tables_data, catering_establishment):
        for table_data in tables_data:
            ce_models.CateringEstablishmentTable.objects.create(
                catering_establishment=catering_establishment,
                **table_data,
            )

    @staticmethod
    def create_dishes(dishes_data, catering_establishment):
        folder_media_path = f'{dish_constants.MEDIA_FOLDER_NAME}/{dish_constants.PHOTOS_FOLDER_NAME}'

        for dish_data in dishes_data:
            file_path = save_base64_encoded_file(dish_data['photo'], folder_media_path)
            catering_establishment_dish = CateringEstablishmentDish.objects.create(
                catering_establishment=catering_establishment,
                dish=dish_data['dish'],
                photo=file_path,
                description=dish_data['description'],
                price=dish_data['price'],
            )
            if discount_data := dish_data.get('discount'):
                Discount.objects.create(
                    catering_establishment_dish=catering_establishment_dish,
                    **discount_data,
                )

    def update(self, instance, validated_data):
        catering_establishment_data = self._get_catering_establishment_data(validated_data)
        self.update_not_relational_catering_establishment_fields(instance, catering_establishment_data)
        self.update_one_to_one_field(instance, 'address', validated_data['address'], Address)
        self.update_one_to_one_field(instance, 'work_hours', validated_data['work_hours'], ce_models.WorkHours)

        self.delete_catering_establishment_related_objects(instance)

        self.create_catering_establishment_photos(validated_data['photos'], instance)
        self.create_tables(validated_data['tables'], instance)
        self.create_dishes(validated_data['dishes'], instance)

        return instance

    @staticmethod
    def update_not_relational_catering_establishment_fields(instance, catering_establishment_data):
        for key, value in catering_establishment_data.items():
            setattr(instance, key, value)
        instance.save()

    @staticmethod
    def update_one_to_one_field(instance, relation_name, relation_data, relation_model):
        old_field = getattr(instance, relation_name)
        setattr(instance, relation_name, relation_model.objects.create(**relation_data))
        instance.save()
        old_field.delete()

    @staticmethod
    def delete_catering_establishment_related_objects(instance):
        ce_models.CateringEstablishmentPhoto.objects.filter(catering_establishment=instance).delete()
        ce_models.CateringEstablishmentTable.objects.filter(catering_establishment=instance).delete()
        CateringEstablishmentDish.objects.filter(catering_establishment=instance).delete()

    def to_representation(self, instance):
        prefetch_related_objects((instance,), 'photos', 'tables', 'catering_establishment_dishes')

        return {
            'name': instance.name,
            'description': instance.description,
            'is_visible': instance.is_visible,
            'address': AddressSerializer(instance.address).data,
            'work_hours': WorkHoursSerializer(instance.work_hours).data,
            'photos': self.get_photos_representation(instance),
            'tables': instance.tables.all().values('number', 'serving_clients_number'),
            'dishes': self.get_dishes_representation(instance),
        }

    @staticmethod
    def get_address_representation(instance):
        address_serializer = AddressSerializer(instance.address)
        address_serializer.is_valid(raise_exception=True)
        return address_serializer.data

    @staticmethod
    def get_photos_representation(instance):
        raw_photos = instance.photos.all().values_list('photo', flat=True)
        return list(map(lambda photo: build_absolute_url_to_media_file(photo), raw_photos))

    @staticmethod
    def get_dishes_representation(instance):
        dishes_data = instance.catering_establishment_dishes.all().values(
            'dish',
            'description',
            'photo',
            'price',
            'discount__type',
            'discount__amount',
            'discount__start_datetime',
            'discount__end_datetime',
        )

        for data_item in dishes_data:
            if data_item['discount__type']:
                data_item['discount'] = {
                    'type': data_item['discount__type'],
                    'amount': data_item['discount__amount'],
                    'start_datetime': data_item['discount__start_datetime'].strftime(DATETIME_DESERIALIZATION_FORMAT),
                    'end_datetime': data_item['discount__end_datetime'].strftime(DATETIME_DESERIALIZATION_FORMAT),
                }
            del data_item['discount__type']
            del data_item['discount__amount']
            del data_item['discount__start_datetime']
            del data_item['discount__end_datetime']
            data_item['photo'] = build_absolute_url_to_media_file(data_item['photo'])
        return dishes_data


class CateringEstablishmentCatalogItemSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=ce_models.CateringEstablishment.objects.all())
    name = serializers.CharField(max_length=ce_constants.CATERING_ESTABLISHMENTS_NAME_MAX_LENGTH)
    photo = serializers.ImageField(required=False)
    rating = serializers.FloatField()
    settlement = serializers.PrimaryKeyRelatedField(queryset=Settlement.objects.all())
    address = serializers.CharField(max_length=256)
    description = serializers.CharField(max_length=ce_constants.CUT_CATERING_ESTABLISHMENTS_DESCRIPTION_LENGTH)

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'name': instance.name,
            'rating': instance.rating,
            'settlement': instance.settlement,
            'address': instance.address.name,
            'description': instance.description[: ce_constants.CUT_CATERING_ESTABLISHMENTS_DESCRIPTION_LENGTH],
        }
        if first_photo := instance.photos.all().first():
            representation['photo'] = build_absolute_url_to_media_file(first_photo)

        return representation


class CateringEstablishmentMainInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=ce_constants.CATERING_ESTABLISHMENTS_NAME_MAX_LENGTH)
    description = serializers.CharField()
    rating = serializers.FloatField()
    photos = serializers.ListField(child=serializers.ImageField())
    address = serializers.CharField()

    def to_representation(self, instance):
        return {
            'name': instance.name,
            'description': instance.description,
            'rating': instance.rating,
            'photos': map(build_absolute_url_to_media_file, instance.photos.values_list('photo', flat=True)),
            'address': str(instance.address),
        }


class CateringEstablishmentUserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.CateringEstablishmentRating
        fields = ('rating', 'catering_establishment', 'visitor')


class CateringEstablishmentFeedbackInfoSerializer(serializers.ModelSerializer):
    visitor = serializers.CharField()

    class Meta:
        model = ce_models.CateringEstablishmentFeedback
        fields = ('visitor', 'feedback', 'created')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['visitor'] = instance.visitor.username
        return representation


class CateringEstablishmentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.CateringEstablishmentFeedback
        fields = '__all__'


class BookingReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.Booking
        fields = ('id', 'catering_establishment_table', 'start_datetime', 'end_datetime')


class BookingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.Booking
        fields = '__all__'


class ExtendedBookingSerializer(BookingReadSerializer):
    ordered_dishes = OrderedDishWithFinalPriceSerializer(many=True)
    is_active = serializers.BooleanField()
    is_paid = serializers.BooleanField()

    class Meta(BookingReadSerializer.Meta):
        fields = BookingReadSerializer.Meta.fields + ('ordered_dishes', 'is_active', 'is_paid')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['catering_establishment'] = instance.catering_establishment_table.catering_establishment.id
        representation['is_active'] = instance.is_active
        representation['is_paid'] = instance.is_paid
        return representation


class BookingPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ce_models.BookingPayment
        fields = '__all__'


class EstablishmentBookingsCountSerializer(serializers.ModelSerializer):
    bookings_count = serializers.IntegerField()

    class Meta:
        model = ce_models.CateringEstablishment
        fields = ('name', 'bookings_count')
