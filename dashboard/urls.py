from django.urls import path
from .views import DashboardView, product_list, add_product, CategoryView, add_category, get_category, delete_category, OrderView, OrderDetailView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('product-list/', product_list, name='product_list'),
    path('product-add/', add_product, name='product_add'),
    path('media-center/', product_list, name='media_center'),

    path('category-list/', CategoryView.as_view(), name='category_list'),
    path('category-add/', add_category, name='category_add'),
    path('get-category/<int:id>/', get_category, name='get_category'),
    path('delete-category/<int:id>/', delete_category, name='delete_category'),

    path('order-list/', OrderView.as_view(), name='order_list'),
    path('order-detail/<int:id>/', OrderDetailView.as_view(), name='order_detail'),
]
