from rest_framework import serializers
from settings_app.models import SiteSettings
from catalog.models import Category
from settings_app.models import Tag

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
