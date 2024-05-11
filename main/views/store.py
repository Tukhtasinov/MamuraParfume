from celery.bin.control import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, filters
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from main.models import StoreHistory, Store, Product
from main.serializers import StoreCreateSerializer, StoreHistorySerializer, StoreAllFieldSerializer


class StoreCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StoreCreateSerializer

    def post(self, request):
        product_id = request.data.get('product')
        if not Store.objects.filter(product=product_id).exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            store_data = serializer.save()
            data = serializer.data
            data.update({'store_id': store_data.id})
            store_history = StoreHistorySerializer(data=data)
            store_history.is_valid(raise_exception=True)
            store_history.save()

            return Response({'success': True, 'message': "Store Created Successfully!"})
        store = Store.objects.get(product=product_id)
        return Response({'success': False, 'message': "Bunday Mahsulot Zaxirasi Avval Qo'shilgan", 'store_id': store.id})


class StoreGetWithExtra(GenericAPIView):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    serializer_class = StoreAllFieldSerializer

    def get(self, request, extra):
        stores = 0
        if extra == 'all':
            stores = Store.objects.all()
        if extra == 'less':
            stores = Store.objects.filter(count__lt=6)
        if extra == 'finished':
            stores = Store.objects.filter(count=0)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(stores, request)
        if not request.query_params.get(self.pagination_class.page_query_param):
            serializer = self.get_serializer(stores, many=True)
            return Response({'success':True, 'data':serializer.data})
        serializer = self.get_serializer(page, many=True)

        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        stores_data = serializer.data
        for store_data in stores_data:
            product_id = store_data['product']
            product = Product.objects.get(id=product_id)
            store_data.update({'product_name': product.name})
        response_data = {
            'results': stores_data,
            'page_size': page_count,
            'current_page': current_page
        }
        text = 'Bunday zaxiralar hozirda mavjud emas 🙂'

        return Response({'success': True, 'data': response_data if len(stores_data) > 0 else text})


class StoreObtainEditView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StoreAllFieldSerializer

    def get_store(self, pk):
        store_data = Store.objects.get(pk=pk)
        return store_data

    def get(self, request, pk):
        try:
            store = self.get_store(pk)
            serializer = self.get_serializer(store)
            serializer_data = serializer.data
            serializer_data.update({'product_image': store.product.image.url})
            serializer_data.update({'product_name': store.product.name})

            return Response({'success': True, 'data': serializer_data}, status=200)
        except ObjectDoesNotExist:
            return Response({'success': False}, status=404)

    def patch(self, request, pk):
        try:
            store = self.get_store(pk)
            data = {
                'store_id': store.id,
                'sell_price': store.sell_price,
                'count': store.count,
                'buy_price': store.buy_price,
            }
            request.data['count'] += store.count
            serializer = self.get_serializer(store, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            store_history = StoreHistorySerializer(data=data)
            store_history.is_valid(raise_exception=True)
            store_history.save()

            return Response({'success': True, 'message': 'Store Edited Successfully'}, status=200)

        except ObjectDoesNotExist:
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


class StoreHistoryView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StoreHistorySerializer

    def get(self, request, store_id):
        store_histories = StoreHistory.objects.filter(store_id=store_id)
        serializer = self.get_serializer(store_histories, many=True)

        return Response({'success': True, "store_histories": serializer.data}, status=200)


class StoreSearchView(ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreAllFieldSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__id', 'product__name']

