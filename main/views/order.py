import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.core.serializers import serialize
from django.db.models import Sum
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import filters
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from main.models import Order, Store, StoreHistory
from main.serializers import OrderCreateSerializer, OrderSerializer, NotificationSerializer
from main.tasks import kirim_chiqim_canculator


class OrderCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer

    def post(self, request):
        try:
            with transaction.atomic():
                store = Store.objects.select_for_update().get(pk=request.data.get('store_id'))
                if store.count >= request.data.get('count'):
                    store.count -= request.data.get('count')
                    store.save()

                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    if store.count == 0:
                        text = f"""       Ogohlantirish!!!

                                {store.product.name} - ushbu mahsulotdan zaxirada qolmadi!
                                                """
                        data = {
                            'name': text,
                            'store_id': store.id,
                        }
                        notification = NotificationSerializer(data=data)
                        notification.is_valid(raise_exception=True)
                        notification.save()

                    elif store.count <= 5:
                        text = f"""       Ogohlantirish!!!

                        {store.product.name } - ushbu mahsulot {store.count} dona qoldi!
                        """
                        data = {
                            'name': text,
                            'store_id': store.id,
                        }
                        notification = NotificationSerializer(data=data)
                        notification.is_valid(raise_exception=True)
                        notification.save()

                else:
                    return Response({'success': False, 'message': "Incorrect count Of Product"})

            return Response({'success': True, 'message': 'Order Created Successfully'}, status=201)
        except ObjectDoesNotExist:
            return Response({'status': False}, status=404)


class OrderEditOrDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def patch(self, request, pk):
        order = Order.objects.get(pk=pk)
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True, 'message': 'Order Edited Successfully'}, status=200)

    def delete(self, request, pk):
        order = Order.objects.get(pk=pk)
        order.delete()

        return Response({'success': True, 'message': 'Order Deleted Successfully'})


class OrderGetView(GenericAPIView):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request):
        order = Order.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(order, request)
        if page is None:
            serializer = self.get_serializer(order, many=True)
            return Response({'success': True, 'data': serializer.data})
        serializer = self.get_serializer(page, many=True)
        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        # Construct response data
        response_data = {
            'results': serializer.data,
            'page_size': page_count,
            'current_page': current_page
        }
        return Response({'success': True, 'data': response_data})


class OrderSearchView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        product_id = self.request.query_params.get('product_id')
        product_name = self.request.query_params.get('product_name')
        temp = [{'success': True, 'order': 'Hozirda bunday malumotlar yoq'}]
        if product_id:

            temp = queryset.filter(store_id__product_id=product_id)
        if product_name:

            temp = queryset.filter(store_id__product__name__icontains=product_name)

        return temp


class OrderFilterByToday(GenericAPIView):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request):
        today = timezone.now().date()
        orders = Order.objects.filter(created_at__date=today)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if page is None:
            serializer = self.get_serializer(orders, many=True)
            return Response({'success': True, 'data': serializer.data})
        serializer = self.get_serializer(page, many=True)

        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        # Construct response data
        response_data = {
            'results': serializer.data,
            'page_size': page_count,
            'current_page': current_page
        }
        return Response({'success': True, 'data': response_data})


class OrderFilterByDates(GenericAPIView):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request):
        start_day = request.data.get('start_day')
        end_day = request.data.get('end_day')
        orders = []
        if start_day and end_day:
            orders = Order.objects.filter(created_at__range=(start_day, end_day))

        elif start_day:
            orders = Order.objects.filter(created_at__date=start_day)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if page is None:
            serializer = self.get_serializer(orders, many=True)
            return Response({'success': True, 'data': serializer.data})
        serializer = self.get_serializer(page, many=True)

        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        # Construct response data
        response_data = {
            'results': serializer.data,
            'page_size': page_count,
            'current_page': current_page
        }
        return Response({'success': True, 'data': response_data})


