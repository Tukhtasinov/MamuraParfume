from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from rest_framework import status, filters
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Product, Store, Order
from main.serializers import ProductAddSerializer, ProductAllFieldsSerializer, ProductPatchSerializer, \
    TopSoldProductSerializer


class AllProductGetView(GenericAPIView):
    serializer_class = ProductAllFieldsSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = Product.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(data, request)
        if page is None:
            serializer = self.get_serializer(data, many=True)
            return Response({'success': True, 'data': serializer.data})
        serializer = self.get_serializer(page, many=True)
        products_data = serializer.data
        for product in products_data:
            product_id = product.get('id')
            currently_count = Store.objects.get(product_id=product_id)
            sold_count = Order.objects.aggregate(count=Sum('count'))
            product.update({'currently_product_count': currently_count.count})
            product.update({'sold_product_count': sold_count['count'] if sold_count['count'] is not None else 0})

        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        # Construct response data
        response_data = {
            'results': products_data,
            'page_size': page_count,
            'current_page': current_page
        }
        return Response({'success': True, 'data': response_data})


class ProductAddGenericApiView(GenericAPIView):
    serializer_class = ProductAddSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True}, status=status.HTTP_201_CREATED)


class ProductCRUDGenericAPIView(GenericAPIView):
    serializer_class = ProductPatchSerializer
    permission_classes = (IsAuthenticated,)

    def get_product(self, product_id):
        product = Product.objects.get(pk=product_id)
        return product

    def patch(self, request, pk):
        try:
            product = self.get_product(pk)
            serializer = self.get_serializer(product, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({'success': True, 'message': 'Product Edited Successfully'}, status=status.HTTP_206_PARTIAL_CONTENT)
        except ObjectDoesNotExist:
            return Response({'detail': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            product = self.get_product(pk)
            product.delete()

            return Response({'success': True, 'message': 'Product Deleted Successfully'})
        except ObjectDoesNotExist:
            return Response({'detail': 'Such product does not exist'})


class ProductDetailView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductAllFieldsSerializer

    def get(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
            serializer = self.get_serializer(product)
            product_data = serializer.data
            currently_count = Store.objects.get(product_id=pk)
            sold_count = Order.objects.aggregate(count=Sum('count'))
            product_data.update({'currently_product_count': currently_count.count})
            product_data.update({'sold_product_count': sold_count['count'] if sold_count['count'] is not None else 0})

            return Response({'success': True, 'product_data': product_data}, status=200)
        except ObjectDoesNotExist:
            return Response({'detail': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)


class ProductSearchView(GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductAllFieldsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'name', 'brand.name', 'category.name']


class TheMostSoldProductView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TopSoldProductSerializer

    def get(self, request):
        top_sold_product = Order.objects.values('store_id__product__name').annotate(
            total_count=Sum('count'),
            total_price=Sum('price')
        ).order_by('-total_count')
        serializer = {}
        result = []
        for product in top_sold_product:
            product_name = product['store_id__product__name']
            total_count = product['total_count']
            orders = Order.objects.filter(store_id__product__name=product_name)
            total_price = 0
            for i in orders:
                total_price += i.price * i.count

            data = {
                'product_name': product_name,
                'total_count': total_count,
                'total_price': total_price,
            }
            result.append(data)
            serializer.update({f'{product_name}': data})
        return Response({'status': True,  'result': result})

