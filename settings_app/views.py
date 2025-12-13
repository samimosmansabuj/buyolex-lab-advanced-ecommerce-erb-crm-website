from django.shortcuts import render, redirect


def custom_404_view(request, exception):
    return redirect("product_landing_page")

def home(request):
    return render(request, "home/index.html")

