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
from django.utils.text import slugify


def product_landing_page(request):
    try:
        landing_page_product = HomePageLandingPage.objects.filter(is_active=True).first()
        product = landing_page_product.product
        primary_hero = product.images.filter(role=PRODUCT_MEDIA_ROLE.PRIMARY).first()
        # if len(product.videos.all()) > 0 and landing_page_product.hero_type == LandingPageHeroType.VIDEO:
        #     primary_hero = product.videos.all().first()
        # else:
        #     primary_hero = product.images.filter(role=PRODUCT_MEDIA_ROLE.PRIMARY).first()
        context = {
            "landing_page_product": landing_page_product,
            "primary_hero": primary_hero,
            "whybuyolex": WhyBuyolex.objects.first(),
            "deliveryreturnpolicy": DeliveryReturnPolicy.objects.first()
        }
        return render(request, "02/product_landing_page.html", context)
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

    def generate_unique_username(self, name):
        base = slugify(name) or "user"
        username = base
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{username}-{counter}"
            counter += 1
        return username

    def get_user_profile(self, name, phone, whatsapp=None, email=None):
        if email:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                customer_profile = user.customer_profile
                if whatsapp:
                    customer_profile.whatsapp = whatsapp
                customer_profile.save()
                return customer_profile
            
            user = CustomUser.objects.create(
                email=email, full_name=name, username=self.generate_unique_username(name)
            )
            customer = user.customer_profile
            customer.phone = phone
            if whatsapp:
                customer.whatsapp = whatsapp
            customer.save()
            return customer
        else:
            customer, created = CustomerProfile.objects.get_or_create(
                phone=phone, whatsapp=whatsapp,
                defaults={"full_name": name}
            )
        return customer
    
    def get_make_address(self, customer, district, upazila, area, address):
        address = CustomerAddress.objects.create(
            customer=customer,
            address= address,
            # area= area,
            # upazila= upazila,
            district= district,
        )
        return address.get_address
    
    def verify_input(self, data):
        required_fields = [
            "product_id", "product_price", "name", "phone",
            "address", "district", "qty",
            # "notes"
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        return missing_fields
    
    def get_metadata(self, data):
        EXTRA_PERSONAL_FIELDS = [
            "babyName", "babyBirthPlace", "babyDOB", "babyBirthTime", "fatherName", "motherName", "birthNote",
            "groomName", "brideName", "groomFatherName", "brideFatherName", "groomMotherName", "brideMotherName", "marriageDate", "marriageNote",
            "deceasedName", "deceasedDate", "parentName", "deceasedNote",
            "remeberName", "rememberDate", "remeberTime", "varianteNote", "receiver",
        ]
        

        extra_personal_info = {
            field: data.get(field)
            for field in EXTRA_PERSONAL_FIELDS
            if data.get(field) not in [None, ""]
        }
        return extra_personal_info

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            extra_personal_info = self.get_metadata(data)
            missing_fields = self.verify_input(data)
            if missing_fields:
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"The following fields must be filled: {', '.join(missing_fields)}"
                    },
                    status=HTTPStatus.BAD_REQUEST
                )

            with transaction.atomic():
                product = self.get_product(data.get("product_id"))
                variante = None
                if data.get("variante"):
                    variante, price = self.get_product_variante(product, data.get("variante"))
                
                self.price_verify___(data.get("product_price"), product.discount_price)
                customer = self.get_user_profile(data.get("name"), data.get("phone"), data.get("whatsapp"), data.get("email") or None)

                address = self.get_make_address(customer, data.get("district"), data.get("upazila", None), data.get("area", None), data.get("address", None))
                
                qty = data.get("qty")
                metadata = {"note": data.get("notes"), "extra_personal_info": extra_personal_info}
                order = Order.objects.create(
                    customer = customer,
                    billing_address = address,
                    shipping_address = address,
                    metadata=metadata,
                    shipping_total=data.get("delivery_charge")
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variante,
                    quantity=int(qty),
                    c_unit_price=product.price,
                    d_unit_price=product.discount_price,
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
            print("Error in CreateOrderView: ", e)
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






