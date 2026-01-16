from rest_framework import serializers
from settings_app.models import SiteSettings
from catalog.models import Category, Product
from settings_app.models import Tag, MainSlider
from catalog.models import Attribute, AttributeValue

class MainSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainSlider
        fields = "__all__"
    
    def get_image(self, obj):
        pic = getattr(obj, "image", None)
        if not pic or getattr(pic, "url", None):
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(pic.url)
        return pic.url


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"
    
    def get_primary_logo(self, obj):
        pic = getattr(obj, "primary_logo", None)
        if not pic or getattr(pic, "url", None):
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(pic.url)
        return pic.url

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
    
    def get_banner_image(self, obj):
        pic = getattr(obj, "banner_image", None)
        if not pic or getattr(pic, "url", None):
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(pic.url)
        return pic.url

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name", "slug"]





class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ["value"]

class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True)
    class Meta:
        model = Attribute
        fields = ["name", "slug", "type", "values"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
    
    def get_images(self, obj):
        pic = getattr(obj, "images", None)
        if not pic or getattr(pic, "url", None):
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(pic.url)
        return pic.url


class DeliveryChargeCalculateSerializer(serializers.Serializer):
    district = serializers.CharField()
    upazilla = serializers.CharField(required=False)
    union = serializers.CharField(required=False)
