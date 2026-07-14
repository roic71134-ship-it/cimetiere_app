from ninja import Schema
from typing import Optional
from datetime import datetime


class PaiementCreateSchema(Schema):
    reservation_id: Optional[int] = None
    montant_xaf: float
    canal: str
    numero_transaction: str = ""
    notes: str = ""


class PaiementSchema(Schema):
    id: int
    reference: str
    montant_xaf: float
    canal: str
    statut: str
    numero_transaction: str
    notes: str
    date_paiement: datetime
    date_confirmation: Optional[datetime] = None
    reservation_id: Optional[int] = None
    client_id: int

    class Config:
        from_attributes = True


class MessageSchema(Schema):
    message: str
    reference: str = ""