from django.shortcuts import render
from django.http import JsonResponse

def api_welcome_message(request):
    return JsonResponse({"message": "Welcome Buyelox API Server!"})

