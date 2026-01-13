from django.urls import path
from .views import api_welcome_message, SiteSettingsAPIViews, CategoryAPIViews, TagAPIViews, AttributeAPIViews, MainSliderAPIViews, ProductAPIViews
from rest_framework.routers import DefaultRouter

app_name = "api"

router = DefaultRouter()
router.register(r"attribute", AttributeAPIViews, basename="attribute_api")
router.register(r"product", ProductAPIViews, basename="product_api")

urlpatterns = [
    path("", api_welcome_message, name="api_welcome_message"),
    path("site-settings/", SiteSettingsAPIViews.as_view(), name="site_settings_api"),
    path("main-slider/", MainSliderAPIViews.as_view(), name="main_slider_api"),

    path("category/", CategoryAPIViews.as_view(), name="category_api"),
    path("tag/", TagAPIViews.as_view(), name="tag_api")
]

urlpatterns += router.urls

