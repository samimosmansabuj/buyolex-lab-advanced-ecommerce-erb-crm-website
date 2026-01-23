from django.shortcuts import render, redirect
from django.views import View
from accounts.models import CustomUser
from .utix import USER_TYPE
from django.contrib.auth import authenticate, login, logout

class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'db_auth/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = authenticate(username=email, password=password)
            if user is not None and user.user_type in (USER_TYPE.ADMIN, USER_TYPE.SUPER_ADMIN, USER_TYPE.STAFF):
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'db_auth/login.html', {'error': 'Invalid credentials or insufficient permissions.'})
        except CustomUser.DoesNotExist:
            return render(request, 'db_auth/login.html', {'error': 'User does not exist.'})


def logout_view(request):
    logout(request)
    return redirect('admin_login')
