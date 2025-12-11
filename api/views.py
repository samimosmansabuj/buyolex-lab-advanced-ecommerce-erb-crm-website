from django.http import JsonResponse
from rest_framework import views, status, permissions
from rest_framework.response import Response

from .serializers import SiteSettingsSerializer, CategorySerializer
from settings_app.models import SiteSettings
from catalog.models import Category


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

class CategoryAPIViews(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            category_id = request.query_params.get('category')
            # sub_category_id = request.query_params.get('sub-category')

            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    sub_category = category.children.all()
                    return Response(
                        {
                            "status": True,
                            "data": CategorySerializer(sub_category, many=True).data
                        }, status=status.HTTP_200_OK
                    )
                except Category.DoesNotExist:
                    return Response(
                        {
                            "status": False,
                            "message": "Category not found"
                        }, status=status.HTTP_404_NOT_FOUND
                    )
            # if sub_category_id:
            #     try:
            #         sub_category = Category.objects.get(id=sub_category_id)
            #         sub_sub_category = sub_category.children.all()
            #         return Response(
            #             {
            #                 "status": True,
            #                 "data": CategorySerializer(sub_sub_category, many=True).data
            #             }, status=status.HTTP_200_OK
            #         )
            #     except Category.DoesNotExist:
            #         return Response(
            #             {
            #                 "status": False,
            #                 "message": "Sub-category not found"
            #             }, status=status.HTTP_404_NOT_FOUND
            #         )

            categories = Category.objects.filter(parent__isnull=True)
            return Response(
                {
                    "status": True,
                    "data": CategorySerializer(categories, many=True, context={"request": request}).data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
