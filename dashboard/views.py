from django.shortcuts import render
from catalog.models import Product, Category
from catalog.utix import CATEGORY_STATUS
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from http import HTTPStatus

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


def add_category(request):
    if request.method == "POST":
        Category.objects.create(
            name=request.POST.get("name"),
            slug=request.POST.get("slug"),
            parent=request.POST.get("parent"),
            status=request.POST.get("status"),
            image=request.FILES.get("image"),
        )
        return JsonResponse({"message": "Category added successfully"})

    if request.htmx:
        return render(request, "db_category/partial/partial_add_category.html")
    return render(request, "db_category/add_category.html")

class CategoryView(View):
    def get(self, request):
        categories = Category.objects.all()
        if request.htmx:
            return render(request, "db_category/partial/partial_category_list.html", {"categories": categories})
        return render(request, "db_category/category_list.html", {"categories": categories})
    
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.POST
                if data.get("category_title") == "":
                    return JsonResponse({
                        "status": False,
                        "message": "Category title is required"
                    }, status=HTTPStatus.BAD_REQUEST)
                if data.get("category_description") == "":
                    return JsonResponse({
                        "status": False,
                        "message": "Category description is required"
                    }, status=HTTPStatus.BAD_REQUEST)
                Category.objects.create(
                    name=data.get("category_title"),
                    description=data.get("category_description"),
                    status=CATEGORY_STATUS.ACTIVE,
                )
                return JsonResponse({
                    "status": True,
                    "message": "Category added successfully"
                }, status=HTTPStatus.CREATED)
        except Exception as e:
            print("Exception", e)
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=HTTPStatus.BAD_REQUEST)
