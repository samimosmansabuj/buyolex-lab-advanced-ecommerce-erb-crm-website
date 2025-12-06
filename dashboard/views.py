from django.shortcuts import render, get_object_or_404
from catalog.models import Product, Category
from catalog.utix import CATEGORY_STATUS
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from http import HTTPStatus
from orders.models import Order
from orders.utix import ORDER_STATUS

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

                if data.get("category_id"):
                    category = Category.objects.get(id=data.get("category_id"))
                    category.name = data.get("category_title")
                    category.description = data.get("category_description")
                    category.save()
                    return JsonResponse({
                        "status": True,
                        "message": "Category updated successfully"
                    }, status=HTTPStatus.OK)
                
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

def get_category(request, id):
    try:
        category = get_object_or_404(Category, id=id)
        return JsonResponse({
            "status": True,
            "category": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "status": category.status
            }
        }, status=HTTPStatus.OK)
    except Exception as e:
        print("Exception", e)
        return JsonResponse({
            "status": False,
            "message": str(e)
        }, status=HTTPStatus.BAD_REQUEST)

def delete_category(request, id):
    if request.method == "DELETE":
        try:
            category = get_object_or_404(Category, id=id)
            category.delete()
            return JsonResponse({
                "status": True,
                "message": "Category deleted successfully"
            }, status=HTTPStatus.OK)
        except Exception as e:
            print("Exception", e)
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=HTTPStatus.BAD_REQUEST)
    return JsonResponse({
        "status": False,
        "message": "Invalid request"
    }, status=HTTPStatus.BAD_REQUEST)




class OrderView(View):
    def get(self, request):
        orders = Order.objects.all()
        if request.htmx:
            return render(request, "db_order/partial/partial_order_list.html", {"orders": orders})
        return render(request, "db_order/order_list.html", {"orders": orders})
    
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.POST

                if data.get("order_id"):
                    order = Order.objects.get(id=data.get("order_id"))
                    order.name = data.get("order_title")
                    order.description = data.get("order_description")
                    order.save()
                    return JsonResponse({
                        "status": True,
                        "message": "Order updated successfully"
                    }, status=HTTPStatus.OK)
                
                if data.get("order_title") == "":
                    return JsonResponse({
                        "status": False,
                        "message": "Order title is required"
                    }, status=HTTPStatus.BAD_REQUEST)
                if data.get("order_description") == "":
                    return JsonResponse({
                        "status": False,
                        "message": "Order description is required"
                    }, status=HTTPStatus.BAD_REQUEST)
                Order.objects.create(
                    name=data.get("order_title"),
                    description=data.get("order_description"),
                    status=ORDER_STATUS.ACTIVE,
                )
                return JsonResponse({
                    "status": True,
                    "message": "Order added successfully"
                }, status=HTTPStatus.CREATED)
        except Exception as e:
            print("Exception", e)
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=HTTPStatus.BAD_REQUEST)

class OrderDetailView(View):
    def get(self, request, id):
        order = Order.objects.get(id=id)
        if request.htmx:
            return render(request, "db_order/partial/partial_order_detail.html", {"order": order})
        return render(request, "db_order/order_detail.html", {"order": order})


