from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

class OrderCreateAPIViews(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        return Response(
            {
                "success": True,
                "message": "Order created successfully."
            }, status=status.HTTP_201_CREATED
        )
    
    def get(self, request, *args, **kwargs):
        return Response(
            {
                "success": True,
                "message": "This is order API endpoint."
            }, status=status.HTTP_200_OK
        )
