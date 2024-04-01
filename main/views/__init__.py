from .product import ProductAddGenericApiView, ProductCRUDGenericAPIView, ProductDetailView, ProductSearchView, \
    TheMostSoldProductView
from .category import CategoryAdd, CategoryGetAll, CategoryEditView, CategorySearchView
from .brand import BrandAddView, BrandEditView, BrandAllGetView, BrandSearchView, TheBestSellerBrand
from .store import StoreCreateView, StoreObtainEditView, StoreHistoryView, StoreGetWithExtra, StoreSearchView
from .order import OrderCreateView, OrderEditOrDeleteView, OrderGetView, OrderSearchView, OrderFilterByToday, \
    OrderFilterByDates, DiagramByPaymentMethod, KirimChiqimView, DiagramAPIView
from .notification import GetNotificationView, NotificationDetailView

