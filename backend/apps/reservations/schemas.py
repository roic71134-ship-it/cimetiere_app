from ninja import Schema
from typing import Optional
from datetime import date, datetime


class DefuntSchema(Schema):
    id: int
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    date_deces: date
    lieu_naissance: str
    lieu_deces: str
    nationalite: str
    sexe: str
    numero_acte_deces: str
    numero_permis_inhumer: str
    nom_famille_responsable: str
    telephone_famille: str
    notes: str

    class Config:
        from_attributes = True


class DefuntCreateSchema(Schema):
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    date_deces: date
    lieu_naissance: str = ""
    lieu_deces: str = ""
    nationalite: str = "Congolaise"
    sexe: str = "M"
    numero_acte_deces: str = ""
    numero_permis_inhumer: str = ""
    nom_famille_responsable: str = ""
    telephone_famille: str = ""
    notes: str = ""


class ReservationCreateSchema(Schema):
    caveau_id: int
    type_concession: str
    notes_client: str = ""
    defunt: DefuntCreateSchema


class ReservationSchema(Schema):
    id: int
    numero: str
    statut: str
    type_concession: str
    montant_total_xaf: float
    notes_client: str
    motif_refus: str
    notes_admin: str
    date_soumission: datetime
    date_validation: Optional[datetime] = None
    caveau_id: int
    client_id: int
    defunt: DefuntSchema

    class Config:
        from_attributes = True


class ValidationSchema(Schema):
    notes_admin: str = ""


class RefusSchema(Schema):
    motif_refus: str


class MessageSchema(Schema):
    message: str
    numero: str = ""