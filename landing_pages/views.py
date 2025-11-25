from django.shortcuts import render

def product_landing_page(request):
    return render(request, "product_landing_page.html")

