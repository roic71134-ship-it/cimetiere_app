from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os
from core.api import api


def carte_view(request):
    carte_path = os.path.join(settings.BASE_DIR, "carte.html")
    with open(carte_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("carte/", carte_view, name="carte"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)