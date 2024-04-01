from datetime import timedelta
from django.utils import timezone

from celery import shared_task

from main.models import StoreHistory, Order


@shared_task()
def kirim_chiqim_canculator(key):
    data = {}
    kirim = 0
    chiqim = 0
    orders = 0
    stores = 0
    today = timezone.now().date()
    start_day = 0

    if key == 'today':
        stores = StoreHistory.objects.filter(created_at__date=today)
        orders = Order.objects.filter(created_at__date=today)
    if key == 'weekly':
        start_day = today - timedelta(days=7)
        orders = Order.objects.filter(created_at__date__range=[start_day, today])
        stores = StoreHistory.objects.filter(created_at__date_range=[start_day, today])
    if key == 'monthly':
        start_day = today - timedelta(days=30)
        orders = Order.objects.filter(created_at__date__range=[start_day, today])
        stores = StoreHistory.objects.filter(created_at__date_range=[start_day, today])

    for order in orders:
        kirim += order.count + order.price
    for store in stores:
        chiqim += store.count + store.buy_price

    data.update({'kirim': kirim})
    data.update({'chiqim': chiqim})

    return data
