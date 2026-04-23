from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.shortcuts import get_object_or_404

from decimal import Decimal

from catalog.models import Product, ProductVariant
from orders.models import Order, OrderItem
from accounts.models import CustomerProfile, CustomerAddress
from landing_pages.models import HomePageLandingPage

from .serializers import LandingPageProductSerializer
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from .utils import OrderConfirmatinoEmailSend


# ===============================
# PRODUCT API (CODE BASED)
class LandingPageProductAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        product_id = request.query_params.get("product_id")

        product = None

        if code:
            landing = HomePageLandingPage.objects.filter(
                code=code,
                is_active=True
            ).first()

            if not landing or not landing.product:
                return Response({
                    "success": False,
                    "message": "Invalid or inactive landing code"
                }, status=status.HTTP_404_NOT_FOUND)

            product = landing.product
        elif product_id:
            product = get_object_or_404(Product, id=product_id)

        else:
            return Response({
                "success": False,
                "message": "code or product_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = LandingPageProductSerializer(
            product,
            context={"request": request}
        )

        return Response({
            "success": True,
            "product": serializer.data
        }, status=status.HTTP_200_OK)

# ===============================

# ===============================
# ORDER API (PRODUCTION SAFE)
class LandingPageOrderAPIView(APIView):
    permission_classes = [AllowAny]

    def get_make_address(self, customer: CustomerProfile, district: str, address: str, upazila=None, area=None):
        address = CustomerAddress.objects.create(
            customer=customer,
            address= address,
            # area= area,
            # upazila= upazila,
            district= district,
        )
        return address.get_address

    def get_product(self, id):
        try:
            product = get_object_or_404(Product, id=id)
            return product
        except Product.DoesNotExist as e:
            raise ObjectDoesNotExist("Product Not Found or Wrong Product ID")

    def get_product_variant(self, product: object, sku: str):
        try:
            variant = get_object_or_404(ProductVariant, product=product, sku=sku)
            return variant, variant.discount_price
        except ProductVariant.DoesNotExist as e:
            raise ObjectDoesNotExist("Product Variant Not Found or Wrong Product ID")

    def verify_input(self, data):
        required_fields = [
            "product_id", "delivery_charge",
            # "product_price", 
            "name", "phone",
            "address", "district", "qty",
            # "notes"
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        return missing_fields

    def get_price(self, variant: object, product: Product):
        if variant:
            c_unit_price = variant.price
            d_unit_price = variant.discount_price or variant.price
        else:
            c_unit_price = product.price
            d_unit_price = product.discount_price or product.price
        return c_unit_price, d_unit_price

    def get_customer(self, phone: str, full_name: str):
        if CustomerProfile.objects.filter(phone=phone).exists():
            customer = CustomerProfile.objects.filter(phone=phone).first()
            customer.full_name = full_name
            customer.save()
        else:
            customer = CustomerProfile.objects.create(phone=phone, full_name=full_name)
        return customer

    def post(self, request):
        data = request.data
        missing_fields = self.verify_input(data)
        if missing_fields:
            return Response(
                {
                    "success": False,
                    "message": f"The following fields must be filled: {', '.join(missing_fields)}"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            phone = str(data.get("phone")).strip()
            name = data.get("name", "").strip()
            address = data.get("address", "").strip()
            city = data.get("district").strip()
            qty = int(data.get("qty", 1))
            delivery_charge = data.get("delivery_charge", 0)

            with transaction.atomic():
                product = self.get_product(data.get("product_id"))
                variant = data.get("variant", None)
                if variant:
                    variant, price = self.get_product_variant(product, variant)
                
                if qty <= 0:
                    return Response({
                        "success": False,
                        "message": "Quantity must be greater than 0"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                c_unit_price, d_unit_price = self.get_price(variant, product)
                customer = self.get_customer(phone, name)
                address = self.get_make_address(customer, city, address)

                # Create Order Object----
                order = Order.objects.create(
                    customer=customer,
                    billing_address=address,
                    shipping_address=address,
                    shipping_total=Decimal(str(delivery_charge or 0)),
                    metadata={
                        "source": "landing_page",

                        "name": data.get("name"),
                        "phone": phone,

                        "address": data.get("address"),
                        "district": data.get("district"),

                        "qty": qty,
                        "product_id": product.id,
                        "product_title": product.title,

                        "variant_id": variant.id if variant else None,
                        "variant_attributes": getattr(variant, "attributes", None),

                        "unit_price": str(d_unit_price),
                        "delivery_charge": str(delivery_charge),
                        "total_estimate": str((d_unit_price * qty) + delivery_charge),
                    }
                )

                # Order Item Create---
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    quantity=int(qty),

                    c_unit_price=c_unit_price,
                    d_unit_price=d_unit_price,

                    total_price=Decimal(c_unit_price) * Decimal(qty),
                    discount_total_price=Decimal(d_unit_price) * int(qty),

                    product_snapshot={
                        "product_id": product.id,
                        "title": product.title,
                        "variant_id": variant.id if variant else None,
                        "attributes": getattr(variant, "attributes", None),
                    }
                )

                if data.get("email"):
                    send_mail = OrderConfirmatinoEmailSend(order, data.get("email"))
                    send_mail.order_confirmation_mail_send()

                return Response({
                    "success": True,
                    "order_id": order.order_id,
                    "message": "Order placed successfully"
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# ===============================
