from django.urls import path
from accounts.views import UserLoginView, logout_view

urlpatterns = [
    path('admin-login/', UserLoginView.as_view(), name='admin_login'),
    path('admin-logout/', logout_view, name='admin_logout'),
]
