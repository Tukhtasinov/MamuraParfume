from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from rest_framework import status, filters
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Brand, Product, Order
from main.serializers import BrandAddSerializer, BrandAllFieldSerializer, BrandForTheBest


class BrandAllGetView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BrandAllFieldSerializer

    def get(self, request):
        brands_data = Brand.objects.filter().order_by('-id')
        print(brands_data)
        serializer = self.serializer_class(brands_data, many=True)
        serializer_data = serializer.data
        for brand_data in serializer_data:
            print("Brand >>>>", brand_data)
            brand_id = brand_data['id']
            product_count = Product.objects.filter(brand_id=brand_id).count()
            brand_data.update({'product_count': product_count})

        return Response({'success': True, 'brands': serializer_data})


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
    permission_classes = [IsAuthenticated]
    serializer_class = BrandForTheBest

    def get(self, request):

        top_sold_products = Order.objects.values('store_id__product__brand__name', 'store_id__product__name').annotate(
            total_sold=Sum('count')).order_by('-total_sold')[:5]

        brand_sales = {}
        for product in top_sold_products:
            brand_name = product['store_id__product__brand__name']
            product_name = product['store_id__product__name']

            orders = Order.objects.filter(store_id__product__name=product_name)
            total_price = 0
            total_sold = product['total_sold']
            for i in orders:
                total_price += i.price * i.count

            if brand_name in brand_sales:
                brand_sales[brand_name]['total_sold'] += total_sold
                brand_sales[brand_name]['total_price'] += total_price
            else:
                brand_sales[brand_name] = {'total_sold': total_sold, 'total_price': total_price}

        return Response(brand_sales)



