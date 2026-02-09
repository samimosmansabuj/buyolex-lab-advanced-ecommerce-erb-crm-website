from django.shortcuts import render, get_object_or_404, redirect
from catalog.models import Product, Category
from catalog.utix import CATEGORY_STATUS
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from http import HTTPStatus
from orders.models import Order
from orders.utix import ORDER_STATUS
import json
from django.db import transaction
from django.http import QueryDict
from accounts.models import CustomUser
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from accounts.utix import USER_TYPE
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum, F, Value, DecimalField
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models.functions import Coalesce


class DashboardView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def get_today_order_count(self, orders):
        today = timezone.now().date()
        return orders.filter(placed_at__date=today).count()
    
    def new_orders_count (self, orders):
        return orders.filter(order_status=ORDER_STATUS.NEW).count()
    
    def get_total_order_amount(self, orders):
        return orders.aggregate(
            total_amount=Coalesce(
                Sum('items__discount_total_price') + Sum('shipping_total'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )['total_amount']
    
    def get(self, request):
        orders = Order.objects.all().order_by("-placed_at")
        context = {
            "orders": orders[:10],
            "total_order_amount": self.get_total_order_amount(orders),
            "total_orders": orders.count(),
            "today_order_count": self.get_today_order_count(orders),
            "new_orders_count": self.new_orders_count(orders),
        }
        if request.htmx:
            return render(request, "db_home/main_wrapper.html", context)
        return render(request, "dashboard.html", context)

@login_required(login_url='admin_login')
def product_list(request):
    products = Product.objects.all()
    if request.htmx:
        return render(request, "db_product/partial/partial_product_list.html", {"products": products})
    return render(request, "db_product/product_list.html", {"products": products})

@login_required(login_url='admin_login')
def add_product(request):
    if request.htmx:
        return render(request, "db_product/partial/partial_add_product.html")
    return render(request, "db_product/add_product.html")

@login_required(login_url='admin_login')
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

# @login_required(login_url='admin_login')
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

@login_required(login_url='admin_login')
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

@login_required(login_url='admin_login')
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



class OrderView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def status_wise_order_count(self):
        qs = (
            Order.objects
            .values('order_status')
            .annotate(total=Count('id'))
        )
        order_count = {status: 0 for status, _ in ORDER_STATUS.choices}
        for row in qs:
            order_count[row['order_status']] = row['total']
        order_count['all'] = sum(order_count.values())
        return order_count
    
    def get_order_queryset(self, request):
        status = request.GET.get('status')
        search = request.GET.get('q', '')
        orders = Order.objects.all().order_by("-placed_at")
        
        if status and status in ORDER_STATUS.values:
            orders = orders.filter(order_status=status)
        
        if search:
            orders = orders.filter(
                Q(order_id__icontains=search) |
                Q(customer__full_name__icontains=search) |
                Q(customer__phone__icontains=search) |
                Q(order_status__icontains=search) |
                Q(payment_status__icontains=search) |
                Q(delivery_type__icontains=search) |
                Q(shipping_address__icontains=search)
            )
        
        page_number = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 10))
        paginator = Paginator(orders, per_page)
        orders = paginator.get_page(page_number)
        
        return orders, paginator, per_page, page_number
    
    def permission_denied(self, request):
        if not request.user.is_authenticated:
            return redirect('product_landing_page')
        elif request.user.user_type not in [USER_TYPE.ADMIN, USER_TYPE.STAFF, USER_TYPE.SUPER_ADMIN]:
            return redirect('product_landing_page')
    
    def get(self, request):
        orders, paginator, per_page, page_number = self.get_order_queryset(request)
        context = {
            "orders": orders,
            "paginator": paginator,
            "per_page": per_page,
            "page_number": page_number,
            "order_count": self.status_wise_order_count(),
            "current_status": request.GET.get('status', 'all'),
            "current_search": request.GET.get('q', ''),
        }
        if request.htmx:
            return render(request, "db_order/partial/partial_order_list.html", context)
        return render(request, "db_order/order_list.html", context)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('product_landing_page')
        elif request.user.user_type not in [USER_TYPE.ADMIN, USER_TYPE.STAFF, USER_TYPE.SUPER_ADMIN]:
            return redirect('product_landing_page')
        
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
                    status=STATUS.Pending,
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
        if not request.user.is_authenticated:
            return redirect('product_landing_page')
        elif request.user.user_type not in [USER_TYPE.ADMIN, USER_TYPE.STAFF, USER_TYPE.SUPER_ADMIN]:
            return redirect('product_landing_page')
        
        order = self.get_order(id)

        if request.htmx:
            return render(request, "db_order/partial/partial_order_detail.html", {"order": order})
        return render(request, "db_order/order_detail.html", {"order": order})

    def get_order(self, id):
        return get_object_or_404(Order, id=id)

    def generate_unique_username(self, name):
        base = slugify(name) or "user"
        username = base
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{username}-{counter}"
            counter += 1
        return username

    def update_customer_profile(self, data, profile):
        profile.full_name = data.get("full_name", profile.full_name)
        profile.phone = data.get("phone", profile.phone)
        profile.whatsapp = data.get("whatsapp", profile.whatsapp)
        if data.get("email"):
            if profile.user:
                profile.user.email = data.get("email", profile.user.email)
                profile.user.save()
            else:
                user = CustomUser.objects.create(
                    email=data.get("email"),
                    full_name=profile.full_name,
                    username=self.generate_unique_username(profile.full_name)
                )
                profile.user = user
        profile.save()
        return True
    
    def update_order_object(self, data, order):
        if data.get("delivery_date"):
            order.delivery_date = data.get("delivery_date", order.delivery_date)
        order.shipping_address = data.get("shipping_address", order.shipping_address)
        order.payment_status = data.get("payment_status", order.payment_status)
        order.order_status = data.get("order_status", order.order_status)
        order.save()
        return True

    def post(self, request, id):
        if not request.user.is_authenticated:
            return redirect('product_landing_page')
        elif request.user.user_type not in [USER_TYPE.ADMIN, USER_TYPE.STAFF, USER_TYPE.SUPER_ADMIN]:
            return redirect('product_landing_page')
        
        if request.POST.get("_method") == "PATCH":
            return self.patch(request, id)
        return JsonResponse({"error": "Invalid request"}, status=400)

    def patch(self, request, id):
        order = self.get_order(id)
        
        data = request.POST
        if order:
            try:
                with transaction.atomic():
                    profile = order.customer
                    self.update_customer_profile(data, profile)
                    self.update_order_object(data, order)
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Order updated successfully"
                        }, status=200
                    )
                
            except Exception as e:
                print("error: ", e)
                return JsonResponse(
                    {
                        "success": False,
                        "message": str(e)
                    }
                )

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == "patch":
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

class OrderInvoiceView(View):
    def get_order(self, id):
        return get_object_or_404(Order, id=id)

    def get(self, request, id):
        order = self.get_order(id)
        if order:
            return render(request, "db_order/invoice.html", {"order": order})
        return redirect(request.META.get('HTTP_REFERER'))

