from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import HomePageLandingPage
from catalog.utix import PRODUCT_MEDIA_ROLE
from .utix import LandingPageHeroType
from settings_app.models import WhyBuyolex, DeliveryReturnPolicy
import time
from django.views import View
from catalog.models import Product, ProductVariant
from http import HTTPStatus
from django.core.exceptions import ObjectDoesNotExist
from orders.models import Order, OrderItem
from accounts.models import CustomUser, CustomerProfile, CustomerAddress
from .utils import OrderConfirmatinoEmailSend
from django.db import transaction


def product_landing_page(request):
    try:
        landing_page_product = HomePageLandingPage.objects.filter(is_active=True).first()
        product = landing_page_product.product
        if len(product.videos.all()) > 0 and landing_page_product.hero_type == LandingPageHeroType.VIDEO:
            primary_hero = product.videos.all().first()
        else:
            primary_hero = product.images.filter(role=PRODUCT_MEDIA_ROLE.PRIMARY).first()
        
        context = {
            "landing_page_product": landing_page_product,
            "primary_hero": primary_hero,
            "whybuyolex": WhyBuyolex.objects.first(),
            "deliveryreturnpolicy": DeliveryReturnPolicy.objects.first()
        }
        return render(request, "product_landing_page.html", context)
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": str(e)
            }, status=HTTPStatus.BAD_REQUEST
        )


class CreateOrderView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                "success": False,
                "message": "Get method not allowed!"
            }, status=HTTPStatus.METHOD_NOT_ALLOWED
        )
    
    def get_product(self, id):
        try:
            product = get_object_or_404(Product, id=id)
            return product
        except Product.DoesNotExist as e:
            raise ObjectDoesNotExist("Product Not Found or Wrong Product ID")

    def get_product_variante(self, product: object, sku: str):
        try:
            variante = get_object_or_404(ProductVariant, product=product, sku=sku)
            return variante, variante.discount_price
        except ProductVariant.DoesNotExist as e:
            raise ObjectDoesNotExist("Product Variante Not Found or Wrong Product ID")
    
    def price_verify___(self, input_price, price):
        if float(price) != float(input_price):
            raise Exception("Input Price and Product Price not Same!")
        return True

    def get_user_profile(self, name, phone, email=None):
        if CustomUser.objects.filter(email=email).exists():
            return CustomUser.objects.get(email=email).customer_profile
        else:
            if email:
                user = CustomUser.objects.create(
                    email=email, full_name=name
                )
                customer = user.customer_profile
                customer.phone = phone
                customer.save()
            else:
                customer, created = CustomerProfile.objects.get_or_create(
                    phone = phone,
                    full_name = name
                )
            return customer
    
    def get_make_address(self, customer, address, district, upazila, area):
        address = CustomerAddress.objects.create(
            customer=customer,
            address= address,
            area= area,
            upazila= upazila,
            district= district,
        )
        return address.get_address
    
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.POST
                product = self.get_product(data.get("product_id"))
                variante = None
                if data.get("variante"):
                    variante, price = self.get_product_variante(product, data.get("variante"))
                
                self.price_verify___(data.get("product_price"), product.discount_price)
                customer = self.get_user_profile(data.get("name"), data.get("phone"), data.get("email") or None)

                address = self.get_make_address(customer, data.get("address"), data.get("district"), data.get("upazila"), data.get("area"))
                
                qty = data.get("qty")
                metadata = {"note": data.get("notes")}

                order = Order.objects.create(
                    customer = customer,
                    billing_address = address,
                    shipping_address = address,
                    metadata=metadata
                )
                OrderItem.objects.create(
                    order= order,
                    product= product,
                    variant= variante,
                    quantity= int(qty),
                    c_unit_price= product.price,
                    d_unit_price= product.discount_price,
                )
                if data.get("email"):
                    send_mail = OrderConfirmatinoEmailSend(order, data.get("email"))
                    send_mail.order_confirmation_mail_send()

                return JsonResponse(
                    {
                        "success": True,
                        "message": "Order Successfully Created!"
                    }, status=HTTPStatus.CREATED
                )
        except Exception as e:
            print("error: ", str(e))
            return JsonResponse(
                {
                    "success": False,
                    "message": str(e)
                }, status=HTTPStatus.BAD_REQUEST
            )


def get_order(request, id):
    try:
        order = get_object_or_404(Order, id=id)
        return JsonResponse(
            {
                "status": True,
                "message": "OK",
                "data": {
                    "get_items_total" : order.get_items_total,
                    "get_total_quantity" : order.get_total_quantity,
                    "get_current_total" : order.get_current_total,
                    "get_discount_total" : order.get_discount_total,
                    "get_discount_percentage" : order.get_discount_percentage,
                }
            }, status=HTTPStatus.OK
        )
    except Exception as e:
        return JsonResponse(
            {
                "status": True,
                "message": str(e)
            }
        )






