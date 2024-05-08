from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from main.models import Product, Category, Brand, Store, StoreHistory, Order, Notification


class CategoryAddSerializer(ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class CategoryAllFieldsSerializer(ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class ProductAddSerializer(ModelSerializer):

    class Meta:
        model = Product
        exclude = ("id",)


class BrandAddSerializer(ModelSerializer):

    class Meta:
        model = Brand
        exclude = ("id",)


class BrandAllFieldSerializer(ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'


class BrandForTheBest(ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'


class ProductAllFieldsSerializer(ModelSerializer):
    category = CategoryAllFieldsSerializer(read_only=True)
    brand = BrandAllFieldSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductPatchSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class StoreCreateSerializer(ModelSerializer):

    class Meta:
        model = Store
        exclude = ('id',)


class StoreAllFieldSerializer(ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'product', 'product_name', 'sell_price', 'count', 'buy_price', 'updated_at']


class StoreHistorySerializer(ModelSerializer):

    class Meta:
        model = StoreHistory
        exclude = ('id',)


class OrderCreateSerializer(ModelSerializer):

    class Meta:
        model = Order
        exclude = ('id',)


class OrderSerializer(ModelSerializer):
    # product_id = serializers.IntegerField(source='store_id.product_id', read_only=True)
    # product_name = serializers.CharField(source='store_id.product.name', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class NotificationSerializer(ModelSerializer):

    class Meta:
        model = Notification
        exclude = ('id',)


class NotificationGetSerializer(ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'


class TopSoldProductSerializer(serializers.Serializer):
    product_name = serializers.CharField(source='store_id__product__name')
    total_count = serializers.IntegerField()
    total_price = serializers.IntegerField()
