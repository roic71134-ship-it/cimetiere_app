from ninja import Router
from ninja.security import HttpBearer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Utilisateur, SessionMFA, Role
from .schemas import (
    LoginSchema, MFASchema, TokenSchema,
    UtilisateurSchema, MessageSchema
)
from .services import envoyer_code_mfa

router = Router()


class InscriptionSchema:
    pass


from ninja import Schema
from typing import Optional


class InscriptionClientSchema(Schema):
    email: str
    password: str
    nom: str
    prenom: str
    telephone: str
    adresse: str = ""


@router.post("/login", response=MessageSchema, auth=None)
def login(request, data: LoginSchema):
    try:
        user = Utilisateur.objects.get(email=data.email)
        if not user.check_password(data.password):
            return {"message": "Email ou mot de passe incorrect."}
        if not user.est_actif:
            return {"message": "Compte désactivé."}
        session = SessionMFA.creer_pour(user, request.META.get("REMOTE_ADDR"))
        envoyer_code_mfa(user, session.code)
        return {"message": "Code MFA envoyé à votre adresse email."}
    except Utilisateur.DoesNotExist:
        return {"message": "Email ou mot de passe incorrect."}


@router.post("/inscription", response=MessageSchema, auth=None)
def inscription_client(request, data: InscriptionClientSchema):
    """Inscription publique pour les citoyens (rôle CLIENT)."""
    if Utilisateur.objects.filter(email=data.email).exists():
        return {"message": "Cet email est déjà utilisé."}

    if len(data.password) < 8:
        return {"message": "Le mot de passe doit contenir au moins 8 caractères."}

    role, _ = Role.objects.get_or_create(
        nom="CLIENT",
        defaults={
            "peut_valider_reservations": False,
            "peut_modifier_carte": False,
            "peut_voir_finances": False,
            "peut_gerer_concessions": False,
            "peut_gerer_exhumations": False,
            "peut_enregistrer_paiements": False,
            "peut_exporter_donnees": False,
            "peut_voir_audit": False,
        }
    )
    user = Utilisateur.objects.create_user(
        email=data.email,
        password=data.password,
        nom=data.nom,
        prenom=data.prenom,
        telephone=data.telephone,
        adresse=data.adresse,
        role=role,
    )

    # Email de bienvenue
    try:
        from apps.notifications.services import notifier_inscription_client
        notifier_inscription_client(user)
    except Exception as e:
        print(f"Erreur notification inscription : {e}")

    return {"message": f"Compte créé avec succès. Bienvenue {user.prenom} !"}


@router.post("/verify-mfa", response=TokenSchema, auth=None)
def verify_mfa(request, data: MFASchema):
    try:
        user = Utilisateur.objects.get(email=data.email)
        session = SessionMFA.objects.filter(
            utilisateur=user,
            code=data.code,
            est_utilise=False
        ).latest("cree_le")

        if not session.est_valide:
            return {"access": "", "refresh": "", "error": "Code expiré ou invalide."}

        session.est_utilise = True
        session.save()

        user.derniere_connexion_app = timezone.now()
        user.save(update_fields=["derniere_connexion_app"])

        refresh = RefreshToken.for_user(user)
        refresh["user_id"] = user.id
        refresh["email"] = user.email
        refresh["role"] = user.role.nom if user.role else None

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "error": ""
        }
    except (Utilisateur.DoesNotExist, SessionMFA.DoesNotExist):
        return {"access": "", "refresh": "", "error": "Code invalide."}


@router.post("/refresh", auth=None)
def refresh_token(request, refresh: str):
    try:
        token = RefreshToken(refresh)
        return {"access": str(token.access_token)}
    except Exception:
        return {"error": "Token invalide."}


@router.get("/me", response=UtilisateurSchema)
def get_me(request):
    return request.auth