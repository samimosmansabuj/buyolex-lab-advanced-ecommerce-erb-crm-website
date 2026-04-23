from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.shortcuts import get_object_or_404

from decimal import Decimal

from catalog.models import Product, ProductVariant
from orders.models import Order, OrderItem
from accounts.models import CustomerProfile
from landing_pages.models import HomePageLandingPage

from .serializers import LandingPageProductSerializer
from rest_framework.permissions import AllowAny


# ===============================
# 1. PRODUCT API (CODE BASED)
# ===============================
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
# 2. ORDER API (PRODUCTION SAFE)
# ===============================
class LandingPageOrderAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        data = request.data

        required_fields = ["product_id", "name", "phone", "qty"]
        missing = [f for f in required_fields if data.get(f) is None]

        if missing:
            return Response({
                "success": False,
                "message": f"Missing fields: {', '.join(missing)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                product = get_object_or_404(Product, id=data["product_id"])

                variant = None

                if data.get("variant_id"):
                    variant = get_object_or_404(
                        ProductVariant,
                        id=data["variant_id"],
                        product=product
                    )

                try:
                    qty = int(data.get("qty", 1))
                except:
                    qty = 1

                if qty <= 0:
                    return Response({
                        "success": False,
                        "message": "Quantity must be greater than 0"
                    }, status=status.HTTP_400_BAD_REQUEST)

                if variant:
                    unit_price = variant.discount_price or variant.price
                else:
                    unit_price = product.discount_price or product.price

                delivery_charge = data.get("delivery_charge", 0)
                try:
                    delivery_charge = Decimal(str(delivery_charge or 0))
                except:
                    delivery_charge = Decimal("0")

                phone = str(data.get("phone")).strip()

                customer, _ = CustomerProfile.objects.get_or_create(
                    phone=phone.replace("+880", "0").strip(),
                    defaults={
                        "full_name": data.get("name", "").strip()
                    }
                )

                # ✅ FIXED (float → str)
                order = Order.objects.create(
                    customer=customer,
                    shipping_total=delivery_charge,

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

                        # 🔥 SAFE STRING
                        "unit_price": str(unit_price),
                        "delivery_charge": str(delivery_charge),
                        "total_estimate": str((unit_price * qty) + delivery_charge),
                    }
                )

                # ✅ FIXED (Decimal safe math)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    quantity=qty,

                    c_unit_price=unit_price,
                    d_unit_price=unit_price,

                    total_price=Decimal(unit_price) * Decimal(qty),
                    discount_total_price=Decimal(unit_price) * Decimal(qty),

                    product_snapshot={
                        "product_id": product.id,
                        "title": product.title,
                        "variant_id": variant.id if variant else None,
                        "attributes": getattr(variant, "attributes", None),
                    }
                )

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