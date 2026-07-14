from ninja import Schema
from typing import Optional


class LoginSchema(Schema):
    email: str
    password: str


class MFASchema(Schema):
    email: str
    code: str


class TokenSchema(Schema):
    access: str
    refresh: str
    error: str = ""


class MessageSchema(Schema):
    message: str


class RoleSchema(Schema):
    id: int
    nom: str
    peut_valider_reservations: bool
    peut_modifier_carte: bool
    peut_voir_finances: bool
    peut_gerer_concessions: bool
    peut_gerer_exhumations: bool
    peut_enregistrer_paiements: bool
    peut_exporter_donnees: bool
    peut_voir_audit: bool


class UtilisateurSchema(Schema):
    id: int
    email: str
    nom: str
    prenom: str
    telephone: str
    adresse: str
    est_actif: bool
    mfa_active: bool
    role: Optional[RoleSchema] = None

    class Config:
        from_attributes = True