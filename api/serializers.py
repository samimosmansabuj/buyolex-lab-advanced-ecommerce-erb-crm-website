from rest_framework import serializers
from settings_app.models import SiteSettings

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