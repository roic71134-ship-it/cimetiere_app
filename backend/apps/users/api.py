"""API d'authentification avec MFA."""
from ninja import Router, Schema
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime, timedelta
import jwt
import random
import string
from django.conf import settings
from django.core.mail import send_mail
from typing import Optional

from .models import Utilisateur

router = Router(tags=["Authentification"])


# ─── Schémas ───────────────────────────────────────────────────────────────────

class LoginSchema(Schema):
    email: str
    password: str

class MFAVerifySchema(Schema):
    email: str
    code: str

class RegisterSchema(Schema):
    email: str
    password: str
    nom: str
    prenom: str
    telephone: Optional[str] = ""
    role: Optional[str] = "client"

class TokenSchema(Schema):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    nom_complet: str

class MessageSchema(Schema):
    message: str

class UserSchema(Schema):
    id: int
    email: str
    nom: str
    prenom: str
    role: str
    telephone: str


# ─── Utilitaires ───────────────────────────────────────────────────────────────

def generer_token_jwt(user: Utilisateur) -> str:
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generer_code_mfa() -> str:
    return ''.join(random.choices(string.digits, k=6))


def envoyer_code_mfa(user: Utilisateur, code: str):
    send_mail(
        subject="[Cimetière] Votre code de vérification",
        message=f"""
Bonjour {user.prenom},

Votre code de vérification MFA est : {code}

Ce code expire dans 10 minutes.

Cordialement,
Administration du Cimetière
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response=MessageSchema, auth=None)
def login(request, payload: LoginSchema):
    """Étape 1 : Vérification email/mot de passe, envoi du code MFA."""
    user = authenticate(request, username=payload.email, password=payload.password)
    if not user:
        return 401, {"message": "Email ou mot de passe incorrect."}

    code = generer_code_mfa()
    user.mfa_code = code
    user.mfa_code_expiry = timezone.now() + timedelta(minutes=10)
    user.save()

    envoyer_code_mfa(user, code)
    return {"message": f"Code MFA envoyé à {user.email}. Vérifiez votre boîte mail."}


@router.post("/verify-mfa", response=TokenSchema, auth=None)
def verify_mfa(request, payload: MFAVerifySchema):
    """Étape 2 : Vérification du code MFA et émission du JWT."""
    try:
        user = Utilisateur.objects.get(email=payload.email)
    except Utilisateur.DoesNotExist:
        return 404, {"message": "Utilisateur introuvable."}

    if user.mfa_code != payload.code:
        return 400, {"message": "Code MFA incorrect."}

    if timezone.now() > user.mfa_code_expiry:
        return 400, {"message": "Code MFA expiré. Veuillez vous reconnecter."}

    # Réinitialiser le code
    user.mfa_code = ""
    user.save()

    token = generer_token_jwt(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "nom_complet": user.nom_complet(),
    }


@router.post("/register", response=MessageSchema, auth=None)
def register(request, payload: RegisterSchema):
    """Inscription d'un nouveau client."""
    if Utilisateur.objects.filter(email=payload.email).exists():
        return 400, {"message": "Cet email est déjà utilisé."}

    # Seuls les clients peuvent s'inscrire via l'API publique
    role = "client"

    Utilisateur.objects.create_user(
        email=payload.email,
        password=payload.password,
        nom=payload.nom,
        prenom=payload.prenom,
        telephone=payload.telephone or "",
        role=role,
    )
    return {"message": "Compte créé avec succès. Vous pouvez maintenant vous connecter."}


@router.get("/me", response=UserSchema)
def get_me(request):
    """Récupérer les informations de l'utilisateur connecté."""
    user = request.user
    return {
        "id": user.id,
        "email": user.email,
        "nom": user.nom,
        "prenom": user.prenom,
        "role": user.role,
        "telephone": user.telephone,
    }


@router.get("/utilisateurs", response=list[UserSchema])
def lister_utilisateurs(request):
    """[ADMIN] Lister tous les utilisateurs."""
    if request.user.role != Utilisateur.ADMIN:
        return 403, {"message": "Accès refusé."}
    return list(Utilisateur.objects.all().values(
        "id", "email", "nom", "prenom", "role", "telephone"
    ))
