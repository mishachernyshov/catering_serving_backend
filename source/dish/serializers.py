from rest_framework import serializers

from catering_establishment import models as ce_models
from common.validators import validate_encoded_file
from dish import models as dish_models


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = dish_models.Dish
        fields = '__all__'


class DishNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = dish_models.Dish
        fields = ('id', 'name')


class DishSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = dish_models.DishSubcategory
        fields = '__all__'


class DishCategorySerializer(serializers.ModelSerializer):
    subcategories = DishSubcategorySerializer(many=True)

    class Meta:
        model = dish_models.DishCategory
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = dish_models.Food
        fields = '__all__'


class DishCharacteristicsSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=dish_models.Dish.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=dish_models.DishCategory.objects.all())
    subcategory = serializers.PrimaryKeyRelatedField(queryset=dish_models.DishSubcategory.objects.all())
    food = serializers.PrimaryKeyRelatedField(queryset=dish_models.Food.objects.all())

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'category': instance.subcategory.category.id,
            'subcategory': instance.subcategory.id,
            'food': instance.food.id,
        }


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = dish_models.Discount
        fields = ('type', 'amount', 'start_datetime', 'end_datetime')


class CateringEstablishmentDishSerializer(serializers.ModelSerializer):
    photo = serializers.CharField(validators=[validate_encoded_file])
    discount = DiscountSerializer(required=False)

    class Meta:
        model = dish_models.CateringEstablishmentDish
        fields = ('dish', 'description', 'photo', 'discount', 'price')


class CateringEstablishmentDishFinalPriceSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField('get_final_price')

    def get_final_price(self, obj):
        return obj.final_price

    class Meta:
        model = dish_models.CateringEstablishmentDish
        fields = ('id', 'dish', 'final_price')


class CateringEstablishmentMenuItemSerializer(serializers.ModelSerializer):
    dish = DishCharacteristicsSerializer()
    discount = DiscountSerializer()
    final_price = serializers.FloatField()

    class Meta:
        model = dish_models.CateringEstablishmentDish
        fields = ('id', 'description', 'photo', 'dish', 'price', 'final_price', 'discount')


class OrderedDishWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = dish_models.OrderedDish
        fields = '__all__'


class OrderedDishReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = dish_models.OrderedDish
        fields = ('weight', 'catering_establishment_dish')


class OrderedDishWithFinalPriceSerializer(serializers.ModelSerializer):
    catering_establishment_dish = CateringEstablishmentDishFinalPriceSerializer()

    class Meta:
        model = dish_models.OrderedDish
        fields = ('id', 'weight', 'catering_establishment_dish')


class OrderUpdateSerializer(serializers.Serializer):
    booking = serializers.PrimaryKeyRelatedField(queryset=ce_models.Booking.objects.all())
    ordered_dishes = OrderedDishReadSerializer(many=True)


class DishOrderingStatisticsSerializer(serializers.ModelSerializer):
    orders_count = serializers.IntegerField()

    class Meta:
        model = dish_models.Dish
        fields = ('name', 'orders_count')
