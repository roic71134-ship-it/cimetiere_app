"""API pour la gestion financière."""
from ninja import Router, Schema
from typing import List, Optional
from datetime import date
from apps.users.models import Utilisateur
from .models import Facture, Paiement

router = Router(tags=["Finances"])


class PaiementCreateSchema(Schema):
    facture_id: int
    montant: float
    canal: str
    reference_transaction: Optional[str] = ""
    observations: Optional[str] = ""

class PaiementSchema(Schema):
    id: int
    montant: float
    canal: str
    reference_transaction: str
    date_paiement: str

class FactureSchema(Schema):
    id: int
    numero: str
    reservation_id: int
    client_nom: str
    montant_total: float
    montant_paye: float
    montant_restant: float
    statut: str
    date_emission: str
    paiements: List[PaiementSchema]

class RevenusSchema(Schema):
    total_factures: float
    total_encaisse: float
    total_restant: float
    nombre_factures: int
    nombre_payees: int


@router.get("/factures", response=List[FactureSchema])
def lister_factures(request, statut: Optional[str] = None):
    """Lister les factures."""
    if not request.user.peut_voir_finances:
        # Client voit seulement ses factures
        qs = Facture.objects.select_related(
            'reservation__client'
        ).filter(reservation__client=request.user)
    else:
        qs = Facture.objects.select_related('reservation__client').all()

    if statut:
        qs = qs.filter(statut=statut)

    result = []
    for f in qs:
        paiements = [
            {
                "id": p.id,
                "montant": float(p.montant),
                "canal": p.canal,
                "reference_transaction": p.reference_transaction,
                "date_paiement": p.date_paiement.isoformat(),
            }
            for p in f.paiements.all()
        ]
        result.append({
            "id": f.id,
            "numero": f.numero,
            "reservation_id": f.reservation_id,
            "client_nom": f.reservation.client.nom_complet(),
            "montant_total": float(f.montant_total),
            "montant_paye": float(f.montant_paye),
            "montant_restant": float(f.montant_restant),
            "statut": f.statut,
            "date_emission": f.date_emission.isoformat(),
            "paiements": paiements,
        })
    return result


@router.post("/paiements", response=PaiementSchema)
def enregistrer_paiement(request, payload: PaiementCreateSchema):
    """[ADMIN/SECRETARIAT] Enregistrer un paiement."""
    if not request.user.peut_voir_finances:
        return 403, {"message": "Accès refusé."}
    try:
        facture = Facture.objects.get(id=payload.facture_id)
    except Facture.DoesNotExist:
        return 404, {"message": "Facture introuvable."}

    if facture.statut == Facture.PAYEE:
        return 400, {"message": "Cette facture est déjà payée."}

    if payload.montant > float(facture.montant_restant):
        return 400, {"message": f"Montant supérieur au restant dû ({facture.montant_restant} FCFA)."}

    paiement = Paiement.objects.create(
        facture=facture,
        montant=payload.montant,
        canal=payload.canal,
        reference_transaction=payload.reference_transaction or "",
        observations=payload.observations or "",
        enregistre_par=request.user,
    )

    return {
        "id": paiement.id,
        "montant": float(paiement.montant),
        "canal": paiement.canal,
        "reference_transaction": paiement.reference_transaction,
        "date_paiement": paiement.date_paiement.isoformat(),
    }


@router.get("/revenus", response=RevenusSchema)
def tableau_revenus(request):
    """[ADMIN/SECRETARIAT] Dashboard financier."""
    if not request.user.peut_voir_finances:
        return 403, {"message": "Accès refusé."}

    from django.db.models import Sum
    from decimal import Decimal

    factures = Facture.objects.all()
    total_factures = factures.aggregate(t=Sum('montant_total'))['t'] or Decimal('0')
    total_encaisse = factures.aggregate(t=Sum('montant_paye'))['t'] or Decimal('0')

    return {
        "total_factures": float(total_factures),
        "total_encaisse": float(total_encaisse),
        "total_restant": float(total_factures - total_encaisse),
        "nombre_factures": factures.count(),
        "nombre_payees": factures.filter(statut=Facture.PAYEE).count(),
    }
