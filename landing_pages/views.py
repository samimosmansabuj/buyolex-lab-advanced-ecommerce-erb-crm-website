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
from accounts.models import CustomUser
from accounts.utix import USER_TYPE

def product_landing_page(request):
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


def create_order(request):
    time.sleep(1)
    # if request.method == "POST":
        
    return JsonResponse(
        {"success": False, "message": "Get method not allowed!"}, status=404
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
            return product, product.discount_price
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

    def get_user(self, name, phone, email=None):
        if CustomUser.objects.filter(email=email).exists():
            return CustomUser.objects.get(email=email)
        else:
            user, created = CustomUser.objects.get_or_create(full_name=name, phone=phone)
            if email:
                user.email = email
            user.save()
            return user
    
    def get_make_address(self, address, district, upazila, area):
        full_address = ""
        if address:
            full_address = address
        if area:
            full_address = f"{full_address}, {area}"
        if upazila:
            full_address = f"{full_address}, {upazila}"
        if district:
            full_address = f"{full_address}, {district}"
        return full_address

    
    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            print("data: ", data)
            product, price = self.get_product(data.get("product_id"))
            variante = None
            if data.get("variante"):
                variante, price = self.get_product_variante(product, data.get("variante"))
            
            self.price_verify___(data.get("product_price"), price)
            user = self.get_user(data.get("name"), data.get("phone"), data.get("email") or None)

            address = self.get_make_address(data.get("address"), data.get("district"), data.get("upazila"), data.get("area"))

            qty = data.get("qty")
            metadata = {"note": data.get("notes")}

            print("product: ", product)
            print("prince: ", price)
            print("address: ", address)
            print("quantity: ", qty)
            # price("Metadata: ", metadata)

            order = Order.objects.create(
                user = user,
                items_total = qty,
                billing_address = address,
                shipping_address = address,
                metadata=metadata
            )
            OrderItem.objects.create(
                order= order,
                product= product,
                variant= variante,
                quantity= int(qty),
                unit_price= price,
            )

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





