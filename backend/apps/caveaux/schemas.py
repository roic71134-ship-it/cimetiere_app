from ninja import Schema
from typing import Optional


class CaveauSchema(Schema):
    id: int
    reference: str
    numero: int
    statut: str
    couleur_carte: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    longueur_m: float
    largeur_m: float
    profondeur_m: float
    type_concession_autorise: str
    est_accessible_pmr: bool
    capacite_corps: int
    prix_temporaire_xaf: float
    prix_trentenaire_xaf: float
    prix_perpetuelle_xaf: float
    notes: str
    bloc_id: int

    class Config:
        from_attributes = True


class CaveauGeoJSONSchema(Schema):
    type: str
    geometry: dict
    properties: dict