class DiagramByPaymentMethod(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.all()
        total_price_cash = 0
        total_price_card = 0

        for order in orders:
            if order.payment_method == 'CASH':
                total_price_cash += order.price * order.count
            else:
                total_price_card += order.price * order.count

        data = {
            'total_price': total_price_cash + total_price_card,
            'total_price_by_cash': total_price_cash,
            'total_price_by_card': total_price_card
        }

        return Response({'success': True, 'data': data})


class KirimChiqimView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, keyword):
        data = {}
        kirim = 0
        chiqim = 0
        orders = 0
        stores = 0
        profit = 0
        today = timezone.now().date()
        start_day = 0

        if keyword == 'today':
            stores = StoreHistory.objects.filter(created_at__date=today)
            orders = Order.objects.filter(created_at__date=today)
        if keyword == 'weekly':
            start_day = today - timedelta(days=7)
            orders = Order.objects.filter(created_at__date__range=[start_day, today])
            stores = StoreHistory.objects.filter(created_at__date__range=[start_day, today])
        if keyword == 'monthly':
            start_day = today - timedelta(days=30)
            orders = Order.objects.filter(created_at__date__range=[start_day, today])
            stores = StoreHistory.objects.filter(created_at__date__range=[start_day, today])
        if keyword == 'year':
            start_day = today - timedelta(days=365)
            orders = Order.objects.filter(created_at__date__range=[start_day, today])
            stores = StoreHistory.objects.filter(created_at__date__range=[start_day, today])

        for order in orders:
            kirim += order.count * order.price
            profit += (order.price - order.store_id.buy_price) * order.count

        for store in stores:
            chiqim += store.count * store.buy_price

        data.update({'kirim': kirim})
        data.update({'xaridlar_soni': len(orders)})
        data.update({'foyda': profit})
        data.update({'chiqim': chiqim})

        return Response({'success': True, 'data': data})


class DiagramAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, key):

        data = {}
        today = timezone.now().date()
        day = timezone.now()

        if key == 'today':
            for i in range(24):
                start_hour = timezone.now().replace(hour=day.hour, minute=day.minute, second=day.second, microsecond=day.microsecond) - timedelta(hours=i + 1)
                end_hour = start_hour + timedelta(hours=1)

                orders = Order.objects.filter(created_at__gte=start_hour, created_at__lt=end_hour)

                report = sum(order.count * order.price for order in orders)

                hour_key = start_hour.strftime('%Y-%m-%d %H:%M:%S')
                data[hour_key] = report

        if key == 'weekly':

            for i in range(0, 6):
                date = today - timedelta(days=i)
                orders = Order.objects.filter(created_at__date=date)
                report = sum(order.count * order.price for order in orders)
                data[f'report_{date}'] = report

        if key == 'monthly':
            kun = 0
            for i in range(0, 30):
                date = today - timedelta(days=i)
                orders = Order.objects.filter(created_at__date=date)
                report = sum(order.count * order.price for order in orders)
                kun += 1
                data[f'report_{date}'] = report

        if key == 'year':
            end_day = today
            for i in range(1, 13):
                start_day = end_day - timedelta(days=30)
                orders = Order.objects.filter(created_at__date__range=[start_day, end_day])
                report = sum(order.price * order.count for order in orders)
                data[f'report_{end_day}'] = report
                end_day = start_day

        return Response({'success': True, 'data': data})


class FilterByPaymentMethod(GenericAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    serializer_class = OrderSerializer

    def get(self, request, type):
        type = type.upper()
        if type not in ['CASH', 'CARD']:
            return Response({'success': False, 'message': 'Invalid payment type, You can write CASH or CARD types for getting data🙃'})
        orders = Order.objects.filter(payment_method=type).order_by('id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if page is None:
            serializer = self.get_serializer(orders, many=True)
            return Response({'success': True, 'data': serializer.data})
        serializer = self.get_serializer(page, many=True)

        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        # Construct response data
        response_data = {
            'results': serializer.data,
            'page_size': page_count,
            'current_page': current_page
        }
        return Response({'success': True, 'data': response_data})



