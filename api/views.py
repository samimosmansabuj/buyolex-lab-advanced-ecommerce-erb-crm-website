from django.http import JsonResponse
from rest_framework import views, status, permissions, viewsets
from rest_framework.response import Response
from .serializers import SiteSettingsSerializer, CategorySerializer, TagSerializer, AttributeSerializer, MainSliderSerializer
from settings_app.models import SiteSettings, Tag, MainSlider
from catalog.models import Category, Attribute


def api_welcome_message(request):
    return JsonResponse({"message": "Welcome Buyelox API Server!"})


class SiteSettingsAPIViews(views.APIView):
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

class MainSliderAPIViews(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            sliders = MainSlider.objects.filter(is_active=True)
            serializer = MainSliderSerializer(sliders, many=True, context={"request": request})
            return Response(
                {
                    "status": True,
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoryAPIViews(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            category_id = request.query_params.get('category')
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

class TagAPIViews(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            q = request.query_params.get('q')
            if q:
                try:
                    tags = Tag.objects.filter(name__icontains=q)
                    print("Tags: ", tags)
                    return Response(
                        {
                            "status": True,
                            "data": TagSerializer(tags, many=True).data
                        }, status=status.HTTP_200_OK
                    )
                except Tag.DoesNotExist:
                    return Response(
                        {
                            "status": False,
                            "message": "Tag not found"
                        }, status=status.HTTP_404_NOT_FOUND
                    )
            tags = Tag.objects.all()
            return Response(
                {
                    "status": True,
                    "data": TagSerializer(tags, many=True).data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = TagSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Tag created successfully",
                        "data": serializer.data
                    }, status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    "status": False,
                    "message": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AttributeAPIViews(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.AllowAny]
    
    def list(self, request, *args, **kwargs):
        try:
            attributes = Attribute.objects.all()
            return Response(
                {
                    "status": True,
                    "data": AttributeSerializer(attributes, many=True).data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
