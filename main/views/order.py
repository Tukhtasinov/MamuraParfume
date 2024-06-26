from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework import filters
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Order, Store, StoreHistory
from main.serializers import OrderCreateSerializer, OrderSerializer, NotificationSerializer, \
    OrderFilterByDatesSerializer


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

                        {store.product.name} - ushbu mahsulot {store.count} dona qoldi!
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
    # permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request):
        order = Order.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(order, request)
        if not request.query_params.get(self.pagination_class.page_query_param):
            serializer = self.get_serializer(order, many=True)
            data = {'result': serializer.data}
            return Response({'success': True, 'data': data})
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
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'store_id__id', 'store_id__product__id', 'store_id__product__name']


class OrderFilterByToday(GenericAPIView):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request):
        today = timezone.now().date()
        orders = Order.objects.filter(created_at__date=today)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if not request.query_params.get(self.pagination_class.page_query_param):
            serializer = self.get_serializer(orders, many=True)
            data = {'result': serializer.data}
            return Response({'success': True, 'data': data})
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
    serializer_class = OrderFilterByDatesSerializer

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        orders = []
        if start_date and end_date:
            # Convert date strings to datetime objects
            start_datetime = timezone.datetime.strptime(start_date, '%d.%m.%Y').date()
            end_datetime = timezone.datetime.strptime(end_date, '%d.%m.%Y').date()

            orders = Order.objects.filter(created_at__range=(start_datetime, end_datetime))
        elif start_date:
            start_datetime = timezone.datetime.strptime(start_date, '%d.%m.%Y').date()
            orders = Order.objects.filter(created_at__date=start_datetime)
        else:
            orders = []

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if not request.query_params.get(self.pagination_class.page_query_param):
            serializer = OrderSerializer(orders, many=True)
            data = {"result": serializer.data}
            return Response({'success': True, 'data': data})
        serializer = OrderSerializer(page, many=True)

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
        today = timezone.localtime().date()
        day = timezone.localtime()

        if key == 'today':
            for i in range(24):
                start_hour = timezone.now().replace(hour=day.hour, minute=day.minute, second=day.second,
                                                    microsecond=day.microsecond) - timedelta(hours=i + 1)
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
            return Response({'success': False,
                             'message': 'Invalid payment type, You can write CASH or CARD types for getting data🙃'})
        orders = Order.objects.filter(payment_method=type).order_by('id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if not request.query_params.get(self.pagination_class.page_query_param):
            serializer = self.get_serializer(orders, many=True)
            data = {'result': serializer.data}
            return Response({'success': True, 'data': data})
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
