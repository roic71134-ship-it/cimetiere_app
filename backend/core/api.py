from ninja import NinjaAPI
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            from apps.auth_app.models import Utilisateur
            user = Utilisateur.objects.select_related("role").get(
                id=user_id, est_actif=True
            )
            request.user = user
            return user
        except (TokenError, Exception):
            return None


api = NinjaAPI(
    title="France_paris",
    version="1.0.0",
    description="API gestion de cimetiere de France.",
    docs_url="/docs",
    auth=JWTAuth(),
    csrf=False,
)

from apps.auth_app.api import router as auth_router
from apps.auth_app.admin_api import router as admin_router
from apps.terrain.api import router as terrain_router
from apps.caveaux.api import router as caveaux_router
from apps.reservations.api import router as reservations_router
from apps.paiements.api import router as paiements_router
from apps.reporting.api import router as reporting_router
from apps.concessions.api import router as concessions_router
from apps.exhumations.api import router as exhumations_router

api.add_router("/auth", auth_router, tags=["Authentification"])
api.add_router("/admin", admin_router, tags=["Administration"])
api.add_router("/terrain", terrain_router, tags=["Terrain"])
api.add_router("/caveaux", caveaux_router, tags=["Caveaux"])
api.add_router("/reservations", reservations_router, tags=["Réservations"])
api.add_router("/paiements", paiements_router, tags=["Paiements"])
api.add_router("/reporting", reporting_router, tags=["Reporting"])
api.add_router("/concessions", concessions_router, tags=["Concessions"])
api.add_router("/exhumations", exhumations_router, tags=["Exhumations"])