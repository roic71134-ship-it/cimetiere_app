from ninja import Schema
from typing import Optional
from datetime import date, datetime


class ConcessionSchema(Schema):
    id: int
    numero_contrat: str
    type_concession: str
    statut: str
    date_debut: date
    date_fin: Optional[date] = None
    date_alerte_renouvellement: Optional[date] = None
    nombre_renouvellements: int
    montant_initial_xaf: float
    montant_renouvellement_xaf: float
    jours_restants: Optional[int] = None
    est_expiree: bool
    alerte_expiration: bool
    notes: str
    caveau_id: int
    titulaire_id: int

    class Config:
        from_attributes = True


class RenouvellementSchema(Schema):
    montant_xaf: float
    notes: str = ""


class ResiliationSchema(Schema):
    motif_resiliation: str


class MessageSchema(Schema):
    message: str
    numero_contrat: str = ""