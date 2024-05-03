from django.urls import path
from .views import ProductAddGenericApiView, ProductCRUDGenericAPIView, CategoryAdd, CategoryGetAll, CategoryEditView, \
    ProductDetailView, BrandAddView, BrandEditView, BrandAllGetView, StoreCreateView, StoreObtainEditView, \
    StoreHistoryView, OrderEditOrDeleteView, OrderCreateView, NotificationDetailView, GetNotificationView, \
    StoreGetWithExtra, StoreSearchView, OrderGetView, OrderSearchView, OrderFilterByToday, OrderFilterByDates, \
    BrandSearchView, CategorySearchView, TheBestSellerBrand, ProductSearchView, TheMostSoldProductView, \
    DiagramByPaymentMethod, KirimChiqimView, DiagramAPIView, AllProductGetView, FilterByPaymentMethod

urlpatterns = [
    path('product-add/', ProductAddGenericApiView.as_view(), name='product-add'),
    path('product-crud/<int:pk>', ProductCRUDGenericAPIView.as_view(), name='product-edit'),
    path('product-get/<int:pk>', ProductDetailView.as_view(), name='product-get'),
    path('category-add/', CategoryAdd.as_view(), name='category-add'),
    path('categories/', CategoryGetAll.as_view(), name='categories'),
    path('category-edit/<int:pk>', CategoryEditView.as_view(), name='category-edit'),
    path('brand-add/', BrandAddView.as_view(), name='brand-add'),
    path('brand-edit/<int:pk>', BrandEditView.as_view(), name='brand-edit'),
    path('brands/', BrandAllGetView.as_view(), name='brands'),
    path('store-create/', StoreCreateView.as_view(), name='store-create'),
    path('store-get-edit/<int:pk>', StoreObtainEditView.as_view(), name='store-get-edit'),
    path('store-histories/<int:store_id>', StoreHistoryView.as_view(), name='store-histories'),
    path('order-create/', OrderCreateView.as_view(), name='order-create'),
    path('order-crud/<int:pk>', OrderEditOrDeleteView.as_view(), name='order-crud'),
    path('notifications/', GetNotificationView.as_view(), name='notifications'),
    path('notification-detail/<int:pk>', NotificationDetailView.as_view(), name='notification-detail'),
    path('stores/<str:extra>', StoreGetWithExtra.as_view(), name='stores-with-extra'),
    path('store-search/', StoreSearchView.as_view(), name='stores-with-extra'),
    path('orders/', OrderGetView.as_view(), name='orders'),
    path('order-search/', OrderSearchView.as_view(), name='order-search'),
    path('order-filter-by-today/', OrderFilterByToday.as_view(), name='order-filter-by-today'),
    path('order-filter-by-dates/', OrderFilterByDates.as_view(), name='order-filter-by-dates'),
    path('brand-serach/', BrandSearchView.as_view(), name='brand-search'),
    path('category-serach/', CategorySearchView.as_view(), name='category-search'),
    path('thebest-seller-brand/', TheBestSellerBrand.as_view(), name='the-best-seller-brand'),
    path('product-search/', ProductSearchView.as_view(), name='product-search'),
    path('themost-sold-products/', TheMostSoldProductView.as_view(), name='the-most-sold-products'),
    path('report-about-paymant-method/', DiagramByPaymentMethod.as_view(), name='report-by payment-method'),
    path('kirim-chiqim/<str:keyword>', KirimChiqimView.as_view(), name='kirim-chiqim'),
    path('diagram/<str:key>', DiagramAPIView.as_view(), name='diagram'),
    path('products/', AllProductGetView.as_view(), name='products'),
    path('order-filter-by-payment-method/<str:type>', FilterByPaymentMethod.as_view(), name='order-filter-by-payment-method'),
]