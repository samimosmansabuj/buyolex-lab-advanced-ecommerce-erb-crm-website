from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.shortcuts import get_object_or_404

from catalog.models import Product, ProductVariant
from orders.models import Order, OrderItem
from accounts.models import CustomerProfile

from .serializers import LandingPageProductSerializer


# ===============================
# 1. PRODUCT API
# ===============================
class LandingPageProductAPIView(APIView):

    def get(self, request):
        product_id = request.query_params.get("product_id")

        if not product_id:
            return Response({
                "success": False,
                "message": "product_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        serializer = LandingPageProductSerializer(
            product,
            context={"request": request}
        )

        return Response({
            "success": True,
            "product": serializer.data
        }, status=status.HTTP_200_OK)


# ===============================
# 2. ORDER API
# ===============================
class LandingPageOrderAPIView(APIView):

    def post(self, request):
        data = request.data

        required_fields = ["product_id", "name", "phone", "qty"]
        missing = [f for f in required_fields if not data.get(f)]

        if missing:
            return Response({
                "success": False,
                "message": f"Missing fields: {', '.join(missing)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                product = get_object_or_404(Product, id=data["product_id"])

                variant = None

                # SAFE VARIANT VALIDATION
                if data.get("variant_id"):
                    variant = get_object_or_404(
                        ProductVariant,
                        id=data["variant_id"],
                        product=product
                    )

                # ===============================
                # FIX 1: SAFE QTY VALIDATION
                # ===============================
                qty = int(data.get("qty", 1))
                if qty <= 0:
                    return Response({
                        "success": False,
                        "message": "Quantity must be greater than 0"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # ===============================
                # SAFE PRICE LOGIC
                # ===============================
                if variant:
                    unit_price = variant.discount_price or variant.price
                else:
                    unit_price = product.discount_price or product.price

                # ===============================
                # CUSTOMER
                # ===============================
                customer, _ = CustomerProfile.objects.get_or_create(
                    phone=data["phone"],
                    defaults={"full_name": data.get("name")}
                )

                # ===============================
                # ORDER CREATE
                # ===============================
                order = Order.objects.create(
                    customer=customer,
                    shipping_total=data.get("delivery_charge", 0),
                    metadata={
                        "source": "landing_page",
                        "notes": data.get("notes", ""),
                    }
                )

                # ===============================
                # ORDER ITEM (SAFE SNAPSHOT FIXED)
                # ===============================
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    quantity=qty,
                    c_unit_price=product.price,
                    d_unit_price=unit_price,
                    product_snapshot={
                        "product_id": product.id,
                        "title": product.title,
                        "variant_id": variant.id if variant else None,
                        "attributes": variant.attributes if variant else None,
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