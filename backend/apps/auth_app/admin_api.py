from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Utilisateur, Role
from ninja import Schema
from typing import Optional

router = Router()


class UtilisateurCreateSchema(Schema):
    email: str
    password: str
    nom: str
    prenom: str
    telephone: str = ""
    adresse: str = ""
    role_nom: str = "CLIENT"


class UtilisateurUpdateSchema(Schema):
    nom: str = ""
    prenom: str = ""
    telephone: str = ""
    adresse: str = ""
    role_nom: str = ""
    est_actif: bool = True


class UtilisateurListSchema(Schema):
    id: int
    email: str
    nom: str
    prenom: str
    telephone: str
    est_actif: bool
    role_nom: Optional[str] = None

    class Config:
        from_attributes = True


class MessageSchema(Schema):
    message: str


@router.get("/utilisateurs", response=list[UtilisateurListSchema])
def liste_utilisateurs(request):
    if not request.auth.est_admin:
        return []
    return Utilisateur.objects.select_related("role").all()


@router.post("/utilisateurs", response=MessageSchema)
def creer_utilisateur(request, data: UtilisateurCreateSchema):
    if not request.auth.est_admin:
        return {"message": "Permission refusée."}

    if Utilisateur.objects.filter(email=data.email).exists():
        return {"message": "Cet email est déjà utilisé."}

    role, _ = Role.objects.get_or_create(nom=data.role_nom)
    user = Utilisateur.objects.create_user(
        email=data.email,
        password=data.password,
        nom=data.nom,
        prenom=data.prenom,
        telephone=data.telephone,
        adresse=data.adresse,
        role=role,
    )
    return {"message": f"Utilisateur {user.nom_complet} créé avec succès."}


@router.patch("/utilisateurs/{user_id}", response=MessageSchema)
def modifier_utilisateur(request, user_id: int, data: UtilisateurUpdateSchema):
    if not request.auth.est_admin:
        return {"message": "Permission refusée."}

    user = get_object_or_404(Utilisateur, id=user_id)

    if data.nom:
        user.nom = data.nom
    if data.prenom:
        user.prenom = data.prenom
    if data.telephone:
        user.telephone = data.telephone
    if data.adresse:
        user.adresse = data.adresse
    if data.role_nom:
        role, _ = Role.objects.get_or_create(nom=data.role_nom)
        user.role = role
    user.est_actif = data.est_actif
    user.save()

    return {"message": f"Utilisateur {user.nom_complet} modifié avec succès."}


@router.delete("/utilisateurs/{user_id}", response=MessageSchema)
def desactiver_utilisateur(request, user_id: int):
    if not request.auth.est_admin:
        return {"message": "Permission refusée."}

    user = get_object_or_404(Utilisateur, id=user_id)
    user.est_actif = False
    user.save()

    return {"message": f"Compte {user.email} désactivé."}