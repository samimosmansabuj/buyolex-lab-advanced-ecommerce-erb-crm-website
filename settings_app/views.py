from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import MainSlider


def custom_404_view(request, exception):
    return redirect("product_landing_page")

def home(request):
    return render(request, "home/index.html")



