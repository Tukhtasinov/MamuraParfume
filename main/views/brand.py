from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from rest_framework import status, filters
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Brand, Product, Order
from main.serializers import BrandAddSerializer, BrandAllFieldSerializer, BrandForTheBest


class BrandAllGetView(GenericAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = BrandAllFieldSerializer

    def get(self, request):
        brands_data = Brand.objects.filter().order_by('-id')
        print(brands_data)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(brands_data, request)
        serializer = self.serializer_class(page, many=True)

        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number
        serializer_data = serializer.data
        for brand_data in serializer_data:
            print("Brand >>>>", brand_data)
            brand_id = brand_data['id']
            product_count = Product.objects.filter(brand_id=brand_id).count()
            brand_data.update({'product_count': product_count})

        # Construct response data
        response_data = {
            'results': serializer.data,
            'page_size': page_count,
            'current_page': current_page
        }
        return Response({'success': True, 'data': response_data})


class BrandAddView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BrandAddSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True}, status=status.HTTP_201_CREATED)


class BrandEditView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BrandAllFieldSerializer

    def patch(self, request, pk):
        brand = Brand.objects.get(pk=pk)
        serializer = self.get_serializer(brand, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True}, status=200)


class BrandSearchView(GenericAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandAllFieldSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class TheBestSellerBrand(GenericAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = BrandForTheBest

    def get(self, request):
        top_sold_products = Order.objects.values('store_id__product__brand__name', 'store_id__product__name').annotate(
            total_sold=Sum('count')).order_by('-total_sold')[:5]

        brand_sales = []
        for product in top_sold_products:
            brand_name = product['store_id__product__brand__name']
            product_name = product['store_id__product__name']

            orders = Order.objects.filter(store_id__product__name=product_name)
            total_price = sum(order.price * order.count for order in orders)
            total_sold = product['total_sold']

            brand_data = {
                'name': brand_name,
                'total_count': total_sold,
                'total_price': total_price
            }
            brand_sales.append(brand_data)

        return Response(brand_sales)



