from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, filters
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Category, Product
from main.serializers import CategoryAddSerializer, CategoryAllFieldsSerializer


class CategoryAdd(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CategoryAddSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class CategoryGetAll(GenericAPIView):
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = CategoryAllFieldsSerializer

    def get(self, request):
        categories = Category.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(categories, request)
        if not request.query_params.get(self.pagination_class.page_query_param):

            serializer = self.get_serializer(categories, many=True)
            categories_data = serializer.data
            for category in categories_data:
                category_id = category['id']
                product_count = Product.objects.filter(category_id=category_id).count()
                category.update({'product_count': product_count})
            return Response({'success': True, 'data': categories_data})

        serializer = self.get_serializer(page, many=True)

        page_count = paginator.page.paginator.num_pages
        current_page = paginator.page.number
        serializer_data = serializer.data
        for category_data in serializer_data:
            category_id = category_data['id']
            product_count = Product.objects.filter(category_id=category_id).count()
            category_data.update({'product_count': product_count})

        # Construct response data
        response_data = {
            'results': serializer.data,
            'page_size': page_count,
            'current_page': current_page
        }
        return Response({'success': True, 'data': response_data})


class CategoryEditView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CategoryAllFieldsSerializer

    def get_category(self, pk):
        category = Category.objects.get(pk=pk)
        return category

    def patch(self, request, pk):
        try:
            category = self.get_category(pk)
            serializer = self.serializer_class(category, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


class CategorySearchView(GenericAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryAllFieldsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
