from django.http import JsonResponse
from rest_framework import views, status, permissions
from rest_framework.response import Response

from .serializers import SiteSettingsSerializer
from settings_app.models import SiteSettings


def api_welcome_message(request):
    return JsonResponse({"message": "Welcome Buyelox API Server!"})


class SiteSettingsViews(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        site_settings = SiteSettings.objects.all().first()
        serializer = SiteSettingsSerializer(site_settings, context={"request": request})
        return Response(
            {
                "status": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )


