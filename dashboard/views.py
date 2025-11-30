from django.shortcuts import render

def dashboard(request):
    if request.htmx:
        return render(request, "db_home/main_wrapper.html")
    return render(request, "dashboard.html")

def product_list(request):
    if request.htmx:
        return render(request, "db_product/partial/partial_product_list.html")
    return render(request, "db_product/product_list.html")

def add_product(request):
    if request.htmx:
        return render(request, "db_product/partial/partial_add_product.html")
    return render(request, "db_product/add_product.html")


def category_list(request):
    if request.htmx:
        return render(request, "db_category/partial/partial_category_list.html")
    return render(request, "db_category/category_list.html")

def add_category(request):
    if request.htmx:
        return render(request, "db_category/partial/partial_add_category.html")
    return render(request, "db_category/add_category.html")

