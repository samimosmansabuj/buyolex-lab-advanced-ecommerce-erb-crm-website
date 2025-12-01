from django.urls import path
from .views import dashboard, product_list, add_product, CategoryView, add_category

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('product-list/', product_list, name='product_list'),
    path('product-add/', add_product, name='product_add'),
    path('media-center/', product_list, name='media_center'),

    path('category-list/', CategoryView.as_view(), name='category_list'),
    path('category-add/', add_category, name='category_add'),
]
