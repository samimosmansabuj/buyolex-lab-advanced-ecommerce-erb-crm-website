from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve as static_serve
import os

admin.site.site_title = "Buyolex"
admin.site.site_header = "Buyolex"
admin.site.app_index = "Welcome to Buyolex"

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include All App Urls=======
    path('', include("accounts.urls")),
    path('', include("catalog.urls")),
    path('', include("landing_pages.urls")),
    path('', include("marketing.urls")),
    path('', include("offers.urls")),
    path('', include("orders.urls")),
    path('', include("settings_app.urls")),

    # Include For API Develop URL
    path('api/v1/', include("api.urls", namespace="api")),
    
    # Dashboard
    path('dashboard/', include("dashboard.urls")),
]

SERVE_MEDIA = os.getenv("SERVE_MEDIA", "False").strip().lower() in ("true","1","yes")
if SERVE_MEDIA:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', static_serve, {'document_root': settings.STATIC_ROOT}),
    ]
