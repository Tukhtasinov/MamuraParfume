from django.contrib import admin
from .models import Category, Brand, Product, Store, StoreHistory, Order, Notification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'created_at']


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['product', 'sell_price', 'count', 'buy_price', 'updated_at']


@admin.register(StoreHistory)
class StoreHistoryAdmin(admin.ModelAdmin):
    list_display = ['store_id', 'sell_price', 'count', 'buy_price', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['store_id', 'count', 'price', 'payment_method']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'store_id']
