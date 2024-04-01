
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Brand(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Store(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    sell_price = models.PositiveIntegerField()
    count = models.PositiveIntegerField(default=0)
    buy_price = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)


class StoreHistory(models.Model):
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    sell_price = models.PositiveIntegerField()
    count = models.PositiveIntegerField(default=0)
    buy_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class PaymentMethod(models.TextChoices):
    CARD = 'CARD'
    CASH = 'CASH'


class Order(models.Model):
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=4, choices=PaymentMethod.choices)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    name = models.CharField(max_length=255)
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)