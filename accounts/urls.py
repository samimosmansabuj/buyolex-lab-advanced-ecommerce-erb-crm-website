from django.urls import path
from accounts.views import UserLoginView

urlpatterns = [
    path('admin-login/', UserLoginView.as_view(), name='admin_login'),
]
