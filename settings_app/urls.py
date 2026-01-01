from django.urls import path
from django.conf.urls import handler500
from .views import custom_404_view, home

handler500 = custom_404_view

app_name = "settings_app"

urlpatterns = [
    # path("", home, name="home"),
]
