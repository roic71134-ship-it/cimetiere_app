"""URLs principales de l'application."""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from ninja.security import HttpBearer
import jwt
from datetime import datetime, timedelta

from apps.users.api import router as users_router
from apps.terrain.api import router as terrain_router
from apps.reservations.api import router as reservations_router
from apps.finances.api import router as finances_router


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            from apps.users.models import Utilisateur
            user = Utilisateur.objects.get(id=payload["user_id"])
            request.user = user
            return user
        except Exception:
            return None


api = NinjaAPI(
    title="API Gestion de Cimetière",
    version="1.0.0",
    description="API RESTful pour la gestion du cimetière - GI2 2026",
    auth=AuthBearer(),
)

api.add_router("/auth/", users_router)
api.add_router("/terrain/", terrain_router)
api.add_router("/reservations/", reservations_router)
api.add_router("/finances/", finances_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
