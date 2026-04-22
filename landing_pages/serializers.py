from rest_framework import serializers
from catalog.models import Product, ProductVariant


class LandingPageVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "sku",
            "price",
            "discount_price",
            "attributes",
            "inventory_quantity",
        ]


class LandingPageProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "uuid",
            "title",
            "slug",
            "price",
            "discount_price",
            "short_description",
            "images",
            "variants",
        ]

    def get_images(self, obj):
        request = self.context.get("request")

        if not request:
            return []

        return [
            request.build_absolute_uri(img.image.url)
            for img in obj.images.all()
            if img.image and hasattr(img.image, "url")
        ]

    def get_variants(self, obj):
        variants = obj.variants.filter(is_active=True)
        return LandingPageVariantSerializer(variants, many=True).data