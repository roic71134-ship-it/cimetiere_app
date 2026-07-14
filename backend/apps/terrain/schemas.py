from ninja import Schema
from typing import Optional


class CimetiereSchema(Schema):
    id: int
    nom: str
    adresse: str
    ville: str
    pays: str
    telephone: str
    email_contact: str
    superficie_m2: float
    taille_std_longueur: float
    taille_std_largeur: float
    taille_std_profondeur: float
    est_actif: bool

    class Config:
        from_attributes = True


class ZoneSchema(Schema):
    id: int
    nom: str
    code: str
    type_zone: str
    description: str
    couleur_carte: str
    est_active: bool
    ordre_affichage: int
    cimetiere_id: int

    class Config:
        from_attributes = True


class BlocSchema(Schema):
    id: int
    nom: str
    code: str
    capacite_theorique: int
    est_actif: bool
    ordre_affichage: int
    zone_id: int
    reference: str

    class Config:
        from_attributes = True