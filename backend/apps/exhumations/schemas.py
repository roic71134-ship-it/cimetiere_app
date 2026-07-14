from ninja import Schema
from typing import Optional
from datetime import date, datetime


class ExhumationCreateSchema(Schema):
    caveau_id: int
    defunt_id: int
    concession_id: Optional[int] = None
    motif: str
    motif_detail: str = ""
    date_exhumation_prevue: Optional[date] = None
    notes: str = ""


class ExhumationSchema(Schema):
    id: int
    numero: str
    statut: str
    motif: str
    motif_detail: str
    notes: str
    motif_refus: str
    date_demande: datetime
    date_validation: Optional[datetime] = None
    date_exhumation_prevue: Optional[date] = None
    date_exhumation_reelle: Optional[date] = None
    caveau_id: int
    defunt_id: int
    demandeur_id: int

    class Config:
        from_attributes = True


class ValidationExhumationSchema(Schema):
    notes: str = ""


class RefusExhumationSchema(Schema):
    motif_refus: str


class MessageSchema(Schema):
    message: str
    numero: str = ""