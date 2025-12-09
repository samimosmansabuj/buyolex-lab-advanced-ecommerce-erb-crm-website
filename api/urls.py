from django.urls import path
from .views import api_welcome_message, SiteSettingsViews

urlpatterns = [
    path("", api_welcome_message, name="api_welcome_message"),
    path("site-settings/", SiteSettingsViews.as_view(), name="site_settings_api")
]
